"""Bounded in-process analysis orchestration through small ports."""

import asyncio
import hashlib
import json
import logging
import time
from datetime import datetime, timezone

from pydantic import ValidationError

from .domain import (
    AppError,
    Assessment,
    Extraction,
    align_evidence_whitespace,
    validate_evidence,
)

logger = logging.getLogger("mailrisk.analysis")


class AnalysisService:
    def __init__(self, store, provider, settings):
        self.store, self.provider, self.settings = store, provider, settings
        self.store.ensure_risk_context(
            self.settings.path(self.settings.risk_context_path)
        )
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
                self.settings.agent_repair_system_prompt_path,
            )
        ]
        context_revision = self.store.active_risk_context()
        risk_context = context_revision["catalog"]
        provenance = {
            "provider": self.settings.llm_provider,
            "model": self.settings.model,
            "schema_version": "1",
            "policy_version": risk_context["version"],
            "risk_context_snapshot": risk_context,
            "risk_context_hash": context_revision["hash"],
            "risk_context_revision_id": context_revision["revision_id"],
            "orchestration_version": "4",
            "generation_settings": {
                "temperature": 0,
                "ollama_num_ctx": self.settings.ollama_num_ctx
                if self.settings.llm_provider == "ollama"
                else None,
                "ollama_think": self.settings.ollama_think
                if self.settings.llm_provider == "ollama"
                else None,
                "timeout_seconds": self.settings.llm_timeout_seconds,
                "max_retries": self.settings.llm_max_retries,
            },
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
        history = []
        repair = None
        for attempt in range(1 + self.settings.llm_max_retries):
            attempt_started = time.monotonic()
            usage = {}
            validation_errors = []
            evidence_alignments = []
            request_input = (
                input if repair is None else {**input, "repair_context": repair}
            )
            request_instructions = instructions
            if repair is not None:
                request_instructions += "\n" + run["prompt_snapshots"][2]
            try:
                raw, usage = await asyncio.wait_for(
                    self.provider.generate_structured(
                        request_instructions,
                        request_input,
                        schema.model_json_schema(),
                        self.settings.llm_timeout_seconds,
                    ),
                    timeout=self.settings.llm_timeout_seconds,
                )
                try:
                    result = schema.model_validate_json(raw)
                except ValidationError as caught:
                    validation_errors = [
                        {
                            "path": list(item["loc"]),
                            "code": item["type"],
                            "message": item["msg"],
                        }
                        for item in caught.errors(
                            include_input=False,
                            include_context=False,
                            include_url=False,
                        )[:20]
                    ]
                    # The invalid output is bounded request-local state, not durable history.
                    repair = {
                        "previous_output": raw[:8000],
                        "previous_output_truncated": len(raw) > 8000,
                        "errors": validation_errors,
                    }
                    raise AppError(
                        "invalid_output",
                        "The model output did not match the required schema.",
                        True,
                    ) from None
                try:
                    evidence_alignments = align_evidence_whitespace(result, sources)
                    validate_evidence(result, sources)
                except AppError as caught:
                    validation_errors = getattr(caught, "validation_errors", [])
                    repair = {
                        "previous_output": raw[:8000],
                        "previous_output_truncated": len(raw) > 8000,
                        "errors": validation_errors,
                    }
                    raise
                error = None
            except asyncio.TimeoutError:
                error = AppError("timeout", "The model request timed out.", True)
            except AppError as caught:
                error = caught
            entry = {
                "attempt": attempt + 1,
                "mode": "repair" if "repair_context" in request_input else "generate",
                "outcome": "failure" if error else "success",
                "duration_ms": round((time.monotonic() - attempt_started) * 1000),
                "usage": usage,
            }
            if error:
                entry["error_code"] = error.code
            if evidence_alignments:
                entry["evidence_alignments"] = evidence_alignments
            if validation_errors:
                entry["validation_errors"] = [
                    {"path": item["path"], "code": item["code"]}
                    for item in validation_errors
                ]
            history.append(entry)
            metadata = {
                "duration_ms": round((time.monotonic() - started) * 1000),
                "attempts": attempt + 1,
                "attempt_history": history,
                "usage": usage,
            }
            if error:
                metadata["error_code"] = error.code
            self.store.update_run(run["id"], **{name + "_metadata": metadata})
            logger.info(
                json.dumps(
                    {
                        "message_id": run["message_id"],
                        "analysis_run_id": run["id"],
                        "stage": name,
                        "attempt": attempt + 1,
                        "mode": entry["mode"],
                        "outcome": entry["outcome"],
                        "evidence_alignment_count": len(evidence_alignments),
                        "error_code": error.code if error else None,
                        "provider": run["provider"],
                        "model": run["model"],
                        "policy_version": run["policy_version"],
                        "risk_context_hash": run["risk_context_hash"],
                        "repair_prompt_hash": run["prompt_hashes"][2]
                        if entry["mode"] == "repair"
                        else None,
                        "prompt_hash": run["prompt_hashes"][
                            0 if name == "extraction" else 1
                        ],
                        "duration_ms": entry["duration_ms"],
                    }
                )
            )
            if error is None:
                return result
            if not error.retryable or attempt == self.settings.llm_max_retries:
                raise error
            if error.code != "invalid_output":
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
                {
                    "extraction": extraction.model_dump(),
                    "sources": message["sources"],
                    "risk_policy_context": run["risk_context_snapshot"],
                },
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
