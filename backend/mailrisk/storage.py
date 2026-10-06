"""SQLite persistence; successful run selection and graph writes are atomic."""

import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import uuid4

from .domain import AppError
from .risk_context import load_risk_context, parse_risk_context


def now():
    return datetime.now(timezone.utc).isoformat()


def encode(value):
    return json.dumps(value, ensure_ascii=False)


class SQLiteStore:
    def __init__(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = str(path)
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS messages(id TEXT PRIMARY KEY, content TEXT NOT NULL, selected_run TEXT);
            CREATE TABLE IF NOT EXISTS analysis_runs(id TEXT PRIMARY KEY, message_id TEXT NOT NULL REFERENCES messages(id), status TEXT NOT NULL, data TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS runs_message ON analysis_runs(message_id);
            CREATE TABLE IF NOT EXISTS entities(id TEXT PRIMARY KEY, type TEXT NOT NULL, label TEXT NOT NULL, canonical_key TEXT UNIQUE);
            CREATE TABLE IF NOT EXISTS entity_mentions(run_id TEXT NOT NULL REFERENCES analysis_runs(id), entity_id TEXT NOT NULL REFERENCES entities(id), evidence TEXT NOT NULL DEFAULT '[]', PRIMARY KEY(run_id,entity_id));
            CREATE TABLE IF NOT EXISTS relationships(id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES analysis_runs(id), source_id TEXT NOT NULL REFERENCES entities(id), target_id TEXT NOT NULL REFERENCES entities(id), type TEXT NOT NULL, evidence TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS risk_context_revisions(id TEXT PRIMARY KEY, version TEXT NOT NULL, hash TEXT NOT NULL UNIQUE, content TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS risk_context_selection(id INTEGER PRIMARY KEY CHECK(id=1), revision_id TEXT NOT NULL REFERENCES risk_context_revisions(id));
            """)
            columns = {
                row["name"] for row in db.execute("PRAGMA table_info(entity_mentions)")
            }
            if "evidence" not in columns:
                db.execute(
                    "ALTER TABLE entity_mentions ADD COLUMN evidence TEXT NOT NULL DEFAULT '[]'"
                )
            relationship_columns = {
                row["name"] for row in db.execute("PRAGMA table_info(relationships)")
            }
            if "modality" not in relationship_columns:
                db.execute(
                    "ALTER TABLE relationships ADD COLUMN modality TEXT NOT NULL DEFAULT 'unspecified'"
                )

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def active_risk_context(self):
        with self.connect() as db:
            row = db.execute(
                "SELECT r.* FROM risk_context_revisions r JOIN risk_context_selection s ON s.revision_id=r.id WHERE s.id=1"
            ).fetchone()
        if not row:
            return None
        catalog, context_hash = parse_risk_context(row["content"])
        if context_hash != row["hash"] or catalog["version"] != row["version"]:
            raise AppError(
                "configuration", "Stored risk catalog integrity check failed."
            )
        return {
            "revision_id": row["id"],
            "version": row["version"],
            "hash": context_hash,
            "catalog": catalog,
            "created_at": row["created_at"],
        }

    def ensure_risk_context(self, path):
        current = self.active_risk_context()
        if current is not None:
            return current
        catalog, _ = load_risk_context(path)
        return self.save_risk_context(catalog)

    def save_risk_context(self, catalog, expected_revision_id=None):
        catalog, context_hash = parse_risk_context(encode(catalog))
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute(
                "SELECT revision_id FROM risk_context_selection WHERE id=1"
            ).fetchone()
            if (current["revision_id"] if current else None) != expected_revision_id:
                raise AppError(
                    "conflict",
                    "Risk catalog changed. Reload the current revision before saving.",
                    False,
                    409,
                )
            existing = db.execute(
                "SELECT id FROM risk_context_revisions WHERE hash=?", (context_hash,)
            ).fetchone()
            revision_id = existing["id"] if existing else str(uuid4())
            if not existing:
                db.execute(
                    "INSERT INTO risk_context_revisions VALUES (?,?,?,?,?)",
                    (
                        revision_id,
                        catalog["version"],
                        context_hash,
                        encode(catalog),
                        now(),
                    ),
                )
            db.execute(
                "INSERT INTO risk_context_selection VALUES (1,?) ON CONFLICT(id) DO UPDATE SET revision_id=excluded.revision_id",
                (revision_id,),
            )
            created_at = db.execute(
                "SELECT created_at FROM risk_context_revisions WHERE id=?",
                (revision_id,),
            ).fetchone()["created_at"]
        return {
            "revision_id": revision_id,
            "version": catalog["version"],
            "hash": context_hash,
            "catalog": catalog,
            "created_at": created_at,
        }

    def ingest(self, content, message_id=None):
        message_id = message_id or str(uuid4())
        with self.connect() as db:
            cursor = db.execute(
                "INSERT OR IGNORE INTO messages(id,content) VALUES (?,?)",
                (message_id, encode(content)),
            )
            return message_id, bool(cursor.rowcount)

    def message(self, message_id):
        with self.connect() as db:
            row = db.execute(
                "SELECT * FROM messages WHERE id=?", (message_id,)
            ).fetchone()
        if not row:
            raise AppError("not_found", "Email not found.", False, 404)
        return {
            "id": row["id"],
            **json.loads(row["content"]),
            "selected_run": row["selected_run"],
        }

    def run(self, run_id):
        with self.connect() as db:
            row = db.execute(
                "SELECT * FROM analysis_runs WHERE id=?", (run_id,)
            ).fetchone()
        if not row:
            raise AppError("not_found", "Analysis not found.", False, 404)
        return {
            "id": row["id"],
            "message_id": row["message_id"],
            "status": row["status"],
            **json.loads(row["data"]),
        }

    def latest(self, message_id):
        with self.connect() as db:
            row = db.execute(
                "SELECT id FROM analysis_runs WHERE message_id=? ORDER BY rowid DESC LIMIT 1",
                (message_id,),
            ).fetchone()
        return self.run(row["id"]) if row else None

    def new_run(self, message_id, provenance):
        run_id = str(uuid4())
        with self.connect() as db:
            db.execute(
                "INSERT INTO analysis_runs VALUES (?,?,?,?)",
                (
                    run_id,
                    message_id,
                    "queued",
                    encode(
                        {
                            "created_at": now(),
                            "error": None,
                            "extraction": None,
                            "risk": None,
                            **provenance,
                        }
                    ),
                ),
            )
        return run_id

    def update_run(self, run_id, **fields):
        with self.connect() as db:
            row = db.execute(
                "SELECT status,data FROM analysis_runs WHERE id=?", (run_id,)
            ).fetchone()
            data = json.loads(row["data"])
            status = fields.pop("status", row["status"])
            data.update(fields)
            db.execute(
                "UPDATE analysis_runs SET status=?,data=? WHERE id=?",
                (status, encode(data), run_id),
            )

    def interrupt(self):
        with self.connect() as db:
            rows = db.execute(
                "SELECT id,data FROM analysis_runs WHERE status IN ('queued','extracting','assessing')"
            ).fetchall()
            for row in rows:
                data = json.loads(row["data"])
                data["error"] = {
                    "code": "interrupted",
                    "message": "Analysis stopped when the server restarted. Retry to create a new run.",
                    "retryable": True,
                }
                db.execute(
                    "UPDATE analysis_runs SET status='interrupted',data=? WHERE id=?",
                    (encode(data), row["id"]),
                )

    def complete(self, run_id, assessment):
        with self.connect() as db:
            row = db.execute(
                "SELECT message_id,data FROM analysis_runs WHERE id=?", (run_id,)
            ).fetchone()
            mapping = {}
            for entity in assessment["entities"]:
                # Only complete email identifiers merge across runs; names/accounts remain distinct.
                key = (
                    "email:" + entity["label"].strip().lower()
                    if entity["type"] == "email"
                    and re.fullmatch(
                        r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", entity["label"].strip()
                    )
                    else None
                )
                existing = (
                    db.execute(
                        "SELECT id FROM entities WHERE canonical_key=?", (key,)
                    ).fetchone()
                    if key
                    else None
                )
                entity_id = existing["id"] if existing else str(uuid4())
                if not existing:
                    db.execute(
                        "INSERT INTO entities VALUES (?,?,?,?)",
                        (entity_id, entity["type"], entity["label"], key),
                    )
                mapping[entity["id"]] = entity_id
                db.execute(
                    "INSERT OR IGNORE INTO entity_mentions(run_id,entity_id,evidence) VALUES (?,?,?)",
                    (run_id, entity_id, encode(entity["evidence"])),
                )
            for relation in assessment["relationships"]:
                db.execute(
                    "INSERT INTO relationships(id,run_id,source_id,target_id,type,evidence,modality) VALUES (?,?,?,?,?,?,?)",
                    (
                        str(uuid4()),
                        run_id,
                        mapping[relation["source_id"]],
                        mapping[relation["target_id"]],
                        relation["type"],
                        encode(relation["evidence"]),
                        relation.get("modality", "unspecified"),
                    ),
                )
            data = json.loads(row["data"])
            data.update(risk=assessment["risk"], finished_at=now())
            db.execute(
                "UPDATE analysis_runs SET status='completed',data=? WHERE id=?",
                (encode(data), run_id),
            )
            db.execute(
                "UPDATE messages SET selected_run=? WHERE id=?",
                (run_id, row["message_id"]),
            )

    def contribution(self, run_id):
        if not run_id:
            return {"entities": [], "relationships": []}
        with self.connect() as db:
            entities = [
                {**dict(row), "evidence": json.loads(row["evidence"])}
                for row in db.execute(
                    "SELECT e.id,e.type,e.label,m.evidence FROM entities e JOIN entity_mentions m ON m.entity_id=e.id WHERE m.run_id=?",
                    (run_id,),
                )
            ]
            relationships = [
                {**dict(row), "evidence": json.loads(row["evidence"])}
                for row in db.execute(
                    "SELECT id,source_id,target_id,type,evidence,modality FROM relationships WHERE run_id=?",
                    (run_id,),
                )
            ]
        return {"entities": entities, "relationships": relationships}

    def detail(self, message_id):
        message = self.message(message_id)
        latest = self.latest(message_id)
        selected = (
            self.run(message["selected_run"]) if message["selected_run"] else None
        )
        return {
            **message,
            "status": (latest or {}).get("status", "unprocessed"),
            "latest_run": latest,
            "selected_run": selected,
            "extraction": (selected or latest or {}).get("extraction"),
            "risk": (selected or {}).get("risk"),
            **self.contribution(selected["id"] if selected else None),
        }

    def inbox(self):
        with self.connect() as db:
            ids = [
                row["id"]
                for row in db.execute("SELECT id FROM messages ORDER BY rowid DESC")
            ]
        result = []
        for message_id in ids:
            detail = self.detail(message_id)
            result.append(
                {
                    key: detail[key]
                    for key in ("id", "sender", "recipients", "subject", "date")
                }
                | {
                    "status": (detail["latest_run"] or {}).get("status", "unprocessed"),
                    "risk_level": (detail["risk"] or {}).get("level"),
                }
            )
        return result

    def graph(self):
        with self.connect() as db:
            selected = list(
                db.execute(
                    "SELECT id,selected_run FROM messages WHERE selected_run IS NOT NULL"
                )
            )
        entities, relations = {}, []
        for row in selected:
            contribution = self.contribution(row["selected_run"])
            for item in contribution["entities"]:
                entity = entities.setdefault(
                    item["id"], {**item, "evidence": [], "mentions": []}
                )
                entity["evidence"].extend(item["evidence"])
                entity["mentions"].append(
                    {
                        "message_id": row["id"],
                        "analysis_run_id": row["selected_run"],
                        "evidence": item["evidence"],
                    }
                )
            relations.extend(
                {
                    **item,
                    "message_id": row["id"],
                    "analysis_run_id": row["selected_run"],
                }
                for item in contribution["relationships"]
            )
        return {"entities": list(entities.values()), "relationships": relations}
