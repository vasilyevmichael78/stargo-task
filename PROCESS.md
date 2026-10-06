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

### Qwen model selection and bounded repair state

- **Started:** 2026-10-06 11:37:51 UTC.
- **User request:** select the downloaded qwen3.5:4b and implement a bounded repair loop with previous invalid output and concrete validation feedback.
- **Scope:** preserve the existing one-retry budget; isolate repair data from system instructions, retain sanitized attempt history, keep transient retries separate, and preserve partial/previous successful results. Configure thinking explicitly for the local Qwen experiment.
- **Acceptance:** deterministic tests demonstrate schema/evidence/reference repair, exhaustion, and transient retry isolation; execute real Qwen inference and record actual outcomes. No subagents used.
- **Status:** in progress.

- **Completed:** 2026-10-06T11:52:36.722717+00:00. Selected Ollama / qwen3.5:4b in private backend/.env, preserved Groq credentials, set thinking=false, and updated default model/example configuration. Private environment remains ignored and chmod 0600.
- **Implementation:** bounded repair context contains up to 8,000 characters of previous invalid output plus at most 20 schema/evidence/reference errors. Versioned repair prompt configured through AGENT_REPAIR_SYSTEM_PROMPT_PATH; all three prompts snapshot/hash per run. Shared one-retry budget unchanged; transient retries do not create repair context. Per-attempt sanitized state/usage is persisted; raw invalid output is not.
- **Verification:** 29 backend tests passed; Ruff lint/format and diff whitespace checks passed. Tests cover schema, evidence and entity repair, exhaustion, input bounds, transient retry isolation, validated upstream preservation, and immutable repair-prompt snapshots. Existing Starlette deprecation warning remains. Frontend was not changed or retested.
- **Real inference:** final isolated three-case smoke ran 2026-10-06T11:43:24.535453+00:00 to 2026-10-06T11:51:53.608940+00:00 (509.07 seconds). Three validated extractions; zero completed assessments, all failed after two 60-second timeouts. No real invalid-output repair observed; semantic quality remains unscored. See evaluations/QWEN_REPAIR_SMOKE_2026-10-06.md.
- **Correction:** initial evaluation shared the live runtime database and was interrupted by the user's already-running backend autoreload; stopped only the evaluation process and moved to a temporary isolated database. An intermediate isolated run was stopped to restart with the final versioned repair prompt. Incomplete trials are excluded from reported results. The live backend was left running and reports Qwen through /health.
- **Time accounting:** documentation/code/test block began at 11:37:51 UTC; elapsed wall time includes inference waits and corrections, not measured human effort. Model download occurred in the preceding user turn and is excluded from this block's timing.
- **Outcome:** model selection and bounded repair delivered; real Qwen assessment latency remains a limitation. Full ten-case, held-out, prompt-injection, and repeatability evaluation were not performed. No subagents, remote changes, or pushes.

### Llama rollback and versioned JSON risk guidance

- **Started:** 2026-10-06 12:00:48 UTC.
- **User request:** return to Llama and supply a JSON risk map as additional assessment context.
- **Scope:** select llama3.2:3b; add a compact, validated, versioned catalog of signals, examples, counterexamples and advisory combinations. Snapshot/hash it at submission and send it only to Agent B; examples are never source evidence. Preserve the bounded repair loop and the 60-second timeout for this experiment. No vector store, retrieval service or deterministic policy engine is introduced.
- **Acceptance:** startup/configuration and catalog-reference checks, immutable per-run context, stage isolation, API snapshot exclusion, deterministic tests, and actual local inference with explicit limitations.
- **Prior commit:** e6a6568 delivered Qwen selection and bounded repair.
- **Status:** in progress.

