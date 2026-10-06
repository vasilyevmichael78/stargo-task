"""Run the real application pipeline sequentially against a shared regression set."""

import argparse
import asyncio
import hashlib
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from mailrisk.application import AnalysisService
from mailrisk.ingestion import normalize
from mailrisk.providers import create_provider
from mailrisk.settings import Settings
from mailrisk.storage import SQLiteStore


async def evaluate(args):
    dataset = json.loads((ROOT / "evaluations/cases.json").read_text())
    cases = dataset["cases"]
    selected = getattr(args, "ids", None)
    if selected:
        requested = set(selected.split(","))
        if requested - {case["id"] for case in cases}:
            raise ValueError("Unknown evaluation case ID.")
        cases = [case for case in cases if case["id"] in requested]
    seeds = {
        email["id"]: email
        for email in json.loads((ROOT / "mock_mailbox_data.json").read_text())["emails"]
    }
    settings = Settings(
        llm_provider=args.provider,
        groq_model=args.model,
        ollama_model=args.model,
        database_path=str(Path(args.database).resolve()),
    )
    store = SQLiteStore(settings.path(settings.database_path))
    service = AnalysisService(store, create_provider(settings), settings)
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "provider": args.provider,
        "model": args.model,
        "external_case_pacing_seconds": args.pause,
        "dataset_version": dataset["version"],
        "cases_hash": hashlib.sha256(
            json.dumps(cases, sort_keys=True).encode()
        ).hexdigest(),
        "cases": [],
        "execution_status": "running",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Submit and await one case at a time; use the same worker and validators as the API.
    await service.start()
    try:
        for case in cases:
            email = case.get("email") or seeds[case["id"]]
            raw = (
                "\n".join(
                    [
                        "From: " + email["from"],
                        "To: " + ", ".join(email["to"]),
                        "Date: " + email["date"],
                        "Subject: " + email["subject"],
                    ]
                )
                + "\n\n"
                + email["body"]
            )
            metadata = {
                "sender": email["from"],
                "recipients": email["to"],
                "date": email["date"],
                "subject": email["subject"],
            }
            store.ingest(normalize(raw, email.get("attachments"), metadata), case["id"])
            started = time.monotonic()
            run_id = service.submit(case["id"])
            await service.queue.join()
            run = store.run(run_id)
            # Full local report is ignored by Git; never print source/output text.
            report["cases"].append(
                {
                    "id": case["id"],
                    "expectations": case,
                    "run": run,
                    "detail": store.detail(case["id"]),
                    "elapsed_seconds": round(time.monotonic() - started, 2),
                    "level_screen": run.get("risk", {}).get("level")
                    in case["acceptable_levels"]
                    if run["status"] == "completed"
                    else None,
                    "semantic_review": "pending",
                }
            )
            output.write_text(json.dumps(report, indent=2) + "\n")
            print(
                f"{args.provider}/{args.model} {case['id']}: {run['status']}",
                flush=True,
            )
            if args.pause and case is not cases[-1]:
                await asyncio.sleep(args.pause)
        report["execution_status"] = "completed"
    except asyncio.CancelledError:
        report["execution_status"] = "cancelled"
        raise
    except Exception:
        report["execution_status"] = "failed"
        raise
    finally:
        await service.stop()
        store.interrupt()
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        output.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=["groq", "ollama"], required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument(
        "--ids", help="Optional comma-separated case IDs for a focused regression run."
    )
    parser.add_argument(
        "--database",
        required=True,
        help="Use an isolated database or stop its API first.",
    )
    parser.add_argument(
        "--output", required=True, help="Ignored local report, contains source data."
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=0,
        help="External pacing between cases; not an app retry.",
    )
    args = parser.parse_args()
    if args.pause < 0:
        parser.error("--pause must be nonnegative")
    logging.basicConfig(level=logging.WARNING)
    asyncio.run(evaluate(args))
