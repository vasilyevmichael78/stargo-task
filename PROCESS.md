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
