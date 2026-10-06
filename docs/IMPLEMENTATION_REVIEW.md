# Implementation Review — 2026-10-06

This is a source-backed take-home review, not a production-readiness certificate. Runtime behavior and prompts were not changed. The expanded provider comparison was still in progress when reviewed; its partial results must not be presented as a finished four-model benchmark.

## Requirement coverage

| Assignment requirement | Implementation evidence | Assessment |
| --- | --- | --- |
| Ten seed emails and common ingestion pipeline | `api.py` startup import; `ingestion.py` normalization; seed/restart tests | Implemented. Seed ID import is idempotent; new pasted/file messages get new IDs. |
| Paste text; TXT/PDF/EML upload | POST endpoints, MIME/text-layer parsing, frontend ingestion dialog | Implemented with explicit UTF-8, OCR/encryption and attachment limitations. |
| A extracts metadata, summary, facts and attachments | `Extraction`, extraction prompt, saved source segments | Contract implemented; real experiments show missing/unsupported facts. |
| B consumes A and returns risk, entities, relationships | `AnalysisService.process`, `Assessment`, assessment prompt | Implemented. B also receives original sources for evidence and a policy snapshot; stages remain chained. |
| Free-tier or local LLM; unavailable-provider behavior | Explicit Ollama/Groq adapters, environment example, safe failures | Local no-key path implemented. Groq example names a model unavailable to the tested key; README documents an evaluated alternative. |
| Model failures, timeouts, garbage output | Outer timeout, bounded shared retry/repair budget, validators, explicit failed states | Implemented. No silent provider fallback or mocked runtime output. |
| Persist processed emails and graph | SQLite messages/runs/entities/mentions/relationships; atomic completion | Implemented, including prior-success preservation and provenance. |
| Inbox risk badge, original/extraction/rationale, selected-email entities | React inbox/detail components, textual status/risk labels | Implemented; component tests cover important failure and ingestion flows. |
| Narrow viewport usability | Responsive CSS and prior recorded desktop/mobile browser checks | Implemented; this review reruns engineering checks, not a fresh visual/accessibility audit. |
| Bonus aggregate interactive graph | Canvas, pan/zoom, node connections, source navigation and explorer | Implemented for small datasets. |
| React/TypeScript; permitted backend; styling rationale | React/Vite, FastAPI, CSS Modules and README | Conforms. Scoped styles avoid an extra styling framework. |
| Tests, README, AI workflow journal | pytest, Vitest, setup/architecture docs, PROCESS | Present. Deterministic engineering tests and real model evaluations are distinct. |
| Honest 5–6 hour accounting | PROCESS block timings and README explanation | Focused human time has not been measured; wall-clock blocks cannot be summed into that claim. |

The feature scope satisfies the assignment. Semantic reliability is the principal limitation, especially for the pipeline-focused track; feature completeness is not evidence that every model result fulfills the intended extraction/risk meaning.

## Explicit assumptions

- One trusted analyst uses one backend process on loopback. CORS is browser origin policy, not authentication; the unauthenticated catalog editor and mailbox API are inappropriate for shared/external access.
- Risk is advisory per-email triage. Headers, identity claims, allegations and citations are unverified source material. There is no sender/domain reputation check or cross-email risk inference.
- Seed attachment text is already extracted. Uploaded PDFs need readable text layers; OCR and malware scanning are out of scope.
- Inputs are small enough for the chosen model context in normal use. The 100,000-character acceptance limit does **not** guarantee fit in an 8192-token context once schemas, catalog and repair feedback are included. There is no token-aware admission/chunking.
- Original content and analysis history remain local in SQLite without application-level encryption, deletion/retention automation or a tested backup/restore procedure. Groq selection explicitly sends content to an external provider.
- Provider access, installed model and hardware determine capacity. No evaluated stack has been approved for unattended decisions; independent human review is pending.

## Guardrails: guarantees and gaps

| Layer | Current enforcement | What it does not prove |
| --- | --- | --- |
| Input/rendering | File/text limits; inert HTML-to-text; React text rendering; no source-link fetching or agent tools | Parser resource isolation, total HTTP request admission limits or malware safety |
| Generation | System/user separation; versioned instructions; explicit provider; maximum two calls per stage | Injection immunity, semantic accuracy or provider reproducibility |
| Output | Strict Pydantic schemas; existing source IDs; literal quotes after unique whitespace-only alignment; valid entity endpoints | Quote entails fact, relationship direction/type is correct, summary/rationale is grounded |
| Persistence | Validated A before B; atomic completed result/graph selection; retain previous success | Durable queue recovery, exactly-once inference or multi-worker ownership |
| Policy | Immutable catalog revisions/snapshots; size/reference validation; optimistic editing conflict | Authorized policy approval, deterministic scoring, mandatory evidence for every risk signal |

Risk rationale/tags and extraction summary/metadata have no mandatory per-field evidence contract. A relationship can quote real source text yet misrepresent its meaning. Account completeness, amount currency, allegation modality and relationship direction largely depend on prompt adherence and analyst review. Free-form relationship types support extension but complicate consistent aggregation; risk tags are not constrained to catalog IDs. Complete email-shaped labels alone merge email nodes, without authenticating owners or merging people by name.

Future guardrail changes should introduce evidence-bearing risk signals and explicit modality/direction where justified, then test them with actual inference. A deterministic policy layer is a possible design change, not implemented behavior or a guaranteed quality improvement. Do not weaken quote/reference validation to increase completion rates.

