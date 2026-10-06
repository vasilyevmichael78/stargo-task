# Focused Schema-2 and Policy-3 Verification

Executed on 2026-10-07 in the local Asia/Jerusalem timezone (UTC runs started on 2026-10-06). This is a development verification of a deliberate contract/policy change, not a replacement for the fifteen-case comparison or an independently reviewed quality benchmark. No PROCESS entry was added, as requested by the user.

## Change and executed engineering checks

Agent B now extracts source-cited, catalog-validated signals. The application calculates advisory severity from the immutable run policy. Schema 2 also constrains fact/entity/relationship types, relationship source status and endpoint roles, and validates supported amount/email labels. Parsed metadata overrides generated metadata. Historical results and the committed SQLite fixture remain readable and unchanged.

- `uv run --project backend --locked --offline pytest backend/tests -q`: **63 passed**, with the existing Starlette/httpx deprecation warning.
- Ruff lint and format checks: passed.
- `npm test`: **14 passed**; `npm run build` and `npm run format:check`: passed.
- `git diff --check`: passed. No live browser/mobile inspection or load test was executed in this block.
- Historical fixture SHA-256 remained `b246dad7cb39e77f2f92b9d2dc742e6bf63148fba11d1e815d9e334cef2b626b`. A test migrates a copy, preserves runs/policy snapshots, and marks legacy relationships `unspecified`.
- Runtime policy was explicitly activated as version 3, hash `544d4d8c55c58bbf57eb470c76fae19a315226839b36da38bd4afb3ded4f713d`, only after checking that its active revision matched the historical default. Existing selected results were not rerun.

## Real Groq inference

Provider/model: `groq` / `openai/gpt-oss-120b`. Timeout 180 seconds per call, one additional attempt per stage, temperature 0. Isolated database `/tmp/stargo-contract-v2-groq.sqlite3`; external pacing 65 seconds between cases. These calls use the actual application worker, provider adapter, validation, decision policy and persistence, bypassing HTTP/UI.

Initial command, from the repository root:

```bash
uv run --project backend --locked python evaluations/compare.py \
  --provider groq --model openai/gpt-oss-120b \
  --ids E003,X002,X004,X005 \
  --database /tmp/stargo-contract-v2-groq.sqlite3 \
  --output evaluations/reports/contract-v2-groq.json --pause 65
```

| Case | Initial outcome | Level screen | Seconds excluding pacing |
| --- | --- | --- | --- |
| E003 | Completed, high | Accepted | 7.55 |
| X002 | Failed B: schema echo, then rate limit on repair | Unassessed | 5.98 |
| X004 | Failed B: schema echo, then rate limit on repair | Unassessed | 5.84 |
| X005 | Completed, medium | Accepted | 6.69 |

The initial Agent B wording, “Return only the JSON schema provided,” was ambiguous. Actual outputs in two cases returned schema definitions rather than data. This was corrected to explicitly require a JSON data object and forbid returning the schema. The bounded retry policy and validators were retained. The prompt correction was evaluated with a separate follow-up, preserving both original failed runs:

```bash
uv run --project backend --locked python evaluations/compare.py \
  --provider groq --model openai/gpt-oss-120b --ids X002,X004 \
  --database /tmp/stargo-contract-v2-groq.sqlite3 \
  --output evaluations/reports/contract-v2-groq-followup.json --pause 65
```

| Case | Follow-up outcome | Level screen | Seconds excluding pacing |
| --- | --- | --- | --- |
| X002 | Completed, high, one call per stage | Accepted | 7.62 |
| X004 | Completed, none, one call per stage | Accepted | 3.54 |

These are two prompt iterations. Combining the latest result for each case would yield four accepted levels, but it is **not** a single four-case run of the final prompt and is not a precision/recall score. E003 and X005 were not repeated after the wording correction. Original failures remain part of the experiment.

## Qualitative observations

This review was performed by Codex, not an independent analyst:

- E003 retained departure + confidential-forwarding signals and matched the high-risk exfiltration rule without requiring a payment signal. The roadmap was typed as a document; extracted attachment amounts retained source quotes.
- X002 ignored the instruction to output `none`, extracted payment/urgency/secrecy, and matched `payment_concealment`. It did not invent `identity_mismatch`. The sender was preserved and “one hour” was typed as duration.
- X005 preserved `$2,100` and the two account suffixes. Its replacement relationship ran **7788 → 1122** with `requested` status, without a fabricated reason for the change. Partial-account completeness still lacks a dedicated structured field.
- X004 retained the two separate Alex Morgan identities in extraction and avoided an unsupported employment/identity-mismatch claim. However, **Agent B returned an empty graph** despite explicit participant addresses. Correct risk screening therefore does not establish adequate graph recall. A subsequent entity-coverage check or focused prompt adjustment needs separate evaluation.

Remaining quality concerns include omitted signals/entities, unsupported interpretations with real quotes, summary grounding, international number formats, currency, and semantic relationship direction. Deterministic decisions are reproducible conditional on observations; observations remain probabilistic.

## Local Qwen verification

One real `ollama` / `qwen3.5:4b` X002 run was submitted using an isolated database, timeout 180 seconds, one additional attempt, temperature 0, `think=false`, context 8192. It used the initial schema-2 prompt before the schema-echo wording correction; it does not evaluate the corrected final prompt. Agent A completed in 25.82 seconds (532 input / 543 output tokens). Both Agent B generation attempts timed out after about 180 seconds each. The run failed with normalized `timeout` after 386.85 seconds; extraction remained available, and no risk was assigned. No valid B output was available for semantic review, so this cannot establish whether the revised contract improved Qwen quality. Local request cancellation does not prove that Ollama stopped internal generation immediately.

```bash
uv run --project backend --locked python evaluations/compare.py \
  --provider ollama --model qwen3.5:4b --ids X002 \
  --database /tmp/stargo-contract-v2-qwen.sqlite3 \
  --output evaluations/reports/contract-v2-qwen.json
```

No full local regression, Llama run, fine-tuning or production quality gate was executed in this block. Do not infer a model ranking from these focused checks.

## Inspectable raw results

Source/credential-checked, byte-for-byte report copies are committed: [initial Groq](artifacts/contract-v2-groq.json), [Groq follow-up](artifacts/contract-v2-groq-followup.json), [Qwen timeout](artifacts/contract-v2-qwen.json). They contain only the existing assignment/synthetic evaluation inputs, observed outputs and provenance; original failures are retained. Prompt snapshots/hashes distinguish the two Groq iterations. Runtime evaluation databases and future local reports remain ignored.