- **Completed implementation:** 2026-10-06T12:15:12.015950+00:00. Returned private/default model to llama3.2:3b, preserved credentials and repair budget, and configured num_ctx=8192 for the added policy context. Timeout remains 60 seconds.
- **User steering:** user requested SQLite storage for future UI editing, then explicitly selected a simple JSON editor now. Scope expanded to immutable catalog revisions, active selection, GET/PUT /risk-context and optimistic concurrency, plus a native React dialog. File in Git is first-run bootstrap only; restarts preserve edited active policy. No subagents used.
- **Catalog:** version 2, 13 illustrative signals and 7 advisory combinations. It is not company-approved policy or a deterministic scoring engine. Agent A receives no catalog; Agent B receives the submission-time snapshot. Canonical hash/revision/version are retained; snapshots are excluded from analysis/detail API responses.
- **Verification:** 35 backend tests passed; 8 frontend tests passed. Ruff, type checking/build, formatting, whitespace and local documentation links checked before commit. Existing Starlette warning remains. Native browser verified loading, malformed JSON rejection and real idempotent save, desktop/mobile sizing without horizontal overflow; viewport reset afterward. Browser tab remains as deliverable.
- **Actual inference:** isolated smoke 2026-10-06T12:06:43.185057+00:00 to 2026-10-06T12:11:07.835808+00:00 (264.65 seconds). Three validated extractions, two completed assessments, zero accepted risk levels. E001 timed out twice; E009 required and successfully completed an actual entity-reference repair. Both completed risk outputs contain unsupported signals. Codex reviewed sources/results; independent human review pending.
- **Evidence:** evaluations/LLAMA_RISK_CATALOG_2026-10-06.md; raw report ignored. Do not count prior selected successful results or mocked providers as current-model quality evidence.
- **Corrections:** a combined patch failed to match API context and applied no changes; smaller patches completed it. First frontend-test append used a root-relative path while already in frontend, failed before adding tests, then was corrected and tests rerun. First browser lookup used the stale historical port 5174; inventory showed no tab, and process inspection identified this project's actual Vite port 5173. No unrelated processes stopped.
- **Outcome:** Llama/catalog/SQLite/editor feature delivered; quality improvement is not demonstrated. Full ten-case, held-out, adversarial and repeatability evaluation not executed. No pushes/remotes/history rewrite.

### Configurable model examples and 180-second inference budget

- **Started:** 2026-10-06 12:30:08 UTC.
- **User request:** add Qwen 3.5 4B to the environment example and change the timeout to 180 seconds; subsequent message supplied a failed extraction log.
- **Inspection:** private configuration currently selects qwen3.5:4b with a 120-second timeout. Preserve that explicit model choice and credentials. The reported run failed both extraction attempts at facts[3].evidence[0].quote with quote_mismatch, taking roughly 28–29 seconds per call; it did not time out. Raw invalid outputs are not retained, so their exact problematic quote cannot be reconstructed.
- **Scope:** align private/example/default per-call timeout to 180, document both installed model choices, and extend the evaluation collector deadline to accommodate the unchanged maximum of four calls. Preserve validators and one-retry budget.

- **Completed:** 2026-10-06T12:35:50.830472+00:00. Private configuration retains Qwen and now loads timeout=180; example/default timeout=180 and a separate commented Qwen alternative are verified. Updated collector deadline to 900 seconds so it can cover four 180-second calls plus backoff. No validators or retry counts changed.
- **Checks:** 35 backend tests passed; Ruff checks and diff whitespace passed; collector --help verified; Settings loaded private/example configurations as expected without printing credentials; /health confirms running backend with Qwen. Private .env remains ignored. No new real inference/semantic evaluation or frontend checks were performed for this configuration-only block. Existing Starlette warning remains.
- **Diagnostic limitation:** reported failure is an exact-quote mismatch in extraction, not HTTP/provider failure or timeout; Agent B never ran. Larger time budget does not fix this error. Raw failed outputs are intentionally not persisted, so precise offending text is unavailable.

### Source-preserving whitespace alignment for evidence

- **Started:** 2026-10-06 12:39:26 UTC.
- **User request:** fix repeated Qwen extraction invalid_output for the same user-provided email.
- **Diagnosis:** persisted metadata shows facts[3].evidence[0].quote mismatch on both attempts at timeout=180. A direct local extraction reproduction found that this quote fails literal matching but has exactly one match when only whitespace is varied; the other four citations match exactly. No source/model content was printed or saved to debug logs.
- **Scope:** align only uniquely matched whitespace variants to an exact source substring before strict validation; reject altered words/numbers/punctuation, ambiguous matches and unknown source IDs. Record sanitized alignment paths per attempt; preserve original sources and raw-output exclusion.
- **Acceptance:** deterministic boundary tests and a real retry through the application; document any remaining semantic or runtime failures.

