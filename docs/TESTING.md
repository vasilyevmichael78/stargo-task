# Testing and Evaluation Inventory

## Scope and commands

All automated test sources and sanitized evaluation Markdown reports listed here are already tracked in Git. This inventory documents coverage, including three bootstrap regressions added for the precomputed demo. Reviewed raw reports are now archived in Git; future/private runner outputs remain ignored. Most recent recorded results: **51 pytest cases and 13 frontend tests passed**. Parametrization expands backend function count into collected cases. See [PROCESS](../PROCESS.md) for execution dates, warnings and limitations.

From the repository root, after installing dependencies:

```sh
uv run --project backend --locked pytest backend/tests -q
uv run --project backend --locked pytest backend/tests --collect-only -q
uv run --project backend --locked ruff check backend evaluations/compare.py evaluations/run.py
uv run --project backend --locked ruff format --check backend evaluations/compare.py evaluations/run.py
```

Frontend, from frontend/:

```sh
npm test
npm run build
npm run format:check
```

Engineering tests use temporary SQLite, explicit provider doubles and HTTP/fetch mocks; no installed model, working API key or running browser/server is required. Backend module configuration can still read an existing private .env, so invalid selected-provider startup configuration can affect imports; use a valid local configuration when running tests. A known upstream Starlette/httpx TestClient deprecation warning is recorded. Frontend tests run in jsdom; they do not replace real viewport, screen-reader, contrast or native-canvas visual audits.

## Backend test inventory

### [backend/tests/test_backend.py](../backend/tests/test_backend.py)

| Test function | What it verifies |
| --- | --- |
| `test_partial_failure_and_selected_success_survive` | A completed selected result survives failed reanalysis; partial extraction remains available. |
| `test_invalid_evidence_and_bounded_repair` | Unreadable JSON stops after the two-call budget and never creates risk none. |
| `test_outer_timeout` | The orchestration timeout stops a stalled provider independently of its own implementation. |
| `test_seed_idempotency_and_restart` | Seed IDs and active submissions deduplicate; interruption preserves the mailbox record. |
| `test_upload_formats_and_limits` | TXT/EML parsing, recipients, invalid formats/encoding/PDF/empty input and upload size errors. |
| `test_evidence_validation` | A quote absent from its source is rejected. |
| `test_provider_payload_and_auth` | Both provider request/response envelopes, roles, Groq authentication and Ollama thinking flag. |
| `test_provider_errors` | 401, 429, 500 and 404 map to safe normalized codes and retryability without private provider bodies. |
| `test_http_contract` | HTTP submission identifiers/status, details, unknown/invalid inputs, empty graph and prompt snapshot exclusion. |
| `test_selected_graph_and_conservative_identity` | Selected-run projection deduplicates repeated completion; person identities remain run-local and evidence retains provenance. |
| `test_queue_saturation_preserves_message` | A full queue returns 429 but preserves the ingested message without fabricating a run. |
| `test_worker_processes_http_submission` | A TestClient submission passes through the real worker with a test provider and returns persisted completed state. |
| `test_real_seed_restart_import` | The original ten seed records and attachment text import idempotently across application restarts. |
| `test_pdf_text_layer_and_eml_attachment` | A generated text PDF extracts content; supported EML attachment text is preserved and unsupported attachment warnings appear. |
| `test_configuration_and_invalid_prompt` | Missing selected Groq credentials and unreadable prompt paths fail startup actionably. |
| `test_html_only_eml_preserves_inert_link_evidence` | HTML body text/link targets survive normalization while scripts/styles/rendered HTML are excluded. |
| `test_repair_receives_previous_output_and_specific_feedback` | JSON/schema/quote/source/entity/duplicate failures carry bounded feedback to repair, revalidate and retain safe attempt metadata. |
| `test_transient_retry_has_no_repair_context` | A transient rate limit repeats generation without model-repair feedback. |
| `test_repair_output_is_bounded` | Repair truncates previous invalid output to 8,000 characters and never exceeds the retry budget. |
| `test_assessment_repair_preserves_validated_extraction_and_prompt_snapshot` | B repair reuses valid A and submission-time prompt snapshots despite later prompt file changes. |
| `test_risk_catalog_validation_and_size` | Malformed/oversized catalog, duplicate IDs, missing levels and unknown signal references are rejected safely. |
| `test_catalog_revision_persistence_idempotency_and_conflict` | Catalog revisions persist, identical content reuses a revision and stale updates conflict; bootstrap does not overwrite edits. |
| `test_catalog_snapshot_is_only_sent_to_assessment` | The submission-time catalog goes to B, not A, and later edits do not change the active run snapshot. |
| `test_catalog_http_edit_conflict_and_snapshot_exclusion` | Catalog HTTP save/conflict/invalid-input contracts, run provenance and private snapshot exclusion. |
| `test_catalog_bootstrap_failure_is_actionable` | A missing catalog file yields an actionable startup error. |
| `test_catalog_example_is_not_valid_source_evidence` | Policy examples cannot serve as citations unless present in actual message sources. |
| `test_whitespace_alignment_restores_exact_source_span` | Unique whitespace variants recover the exact original substring. |
| `test_alignment_rejects_semantic_changes_ambiguity_and_wrong_source` | Altered words/values/punctuation, unknown sources and ambiguous/overlapping spans are rejected. |
| `test_aligned_extraction_persists_without_model_repair` | Whitespace alignment persists source-exact A evidence and alignment metadata without an extra model call. |
| `test_alignment_applies_to_entity_and_relationship_evidence` | The same formatting-only recovery works on B entities and relationships. |
| `test_graph_preserves_shared_entity_mentions_and_selected_run_evidence` | Shared email entities retain selected provenance across messages, reanalysis and a later failure. |

