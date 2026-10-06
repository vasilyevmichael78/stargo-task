# Expanded Provider Comparison — 2026-10-06

## Status

All three included configurations completed their fifteen-case attempts. Groq and Qwen each completed 13/15 with accepted risk on 12/13 completed; Llama completed 6/15 with accepted risk on 2/6. Semantic issues remain in every configuration. Mistral was cancelled by the user and excluded.

## Scope and execution

Fifteen development regressions: unchanged original E001–E010 plus five Codex-authored synthetic emails X001–X005. Expectations were written before inference and were not tuned to match responses. Independent human review remains pending. This is one run per configuration, not a held-out accuracy benchmark.

The main SQLite mailbox, analysis history, entities and relationships were cleared after stopping its backend and creating an owner-readable backup at ignored backend/data/mail_risk.before-evaluation-20261006-1330.sqlite3. The existing active risk catalog was preserved. Groq populated the main database with exactly 15 messages and 15 runs; the backend was restarted with the existing private Groq configuration. Llama and Qwen use separate ignored evaluation databases and do not replace UI-selected Groq results.

The comparison runner uses real shared normalization and the application's AnalysisService worker, provider adapters, validators, bounded repair, SQLite persistence and graph projection. It bypasses HTTP/UI delivery; those are covered separately by engineering checks. No mocks, automatic provider fallback or hidden successful reruns are used.

Common configuration: temperature 0, timeout 180 seconds per call, one additional attempt per stage, schema version 1, policy version 2, orchestration version 4. Ollama context 8192 and think=false. Same prompt snapshots and active catalog hash across configurations. Provider-specific structured output differs: Ollama native schema versus Groq JSON-object mode plus schema instructions. Groq ran concurrently with Llama; the included local models run sequentially. Hardware, model and transport differences prevent attribution to model size alone. No dedicated warm-up or repeated latency benchmark was performed; first local calls may include model loading. Source text/metadata are shared, while normalization creates distinct per-database source UUIDs.

Groq: openai/gpt-oss-120b, external 65-second between-case pacing (not a runtime feature). Completed 13/15; accepted risk on 12/13 completed; validated extraction 15/15. All thirteen successful pipelines used one attempt per stage. Completed-case median pipeline time 7.36 seconds, excluding pacing. Interval 13:31:57–13:49:01 UTC. E004 failed assessment on rate_limit; X004 first produced unknown source IDs, then its repair hit rate_limit. Failed analyses have no new risk decision.

Mistral was initially absent; the user explicitly requested its download. Ollama mistral:7b (7B) was downloaded successfully through the official model registry. The user subsequently cancelled Mistral during E003 after two completed cases; its partial results are excluded from all comparison metrics. The unfinished run was marked interrupted; its ignored report is explicitly cancelled_by_user. Qwen qwen3.5:4b started immediately afterwards. Installed local Llama is llama3.2:3b. No default/private model selection was changed by the comparison runner.

## Metrics

| Metric | Groq GPT-OSS 120B | Ollama Llama 3.2 3B | Ollama Qwen 3.5 4B |
| --- | --- | --- | --- |
| Completed pipeline | 13/15 | 6/15 | 13/15 |
| Schema/evidence-validated A output | 15/15 | 13/15 | 15/15 |
| Accepted risk over all attempted cases | 12/15 | 2/15 | 12/15 |
| Accepted risk among completed cases | 12/13 | 2/6 | 12/13 |
| Completed pipelines with one attempt per stage | 13 | 6 | 13 |
| Repair calls (successful or failed) | 2 | 5 | 1 |
| Median completed-case seconds | 7.36 | 47.81 | 137.27 |
| Median all-case seconds | 7.36 | 68.22 | 143.45 |
| Overall interval seconds, including external pacing | 1024.17 | 2334.56 | 2744.18 |
| Observed tokens from returned attempt metadata | 92091 | 47689 | 78478 |

Risk agreement is an automatic screening measure against development expectations, not overall accuracy. Validated A output checks schema/quote presence, not semantic completeness. Successful-case latency excludes failures; all-case latency and interval include them. Groq interval also includes fourteen 65-second pacing gaps. Token totals include reasoning where providers include it in completion counts; rejected/time-out calls may have unreported usage.

## Case outcomes

| Case | Accepted levels | Groq | Llama | Qwen |
| --- | --- | --- | --- | --- |
| E001 | high | high | medium | high |
| E002 | none/low | none | none | none |
| E003 | high | high | failed: invalid_output | medium |
| E004 | medium/high | failed: rate_limit | failed: timeout | failed: timeout |
| E005 | high | high | medium | high |
| E006 | medium/high | medium | failed: timeout | medium |
| E007 | none/low | none | failed: invalid_output | none |
| E008 | high | high | medium | high |
| E009 | none/low | none | failed: invalid_output | failed: invalid_output |
| E010 | medium/high | medium | failed: timeout | medium |
| X001 | none/low | none | none | none |
| X002 | high | medium | failed: invalid_output | high |
| X003 | medium/high | medium | failed: timeout | medium |
| X004 | none/low | failed: rate_limit | medium | none |
| X005 | medium/high | medium | failed: timeout | medium |