- **Completed:** 2026-10-06T12:46:04.097254+00:00. Added deterministic whitespace-only alignment before strict validation, with unique-match checks including overlapping spans, sanitized attempt metadata and orchestration version 4. Prompts, provider settings, sources and risk catalog unchanged.
- **Checks:** 46 backend tests passed; Ruff lint/format and diff checks passed. Tests reject changed amounts/negation/punctuation, unknown sources and ambiguous spans; verify persisted source-exact quotes and both extraction/assessment alignment. Frontend unchanged/not retested. Existing Starlette warning remains.
- **Actual retry:** API run completed on Qwen, 2026-10-06T12:42:02.260414+00:00 to 2026-10-06T12:43:50.731252+00:00, 108.45 seconds including polling. Extraction completed in one call after one formatting alignment; assessment completed in one call and returned high. Persisted extraction passed strict evidence validation. No model repair needed. Full semantic correctness is not claimed.
- **Review correction:** added an overlapping-match guard after the real run and checked it against the actual source plus a dedicated deterministic test; it recovers the same substring. No additional inference was needed for this boundary refinement.
- **Artifacts:** evaluations/EVIDENCE_ALIGNMENT_2026-10-06.md; ignored metadata-only smoke report. No private source/output text persisted in debug reports or routine logs; original messages and previous failure history preserved. No subagents, pushes or history rewrite.

### Interactive aggregate canvas knowledge graph

- **Started:** 2026-10-06 12:50:38 UTC.
- **User request:** implement the assignment bonus as a polished canvas graph covering all dependencies.
- **Scope and acceptance:** render every entity and sourced relationship from selected successful analyses, including isolated entities; pan/zoom, fit, node selection/connections and source-email navigation; responsive layout and an accessible entity explorer. Keep SQLite persistence and conservative identity matching; layout/interaction remain browser state. Preserve mention provenance when an email-address entity is shared across messages.
- **Autonomous decisions:** use native Canvas 2D with bounded deterministic layout, avoiding a new graph framework for this small dataset. No prompt/model or inference changes; no subagents.
- **Status:** in progress.

- **Completed verification:** 2026-10-06 13:02:57 UTC (12 minutes 19 seconds wall time since the block start; not measured human effort).
- **Implementation:** native high-DPI Canvas 2D graph, type colors, directed/parallel/self-loop rendering, deterministic component layout with 80 relaxation iterations, neighborhood highlighting, collision-aware labels, pan/zoom/fit, node dragging and focus control. Added email scope, searchable keyboard-accessible explorer, evidence/run inspector and navigation to source emails. All graph entities, including disconnected nodes, remain represented. SQLite projection now retains all selected mentions of shared email identifiers without broadening identity matching.
- **Checks:** 47 backend tests and 13 frontend tests passed; Ruff formatting/lint, TypeScript/Vite production build, Prettier and diff whitespace passed. Tests cover selected-run provenance, multiple-message shared-entity evidence, prior-success preservation, disconnected layout, evidence/navigation, filtering/empty/error states, pointer selection, node dragging and background pan with hit testing after movement. Existing Starlette/httpx deprecation warning remains.
- **Browser:** real API displayed 58 entities and 48 relationships from 10 contributing emails. Verified email scope (E001: 7 nodes/6 links), keyboard node selection, citation/connection inspection, original-email navigation, keyboard zoom/pan, fit/focus controls, isolated-node source access, and mobile layout at actual 325 CSS pixels with scrollWidth=325. Native canvas rendering was visually inspected. Coordinate-based computer-use clicks did not reliably hit their intended targets after viewport overrides; keyboard actions verified the flows, and deterministic pointer tests separately verified canvas selection/drag/pan. Temporary viewport overrides reset; graph tab retained as deliverable. Screenshot saved outside Git at /tmp/stargo-knowledge-graph.png.
- **Corrections:** initial brief/storage filename guesses were wrong and corrected after file discovery. One CSS append used a root-relative path from frontend and was repeated with the correct path. First UI test exposed concatenated accessible labels; explicit entity labels fixed it. A formatter command launched from the repository root was interrupted and rerun using the installed frontend tooling. No dependencies were added or changed.
- **Limitations:** synchronous full-graph layout targets the assignment dataset; large-graph filtering/queries and Web Worker layout remain future work. Camera/layout are not persisted; pinch zoom is not implemented. No new real inference or AI-quality evaluation was performed because prompts, models and analysis behavior were unchanged. Graph links reflect selected model analyses, not independently verified relationships.
- **Outcome:** assignment bonus implemented and documented. Prior reliability commit: 759e7c0. No subagents, remote changes, pushes or history rewriting.

