# Prompt-Only Llama Experiment v2 — 2026-10-06

## Decision

Do not promote v2. Restored both default backend prompts byte-for-byte from the preceding committed version. The attempted improvement made the overall pipeline less reliable. The candidate prompts are preserved under `evaluations/prompts/v2/` alongside this report so that the failed experiment is reproducible.

Only prompts changed in the experiment. Native Ollama 0.35.1 and llama3.2:3b (local model ID a80c4f17acd5), temperature 0, default context, schema/policy versions 1/1, 60-second per-attempt timeout, one retry and application code were unchanged. No retrieval, framework, generation limit or provider switch was introduced.

## Changes tested

The candidate adds explicit fact kinds, exact-substring values, conditional/allegation preservation, short evidence quotes, contrastive synthetic illustrations, a clearer risk rubric, entity-type guidance and limits on graph size. Illustrations do not copy seed names, identifiers or monetary values. However, the prompts were informed by inspected seed failures: this is development-set regression testing, not independent generalization evidence. Multiple prompt dimensions changed together, so this experiment cannot isolate which change caused regression.

## Measured comparison

| Measurement | Original baseline | v2 |
| --- | --- | --- |
| Completed pipeline | 5/10 | 2/10 |
| Persisted validated extraction, including partial results | 8/10 | 6/10 |
| Accepted risk among completed cases | 2/5 | 2/2 |
| Completed and accepted risk over all inputs | 2/10 | 2/10 |
| Final extraction evidence failures | 2 | 4 |
| Final assessment entity-reference failures | 0 | 2 |
| Final assessment timeouts | 3 | 2 |

The 2/2 conditional risk agreement is not a quality improvement: it comes from only two surviving cases, both with semantic errors. Failed runs have no v2 risk decision. API details can show prior successful selections; only the current run's output was counted. A formally validated result is not automatically a semantically correct one.

- Experiment interval: 2026-10-06T10:37:33.205655+00:00 to 2026-10-06T10:49:06.083867+00:00, 692.88 seconds elapsed.
- Extraction prompt SHA-256: `6a82859dd67824d83b380ad302714c172fa97e3326c65270fadf126093336e6a`.
- Assessment prompt SHA-256: `433afbe5bb72edd52d49c9b48976eb88692533f4d9157d5dee4e51ed95e1aee2`.
- Full local output: `evaluations/reports/llama3.2-3b-prompts-v2.json`, ignored by Git. It includes per-run provenance, results and stage metadata; Codex review notes are separate from pending independent human review.
- Original comparison: [baseline](LLAMA_BASELINE_2026-10-06.md).

## Per-case review

| Case | Baseline status | v2 status | v2 risk | Seconds | Codex source/output review |
| --- | --- | --- | --- | --- | --- |
| E001 | completed | failed | — | 58.24 | Extraction rejected after two attempts for evidence/source mismatch. Previous baseline assessment in detail is retained history, not a v2 result. |
| E002 | completed | failed | — | 50.20 | Extraction rejected after two attempts for evidence/source mismatch. Previous none result is not counted for this run. |
| E003 | failed | failed | — | 46.17 | Extraction rejected after two attempts for evidence/source mismatch; no improvement over baseline failure. |
| E004 | failed | failed | — | 82.33 | Extraction rejected after two attempts for evidence/source mismatch; baseline at least preserved partial extraction. |
| E005 | completed | failed | — | 34.16 | Extraction preserved but still types shares as amount and omits deletion request. Assessment failed after two attempts with invalid entity references; old medium assessment is not a v2 result. |
| E006 | completed | completed | high | 34.16 | High risk is accepted and rationale recognizes threats. Extraction misclassifies six months as amount; graph still derives person/organization from an address despite prompt instructions. Not semantically clean. |
| E007 | failed | completed | none | 48.20 | Previously failed case now completes with accepted none risk. arcline is misclassified as account suffix, holidays as organizations, and graph relationships are unsupported by their quotes. Rationale calls the holiday notice maintenance. |
| E008 | failed | failed | — | 60.26 | URL now appears as a dedicated fact, but domains are misclassified as account suffixes. Assessment failed after two attempts with invalid entity references. |
| E009 | completed | failed | — | 140.55 | Partial extraction includes amount, routing and account suffix. Assessment timed out on both attempts. Previous baseline medium risk is not a v2 risk decision. |
| E010 | failed | failed | — | 138.57 | Partial extraction drops currency/approximation in amount value, misses allegation structure and cites an unrelated quote for organization arcline. Assessment timed out on both attempts. |

## Reproduce the archived experiment

From backend/, select the archived files explicitly without modifying the default .env:

```sh
LLM_PROVIDER=ollama OLLAMA_MODEL=llama3.2:3b LLM_TIMEOUT_SECONDS=60 LLM_MAX_RETRIES=1 AGENT_A_SYSTEM_PROMPT_PATH=../evaluations/prompts/v2/extraction_system.txt AGENT_B_SYSTEM_PROMPT_PATH=../evaluations/prompts/v2/risk_graph_system.txt uv run --locked uvicorn mailrisk.api:app --host 127.0.0.1 --port 8000
```

From repository root, with that backend running:

```sh
uv run --project backend --locked python -u evaluations/run.py   --output evaluations/reports/llama3.2-3b-prompts-v2-repeat.json
```

Use a new report name to preserve previous outputs. The local database retains run history; failed reanalysis continues to expose earlier successful selections, not a new successful result.

## Interpretation and next step

Prompt-only optimization was tested before infrastructure or model changes and did not improve this iteration. Longer instructions and negative examples are not proven causes; raw invalid model output is not retained in the collector, and repeatability was not tested. Evidence errors can represent quote or source-ID mismatch. Do not infer a precise cause from the normalized error alone.

A subsequent prompt experiment should change one small element at a time, beginning with a compact positive JSON example for Agent A and explicit supported risk signals for Agent B. Add independently reviewed held-out cases and repeat runs before claiming improvement. Do not promote a candidate solely because conditional risk agreement rises while completion falls. Broader changes such as deterministic extraction, stricter typed contracts, source-ID simplification, or a different model are separate experiments.

Twenty deterministic backend tests passed with the candidate prompts loaded. No application logic or schemas changed. After collecting all ten cases, the backend was stopped; native Ollama remains running. Default prompt files are restored, and .env/seeds are unchanged. The local database contains selected results from different prompt versions, identifiable through persisted prompt hashes.
