# Llama with editable JSON risk context — 2026-10-06

## Method and provenance

Development smoke on E001, E005, and E009 through actual AnalysisService processing and Ollama, in an isolated temporary SQLite database. Original source normalization and seed content were preserved. No expected answers were sent to inference. This is not a held-out evaluation or a model-only/policy-only comparison.

- Model/provider: llama3.2:3b / Ollama; previously downloaded model ID a80c4f17acd5.
- Generation: temperature 0, optional thinking false, num_ctx 8192, timeout 60 seconds per call, one additional call per stage.
- Schema version: 1; policy version: 2; orchestration version: 3.
- Catalog: 13 signals, 7 advisory rules; complete catalog injected only into Agent B. No embeddings, retrieval, autonomous tools, or deterministic rule execution.
- Risk context hash: `9f2e238b853b2367713f2c6dd67546feb6ac363e90a5ad16fdc6dd76bcb11759`; isolated database revision ID: `b44c303c-cd26-4a55-b53f-41a072660ff4`.
- Extraction/assessment/repair prompt hashes: `21c264ccda923e3993828399d62b3acf9173e60160d8f58c52df0eea2ae74821`, `a225638785e35cce9f513e05016598f91130494b4ce255c545055974f3ea6edc`, `66069965ef41e4e42b733f24ad8e80141eadec003e67d3c72997a9c310e8c93d`.
- Started: 2026-10-06T12:06:43.185057+00:00; finished: 2026-10-06T12:11:07.835808+00:00; elapsed 264.65 seconds.
- Backend/Vite remained running; hardware contention was not controlled.

## Results

| Case | Outcome | Risk | Accepted levels | Assessment calls | Elapsed seconds |
| --- | --- | --- | --- | --- | --- |
| E001 | failed | — | high | 2 | 132.76 |
| E005 | completed | medium | high | 1 | 60.37 |
| E009 | completed | medium | none, low | 2 | 71.52 |

Completion: 2/3. Validated extraction: 3/3. Accepted risk among completed cases: 0/2; completed-and-accepted coverage: 0/3. This is a development result, not general accuracy. The historical original Llama baseline completed these three cases but also accepted none of their risk levels; context size, repair orchestration, and policy changed, so causal attribution is not possible.

## Codex source/output review

- **E001:** extraction retained $184,500 and the claimed wire request; "new escrow partner" was incorrectly typed as an account/reference fact. Assessment timed out twice; risk quality cannot be scored. Valid extraction remained available.
- **E005:** extraction captured the deal name, share suggestion and relative announcement timing but mistyped shares as a monetary amount and a deal as payment metadata. Assessment returned medium instead of high and introduced payment, urgency, secrecy and identity-mismatch signals unsupported by this source. It treated absence of threats/allegations as mitigating unrelated trading risk. Catalog context did not prevent these errors.
- **E009:** extraction retained invoice amount, net-15 terms, routing and account suffix. The first assessment referenced an absent entity; the real repair attempt corrected structure and completed. The final medium risk still invented urgency/secrecy and payment-impersonation/exfiltration concerns for an ordinary invoice. Structural repair did not establish semantic correctness.

No independent human review, full ten-case run, repeats, adversarial injection run or held-out testing was executed. Full local report is ignored at evaluations/reports/llama3.2-3b-risk-catalog-smoke.json. Existing selected results were not counted as new successes.

## Engineering/UI validation

35 backend tests passed, including catalog validation/size, bootstrap failures, SQLite restart persistence, duplicate-content reuse, optimistic concurrency, per-run snapshots, A/B context isolation, API snapshot exclusion and rejection of catalog examples as source evidence. Eight frontend tests passed, including local JSON validation/save and retained edits after conflict. Type checking/build and format checks were executed. Existing Starlette TestClient deprecation warning remains.

Real browser checks loaded the current catalog, rejected malformed JSON without saving, and successfully saved identical valid content without creating a redundant revision. Desktop and a 390-pixel viewport override showed no horizontal page overflow; the browser's effective CSS viewport during the mobile check was 325 pixels. Temporary viewport overrides were reset. Meaningful edits/conflicts are covered by deterministic API/UI tests; no substantive test edits were left in the active runtime catalog.

## Interpretation and next work

The editable, versioned catalog is implemented as experimental advisory context. This smoke does not justify a claim of improved risk quality. Next isolate evidence-bearing signal extraction and forbid unsupported signals, evaluate a transparent policy layer separately, investigate timeout/output budgets, and test independently authored examples. Selective retrieval may help as the catalog grows, but keyword or embedding matches alone do not prove a signal is present.

Repeat through the standard API collector after starting the configured backend:

```sh
uv run --project backend python evaluations/run.py --ids E001 E005 E009 --output evaluations/reports/llama-catalog-repeat.json
```