### Clean database and expanded provider evaluation

- **Started:** 2026-10-06 13:30:15 UTC.
- **Request:** clean the main SQL database, add varied JSON evaluation cases, rerun Groq and local Llama, and include Mistral if available.
- **Acceptance:** preserve a recoverable database backup; compare the same 15 cases with unchanged prompts/catalog and bounded repair; record execution, failures and semantic limitations.
- **Decisions:** preserve the active risk catalog while clearing mailbox/analysis/graph data. Groq uses the main database; Llama uses an isolated evaluation database. Mistral is not installed and will be recorded as skipped. No model downloads or silent provider fallback.
- **User clarification:** explicitly requested downloading Mistral 7B after learning it is supported but absent locally. Download started; local model runs will be sequential to avoid inference contention.
- **User steering:** include installed qwen3.5:4b on the same 15 cases. It is scheduled after Mistral, with a separate database and unchanged shared configuration.

### Assignment conformity and operational design review

- **Started:** 2026-10-06 14:16:18 UTC (journal block start; source inspection preceded this entry).
- **Request:** assess the implementation against the take-home requirements and improve documentation of assumptions, trade-offs, scalability, guardrails, evaluation and observability.
- **Acceptance:** source-backed requirement mapping, explicit implemented/proposed distinctions, prioritized gaps, relevant checks, and scoped documentation changes without changing runtime behavior.
- **Decisions:** preserve existing uncommitted expanded-evaluation work and running provider experiments. No subagents, new inference, prompt changes, database edits or provider switches. This review cannot certify unfinished Mistral/Qwen comparisons.
- **Status:** in progress.

- **Completed:** 2026-10-06 14:18:44 UTC; 2 minutes 26 seconds since journal block start, excluding preceding inspection and subsequent commit preparation. Not measured human effort.
- **Outcome:** added docs/IMPLEMENTATION_REVIEW.md with requirement mapping, explicit assumptions, implemented versus proposed guardrails, queue/context/query bottlenecks, evaluation release gates, monitoring gaps and submission priorities; appended a short README entry. Application, prompts, settings and evaluations unchanged by this block.
- **Checks:** 47 backend tests passed (one existing Starlette TestClient deprecation warning); Ruff lint/format passed. 13 frontend tests passed; TypeScript/Vite build and Prettier checks passed. git diff --check passed; local documentation links inspected.
- **Environment corrections:** first uv command was blocked from its default cache; retried successfully with a temporary cache and locked/offline mode. npm was absent from initial PATH; discovered installed mise Node 24.21.0 and reran npm scripts successfully. Checks needed no dependency installs or sandbox escalation; Git index writes required the sandbox override.
- **Limitations:** no new inference, independent human semantic review, live provider availability check, load/restore test or fresh browser/accessibility audit. Existing expanded comparison remains provisional; no remote operations. Only review additions will be committed, preserving pre-existing evaluation changes.
### Expanded evaluation completion and Mistral cancellation

