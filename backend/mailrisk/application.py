"""Bounded in-process analysis orchestration through small ports."""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timezone

from pydantic import ValidationError

from .domain import AppError, Assessment, Extraction, validate_evidence

logger = logging.getLogger("mailrisk.analysis")


class AnalysisService:
    def __init__(self, store, provider, settings):
        self.store, self.provider, self.settings = store, provider, settings
        self.queue = asyncio.Queue(maxsize=20)
        self.task = None

    async def start(self):
        self.store.interrupt()
        self.task = asyncio.create_task(self.worker())

    async def stop(self):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    def submit(self, message_id):
        self.store.message(message_id)
        latest = self.store.latest(message_id)
        if latest and latest["status"] in ("queued", "extracting", "assessing"):
            return latest["id"]
        if self.queue.full():
            raise AppError(
                "rate_limit",
                "The analysis queue is full. Retry this email later.",
                True,
                429,
            )
        prompts = [
            self.settings.path(path).read_text(encoding="utf-8")
            for path in (
                self.settings.agent_a_system_prompt_path,
                self.settings.agent_b_system_prompt_path,
            )
        ]
        provenance = {
            "provider": self.settings.llm_provider,
            "model": self.settings.model,
            "schema_version": "1",
            "policy_version": "1",
            "prompt_snapshots": prompts,
            "prompt_hashes": [
                hashlib.sha256(prompt.encode()).hexdigest() for prompt in prompts
            ],
        }
        run_id = self.store.new_run(message_id, provenance)
        self.queue.put_nowait(run_id)
        return run_id

    async def stage(self, run, name, schema, input, sources, instructions):
        started = time.monotonic()
        for attempt in range(1 + self.settings.llm_max_retries):
            try:
                raw, usage = await asyncio.wait_for(
                    self.provider.generate_structured(
                        instructions,
                        input,
                        schema.model_json_schema(),
                        self.settings.llm_timeout_seconds,
                    ),
                    timeout=self.settings.llm_timeout_seconds,
                )
                try:
                    result = schema.model_validate_json(raw)
                    validate_evidence(result, sources)
                except (ValidationError, ValueError):
                    raise AppError(
                        "invalid_output",
                        "The model output did not match the required schema.",
                        True,
                    ) from None
                duration = round((time.monotonic() - started) * 1000)
                self.store.update_run(
                    run["id"],
                    **{
                        name + "_metadata": {
                            "duration_ms": duration,
                            "attempts": attempt + 1,
                            "usage": usage,
                        }
                    },
                )
                logger.info(
                    json.dumps(
                        {
                            "message_id": run["message_id"],
                            "analysis_run_id": run["id"],
                            "stage": name,
                            "attempt": attempt + 1,
                            "outcome": "success",
                            "provider": run["provider"],
                            "model": run["model"],
                            "prompt_hash": run["prompt_hashes"][
                                0 if name == "extraction" else 1
                            ],
                            "duration_ms": duration,
                        }
                    )
                )
                return result
            except asyncio.TimeoutError:
                error = AppError("timeout", "The model request timed out.", True)
            except AppError as caught:
                error = caught
            logger.info(
                json.dumps(
                    {
                        "message_id": run["message_id"],
                        "analysis_run_id": run["id"],
                        "stage": name,
                        "attempt": attempt + 1,
                        "outcome": "failure",
                        "error_code": error.code,
                        "provider": run["provider"],
                        "model": run["model"],
                        "duration_ms": round((time.monotonic() - started) * 1000),
                    }
                )
            )
            self.store.update_run(
                run["id"],
                **{
                    name + "_metadata": {
                        "duration_ms": round((time.monotonic() - started) * 1000),
                        "attempts": attempt + 1,
                        "error_code": error.code,
                    }
                },
            )
            if not error.retryable or attempt == self.settings.llm_max_retries:
                raise error
            if error.code == "invalid_output":
                instructions += "\nThe previous output was invalid. Return only schema-conforming JSON with exact source evidence."
            else:
                await asyncio.sleep(getattr(error, "retry_after", 1))

    async def process(self, run_id):
        run = self.store.run(run_id)
        message = self.store.message(run["message_id"])
        try:
            self.store.update_run(run_id, status="extracting")
            extraction = await self.stage(
                run,
                "extraction",
                Extraction,
                {
                    "metadata": {
                        key: message[key]
                        for key in ("sender", "recipients", "date", "subject")
                    },
                    "sources": message["sources"],
                },
                message["sources"],
                run["prompt_snapshots"][0],
            )
            self.store.update_run(
                run_id, status="assessing", extraction=extraction.model_dump()
            )
            assessment = await self.stage(
                run,
                "assessment",
                Assessment,
                {"extraction": extraction.model_dump(), "sources": message["sources"]},
                message["sources"],
                run["prompt_snapshots"][1],
            )
            self.store.complete(run_id, assessment.model_dump())
        except AppError as error:
            self.store.update_run(
                run_id,
                status="failed",
                error=error.payload(),
                finished_at=datetime.now(timezone.utc).isoformat(),
            )
        except Exception:
            # Do not log exception payloads that might include private source/model content.
            self.store.update_run(
                run_id,
                status="failed",
                error={
                    "code": "internal",
                    "message": "Analysis could not be completed. Retry or inspect the server configuration.",
                    "retryable": True,
                },
            )
            logger.error(
                json.dumps({"analysis_run_id": run_id, "error_code": "internal"})
            )

    async def worker(self):
        while True:
            run_id = await self.queue.get()
            try:
                await self.process(run_id)
            finally:
                self.queue.task_done()
