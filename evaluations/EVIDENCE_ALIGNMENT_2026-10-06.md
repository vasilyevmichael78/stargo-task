# Evidence whitespace alignment — 2026-10-06

## Diagnosis and correction

The user reported repeated extraction quote_mismatch. Both attempts failed at facts[3].evidence[0].quote in approximately 28 seconds each, despite a 180-second timeout. A direct local extraction reproduction found five evidence references: four literal matches and one unique whitespace-only match. Raw source/model content was not exported or logged.

Orchestration version 4 aligns only a uniquely matched whitespace variant to the original source substring before running strict validators. It does not alter words, punctuation, numbers or source IDs. Unknown sources, ambiguous matches including overlapping spans, and semantic changes remain failures. Original message/source text is unchanged. Per-attempt evidence_alignments records paths/methods; raw invalid outputs remain request-local.

## Actual application verification

- Model: qwen3.5:4b / ollama; temperature 0, num_ctx 8192, thinking false, per-call timeout 180, additional retry budget 1.
- Schema/policy versions: 1 / 2; orchestration version: 4.
- Started: 2026-10-06T12:42:02.260414+00:00; finished: 2026-10-06T12:43:50.731252+00:00; elapsed 108.45 seconds including polling.
- Outcome: completed. Extraction: one call, 23.87 seconds, one deterministic quote alignment. Assessment: one call, 84.42 seconds. Returned risk: high.
- The persisted extraction passes strict evidence validation. Both stages completed without model repair. Selected successful result is available in the existing runtime database; prior failure history remains intact.
- Prompt hashes and catalog hash are unchanged from the failing configuration; only orchestration changed. A single example does not establish general quality; full fact/risk/graph semantics and independent human review remain pending.

A final guard includes overlapping regex matches when checking uniqueness. It was added after the live run, tested with an adversarial overlapping example, and checked against the actual source span; the same original substring was recovered. No further model call was needed for that deterministic boundary check.

## Engineering checks and limitations

46 backend tests passed; Ruff lint/format and whitespace checks passed. Tests cover newline/tab/multiple-space alignment, exact persisted quotes, assessment entity/relationship quotes, rejection of changed amounts/negation/punctuation, unknown sources and ambiguous/overlapping spans. Frontend code was unchanged and not retested for this block. Existing Starlette TestClient deprecation warning remains.

Metadata-only local report: evaluations/reports/qwen-whitespace-alignment-smoke.json (ignored). No private email content appears in this document. No new seed baseline, held-out, repeatability, or prompt-injection evaluation was performed. Formatting alignment preserves source quotation; it does not prove the associated fact or risk interpretation.
