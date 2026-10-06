# Mail Risk Intelligence

A planned local full-stack tool for reviewing email risk, extracting facts, and exploring evidence-linked entities and relationships for a fictional Arcline compliance team.

## Current status

**Documentation preparation only. The application has not been implemented.** There are no runnable services, provider integrations, application tests, or model evaluation results yet. This repository preserves the supplied assignment and ten-email dataset.

- [Original assignment](candidate_task_brief.md)
- [Seed dataset](mock_mailbox_data.json)
- [Detailed implementation plan](docs/IMPLEMENTATION_PLAN.md)
- [Codex instructions](AGENTS.md)
- [AI workflow journal](PROCESS.md)

## Planned stack and workflow

React + TypeScript + Vite with npm and CSS Modules; Python + FastAPI with uv; SQLite persistence; configurable Ollama and Groq adapters. Commit `uv.lock` and `package-lock.json` during implementation. Verified run commands and exact model selection will be added after implementation; none are claimed here.

The backend will be a modular monolith with inward dependencies and separate mailbox ingestion, analysis, persistence, and graph projection responsibilities. Two typed stages perform extraction and risk/graph assessment with validation between them. Evidence and run history are persisted. Graph entities/relationships live in SQLite; visualization state lives in browser memory.

Ollama will be the default and require no API key. Groq will be an explicitly configured alternative using the user's key; current availability and model support must be checked during implementation. Both agents use the selected provider. Failures remain visible and retryable where appropriate, without silent provider switching or mock results.

System prompts will be versioned files selected through `AGENT_A_SYSTEM_PROMPT_PATH` and `AGENT_B_SYSTEM_PROMPT_PATH` in backend `.env`. Each run will retain prompt/model/schema provenance. `.env.example`, prompt files, and lockfiles are future implementation deliverables.

## Assumptions and boundaries

One trusted local analyst; no authentication; assessment is triage rather than a verdict. Source content is untrusted. PDFs require an extractable text layer; OCR is excluded. Risk reasoning operates per email, including attachment evidence. The per-email entity/relationship panel is mandatory; an interactive aggregate graph is optional.

The MVP will process one analysis at a time inside the API process. Persisted results survive restart, but unfinished execution will be marked interrupted and require retry. This is not a durable worker queue. Failed analysis is not risk `none`, and failed reanalysis does not discard previous successful results.

## Planned trade-offs

| Decision | Reason | Limitation |
| --- | --- | --- |
| Modular monolith | Clear responsibilities within a small delivery budget | Shared deployment |
| SQLite | Easy persistent local setup | Write contention at higher scale |
| Two sequential LLM stages | Inspectable intermediate extraction | Latency and propagated extraction errors |
| Ollama default | Local operation without paid credentials | Hardware and model-download requirements |
| Conservative entity matching | Avoid unsupported identity merges | Possible duplicate entities |
| SQL-backed graph | Simple evidence-linked projection | Limited complex traversal scalability |

Evidence validation checks source references, not whether an assessment is objectively correct. Structured operational logs and deterministic engineering tests will be kept separate from real AI evaluation. The ten seed emails provide regression examples, not general accuracy evidence.

## With more time

Introduce durable jobs and restart-safe workers; move to PostgreSQL when deployment or contention warrants it; manage inference capacity; add filtered graph queries and deeper evaluation; provide analyst review/audit history and external-access controls. Add operational metrics/tracing as deployment needs emerge. OCR and cross-email reasoning require explicit product scope. Microservices and graph databases need measured justification.

## Delivery and process

The implementation target is 5–6 focused hours, with actual time recorded separately from documentation preparation. Codex work, user corrections, checks, and limitations belong in [PROCESS.md](PROCESS.md). Commit completed significant logical blocks, including meaningful UI components, provider work, and substantive prompt changes, rather than every small edit.
