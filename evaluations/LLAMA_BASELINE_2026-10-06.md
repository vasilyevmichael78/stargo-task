# Llama 3.2 3B Seed Baseline — 2026-10-06

## Result

The current model/configuration is unsuitable for unattended email triage. Five of ten runs completed; two of the five completed risk levels matched the existing accepted ranges. Two completed risky cases were underestimated, and one ordinary invoice was a false positive. Failed runs are not counted as correct risk decisions. Every completed result also has extraction or graph grounding/type limitations observed during Codex review.

This is one real run per seed email, with bounded retries inside each stage. It is a small regression baseline, not a general accuracy estimate or independently human-reviewed benchmark. No prompts, model settings, or expectations were tuned during this run.

## Reproduction and configuration

- Executed: 2026-10-06 10:10:34–10:20:16 UTC, approximately 9 minutes 42 seconds.
- Native Ollama 0.35.1, Apple M4 / Metal; model llama3.2:3b, local ID a80c4f17acd5. Post-run ollama ps reported 100% GPU and 4096 context.
- Provider: ollama; temperature 0; streaming disabled; schema/policy versions 1/1.
- Current backend timeout: 60 seconds per attempt; one additional attempt maximum per stage. No output-token limit configured in the adapter.
- Extraction prompt SHA-256: `21c264ccda923e3993828399d62b3acf9173e60160d8f58c52df0eea2ae74821`.
- Assessment prompt SHA-256: `c3b2e29a976e395b0d3267985aaf17545deb73de509be15230773186b78b7048`.
- Full local output: `evaluations/reports/llama3.2-3b-baseline.json` (ignored by Git). It includes run identifiers, timestamps, provenance, stage metadata, sources and actual outputs. semantic_review remains pending independent human review; separate codex_review notes are included.
- Collector: `uv run --project backend --locked python -u evaluations/run.py --output evaluations/reports/llama3.2-3b-baseline.json` with the backend explicitly configured for Ollama / llama3.2:3b.

## Results by case

| Case | Pipeline | Actual risk | Accepted risk | Seconds | Codex source/output review |
| --- | --- | --- | --- | --- | --- |
| E001 | completed | medium | high | 32.15 | Underestimated risk (medium versus high). Invented UTC deadline and misclassified personal phone as an account. Identity/organization evidence does not support the entity labels. |
| E002 | completed | none | none/low | 22.10 | Correct none risk. Extraction strengthens a conditional reinstall request into required action. Sender entity cites body text without the address; sender relationship evidence does not establish both endpoints. |
| E003 | failed | — | high | 56.23 | Extraction rejected twice because evidence quotes did not match source. No validated extraction or risk available. |
| E004 | failed | — | medium/high | 136.52 | Validated partial extraction includes amount and new account; old account and historical amounts occur only inside a broad evidence quote rather than dedicated facts. Assessment exhausted retries and ended in timeout. |
| E005 | completed | medium | high | 38.20 | Underestimated risk (medium versus high). Rationale invents confidential forwarding before resignation. Shares typed as monetary amount, deal as account, recipient email as location; unsupported payment relationship. |
| E006 | completed | medium | medium/high | 38.15 | Medium risk is within expectations and threat is recognized. Empty payment fact, organization typed as account, weak identity evidence and incorrect threat direction make the graph unreliable. |
| E007 | failed | — | none/low | 38.19 | Extraction rejected twice for nonmatching evidence. No validated extraction or risk available. |
| E008 | failed | — | high | 84.32 | Partial extraction captures reset request and suspension threat; suspicious URL appears only in evidence, not a dedicated fact value. Assessment exhausted retries and ended in timeout. |
| E009 | completed | medium | none/low | 40.18 | False positive: ordinary invoice assessed medium with unsupported market abuse/exfiltration rationale. Amount, routing, suffix and net-15 terms extracted. Sender email classified as person and amount/account relationship insufficiently supported. |
| E010 | failed | — | medium/high | 96.39 | Partial extraction explicitly preserves allegation and approximately $300K in its quote, although the fact value drops approximately. Assessment exhausted retries and ended in timeout; no final risk or graph available. |

## Reliability versus quality

- Pipeline completion: 5/10. Validated extraction persisted for 8/10, including three partial failures.
- Failures: two extraction evidence-validation failures (E003/E007); three assessment failures ending in timeout (E004/E008/E010). Each failed stage used both permitted attempts. A final timeout does not imply every attempt timed out.
- Risk agreement among completed cases: 2/5. Complete-and-level-match coverage over all inputs: 2/10. Neither metric is a complete semantic quality score.
- Successful case end-to-end latency: 22.10–40.18 seconds; median 38.15 seconds. These include API polling and validation, not only model generation.
- Exact quote presence and schema validation rejected some bad outputs but admitted unsupported interpretations, incorrect entity types, and unsupported relationships. Structural validation cannot establish entailment.
- Benign invoice E009 was a false positive; E001 and E005 were under-triaged. E002/E006 risk agreement does not make their graphs correct.
- No successful model output is claimed for failed assessments. Partial extraction was retained. Groq, prompt injection, repeated-run variance, long attachments and held-out quality were not evaluated.

## Next experiments

1. Compare a larger candidate such as qwen2.5:7b or a suitable Groq model using the same frozen seed specification; do not assume improvement before measuring it.
2. Add separate, explicit facts for URLs, payment account changes and risk signals; preserve modality and uncertainty. Introduce type-specific nonempty value checks and narrower relationship semantics where useful.
3. Test bounded generation output and explicit context settings, then tune timeout from measured stage latency. Increasing timeout alone cannot fix unsupported claims or wrong risk decisions.
4. Evaluate any prompt/schema changes as a new version against benign/adversarial held-out cases, especially system-example contamination, anonymous allegations and embedded instructions. Preserve this baseline.
5. Require analyst review before operational use. Model-generated judgments in this report still need independent human review.

The backend used for evaluation was stopped after collection; Ollama remains available locally. Runs and selected successful results remain in the ignored local SQLite database.
