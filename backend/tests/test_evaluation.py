"""Cancellation must not leave evaluation runs looking active."""

import asyncio
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from mailrisk.storage import SQLiteStore


@pytest.mark.asyncio
async def test_comparison_cancellation_records_interruption(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[2] / "evaluations/compare.py"
    spec = importlib.util.spec_from_file_location("evaluation_compare_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    started = asyncio.Event()

    class WaitingProvider:
        async def generate_structured(self, *args):
            started.set()
            await asyncio.Future()

    monkeypatch.setattr(module, "create_provider", lambda settings: WaitingProvider())
    database = tmp_path / "evaluation.sqlite3"
    output = tmp_path / "report.json"
    task = asyncio.create_task(
        module.evaluate(
            SimpleNamespace(
                provider="ollama",
                model="test-model",
                database=database,
                output=output,
                pause=0,
            )
        )
    )
    await asyncio.wait_for(started.wait(), 5)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    report = json.loads(output.read_text())
    assert report["execution_status"] == "cancelled"
    assert report["finished_at"]
    assert report["cases"] == []
    run = SQLiteStore(database).latest("E001")
    assert run["status"] == "interrupted"
    assert run["risk"] is None