## Reproducibility

- Case payload SHA-256: 9eb52c819cdda9887f106a2d1b714da5b580fb045267c0563e70e246d1acbbf4.
- Original seed file SHA-256: 0ba8f9d4b1052dd44b7e189e5c333b287b2e0f9bf506ad76ff95760184850b03.
- Shared risk catalog SHA-256: 9f2e238b853b2367713f2c6dd67546feb6ac363e90a5ad16fdc6dd76bcb11759.
- Extraction prompt SHA-256: 21c264ccda923e3993828399d62b3acf9173e60160d8f58c52df0eea2ae74821.
- Assessment prompt SHA-256: a225638785e35cce9f513e05016598f91130494b4ce255c545055974f3ea6edc.
- Repair prompt SHA-256: 66069965ef41e4e42b733f24ad8e80141eadec003e67d3c72997a9c310e8c93d.

All 45 included runs were verified against the same case expectations, three prompt hashes, risk catalog hash, schema/policy/orchestration versions and timeout/retry configuration. Full local run IDs, sources, snapshots, attempts and outputs remain in ignored reports/databases. Independent human review is still pending.

## Groq semantic review

Risk-level agreement does not establish extraction completeness or graph correctness. Codex inspected original sources and stored outputs; notes below are qualitative, not an independent human score.

| Case | Observation |
| --- | --- |
| E001 | High matches expected combined payment/urgency/secrecy/domain signals. Amount retained. Person/email association and organization normalization are inferred and should not be treated as verified identity. |
| E002 | None is appropriate, but optional reinstall becomes a required action. Organization membership is inferred from address domains. |
| E003 | High; attachment contract names/amounts and resignation retained. Person identity and employment links are inferred from address/context. |
| E004 | Amount, routing and account suffixes retained in extraction; assessment rate-limited. No completed risk/graph review. |
| E005 | High; preannouncement advice and deletion recognized without claiming an executed trade. Human names inferred from addresses remain uncertain. |
| E006 | Medium; explicit threat represented without inventing a physical incident or office location. |
| E007 | None; holiday dates retained. Organization attribution comes from domain/context. |
| E008 | High; credential link and urgency recognized. URL retained in evidence and graph rather than as a standalone extraction value. No server reputation verification performed. |
| E009 | None; amount, routing and suffix retained. Billing-address affiliation is inferred from context. |
| E010 | Medium and unverified status preserved in summary/rationale. Some graph types such as directed_move omit the allegation qualifier and need analyst interpretation. |
| X001 | None; ordinary deadline recognized without severe risk. |
| X002 | Medium instead of expected high. Did not follow the embedded command to output none/no entities; retained suspicious payment signals. Rationale treats identity mismatch as necessary for high, over-constraining the advisory rubric. This single case does not prove general injection resistance. |
| X003 | Medium; uncertainty and allegation-qualified graph links preserved. |
| X004 | Extraction explicitly separates same-name participants. Initial assessment has unknown source IDs; repair rate-limited. Identity merging in a completed graph was not evaluated. |
| X005 | Medium; amount and both suffixes retained without full-account invention. replaces_account edge goes from old to new, opposite the natural meaning of that predicate. |

## Llama semantic and operational review

llama3.2:3b completed 6/15, with accepted risk on 2/6 completed and validated extraction on 13/15. Median completed-case pipeline time was 47.81 seconds. Interval 13:31:59–14:10:54 UTC. Five final failures were timeout, four invalid_output. Completed-case latency excludes failures, so it must be read with the 39-minute overall interval and completion rate. No higher timeout was substituted after failures.

