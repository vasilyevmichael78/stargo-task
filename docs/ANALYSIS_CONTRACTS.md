# Analysis Contracts, Schema 2

## Ownership and lifecycle

Agent A extracts source-grounded facts; Agent B identifies evidence-bearing policy signals and proposes entities/relationships. Its application stage combines those observations with deterministic policy to produce the assignment-required level, rationale and tags. Both outputs forbid extra fields. The orchestration service validates structure, source quotes and supported references before persistence. Agent B requires validated A. Parsed source metadata replaces generated sender/recipient/date/subject values, without authenticating those headers.

New runs record schema `2`, orchestration `5`, decision engine `1`, provider/model, generation settings, policy revision/hash/snapshot and prompt hashes/snapshots. Repair uses the same immutable run policy and prompts, with the existing maximum of two calls per stage. Failed B preserves A; failed reanalysis preserves previously selected successful results. No provider fallback or automatic startup inference is introduced.

## Model output versus public result

Agent B's risk object contains only observations:

```json
{
  "risk": {
    "signals": [
      {
        "id": "urgency",
        "evidence": [{"source_id": "source-id", "quote": "Exact source text"}]
      }
    ]
  },
  "entities": [],
  "relationships": []
}
```

Each signal must have a distinct ID present in the run's catalog and one to four citations. Source IDs must exist; quotes must be exact substrings after optional unambiguous whitespace alignment. Catalog examples are not source evidence. Unknown IDs, duplicate IDs, missing evidence and invalid references enter bounded repair. The model cannot supply `level`, `rationale` or `tags`.

The application persists and returns the compatible risk result shape: `level`, `rationale`, `tags`, plus `signals`, `matched_rule_ids` and `decision_engine_version`. Tags are the validated observed signal IDs. All rules whose required signals are present match; the highest severity wins and its rule explanations form the rationale. All matched rule IDs are retained. If no rule matches, engine 1 treats `payment_request` and `departure` alone as neutral; other signals yield `low`. Empty observations yield `none`, with an explicit safety limitation. Custom neutral-signal configuration is not implemented.

The existing catalog field `suggested_level` now drives the deterministic advisory decision. Level definitions and examples inform detection; they are not calibrated scores. Editing the catalog changes future submitted runs only. Policy 3 includes `payment_concealment`: payment request + urgency + secrecy produces `high` without requiring a guessed identity mismatch. An unrelated missing payment amount does not downgrade matched exfiltration or trading rules.

## Facts and graph vocabulary

Fact kinds: `amount`, `date`, `duration`, `account`, `reference`, `url`, `document`, `identity`, `request`, `allegation`, `event`, `other`. At most 40 facts, each with nonempty value and source evidence.

Entity types: `person`, `organization`, `amount`, `account`, `location`, `email`, `date`, `duration`, `document`, `url`, `phone`, `other`. At most 40 entities and 60 relationships. Names, dates and account suffixes do not establish shared identity. Only full email labels merge; an address label must appear in its citation. Amount labels require numeric values also present in their evidence, including common English thousand/million notation. This check rejects invented zero or changed numbers, but does not establish currency, monetary meaning or international numeric-format correctness.

| Relationship | Source → target types | Required source status |
| --- | --- | --- |
| `claims_identity` | person → email | `claimed` |
| `employed_by` | person → organization | Explicit status from the source |
| `requests_transfer_to` | person/organization/email → person/organization/account | `requested` |
| `replaces_account` | account → account, new → old | Explicit status from the source |
| `requests_forwarding_to` | person/organization/email → person/organization/email | `requested` |
| `requests_action_from` | person/organization/email → person/organization/email | `requested` |
| `alleges_against` | person/organization/email → person/organization | `alleged` |
| `located_at` | person/organization → location | Explicit status from the source |
| `mentions`, `associated_with` | Existing entities | Explicit status from the source |

Every relationship requires evidence and `modality`: `asserted`, `claimed`, `alleged` or `requested`. `asserted` means stated in the source, not independently verified. Endpoint-role constraints and specific required modality are enforced in code. New-to-old account direction is a prompt contract, not yet a semantic code check. Generic relationships still need analyst review to avoid vague or invented associations.

## Compatibility and activation

Old run JSON remains readable without model revalidation. SQLite adds a relationship `modality` column with `unspecified` for historical rows. The precomputed fixture is unchanged, including policy 2 and observed failures. Frontend extensions are optional for those historical results. Historical scores are not evidence for the new schema/prompts.

From `backend/`, `uv run python -m mailrisk.policy_cli` explicitly activates the catalog at `RISK_CONTEXT_PATH` in the configured runtime database, preserving old revisions and runs. Alternatively use the JSON editor and its optimistic revision check. Export custom edits before explicit replacement; startup never silently overwrites them. Current results change only after a new successful analysis.

## Remaining uncertainty

Quotes establish textual presence, not semantic entailment. The model can omit signals, select a wrong signal with a real quote, misclassify entities, or invent an interpretation in the summary. Deterministic severity makes the policy decision reproducible conditional on signals; it cannot make signal detection reliable by itself. Keep analyst review and evaluate severe misses, benign false positives, evidence entailment and relationship meaning on independently reviewed held-out cases.