### [backend/tests/test_evaluation.py](../backend/tests/test_evaluation.py)

| Test function | What it verifies |
| --- | --- |
| `test_comparison_cancellation_records_interruption` | Cancelling real-service evaluation writes cancelled status and marks the unfinished SQLite run interrupted with no risk. |

### [backend/tests/test_bootstrap.py](../backend/tests/test_bootstrap.py)

| Test function | What it verifies |
| --- | --- |
| `test_precomputed_startup_and_restart_without_inference` | First startup/restart serves fifteen fixture messages, thirteen completed GPT-OSS results and a graph, with zero provider calls and unchanged fixture bytes. |
| `test_existing_database_is_preserved_and_seed_import_does_not_analyze` | Existing user data survives; missing seeds import unassessed with no provider calls. |
| `test_bootstrap_rejects_missing_fixture_and_writable_fixture_target` | Missing snapshot configuration fails actionably and using the fixture as writable runtime path is rejected. |

## Frontend test inventory

### [frontend/src/App.test.tsx](../frontend/src/App.test.tsx)

- Failed analysis is not presented as no risk.
- Partial extraction remains visible with provider error and retry action.
- Inbox search filters by sender or subject without fabricating results.
- Pasted email submits real input and opens persisted message.
- Queue saturation opens the persisted email and preserves the submission error.
- File ingestion sends the chosen file as multipart data.
- Risk catalog editor validates JSON and saves with the loaded revision.
- Risk catalog conflict preserves edits until explicit reload.

### [frontend/src/KnowledgeGraph.test.tsx](../frontend/src/KnowledgeGraph.test.tsx)

- Layout retains disconnected nodes and supports camera hit testing.
- Node explorer exposes directions, evidence and email navigation including isolated nodes.
- Email scope filters canvas and explorer without creating implied relationships.
- Empty graph and refresh failure remain explicit.
- Canvas pointer selection, node dragging and background pan preserve hit targets.

The graph suite includes camera transforms/hit testing, disconnected nodes, direction/citations/navigation, email scope, explicit empty/error states, pointer selection, node dragging and background pan. Component tests verify interactions/data contracts rather than pixel appearance or model semantics.