- **User correction:** stop Mistral and exclude it, then run Qwen. Sent SIGINT to the identified Mistral Python process; two cases had completed and E003 was interrupted. Marked the partial report cancelled_by_user/excluded and its unfinished database run interrupted. The waiting Qwen job started immediately; main Groq database/backend unchanged. Final comparison includes Groq, Llama and Qwen only. The downloaded Mistral model remains installed.
- **Completed verification:** 2026-10-06 15:10:23 UTC; 100 minutes 8 seconds wall time from the evaluation block start, including inference, external pacing, download, cancelled experiment and the separately logged review. This is not measured focused human effort; subsequent commit preparation is excluded.
- **Implementation:** added five synthetic inline JSON regressions without changing the original ten expectations; extended the API collector for inline cases; added a sequential real-service comparison runner with explicit provider/model/database options and cancellation/failure reporting. Added a cancellation regression proving unfinished runs become interrupted rather than appearing active. No application prompts, catalog, private configuration or dependency versions changed.
- **Executed inference:** Groq openai/gpt-oss-120b completed 13/15, accepted risk 12/13 completed, median completed-case 7.36 seconds; Llama llama3.2:3b completed 6/15, accepted risk 2/6, median 47.81 seconds; Qwen qwen3.5:4b completed 13/15, accepted risk 12/13, median 137.27 seconds. All used 180-second calls and the same bounded retry policy. Groq had two final rate-limit failures; Llama had five timeouts/four invalid-output failures; Qwen had one timeout/one invalid-output failure. Mistral is excluded from every comparison denominator.
- **Verification:** 48 backend tests passed with the existing Starlette/httpx warning; Ruff lint/format and diff whitespace checks passed. Verified all 45 included runs against shared case expectations, prompt/catalog hashes, versions and timeout/retry settings. Verified 15 unique cases, unchanged seed expectations, database foreign keys and recoverable backup presence. Main and isolated Llama/Qwen databases each contain 15 messages and 15 runs. /health confirms Groq GPT-OSS with no configuration error. Private .env, databases and raw reports remain ignored. Frontend was unchanged and not rerun for this evaluation block; the separate review above executed its 13 tests/build.
- **Semantic review:** Codex reviewed all included source/output pairs and documented per-case limitations in evaluations/EXPANDED_COMPARISON_2026-10-06.md. Risk agreement is screening, not overall accuracy. Qwen improves operational completion over Llama but still invents some signals/reasons and misclassifies graph entity types. Groq also has unsupported identity/relationship inferences and a missed high-risk synthetic case. Independent human review, held-out evaluation and repeated trials remain pending.
- **Operational outcome:** main database was backed up before reset, active risk catalog retained, backend restored and UI continues to show Groq results. Local model results remain isolated. Full reports are owner-readable and ignored; committed report is sanitized. No subagents, pushes, remotes or history rewriting. Previous documentation review commit: cb787be; previous graph commit: f47cb87.

### Evaluation-informed recommendation and refreshed assignment review

- **Started:** 2026-10-06 15:17:06 UTC (recorded inspection checkpoint, not the exact first command time).
- **Request:** assess current implementation against the original assignment and latest evaluations; document the API-versus-local model recommendation and improvements in README.
- **Acceptance:** distinguish functional coverage from semantic reliability, support recommendations with measured results, preserve the free-tier/local constraint, and update stale pending-comparison statements.
- **Inspection and decisions:** reread the original brief, architecture plan, review, provider/schema/orchestration/ingestion/API and UI sources. Recomputed completion, accepted-level counts, seed-only counts and latency from ignored real reports. Consulted official Groq model/limit documentation; account eligibility and future availability remain conditional. Prefer the tested API configuration for a supervised demo, retain explicit local operation, and make no claim that untested frontier models are proven better. This is a documentation-only block: no provider/default/prompt changes, inference, database reset or subagents. Previous evaluation commit: 6b54347.
- **User steering:** additionally requested settings.py defaults for the 3.5 local model and GPT-OSS instead of hosted Llama. Interpreted 3.5 as the just-evaluated qwen3.5:4b and stated that assumption to the user. Updated settings and .env.example to qwen3.5:4b/openai/gpt-oss-120b, retaining Ollama as the provider default and preserving private .env. This expands the block beyond documentation; no prompts, retry policy or adapters changed.
- **Completed verification:** 2026-10-06 15:20:33 UTC, 3 minutes 27 seconds since the recorded inspection checkpoint; excludes earlier inspection and subsequent commit preparation, not measured human effort. Updated README with measured three-model/seed-only outcomes, conditional API recommendation, assignment coverage and prioritized improvements; refreshed the detailed review and removed obsolete pending-comparison/model-example statements.
- **Checks:** 48 backend tests passed with the existing Starlette/httpx warning. Ruff lint/format and diff whitespace passed. Verified Settings defaults without private .env, .env.example agreement, explicit model override precedence and resolution of local documentation links. Original brief/seed, private .env and model/prompt/catalog evaluation artifacts unchanged. No new inference or frontend tests/build/browser checks; frontend unchanged. No independent human semantic review, fresh account availability check or clean-machine installation claim. No subagents or remote actions.

### Complete run guide and test inventory

