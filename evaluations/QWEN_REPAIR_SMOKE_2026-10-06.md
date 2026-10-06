# Qwen 3.5 4B and bounded repair smoke — 2026-10-06

## Scope and configuration

Actual Ollama inference through `AnalysisService.process` for E001, E005, and E009, using an isolated temporary SQLite database and original seed normalization. This is a development smoke, not a ten-case baseline or a model-only comparison: model, optional thinking configuration, and orchestration changed together. Expected evaluation answers were never passed to inference.

- Provider/model: Ollama / qwen3.5:4b; downloaded manifest ID d8b0f5e9760c (3.3 GB).
- Temperature: 0; thinking: false; per-call timeout: 60 seconds; additional retry budget: 1 per stage.
- Schema/policy versions: 1 / 1; orchestration version: 2.
- Started: 2026-10-06T11:43:24.535453+00:00; finished: 2026-10-06T11:51:53.608940+00:00.
- Elapsed: 509.07 seconds, including retries.
- Prompt hashes, in extraction/assessment/repair order: `21c264ccda923e3993828399d62b3acf9173e60160d8f58c52df0eea2ae74821`, `c3b2e29a976e395b0d3267985aaf17545deb73de509be15230773186b78b7048`, `66069965ef41e4e42b733f24ad8e80141eadec003e67d3c72997a9c310e8c93d`.
- The regular backend remained running with autoreload; this was not a controlled hardware benchmark. `/health` confirmed ollama / qwen3.5:4b.

## Results

| Case | Extraction attempts | Extraction seconds | Assessment attempts | Final outcome |
| --- | --- | --- | --- | --- |
| E001 | 1 | 59.36 | 2 | failed / timeout |
| E005 | 1 | 38.38 | 2 | failed / timeout |
| E009 | 1 | 48.16 | 2 | failed / timeout |

All three extractions passed structural/evidence validation on the first attempt. All three assessments timed out twice. Completion: 0/3. Partial extractions were preserved. No completed risk output exists to score; semantic review remains pending. Timed-out calls did not return token usage.

No real invalid-output repair was observed in this smoke: assessment calls failed at transport timeout, so both attempts used `generate`, not `repair`. Deterministic tests demonstrate successful schema, source/quote, duplicate-ID, and relationship-reference repair, bounds/exhaustion, upstream preservation, immutable repair snapshots, and isolation of transient retries. These tests are not evidence of real-model semantic accuracy.

## Implementation and limitations

Invalid output receives the previous response (at most 8,000 characters) and up to 20 specific validator errors as untrusted request data. The next response is validated completely again. Repair and transient retries share a maximum of two calls per stage. Raw invalid outputs remain request-local; sanitized per-attempt metadata is persisted. Restart marks unfinished runs interrupted; this does not add resumable jobs or conversational memory across runs.

The initial smoke mistakenly shared the live application's runtime database; autoreload interrupted that run. It was stopped, and evaluation was moved to an isolated database. An intermediate isolated process was also stopped before completion to evaluate the final versioned repair-prompt implementation. Neither incomplete trial is included in this report. Existing selected successful results were not used as new outputs.

Next steps: investigate assessment output length and runtime behavior, run a controlled timeout/output-budget experiment, then run the full ten cases and held-out inputs. Do not interpret structural validation as factual entailment, or promote Qwen based on this smoke.

Full local report: `evaluations/reports/qwen3.5-4b-repair-smoke.json` (ignored by Git; contains source-derived results). To repeat the cases through the standard API collector after starting the configured backend:

```sh
uv run --project backend python evaluations/run.py --ids E001 E005 E009 --output evaluations/reports/qwen-repeat.json
```
