"""Collect real API analysis outputs; never replace inference with fixture answers."""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request(base, path, method="GET"):
    req = Request(base.rstrip("/") + path, method=method)
    try:
        with urlopen(req, timeout=15) as response:
            return json.load(response)
    except HTTPError as exc:
        raise RuntimeError(
            f"API returned HTTP {exc.code}; inspect safe API errors."
        ) from None
    except URLError:
        raise RuntimeError(
            "API unavailable; start the backend before evaluation."
        ) from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument(
        "--output", required=True, help="Local report path; contains source data."
    )
    parser.add_argument(
        "--timeout", type=int, default=300, help="Per-case deadline in seconds."
    )
    parser.add_argument("--ids", nargs="*", help="Seed IDs; default all ten cases.")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    cases = json.loads(Path(__file__).with_name("cases.json").read_text())["cases"]
    selected = set(args.ids) if args.ids else {case["id"] for case in cases}
    if selected - {case["id"] for case in cases}:
        parser.error("Unknown seed ID")
    report = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "health": request(args.base_url, "/health"),
        "cases": [],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    for case in cases:
        if case["id"] not in selected:
            continue
        started = time.monotonic()
        submission = request(args.base_url, f"/emails/{case['id']}/analyses", "POST")
        run_id = submission["analysis_run_id"]
        while True:
            run = request(args.base_url, f"/analyses/{run_id}")
            if run["status"] in {"completed", "failed", "interrupted"}:
                break
            if time.monotonic() - started > args.timeout:
                run = {
                    "id": run_id,
                    "status": "evaluation_deadline",
                    "note": "Server run may still be active.",
                }
                break
            time.sleep(2)
        detail = request(args.base_url, f"/emails/{case['id']}")
        risk = run.get("risk") or {}
        report["cases"].append(
            {
                "id": case["id"],
                "elapsed_seconds": round(time.monotonic() - started, 2),
                "expectations": case,
                "run": run,
                "detail": detail,
                "level_screen": risk.get("level") in case["acceptable_levels"]
                if run["status"] == "completed"
                else None,
                "semantic_review": "pending",
            }
        )
        output.write_text(json.dumps(report, indent=2) + "\n")
        print(f"{case['id']}: {run['status']}; semantic review pending")
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    output.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
