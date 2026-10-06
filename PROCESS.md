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
- **Validation/outcome:** implementation and deterministic checks completed; successful real inference remains pending. See delivery verification below.

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

### Delivery verification and shutdown

- **Completed checks:** 20 backend tests, six frontend tests, backend Ruff checks/formatting, frontend TypeScript/Vite production build and Prettier checks. Locked uv installation and npm ci were verified. Updated npm installation reported zero advisories. One upstream Starlette TestClient deprecation warning remains.
- **Runtime evidence:** localhost health succeeded after the final backend restart. Browser flows verified paste and TXT upload persistence, original text, retry/unavailable states, and no horizontal overflow at measured CSS widths 1440 and 390. No browser console errors were observed during the smoke check.
- **Evaluation:** actual E001 collector smoke returned failed/unavailable. No successful inference or semantic evaluation was performed; no Groq call or model installation occurred. The initial prompts and default model remain quality-unvalidated.
- **Documentation:** README now provides actual setup, configuration, APIs, implemented boundaries, trade-offs, and explicit pending validation. Local Markdown links and language checks passed. Original assignment/data SHA-256 hashes are unchanged. No remote or push was configured.
- **Commit references:** c34cd53 evaluation baseline; 3dbcea7 backend/providers/prompts; 0385ab8 responsive UI; edd7773 HTML email normalization.
- **User intervention:** the user interrupted execution twice, then requested current status and possible application shutdown. Root stopped only its backend on 8000 and Vite on 5174 gracefully. Port 5173 belongs to gate-fit-ai and was left untouched. The browser tab now points to a stopped server; restart using README when needed.
- **Time accounting:** implementation start was observed at 09:25:27 UTC; final documentation checks were observed at 09:50:26 UTC (24 minutes 59 seconds elapsed). This interval includes user interruption and parallel agent execution, excludes subsequent shutdown/finalization, and is not a measurement of focused human effort. Historical planning time is unmeasured.
- **Outcome:** application code, deterministic verification, and documentation delivered; real-model validation and optional interactive aggregate graph remain pending. Local smoke emails remain in the ignored runtime database; fresh checkout imports the original ten seeds.
- **Commit:** `docs: finalize setup and implementation verification`.

### Local Ollama installation and private configuration

- **Started:** 2026-10-06T10:06:00.373659+00:00 UTC.
- **User request:** install local Llama inference and create an ignored backend environment file; the user will supply the Groq API key separately.
- **Actions planned:** install native Ollama through Homebrew, download the configured llama3.2:3b model, verify local inference and Git exclusion. Preserve any existing private environment values.
- **Status:** in progress; no model-quality evaluation claimed.

- **Completed:** 2026-10-06T10:09:14.212002+00:00 UTC. Native Ollama 0.35.1 installed via Homebrew; llama3.2:3b downloaded successfully (approximately 2 GB). Homebrew also updated its formula metadata/dependencies and ran automatic cleanup.
- **Runtime:** Ollama is listening on 127.0.0.1:11434 and detected Apple M4 / Metal. Started with ollama serve, without configuring login autostart. Backend and frontend remain stopped.
- **Private configuration:** created backend/.env from all example variables, left GROQ_API_KEY empty, permissions 0600. git check-ignore confirms exclusion; git ls-files confirms the file is untracked. No secret values were printed.
- **Verification:** actual JSON-schema chat request returned {"status":"ok"} in 1.85 seconds, with seven output tokens. This is a provider smoke check, not an evaluation of extraction/risk quality. Full seed evaluation and Groq smoke remain pending.
- **Documentation:** updated README runtime status and made the example environment copy preserve an existing .env. No application logic changed.
- **Outcome:** requested local model and private configuration are ready.

### Llama seed quality evaluation

- **Started:** 2026-10-06T10:10:18.308840+00:00.
- **User request:** evaluate the current local Llama model on email quality.
- **Plan:** explicitly select Ollama / llama3.2:3b, run the ten seed cases through the actual two-stage pipeline, inspect original content and outputs against the existing review specification, and report pipeline reliability separately from semantic quality. No prompt or model tuning during this baseline.

- **Completed:** real collector ran 10:10:34–10:20:16 UTC (9m42s), without model/prompt/configuration tuning. Five of ten pipelines completed; accepted risk matched two of five completed cases. Two evidence failures and three assessment failures ending in timeout; eight validated extractions persisted. Codex reviewed sources, facts, risk and graph; independent human review remains pending.
- **Evidence:** ignored full report evaluations/reports/llama3.2-3b-baseline.json; sanitized committed report evaluations/LLAMA_BASELINE_2026-10-06.md includes per-case findings, latency, model ID, prompt hashes and limitations. No Groq, held-out, prompt-injection or repeatability run performed.
- **Findings:** underestimated E001/E005; false-positive E009; unsupported facts, modality changes and graph type/entailment errors. No corrections to prompts made during baseline.
- **Runtime:** backend gracefully stopped after collection; native Ollama remains running. Successful analyses and failure/partial history persist in ignored SQLite storage.
- **Outcome:** quality baseline completed; current model/configuration is unsuitable for unattended triage. Documentation updated; no application changes or new engineering tests needed.

