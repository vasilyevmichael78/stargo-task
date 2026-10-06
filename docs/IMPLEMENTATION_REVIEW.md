# Implementation Review — 2026-10-06

This is a source-backed take-home review, not a production-readiness certificate. Refreshed after the [completed fifteen-case comparison](../evaluations/EXPANDED_COMPARISON_2026-10-06.md): Groq GPT-OSS, local Llama and local Qwen are included; Mistral was cancelled and excluded. Prompts and orchestration remain unchanged. User-requested settings/example defaults now select Qwen 3.5 4B for Ollama and GPT-OSS 120B for Groq; private configuration was not modified.

## Requirement coverage

| Assignment requirement | Implementation evidence | Assessment |
| --- | --- | --- |
| Ten seed emails and common ingestion pipeline | `api.py` startup import; `ingestion.py` normalization; seed/restart tests | Implemented. Seed ID import is idempotent; new pasted/file messages get new IDs. |
| Paste text; TXT/PDF/EML upload | POST endpoints, MIME/text-layer parsing, frontend ingestion dialog | Implemented with explicit UTF-8, OCR/encryption and attachment limitations. |
| A extracts metadata, summary, facts and attachments | `Extraction`, extraction prompt, saved source segments | Contract implemented; real experiments show missing/unsupported facts. |
| B consumes A and returns risk, entities, relationships | `AnalysisService.process`, `Assessment`, assessment prompt | Implemented. B also receives original sources for evidence and a policy snapshot; stages remain chained. |
| Free-tier or local LLM; unavailable-provider behavior | Explicit Ollama/Groq adapters, aligned environment example, safe failures | Local no-key path implemented with Qwen default; Groq default GPT-OSS was evaluated. Account eligibility remains conditional. Fallback is explicit reconfiguration/restart/retry. |
| Model failures, timeouts, garbage output | Outer timeout, bounded shared retry/repair budget, validators, explicit failed states | Implemented. No silent provider fallback or mocked runtime output. |
| Persist processed emails and graph | SQLite messages/runs/entities/mentions/relationships; atomic completion | Implemented, including prior-success preservation and provenance. |
| Inbox risk badge, original/extraction/rationale, selected-email entities | React inbox/detail components, textual status/risk labels | Implemented; component tests cover important failure and ingestion flows. |
| Narrow viewport usability | Responsive CSS and prior recorded desktop/mobile browser checks | Implemented; no fresh visual/accessibility audit in this refresh. |
| Bonus aggregate interactive graph | Canvas, pan/zoom, node connections, source navigation and explorer | Implemented for small datasets. |
| React/TypeScript; permitted backend; styling rationale | React/Vite, FastAPI, CSS Modules and README | Conforms. Scoped styles avoid an extra styling framework. |
| Tests, README, AI workflow journal | pytest, Vitest, setup/architecture docs, PROCESS | Present. Deterministic engineering tests and real model evaluations are distinct. |
| Honest 5–6 hour accounting | PROCESS block timings and README explanation | Focused human time has not been measured; wall-clock blocks cannot be summed into that claim. |

The feature scope satisfies the assignment. Semantic reliability is the principal limitation, especially for the pipeline-focused track; feature completeness is not evidence that every model result fulfills the intended extraction/risk meaning.

## Latest model evidence and recommendation

| Configuration | Completed / all | Accepted risk / all | Original seeds: completed / accepted | Median completed-case seconds |
| --- | --- | --- | --- | --- |
| Groq openai/gpt-oss-120b | 13/15 | 12/15 | 9/10 / 9/10 | 7.36 |
| Ollama qwen3.5:4b | 13/15 | 12/15 | 8/10 / 7/10 | 137.27 |
| Ollama llama3.2:3b | 6/15 | 2/15 | 4/10 / 1/10 | 47.81 |

Recommend the tested Groq configuration for a supervised demo, with local Qwen retained for explicit offline/private operation. Groq's completed-case median is about 19 times lower on this hardware, and the seed-only results better match the original task. Qwen's aggregate risk agreement equals Groq's, so do not claim measured superiority on that metric. Its known graph typing errors, unsupported signals and invented account-change reason also matter for this assignment; Groq has semantic errors too. Both miss or fail cases. Groq's two final quota failures occurred despite 65-second external pacing; output/token-aware scheduling is absent from the app.

This is one development comparison, not a scored independent semantic benchmark or proof that any frontier model will work better. GPT-OSS is the tested large open-weight API candidate. Evaluate another strong API candidate against frozen, independently reviewed labels before promotion; a paid-only dependency cannot replace the required free-tier/local path. Latencies exclude queue wait/pacing, and hardware/transport/output-mode differences prevent model-size-only conclusions. Full per-case findings and provenance are linked above.

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

A proposed gate is: engineering checks pass, no unreviewed critical hallucination or severe-risk miss in the release set, and agreed completion/false-positive targets are met. Targets need analyst approval and adequate sample sizes; this repository has no automated CI quality gate or established production SLO. Synthetic cases and Codex qualitative reviews should be labeled accordingly. Included comparisons are finished, but independent semantic review remains pending; keep future prompt changes and actual evaluation evidence together.

## Observability

Implemented: structured stage/attempt logs with IDs, provider/model, prompt/catalog hashes, timing and safe error codes; persisted attempts, validation paths, settings and available token usage. Sources, full prompts and raw provider errors/invalid outputs are excluded from routine logs. Raw failed output exclusion reduces exposure but limits diagnosis; a future opt-in redacted diagnostic workflow needs explicit retention/access rules.

Missing: metrics endpoint/dashboard, distributed tracing, request correlation across API/worker, explicit queue-wait/start timestamps, worker-health/readiness probe, alerts and formal SLOs. `/health` reports configuration/process availability, not model readiness or progress of the worker. Generic internal errors have sparse metadata; worker failure outside the per-run error handler can stall processing without a dedicated liveness monitor.

Suggested low-cardinality metrics: queue depth/oldest age, accepted/rejected submissions, completion/error counts by stage/code/provider, stage and end-to-end duration histograms, retries/repairs, missing usage and observed tokens. Put message/run IDs in logs/traces, not metric labels. Alert on worker stall, excessive queue age, sustained provider failures, SQLite errors and severe completion-rate degradation. Operational telemetry cannot detect semantically wrong but structurally valid outputs; sampled analyst review and quality regression reports serve that purpose.

## Submission priorities

1. Independently review the API candidate and a held-out set; fix severe-risk misses, unsupported claims and graph semantics with measured regressions. Evidence-bearing signals, typed facts and explicit allegation/direction contracts precede further prompt/catalog tuning. Do not claim unattended-triage quality from risk-level agreement.
2. Defaults/examples now match tested candidates. Verify a clean lockfile-based setup and add a compact successful two-agent demo plus unavailable-provider recovery. Account limits remain an explicit constraint; a screen recording is optional in the brief.
3. Bound tokens/output and handle quota scheduling; improve readiness, queue age/stage visibility and worker-stall detection. Preserve bounded repair and structural evidence checks.
4. Keep scale/monitoring proposals as follow-up work. Durable jobs and filtered queries come before service splits; RAG/browser tools/frameworks do not resolve the observed entailment/type errors by themselves. Production infrastructure is not required by this take-home.

Check results for the original review and this refresh are recorded in PROCESS.md. No new live inference, account availability check, load test or browser audit was performed in this refresh. Default-model changes are configuration changes, not a newly evaluated orchestration/model experiment; the selected model identifiers are those in the completed comparison.
