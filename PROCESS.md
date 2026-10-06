# AI Development Process

## Purpose and reporting rules

This journal records actual collaboration with Codex, decisions, user interventions, validation, and time. It is not a retrospective claim that the application already exists. Planning estimates are not measured execution time. Record secrets and private source content nowhere in this journal.

## Planning discussion — historical summary

The user asked how a senior full-stack AI engineer should approach the assignment, including scalability, DDD, graph persistence, observability, evaluation, and README trade-offs. The discussion settled on a scoped modular monolith with persisted graph data, evidence-linked analyses, and an optional graph visualization.

User refinements established English project content, uv for Python, npm for React, a common Ollama/Groq provider interface selected through `.env`, prompt files selected through configuration, process documentation, and commits after meaningful completed blocks rather than minor edits. The user explicitly limited the current execution to documentation and a local repository.

Codex prepared and revised the plan interactively. Earlier planning occurred in Plan mode, so no files were created then. No subagents were used. Precise timestamps and focused time for that historical discussion were not measured and are not reconstructed.

## Documentation preparation — 2026-10-06

- **Goal:** create the approved English documentation package and initialize a local Git repository without implementing the application.
- **Instruction summary:** implement the supplied documentation plan; preserve original inputs; define clean architecture, lightweight DDD, configurable providers/prompts, reliability, AI evaluation, observability, tooling, and commit rules.
- **Acceptance criteria:** required documents exist, local links resolve, inputs remain byte-identical, plan and README distinguish future work from implemented behavior, and one local documentation commit exists without a remote.
- **Execution started:** 09:11:01 UTC (12:11:01 Asia/Jerusalem), read from the clock during initial inspection.
- **Codex autonomy:** inspected the assignment and seed shape; chose documentation organization and concrete MVP defaults for bounded execution, evidence, HTTP behavior, and prompt provenance within the approved scope.
- **User interventions during execution:** none at the time of this entry; language, tooling, provider, scope, and commit preferences were supplied during planning.
- **Work:** created IMPLEMENTATION_PLAN, AGENTS, README, this journal, and .gitignore. No application code, dependencies, prompt content, or inference integrations were created.
- **Validation:** Python checks passed for local Markdown links, absence of Cyrillic in authored documents, balanced code fences, ten seed records, and unchanged SHA-256 hashes of both original inputs. Reviewed documentation for scope/configuration consistency. Git initialization initially hit the filesystem sandbox boundary; the approved escalated retry succeeded. Application tests and live inference were not run because no application exists. Git ignore checks confirmed exclusion of local secrets/runtime files while retaining .env.example. Staged review showed exactly the seven intended files; git diff --cached --check passed and no remote was configured. Commit follows this entry.
- **Time:** initial inspection through documentation checks took 2 minutes 58 seconds (09:11:01–09:13:59 UTC); Git finalization follows. This is elapsed tool/session time, not a claim about focused human effort. Historical planning time remains unmeasured.
- **Commit:** intended message `docs: establish implementation plan and agent workflow`; the actual reference will be available in Git history and can be recorded in the next journal update.

## Template for subsequent blocks

### <Logical block name> — <date>

- **Goal / acceptance criteria:**
- **Actual instructions or accurate prompt summary:**
- **Start / end / elapsed time:** identify measurement method; separate estimates from measured time.
- **Codex work and autonomous decisions:**
- **User corrections / interventions:**
- **Changes and reasons:**
- **Validation commands and observed results:**
- **AI evaluation:** provider/model/prompt versions, actual outcomes, or explicit reason not run.
- **Limitations / skipped checks / remaining work:**
- **Outcome:** completed, partial, or blocked with evidence.
- **Commit:** intended message before commit; actual reference in a subsequent entry after it exists.

## Application implementation — 2026-10-06

- **Goal:** implement the mandatory MVP with actual provider adapters, persisted evidence, responsive UI, and deterministic verification.
- **User instruction:** begin implementation; subagents are authorized for frontend/backend/database; a local Llama/Ollama model is not installed.
- **Start:** 09:25:27 UTC (12:25:27 Asia/Jerusalem), observed clock reading shortly after delegation.
- **Delegation:** backend agent owns backend configuration, domain contracts, SQLite, ingestion, providers, prompts, orchestration, API, and tests. Frontend agent owns React/Vite UI, integration, and frontend tests. Root agent owns cross-component contracts, review, evaluation artifacts, documentation, and commits. No nested agents requested.
- **Prompt summaries:** both agents received the approved plan and common HTTP/result shapes; instructed to keep changes within owned directories, run meaningful checks, avoid mock application results, and leave Git commits to the root agent.
- **Acceptance:** supported ingestion and UI flows work; absent inference is visible; no silent provider switching; tests pass; limitations and live evaluation status are explicit.
- **Initial environment:** uv and npm available; ollama executable not found. No model installation or paid access is assumed.
- **Validation/outcome:** implementation in progress.

