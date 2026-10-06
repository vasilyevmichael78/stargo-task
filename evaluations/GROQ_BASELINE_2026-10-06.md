# Groq Baseline Comparison — 2026-10-06

## Outcome

The accessible Groq model openai/gpt-oss-120b completed nine of ten paced runs using the original baseline prompts, versus five of ten for local llama3.2:3b. Seven of nine completed risk levels matched existing accepted ranges, versus two of five for local Llama. GPT-OSS is a more promising candidate for this application, but observed under-triage, extraction gaps and graph grounding issues prevent a claim of unattended reliability.

One paced run ended in a provider rate limit; it has no risk decision and is not a semantic failure score. This is a single small seed regression comparison reviewed by Codex, not an independently human-reviewed or held-out accuracy benchmark.

## Model selection and execution conditions

- User requested Groq with the stronger model configured in backend/.env and baseline prompts.
- Configured llama-3.3-70b-versatile returned model_not_found for the supplied key. Ten submissions failed with configuration errors. The models API listed openai/gpt-oss-120b as accessible. Root explicitly announced selecting it for a separate experiment; no application fallback was added.
- Backend launch override: `LLM_PROVIDER=groq GROQ_MODEL=openai/gpt-oss-120b uv run --locked uvicorn mailrisk.api:app --host 127.0.0.1 --port 8000` from backend/. The private .env was not edited, and its configured model may still be unavailable. Select the tested model explicitly when running Groq.
- Same original prompt files/hashes as the Llama baseline; temperature 0, schema/policy versions 1/1, 60-second timeout and one retry. Application code unchanged.
- Ollama uses native schema format; Groq uses JSON object mode with schema instructions. Provider transport, model, hardware and request pacing differ, so this is a comparison of deployed configurations, not a controlled attribution to model size alone.
- Groq response exposed a free-plan TPM limit of 8000. The app caps Retry-After waits at five seconds; a measured response requested eight seconds. Short retry waits and no token-budget admission control can fail even single-concurrency analysis.
- First GPT-OSS unpaced run: 0/10 completed, eight partial extractions, all ten final failures rate_limit. No quality score inferred from those outages.
- Paced run: initial 60-second cooldown, then the existing CLI once per case with 60-second gaps. Pacing was external evaluation control, not a new app feature. E004 still exceeded quota on assessment.
- Paced experiment interval: 2026-10-06T10:56:35.896442+00:00 to 2026-10-06T11:08:09.445957+00:00, 693.55 seconds including cooldowns/gaps.
- Completed-case median latency: 8.06 seconds, including API polling but excluding between-case cooldowns. Baseline local Llama median: 38.15 seconds. No percentile claim is made from nine observations.
- Successful stage metadata recorded 50012 total tokens across the paced run; failed calls may not expose usage. This is not a complete billed-usage estimate. Reasoning token counts are included where returned by Groq.
- Provider availability/model guidance: [Groq models](https://console.groq.com/docs/models), [rate limits](https://console.groq.com/docs/rate-limits).

## Metrics

| Metric | Local Llama baseline | Groq GPT-OSS, unpaced | Groq GPT-OSS, paced |
| --- | --- | --- | --- |
| Completed pipeline | 5/10 | 0/10 | 9/10 |
| Validated extraction, including partial results | 8/10 | 8/10 | 10/10 |
| Accepted risk among completed cases | 2/5 | Not available | 7/9 |
| Completed and accepted risk over all cases | 2/10 | 0/10 | 7/10 |

Accepted level is a screening check, not an overall semantic quality score. In the paced run, all three benign cases received none, and E001/E008 now received high. E003/E005 remain medium instead of expected high. Rationale text is not matched verbatim.

## Case review

| Case | Local baseline | Groq paced | Seconds | Codex source/output review |
| --- | --- | --- | --- | --- |
| E001 | medium | high | 10.06 | Expected high risk now reached. Amount, secrecy and pending account details extracted. Rationale incorrectly calls pending details changed details; graph models an unspecified future account as an account and asserts identity links not independently verified by their quotes. |
| E002 | none | none | 6.05 | Expected none risk. Summary preserves optional reinstall but one fact states reinstall is required. Organization membership inferred from email domains rather than independently verified. |
| E003 | failed | medium | 10.06 | Completed with medium versus expected high: exfiltration signal recognized but under-triaged. Both contract amounts extracted. Graph infers a person name and employment from an address without sufficient evidence. |
| E004 | failed | failed | 12.08 | Partial extraction includes current and previous account suffixes, routing, invoice amount and historical amounts. Assessment exhausted retries on rate_limit; no new risk or graph decision. |
| E005 | medium | medium | 8.06 | Completed with medium versus expected high. Trading tip recognized but under-triaged; facts is empty and deletion request omitted. Graph infers a person and employment from an address. |
| E006 | medium | medium | 6.05 | Medium is accepted; threats recognized without inventing an office address or physical incident. facts is empty. Organization nodes inferred from domains need uncertainty; graph threat direction is more plausible than baseline. |
| E007 | failed | none | 12.06 | Expected none risk and closure dates extracted. Filename is available in source metadata but the chosen quote does not substantiate the filename label. Organization membership is inferred from domains. |
| E008 | failed | high | 8.05 | Expected high phishing risk, with urgency and lookalike domains recognized. URL is not a dedicated extraction fact; graph organization membership remains inferred rather than verified. |
| E009 | medium | none | 12.07 | Expected none risk, eliminating baseline false positive. Amount, routing, account suffix and net-15 terms extracted. Some invoice relationships cite only target values instead of quotes establishing both endpoints. |
| E010 | failed | medium | 8.05 | Expected medium risk. Summary and rationale preserve anonymous allegation; facts identify person and amount. Graph instructed_move presents the allegation as an event without explicit allegation qualifier, and employee_of lacks evidence for named organization. |

## Reproduction and artifacts

Normal collector command from repository root:

```sh
uv run --project backend --locked python -u evaluations/run.py --output evaluations/reports/groq-gpt-oss-120b-baseline.json
```

For the paced experiment the collector was invoked separately for E001 through E010, with an initial 60-second wait and 60-second gaps between invocations:

```sh
uv run --project backend --locked python -u evaluations/run.py --ids E001 --output evaluations/reports/groq-paced-E001.json
```

An orchestration script combined these single-case outputs into `evaluations/reports/groq-gpt-oss-120b-paced.json`. The existing collector itself has no pacing option. Original and new results were preserved separately:

- `evaluations/reports/groq-llama3.3-70b-baseline.json`: inaccessible configured model.
- `evaluations/reports/groq-gpt-oss-120b-baseline.json`: unpaced quota failures.
- `evaluations/reports/groq-gpt-oss-120b-paced.json`: combined paced run plus Codex review notes.
- `evaluations/reports/groq-paced-E001.json` through E010: original per-case results.

Full reports are ignored by Git because they contain source data. They preserve run IDs, model/provider, prompt hashes, schema/policy versions, timings and available usage. Independent human semantic_review remains pending. Prior selected successful results on a failed reanalysis are not counted as current-run results.

## Next priorities

1. Handle provider quota deliberately: bounded Retry-After compliance, stage/job deferral until sufficient token budget, and explicit generation budgets. Minute-scale waits should not masquerade as model inference latency. No paid-plan upgrade is required to investigate this.
2. Improve structured fact completeness and risk calibration for exfiltration and preannouncement trading on independently reviewed development cases; use held-out cases for evaluation.
3. Preserve uncertainty in identity/employment and alleged graph events; relationship evidence must support its meaning, not merely exist in the source.
4. Repeat runs to assess variability, then evaluate prompt injection and longer attachments before claiming general reliability.

The experiment backend was stopped after collection. Native Ollama remains running; frontend remains stopped. No .env secrets, defaults, prompts, schemas or application code were changed. SQLite retains analysis history and now contains selected successful results from multiple providers/prompt versions.