- **Started:** 2026-10-06 15:22:47 UTC (recorded inspection checkpoint).
- **Request:** document Ollama installation, key requirements, full backend/frontend startup, the author's optional 30-day Groq key offer and test descriptions suitable for Git.
- **Acceptance:** reproducible local and API paths, no secrets committed, an inventory matching every existing automated test, and clear distinction between tracked sanitized reports and ignored raw artifacts.
- **Inspection:** Git is clean; all backend/frontend test sources and sanitized evaluation Markdown reports are already tracked. Ignored evaluations/reports contains source-bearing raw data and SQLite and will remain ignored. Reviewed test assertions, npm scripts, Vite proxy, environment example and official Ollama/Groq quickstarts. The 30-day key lifetime is user-supplied information about their offered key, not a general provider expiry guarantee. No runtime changes, downloads, provider calls or subagents are needed.
- **Completed verification:** 2026-10-06 15:26:02 UTC; 3 minutes 15 seconds since the checkpoint, not measured human effort; commit preparation excluded. Added docs/RUNNING.md with install/key selection, non-overwriting .env copy, backend/frontend terminals, end-to-end checks, proxy/ports, troubleshooting and shutdown. Added docs/TESTING.md describing all 32 backend test functions (48 parametrized cases), 13 frontend tests, inference collectors, tracked result reports and limits. Linked both guides in README and documented the optional privately supplied author key.
- **Checks:** AST/frontend-name inventory comparison confirms every existing automated test is documented; pytest --collect-only collected 48 cases. Both evaluation CLI --help commands verified with locked/offline uv. Local links, English text, code fences and diff whitespace checked. Existing test sources and all evaluation Markdown are tracked. No new test execution, fresh installation, provider inference, browser checks or secret changes; last executed results remain 48 backend/13 frontend passing as documented earlier. No raw reports/databases added to Git. Previous review/defaults commit: 6fc6068.

### Versioned precomputed SQLite and raw evaluation artifacts

- **Started:** 2026-10-06 15:28:02 UTC (inspection checkpoint).
- **Request:** commit the current GPT-OSS SQLite results and avoid startup inference; additionally commit raw JSON reports.
- **Acceptance:** preserve current runtime data, ship a reviewed fixture with the original ten seeds/five synthetic cases, initialize a missing runtime database from it without model calls, and track reviewed JSON artifacts without exposing credentials/private messages.
- **Decisions:** keep runtime SQLite and future raw outputs ignored; add one explicit fixture exception and archive current JSON reports under evaluations/artifacts. Compact the SQLite copy so deleted page contents are not included. Existing databases are never replaced. Seed import without a snapshot also remains idempotent and no longer auto-submits inference; new submissions/manual retry still use configured real providers. Historical result provider/model remain distinct from currently configured inference.
- **Completed verification:** 2026-10-06 15:32:20 UTC; 4 minutes 18 seconds since the checkpoint, not measured human effort; commit preparation excluded. Created a 339,968-byte SQLite fixture with fifteen known seed/synthetic emails, fifteen GPT-OSS runs (thirteen completed/two failed) and the selected graph/catalog/prompt provenance. Added atomic first-use bootstrap with no existing-database replacement, path guard and explicit disable option. Removed seed startup submission; new ingestion/retry behavior is unchanged.
- **Raw archive:** copied all 23 existing JSON reports byte-for-byte to evaluations/artifacts with a Markdown hash index. Matched every available source body/attachment to committed seed/synthetic inputs; checked the actual private key and key-like strings without printing them. The user-email whitespace retry file contains sanitized metadata only. Mistral's cancelled partial report is retained as raw historical evidence but remains excluded from comparison. Compacted SQLite removes unused pages; source identity, provider/model, terminal statuses, integrity/foreign keys and snapshot hash were verified. Runtime DB/private .env are untouched and ignored.
- **Checks:** 51 backend tests passed, including three meaningful bootstrap regressions for no startup/restart inference, preserved existing data/unassessed seed import and invalid snapshot paths. Existing Starlette/httpx warning remains. Ruff lint/format, diff whitespace, documentation links, complete test inventory, raw archive byte equality and ignore boundaries passed. Updated run guide, README, test inventory and review for the new behavior. No new real inference, frontend tests/build or browser audit; frontend unchanged. No subagents, pushes or remote changes. Previous documentation commit: c95ae5c.