### Prompt-only Llama quality iteration

- **Started:** 2026-10-06T10:36:52.375523+00:00.
- **User request:** improve prompts and rerun the same model before other optimizations.
- **Scope:** version both system prompts; preserve model llama3.2:3b, temperature 0, timeout 60 seconds, retry budget 1, schema and application code. Clarify evidence copying, nonempty typed facts, uncertainty, risk rubric and sparse supported graph. Use unrelated illustrative examples.
- **Evaluation caveat:** prompts are informed by observed seed failures; the next seed run is a development regression comparison, not held-out generalization evidence. Baseline commit 341068f remains available.

- **Completed:** 2026-10-06T10:50:29.206119+00:00. Real ten-case v2 experiment ran 2026-10-06T10:37:33.205655+00:00 to 2026-10-06T10:49:06.083867+00:00 (692.88 seconds elapsed).
- **Results:** 2/10 completed versus baseline 5/10; 6/10 validated extractions versus 8/10. Risk agreement was 2/2 among survivors, but complete-and-accepted coverage stayed 2/10. Four extraction evidence failures, two assessment entity-reference failures and two assessment timeouts. Both completed outputs still had semantic fact/graph errors.
- **Decision:** candidate not promoted; default prompt files restored byte-for-byte. Archived v2 prompts and sanitized comparison report committed; ignored full report retained. Prior selected successful runs were not counted as new outputs on failed reanalysis.
- **Validation:** 20 deterministic backend tests passed during the experiment (one existing upstream deprecation warning). Diff/English/provenance checks performed before commit. No raw invalid-output diagnostics, held-out evaluation, repeats or independent human review performed.
- **Runtime:** evaluation backend stopped, Ollama remains available. No application/settings/schema changes; model, timeout, retry budget, .env and original seed files unchanged. SQLite history retains both experiments and mixed selected successful versions.
- **Implementation correction:** the first patch invocation rejected duplicate delete/add targets; no prompt edits were applied by that invocation, then ordinary file writes created the candidates. No subagents used.
- **Prior commit:** 341068f records original baseline.
- **Outcome:** prompt-only hypothesis tested; this candidate regressed reliability and does not justify promotion.

### Groq baseline provider comparison

- **Started:** 2026-10-06T10:52:26.058333+00:00.
- **User request:** run the configured stronger Groq model with original baseline prompts and compare quality.
- **Configuration check:** Groq credentials are present; no secret value displayed. Configured model llama-3.3-70b-versatile, 60-second timeout and one retry. Both baseline prompt hashes match the original Llama experiment.
- **Scope:** explicitly select Groq for this evaluation process without editing .env; run the same ten fictional seed messages through the actual API, review current-run outputs, and retain prior experiments. Provider transport differs (Groq JSON mode versus Ollama schema format), so this compares configured model/provider stacks rather than isolating model size alone.

- **Configured model check:** all ten configured llama-3.3-70b-versatile submissions failed with configuration errors. Direct httpx API inspection confirmed model_not_found; models API listed openai/gpt-oss-120b among available models for this key. An initial urllib models probe returned HTTPError; matching the application httpx transport succeeded. No secret/provider raw content printed.
- **Explicit experiment selection:** root announced openai/gpt-oss-120b as the accessible stronger-model candidate and will use a process environment override. .env and production fallback behavior remain unchanged; no automatic provider/model switching was added. Preserve the unavailable-model report separately from the quality run.

- **Quota diagnosis:** unpaced GPT-OSS run completed 0/10; eight validated partial extractions, all final failures rate_limit. Safe response inspection showed TPM 8000, retry-after 8 seconds, whereas the app caps waits at 5 seconds. No settings/retry policy changed in this block.
- **Paced evaluation:** initial 60-second cooldown; invoked the existing collector once for each E001–E010, with 60-second gaps, then combined reports. Interval 2026-10-06T10:56:35.896442+00:00 to 2026-10-06T11:08:09.445957+00:00 (693.55 seconds including waits). External pacing is not an app feature.
- **Results:** 9/10 completed, 10/10 validated extractions, accepted risk 7/9 completed and 7/10 overall coverage. E004 assessment hit rate limit; E003/E005 under-triaged medium versus expected high. Completed median latency 8.06 seconds excluding between-case waits. Successful-stage metadata totals 50012 tokens, not complete billing usage.
- **Review:** Codex compared sources, facts, risk and graph; independent human review remains pending. Observed modal strengthening, empty fact lists, inferred employment/identity and graph allegations presented as events. No held-out, repeatability or injection evaluation performed.
- **Artifacts:** committed sanitized evaluations/GROQ_BASELINE_2026-10-06.md; full configured/unpaced/paced reports ignored. Baseline prompt hashes verified identical; no secrets printed or committed. Documentation-only change; no new engineering tests needed.
- **Runtime/outcome:** backend stopped after evaluation; frontend stays stopped, Ollama remains running. .env, prompts, defaults and application code unchanged. GPT-OSS is a more promising candidate but provider quota handling and semantic quality still require work.
