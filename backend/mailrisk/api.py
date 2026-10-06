"""HTTP delivery and lifecycle composition root."""

import json
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .application import AnalysisService
from .domain import AppError
from .ingestion import MAX_UPLOAD, normalize, upload
from .providers import create_provider
from .settings import Settings
from .storage import SQLiteStore


class TextInput(BaseModel):
    raw_text: str = Field(min_length=1, max_length=100_000)


def create_app(settings=None, provider=None):
    settings = settings or Settings()
    for path in (
        settings.agent_a_system_prompt_path,
        settings.agent_b_system_prompt_path,
        settings.agent_repair_system_prompt_path,
    ):
        if (
            not settings.path(path).is_file()
            or not settings.path(path).read_text(encoding="utf-8").strip()
        ):
            raise RuntimeError("Configure readable, non-empty system prompt files.")
    if settings.llm_provider not in ("ollama", "groq"):
        raise RuntimeError("LLM_PROVIDER must be ollama or groq.")
    if not settings.model:
        raise RuntimeError("Configure the selected provider model.")
    if settings.llm_provider == "groq" and not settings.groq_api_key:
        raise RuntimeError("Set GROQ_API_KEY in backend/.env before selecting Groq.")
    store = SQLiteStore(settings.path(settings.database_path))
    service = AnalysisService(store, provider or create_provider(settings), settings)

    @asynccontextmanager
    async def lifespan(app):
        await service.start()
        seed_path = settings.path(settings.seed_path)
        if seed_path.is_file():
            for seed in json.loads(seed_path.read_text())["emails"]:
                headers = "\n".join(
                    [
                        "From: " + seed["from"],
                        "To: " + ", ".join(seed["to"]),
                        "Date: " + seed["date"],
                        "Subject: " + seed["subject"],
                    ]
                )
                content = normalize(
                    headers + "\n\n" + seed["body"],
                    seed.get("attachments"),
                    {
                        "sender": seed["from"],
                        "recipients": seed["to"],
                        "date": seed["date"],
                        "subject": seed["subject"],
                    },
                )
                _, inserted = store.ingest(content, seed["id"])
                if inserted:
                    service.submit(seed["id"])
        yield
        await service.stop()

    app = FastAPI(title="Mail Risk Intelligence", lifespan=lifespan)
    app.state.store, app.state.service = store, service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins.split(","),
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.exception_handler(AppError)
    async def app_error(request, error):
        return JSONResponse(
            status_code=error.status, content={"error": error.payload()}
        )

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "provider": settings.llm_provider,
            "model": settings.model,
            "configuration_error": "GROQ_API_KEY is missing"
            if settings.llm_provider == "groq" and not settings.groq_api_key
            else None,
        }

    @app.get("/emails")
    def emails():
        return store.inbox()

    @app.get("/emails/{message_id}")
    def detail(message_id: str):
        result = store.detail(message_id)
        # Prompt snapshots are persisted for reproducibility, never delivered to the browser.
        for key in ("latest_run", "selected_run"):
            if result[key]:
                result[key].pop("prompt_snapshots", None)
        return result

    def ingest(content):
        message_id, _ = store.ingest(content)
        try:
            run_id = service.submit(message_id)
        except AppError as error:
            return JSONResponse(
                status_code=error.status,
                content={"message_id": message_id, "error": error.payload()},
            )
        return {"message_id": message_id, "analysis_run_id": run_id}

    @app.post("/emails", status_code=202)
    async def add_email(input: TextInput):
        return ingest(normalize(input.raw_text))

    @app.post("/emails/upload", status_code=202)
    async def add_file(file: Annotated[UploadFile, File()]):
        data = await file.read(MAX_UPLOAD + 1)
        await file.close()
        return ingest(upload(file.filename or "", data))

    @app.post("/emails/{message_id}/analyses", status_code=202)
    async def analyze(message_id: str):
        return {"message_id": message_id, "analysis_run_id": service.submit(message_id)}

    @app.get("/analyses/{run_id}")
    def run(run_id: str):
        result = store.run(run_id)
        result.pop("prompt_snapshots", None)
        return result

    @app.get("/graph")
    def graph():
        return store.graph()

    return app


logging.basicConfig(level=logging.INFO, format="%(message)s")
app = create_app()