### Evaluation baseline and collector

- **Goal:** define reviewable expectations and collect real analysis outputs without implying validated model quality.
- **Work:** root agent authored ten seed cases, manual review dimensions, adversarial follow-up cases, and an API collector that submits runs and stores provenance/results for human review. Local reports are excluded from Git because they contain source content.
- **Checks:** `python3 evaluations/run.py --help`, `python3 -m py_compile evaluations/run.py`, seed/case ID equality, and `git diff --check` passed. No actual model calls were made; local inference is unavailable.
- **Outcome:** evaluation tooling baseline complete; live quality evaluation pending installation/configuration. Keyword/risk-level screens are not treated as semantic correctness.
- **Commit:** `test: add seed evaluation protocol and real-run collector`.

### Backend pipeline, persistence, and system prompts

- **Delegation outcome:** backend agent implemented domain contracts, file normalization, SQLite, provider adapters, prompt files, bounded queue, API, and an initial 15-test suite. Root reviewed the changes and added integration coverage.
- **Corrections:** submission routes were changed to async to keep asyncio queue operations on its owning loop; SQLite connections now close explicitly; provider-specific payloads/parsing were separated into adapters; entity evidence is persisted; prompt snapshots are withheld from HTTP responses; entity matching requires a complete email-shaped identifier rather than any label containing @.
- **Root additions:** Ruff tooling/formatting, failure-stage timing metadata, API worker completion, actual seed restart idempotency, valid text-layer PDF, EML attachments/skipped attachment warning, and configuration validation tests.
- **Validation:** uv sync --locked, Ruff check/format check, and 19 pytest cases passed. One upstream Starlette TestClient deprecation warning remains; it does not fail tests. Runtime API starts and health responds with Ollama configuration despite the provider being unavailable.
- **Prompt evaluation:** the two versioned system prompts are initial unvalidated candidates. No successful model inference has occurred; the installed model is absent. Deterministic tests verify contracts/failure behavior, not prompt quality.
- **Design simplification:** SQLite stores normalized message/source data and extraction/assessment/provenance as JSON payloads alongside relational entities, mentions, and relationships, rather than separate tables for every value object. Retry starts both stages afresh; previous partial extraction remains available in history. These are deliberate MVP deviations, documented in README.
- **Outcome:** backend logical block implemented and deterministic gates passed; live provider quality remains unverified.
- **Commit:** `feat: implement persisted email analysis pipeline and providers`.

### Responsive frontend and API integration

- **Delegation outcome:** frontend agent built React/Vite components for inbox, detail, badges, ingestion, search/filtering, polling, partial output, previous results, and retry. CSS Modules use system fonts with no remote font dependency.
- **Root review:** upgraded outdated Vite/Vitest tooling after the initial dependency audit found six advisories; the updated dependency tree reported zero. Added queue-saturation notice preservation so a persisted message opens without hiding the failed submission; added multipart upload coverage and ignored TypeScript build caches.
- **Browser checks:** actual localhost API and frontend were exercised in Codex's in-app browser. Verified seed inbox, original content, retry, new pasted message persistence, TXT upload/original-text persistence, and visible unavailable-provider failure. Measured CSS viewport widths 1440 and 390 with scrollWidth equal to innerWidth; also observed the narrower 325 layout without overflow. Console error inspection returned no errors. No successful real-model assessment is claimed.
- **Validation:** frontend agent verified npm ci --offline, formatting, build, and four initial UI tests. Root repeated build/tests after review and added queue/error and upload coverage; six UI tests passed, including multipart upload and queue-saturation notice preservation. A synthetic file chooser test initially hit jsdom native validation; dispatching submit after verifying the selected filename resolved the test-environment limitation, and actual browser TXT upload independently passed.
- **Environment:** localhost binds and dependency downloads required sandbox escalation. Vite selected 5174 because 5173 was already occupied; unrelated services were left untouched. The backend runs on 8000.
- **Outcome:** integrated mandatory UI implemented; aggregate interactive graph remains deferred. Screenshots were captured outside Git for review.
- **Commit:** `feat: add responsive evidence-linked mail review interface`.

### HTML email ingestion compatibility

- **Trigger:** root review identified that rejecting HTML-only EML excluded a common email representation despite the required EML ingestion capability.
- **Work:** added standard-library HTML-to-text normalization for email bodies and textual attachments, retaining link targets as inert text and excluding head/script/style content. No browser rendering, URL fetching, or execution occurs.
- **Validation:** 20 backend tests and Ruff checks passed, including an HTML-only email with a reset link and hidden script/style content. No new dependency was added.
- **Outcome:** HTML-only EML support implemented; normalized source text is the evidence basis. This does not establish semantic correctness or preserve a binary MIME archive.
- **Commit:** `fix: normalize HTML email bodies without rendering source content`.