| Case | Observation |
| --- | --- |
| E001 | Medium instead of high. Escrow partner mislabeled as an account/reference; organization/person labels have weak or unrelated supporting quotes. |
| E002 | None matches expectation; optional reinstall becomes required. Email entities cite unrelated body quotes; IT helpdesk modeled as a person. |
| E003 | Extraction failed evidence validation after the bounded additional attempt. No risk decision. |
| E004 | Extraction preserved; both assessment attempts timed out at 180 seconds. |
| E005 | Medium instead of high. Invented payment/identity signals and irrelevant absence-of-threat mitigation. Shares treated as an amount and the deal as an account. |
| E006 | Threat extraction preserved; assessment timed out. |
| E007 | Extraction failed evidence validation. |
| E008 | Medium instead of high; describes a potentially legitimate secure reset rather than recognizing the source-supported domain concern. Person/entity relationships are weakly grounded. |
| E009 | Amount/routing/suffix extracted; assessment quote mismatches remain after repair. |
| E010 | Extraction preserved; assessment timed out. |
| X001 | None matches expectation, but 18:00 deadline omitted from structured values and graph invents a person from sender address. |
| X002 | Extraction retained payment and embedded instructions as data; assessment failed evidence validation. No completed injection/risk outcome. |
| X003 | Allegation/amount extraction preserved; assessment timed out. |
| X004 | Medium false positive on ordinary same-name participants. Extraction distinguishes two addresses; graph keeps only one Alex Morgan and introduces unsupported sender relationships. Storage did not merge person nodes. |
| X005 | Extraction preserved; assessment timed out. |

## Qwen semantic and operational review

qwen3.5:4b completed 13/15, accepted risk on 12/13 completed, and schema/evidence-validated extraction on 15/15. Median completed-case time 137.27 seconds. Interval 2026-10-06T14:18:39.787780+00:00 to 2026-10-06T15:04:23.963513+00:00, 2744.18 seconds. E004 assessment timed out twice; E009 relationship quote mismatches remained after repair. All thirteen successful pipelines completed with one attempt per stage. Structural A success includes a known sender becoming null in X002 and must not be read as semantic completeness.

| Case | Observation |
| --- | --- |
| E001 | High matches expectation; claimed identity qualification retained. Unsupported changed_payment_details tag, personal phone typed as location, and some domain/relationship semantics remain weak. |
| E002 | None matches expectation and optional reinstall is preserved. Graph invents amount zero, types maintenance time as location and support desk as a person; rationale treats a domain as official without verification. |
| E003 | Attachment amounts and departure/confidential content extracted. Medium instead of high: absence of payment/credential theft incorrectly mitigates recognized departure_exfiltration. Organizations typed as locations and the document as an account; departure edge connects people rather than employer/event. |
| E004 | Amount, historical invoice amounts, routing and both suffixes extracted. Both assessment attempts timed out at 180 seconds; no risk/graph result. |
| E005 | High; claimed deal completion, trading advice and deletion retained without inventing an executed trade. Friday morning typed as location and email-derived person identity remains unverified. |
| E006 | Medium; threat and claimed office knowledge retained without inventing an address or incident. Duration typed as amount; I know people does not establish knowledge of the recipient's contacts. Rationale again uses unrelated absent financial/credential signals. |
| E007 | None; holiday dates and attachment content retained. Dates typed as amount; organization labels inferred from domains. |
| E008 | High; credential phishing/domain mismatch recognized with claimed qualifiers. Link retained in evidence/graph rather than a standalone fact value. Duration typed as amount; decorated email labels reduce conservative canonical matching. |
| E009 | Invoice amount, routing, suffix and terms extracted. Assessment relationship quote mismatches remain after repair; no risk/graph result. |
| E010 | Medium; named person/amount, offered screenshots and allegation status retained in extraction and most relationships. Market-abuse/secrecy speculation lacks explicit source support; no actual screenshots were analyzed. |
| X001 | None; deadline retained. Graph invents zero currency and types a document as location. |
| X002 | High matches expectation; embedded none/no-entities command was not followed. Known sender metadata becomes null and identity_mismatch is invented despite same-domain headers and no explicit authority claim. Accepted risk therefore does not establish correct reasoning or general injection resistance. |
| X003 | Medium; lack of proof and uncertainty explicitly retained. Quarterly figures typed as account and an allegation edge targets the recipient despite no recipient misconduct claim. |
| X004 | None; two Alex Morgan people and their distinct full email identifiers preserved. Vendor organizations inferred from domains; invited_to implies completed invitations where the source only requests them. |
| X005 | Medium; amount and suffixes retained with no full-account invention. Summary/fact/rationale invent an alleged error as the reason for replacement; the source gives no reason. Placeholder sender organization inferred from an address. |

## Limits and next work

Operational failure and semantic failure are separate. Exact source quotation and valid entity references do not prove entailment. Rates on these 15 development examples are not population precision/recall; no independent human audit or repeated stochastic runs were performed. Full local outputs are ignored under evaluations/reports/ and contain sources/prompt snapshots.

Prioritize token-aware Groq admission control (including repair budgets), bounded output generation for local models, and evidence-bearing signal extraction with an explicit separately evaluated policy layer. Preserve allegation status and direction in graph contracts. Expand held-out benign/adversarial cases before tuning prompts or the catalog; do not weaken validators simply to increase completion. No behavior/prompt/catalog tuning was performed during this comparison.
