# Agent Instructions

## Scope and language

Read `candidate_task_brief.md`, `docs/IMPLEMENTATION_PLAN.md`, `README.md`, and the latest `PROCESS.md` entries before implementation. Inspect relevant source files before changing them. The current repository preparation does not authorize application implementation by itself.

All project content must be in English: Markdown, instructions, comments, UI text, API messages, tests, and commit messages. Answer the user in Russian and provide a short summary after completing a task. User instructions take precedence over this file.

## Engineering workflow

- Work in bounded logical blocks with explicit acceptance criteria. Complete mandatory assignment requirements before optional graph work.
- Use uv for Python dependencies, environments, and commands; commit `uv.lock`. Use npm for frontend dependencies and scripts; commit `package-lock.json`.
- Preserve inward dependencies: domain/application logic must not depend on FastAPI, database implementations, or provider SDKs. Use small useful interfaces rather than generic frameworks.
- Keep ingestion, analysis, persistence, delivery, and graph projection responsibilities separate within a modular monolith.
- Use the configured LLM provider through the shared interface. Never silently switch providers or substitute mock output in the application.
- Preserve evidence, analysis provenance, and prior successful results. Processing failure must never be presented as risk `none`.
- Run relevant checks; do not create low-value tests that simply mirror implementation. Report skipped checks and material limitations honestly.
- Do not expose email content, prompts, credentials, or raw provider responses in routine logs.

## System prompts

Store prompts as version-controlled UTF-8 files under `backend/prompts/`. Select them through `AGENT_A_SYSTEM_PROMPT_PATH`, `AGENT_B_SYSTEM_PROMPT_PATH`, and `AGENT_REPAIR_SYSTEM_PROMPT_PATH` in backend configuration; relative paths resolve against `backend/`.

Validate prompt files at startup. Snapshot/hash prompts per analysis run and keep source content separate from instructions. A substantive prompt change requires relevant actual evaluation, or an explicit record that evaluation could not run and why. Keep prompt changes and their evaluation report together in one logical commit. Do not store API keys or private user data in prompts.

## PROCESS.md

Add an entry at the start of each substantial block and update it on completion. Record:

- Goal and acceptance criteria.
- Actual prompt/instructions or an accurate summary.
- Work delegated to Codex and its autonomous decisions.
- User interventions, corrections, and resulting changes.
- Commands/checks, actual results, skipped checks, and limitations.
- Measured elapsed time when available; distinguish it from estimates and focused human time.
- Outcome and commit reference after the commit exists.

Never invent prompts, timestamps, test outcomes, corrections, or subagent use. Do not reconstruct precise timings from memory. Use subagents only when explicitly authorized. Keep journal content factual and omit secrets/private source content.

## Git commit policy

Create a commit after completing a significant logical block and its relevant checks. Examples: a meaningful integrated React component, provider adapter, ingestion capability, materially changed system prompt, or reliability fix. Foundation, ingestion/storage, AI workflow, integrated API/UI, and final verification are milestone checkpoints.

Do not commit every file, scaffold fragment, formatting edit, or intermediate correction. Group small related edits into their completed block. Avoid splitting one coherent change merely to increase commit count.

Before committing:

1. Update `PROCESS.md` with outcomes and validation.
2. Review `git diff`, staged diff, and file scope.
3. Stage only relevant files, including applicable lockfiles and documentation.
4. Exclude secrets, `.env`, local databases, uploads, and generated artifacts.
5. Use a concise English commit message describing the completed behavior.

Record commit references in the next journal update instead of amending solely to insert a commit's own hash. Clearly identify incomplete or unverified work; do not label it completed. Do not push, publish, rewrite history, or add a remote without separate user authorization.
