# Precomputed demo database

mail_risk_groq.sqlite3 is a compacted SQLite snapshot of the real Groq / openai/gpt-oss-120b expanded evaluation completed on 2026-10-06. It contains the unchanged ten assignment seeds plus five synthetic evaluation emails, fifteen runs (thirteen completed, two failed), selected successful results, persisted entities/relationships, evidence, prompt/catalog snapshots and provenance. It is observed model output, not fabricated perfect results or verified compliance findings. Failures remain visible and retryable; see [the comparison](../../evaluations/EXPANDED_COMPARISON_2026-10-06.md).

SHA-256: b246dad7cb39e77f2f92b9d2dc742e6bf63148fba11d1e815d9e334cef2b626b.

The source messages/attachments were checked against mock_mailbox_data.json and evaluations/cases.json. SQLite integrity/foreign keys were checked. The copy was vacuumed to remove unused/deleted page contents, and credentials were checked before committing. Runtime messages, backups and future evaluation databases stay ignored.

On application creation, BOOTSTRAP_DATABASE_PATH copies this fixture atomically to a missing DATABASE_PATH; an existing database is never replaced. The fixture must not be used as the writable runtime path. Startup imports missing seed records but performs no inference. New ingestion and manual retry use the currently configured provider; historical results continue to identify Groq GPT-OSS independently of that provider. Empty BOOTSTRAP_DATABASE_PATH disables copying and yields unassessed seed records in a new database.

Do not edit this binary as an application database. Refresh it only after an explicitly requested evaluation, source/secret review and fixture tests, updating its hash/provenance alongside it. The archive contains the [raw Groq report](../../evaluations/artifacts/groq-expanded.json).
