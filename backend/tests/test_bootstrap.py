"""Precomputed demo results must not trigger startup inference or replace user data."""

import hashlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mailrisk.api import create_app
from mailrisk.bootstrap import bootstrap_database
from mailrisk.ingestion import normalize
from mailrisk.settings import Settings
from mailrisk.storage import SQLiteStore


class NoInferenceProvider:
    calls = 0

    async def generate_structured(self, *args):
        self.calls += 1
        raise AssertionError("Startup must not invoke inference.")


def test_precomputed_startup_and_restart_without_inference(tmp_path):
    settings = Settings(
        database_path=str(tmp_path / "runtime.sqlite3"), llm_provider="ollama"
    )
    fixture = settings.path(settings.bootstrap_database_path)
    digest = hashlib.sha256(fixture.read_bytes()).hexdigest()
    provider = NoInferenceProvider()
    for _ in range(2):
        with TestClient(create_app(settings, provider)) as client:
            inbox = client.get("/emails").json()
            assert len(inbox) == 15
            assert sum(item["status"] == "completed" for item in inbox) == 13
            assert all(item["status"] in ("completed", "failed") for item in inbox)
            detail = client.get("/emails/E001").json()
            assert detail["selected_run"]["provider"] == "groq"
            assert detail["selected_run"]["model"] == "openai/gpt-oss-120b"
            assert detail["risk"]["level"] == "high"
            graph = client.get("/graph").json()
            assert graph["entities"] and graph["relationships"]
            assert client.app.state.service.queue.empty()
    assert provider.calls == 0
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == digest
    assert len(SQLiteStore(Path(settings.database_path)).inbox()) == 15


def test_existing_database_is_preserved_and_seed_import_does_not_analyze(tmp_path):
    path = tmp_path / "existing.sqlite3"
    store = SQLiteStore(path)
    mid, _ = store.ingest(normalize("User data must survive"))
    settings = Settings(database_path=str(path), llm_provider="ollama")
    provider = NoInferenceProvider()
    with TestClient(create_app(settings, provider)) as client:
        inbox = client.get("/emails").json()
        assert len(inbox) == 11
        assert client.get("/emails/" + mid).json()["body"] == "User data must survive"
        assert client.get("/emails/E001").json()["latest_run"] is None
        assert client.app.state.service.queue.empty()
    assert provider.calls == 0


def test_bootstrap_rejects_missing_fixture_and_writable_fixture_target(tmp_path):
    missing = tmp_path / "missing.sqlite3"
    with pytest.raises(RuntimeError, match="BOOTSTRAP_DATABASE_PATH"):
        bootstrap_database(tmp_path / "runtime.sqlite3", missing)
    fixture = tmp_path / "fixture.sqlite3"
    fixture.write_bytes(b"untouched")
    with pytest.raises(RuntimeError, match="must differ"):
        bootstrap_database(fixture, fixture)
    assert fixture.read_bytes() == b"untouched"