## Real AI evaluation

[Evaluation protocol](../evaluations/README.md) describes review dimensions and collectors. [cases.json](../evaluations/cases.json) defines fifteen development cases: E001–E010 from unchanged seed data, plus X001 benign urgency, X002 concealed payment/prompt injection, X003 unverified allegation, X004 distinct same-name participants and X005 account replacement. Do not compare rationale strings verbatim. Required facts/signals/prohibited claims require semantic review; automatic level_screen only compares accepted risk ranges.

From the repository root, with an installed Qwen model and Ollama running:

```sh
uv run --project backend --locked python evaluations/compare.py --provider ollama --model qwen3.5:4b --database evaluations/reports/qwen-review.sqlite3 --output evaluations/reports/qwen-review.json
```

Or with a private eligible Groq key:

```sh
uv run --project backend --locked python evaluations/compare.py --provider groq --model openai/gpt-oss-120b --database evaluations/reports/groq-review.sqlite3 --output evaluations/reports/groq-review.json --pause 65
```

Use an isolated database not owned by a running API. A new database bootstraps the versioned catalog; compare active catalog hashes when reproducing a UI-edited policy. Runs create history; use a new destination pair to retain old comparisons. The runner executes the real shared service, validation/repair and persistence, bypassing HTTP/UI. Sequential local models avoid inference contention. Groq pacing is an evaluation condition, not an implemented scheduler or quota guarantee.

To exercise HTTP submission/polling against a running backend instead:

```sh
uv run --project backend --locked python evaluations/run.py --ids E001 --output evaluations/reports/api-smoke.json
```

This creates a new analysis in the backend's database; the full default collector evaluates all fifteen and ingests inline synthetic emails. It does not cancel server work when its own deadline expires. No real inference is part of pytest/npm test.

## Tracked human-readable result reports

| Report | Purpose |
| --- | --- |
| [Llama baseline](../evaluations/LLAMA_BASELINE_2026-10-06.md) | Original ten-case local baseline and semantic limitations. |
| [Prompt-only v2 experiment](../evaluations/PROMPT_EXPERIMENT_V2_2026-10-06.md) | Candidate prompt regression; not promoted. Archived candidate prompts are tracked. |
| [Groq baseline](../evaluations/GROQ_BASELINE_2026-10-06.md) | Original API comparison, access/quota constraints and quality observations. |
| [Qwen repair smoke](../evaluations/QWEN_REPAIR_SMOKE_2026-10-06.md) | Historical local Qwen/repair smoke, with its actual settings. |
| [Llama risk catalog smoke](../evaluations/LLAMA_RISK_CATALOG_2026-10-06.md) | Small policy-context experiment, not a full accuracy benchmark. |
| [Evidence alignment verification](../evaluations/EVIDENCE_ALIGNMENT_2026-10-06.md) | Formatting-only validator correction and real Qwen verification. |
| [Expanded comparison](../evaluations/EXPANDED_COMPARISON_2026-10-06.md) | Latest fifteen-case Groq/Llama/Qwen results, hashes, failures and per-case review; Mistral cancelled/excluded. |

The [raw artifact archive](../evaluations/artifacts/README.md) tracks 23 unchanged reviewed JSON reports, including failures and cancelled Mistral output, with hashes. Source text was matched to committed seed/synthetic cases and credentials checked. The [compacted GPT-OSS SQLite fixture](../backend/fixtures/README.md) is also tracked for startup without inference. Future/private outputs under evaluations/reports/, runtime SQLite and backups remain ignored. Refresh committed artifacts only after source/credential review; no credentials belong in reports.

## What is not verified by the automated suite

Independent human labels/semantic quality, population precision/recall, repeated stochastic reproducibility, clean-machine installation, load/concurrent worker safety, durable queue crash recovery, backup restoration, production authentication/retention, and a fresh browser/accessibility audit are not established by these tests. Earlier desktop/mobile/browser checks are described factually in PROCESS. No evaluated model is approved for unattended triage.