## Scalability and reliability

The modular monolith is appropriate for this assignment. Internal boundaries permit extraction of workers later; adding microservices or a graph database now would not resolve the main inference bottleneck.

Current limits are one sequential analysis worker, 20 pending jobs, synchronous SQLite/parser operations and complete inbox/graph responses. Inbox construction loads each message detail and graph contribution separately (an N+1 query pattern), even though its response only needs summary fields; summary queries and pagination should precede larger deployments. More Uvicorn workers are unsafe: each owns an independent queue, and startup interruption handling can invalidate another worker's active runs. Persisted states are recovery evidence, not durable job execution. User resubmission of identical content creates another message; only seed IDs and active analysis submission are deduplicated.

With a 180-second timeout and one retry per stage, a run can consume about 720 seconds plus bounded backoff, excluding queue wait. Twenty slow predecessors imply roughly four hours of waiting under that timeout scenario. This is a budget illustration, not a measured throughput/SLA. A bounded queue limits count, not acceptable latency or persisted storage growth. Provider output length has no explicit request-level generation cap. Local context capacity and Groq token quotas must be managed separately from worker count.

Scale in this order, conditional on measured workload:

1. Bound token input/output and queue age; add explicit admission responses and quota-aware scheduling. Isolate PDF parsing with CPU/memory/time limits.
2. Introduce durable job claims/leases, restart recovery, idempotent completion and transactional enqueue; keep prior-success and source/run provenance invariants. Test concurrent ownership and crash windows before enabling multiple workers.
3. Paginate/filter inbox and graph server-side; offer neighborhood queries and move expensive browser layout to a Web Worker. Current email scope filters an already downloaded graph.
4. Add migrations and appropriate indexes; move to PostgreSQL when concurrent write/query needs justify it. Benchmark before selecting specialized graph storage.
5. Add auth, access control, audit, retention and backup/restore before handling sensitive shared data externally.

## Evaluation and release gates

Engineering tests establish lifecycle, parser, provider and UI contracts using explicit test doubles. Real experiments use the actual provider/orchestration. Neither replaces the other. The fifteen current examples are a development regression set, including a synthetic injection case; they are not held-out generalization evidence. Accepted risk-level screening does not score extraction, graph semantics or factual grounding.

For future model/prompt/catalog releases, use a frozen, independently reviewed held-out set and report:

- All-submission completion and complete-and-accepted coverage; accepted levels among completed runs only as a secondary metric. Separate quota/timeouts from schema and semantic failures.
- Required-fact recall, unsupported-claim rate, missed severe signals, benign false positives, evidence entailment, allegation preservation and relationship direction/type correctness. Define denominators and review labels before scoring.
- First-attempt versus repaired success, end-to-end latency including queue wait/failures, per-stage percentiles and observed token usage across all attempts. Missing usage remains unknown.
- Benign urgency, embedded instructions in bodies/attachments, same-name identities, account suffix collisions, long inputs/context pressure, malformed attachments and provider outage/recovery cases.
- Repeat runs with identical snapshots/settings and review disagreements. Temperature zero does not establish deterministic provider output.

A proposed gate is: engineering checks pass, no unreviewed critical hallucination or severe-risk miss in the release set, and agreed completion/false-positive targets are met. Targets need analyst approval and adequate sample sizes; this repository has no automated CI quality gate or established production SLO. Synthetic cases and Codex qualitative reviews should be labeled accordingly. Finish pending comparisons before promoting a candidate; keep prompt changes and actual evaluation evidence together.

## Observability

Implemented: structured stage/attempt logs with IDs, provider/model, prompt/catalog hashes, timing and safe error codes; persisted attempts, validation paths, settings and available token usage. Sources, full prompts and raw provider errors/invalid outputs are excluded from routine logs. Raw failed output exclusion reduces exposure but limits diagnosis; a future opt-in redacted diagnostic workflow needs explicit retention/access rules.

Missing: metrics endpoint/dashboard, distributed tracing, request correlation across API/worker, explicit queue-wait/start timestamps, worker-health/readiness probe, alerts and formal SLOs. `/health` reports configuration/process availability, not model readiness or progress of the worker. Generic internal errors have sparse metadata; worker failure outside the per-run error handler can stall processing without a dedicated liveness monitor.

Suggested low-cardinality metrics: queue depth/oldest age, accepted/rejected submissions, completion/error counts by stage/code/provider, stage and end-to-end duration histograms, retries/repairs, missing usage and observed tokens. Put message/run IDs in logs/traces, not metric labels. Alert on worker stall, excessive queue age, sustained provider failures, SQLite errors and severe completion-rate degradation. Operational telemetry cannot detect semantically wrong but structurally valid outputs; sampled analyst review and quality regression reports serve that purpose.

## Submission priorities

1. Finish and accurately label pending evaluation results; independently review the strongest candidate. Do not claim unattended-triage quality from risk-level agreement.
2. Align the Groq environment example with an explicitly available tested model; make readiness versus health and local trust assumptions easy to find.
3. Add a compact reproducible successful two-agent demo and unavailable-provider demonstration; a screen recording is optional in the brief.
4. Keep scale/monitoring proposals as documented follow-up work. Production infrastructure is not required by this take-home and should not delay a clear, runnable submission.

Check results for this review are recorded in PROCESS.md. No new live inference, provider availability check, load test or browser audit was performed for this documentation-only block.
