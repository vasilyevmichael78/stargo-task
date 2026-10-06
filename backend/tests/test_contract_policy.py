import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from mailrisk.application import AnalysisService
from mailrisk.decision import decide_risk
from mailrisk.domain import (
    Assessment,
    OutputValidationError,
    RiskFindings,
    validate_evidence,
)
from mailrisk.ingestion import normalize
from mailrisk.risk_context import load_risk_context
from mailrisk.settings import Settings
from mailrisk.storage import SQLiteStore

CATALOG = load_risk_context(Path(__file__).parents[1] / "policies/risk_context.json")[0]


def findings(*ids):
    return RiskFindings.model_validate(
        {
            "signals": [
                {
                    "id": id,
                    "evidence": [{"source_id": "body", "quote": "Send now privately"}],
                }
                for id in ids
            ]
        }
    )


def test_concealed_urgent_payment_escalates_without_invented_identity():
    risk = decide_risk(findings("payment_request", "urgency", "secrecy"), CATALOG)
    assert risk["level"] == "high"
    assert risk["matched_rule_ids"] == ["payment_concealment"]
    assert "identity_mismatch" not in risk["tags"]
    assert risk["signals"][0]["evidence"][0]["source_id"] == "body"


def test_missing_payment_does_not_downgrade_unrelated_high_risk():
    rule = next(
        rule for rule in CATALOG["rules"] if rule["id"] == "departure_exfiltration"
    )
    risk = decide_risk(findings(*rule["required_signals"]), CATALOG)
    assert risk["level"] == "high"
    assert "payment_request" not in risk["tags"]


@pytest.mark.parametrize("ids", [("invented_signal",), ("urgency", "urgency")])
def test_unknown_and_duplicate_signals_cannot_drive_policy(ids):
    with pytest.raises(OutputValidationError):
        decide_risk(findings(*ids), CATALOG)


def test_signal_requires_evidence_and_model_cannot_assign_severity():
    with pytest.raises(ValidationError):
        RiskFindings.model_validate({"signals": [{"id": "urgency", "evidence": []}]})
    with pytest.raises(ValidationError):
        RiskFindings.model_validate({"signals": [], "level": "high"})
    assert decide_risk(findings("payment_request"), CATALOG)["level"] == "none"
    assert decide_risk(findings("urgency"), CATALOG)["level"] == "low"


def assessment(entities=None, relationships=None, signals=None):
    return Assessment.model_validate(
        {
            "risk": {"signals": signals or []},
            "entities": entities or [],
            "relationships": relationships or [],
        }
    )


@pytest.mark.parametrize(
    "kind,label,quote,code",
    [
        ("amount", "$0", "No payment amount was specified", "unsupported_amount"),
        ("amount", "$200", "Send $100", "unsupported_amount"),
        ("email", "From: a@example.com", "From: a@example.com", "unsupported_email"),
    ],
)
def test_unsupported_graph_values_are_repairable(kind, label, quote, code):
    result = assessment(
        entities=[
            {
                "id": "e",
                "type": kind,
                "label": label,
                "evidence": [{"source_id": "body", "quote": quote}],
            }
        ]
    )
    with pytest.raises(OutputValidationError) as error:
        validate_evidence(result, [{"id": "body", "text": quote}])
    assert error.value.validation_errors[0]["code"] == code


def test_risk_signal_cannot_cite_catalog_examples_as_source():
    result = assessment(signals=findings("urgency").model_dump()["signals"])
    with pytest.raises(OutputValidationError) as error:
        validate_evidence(result, [{"id": "body", "text": "An ordinary greeting"}])
    assert error.value.validation_errors[0]["path"][:2] == ["risk", "signals"]


def test_relationship_preserves_request_status_and_endpoint_roles():
    evidence = [{"source_id": "body", "quote": "Please send to account 1234"}]
    entities = [
        {"id": "sender", "type": "person", "label": "Sender", "evidence": evidence},
        {"id": "account", "type": "account", "label": "1234", "evidence": evidence},
    ]
    relation = {
        "source_id": "account",
        "target_id": "sender",
        "type": "requests_transfer_to",
        "modality": "asserted",
        "evidence": evidence,
    }
    with pytest.raises(OutputValidationError) as error:
        validate_evidence(
            assessment(entities, [relation]),
            [{"id": "body", "text": evidence[0]["quote"]}],
        )
    assert {item["code"] for item in error.value.validation_errors} == {
        "invalid_relation_roles",
        "invalid_modality",
    }
    relation.update(source_id="sender", target_id="account", modality="requested")
    validate_evidence(
        assessment(entities, [relation]), [{"id": "body", "text": evidence[0]["quote"]}]
    )


def test_legacy_fixture_migration_preserves_results_and_marks_unspecified(tmp_path):
    import shutil
    import sqlite3

    fixture = Path(__file__).parents[1] / "fixtures/mail_risk_groq.sqlite3"
    target = tmp_path / "legacy.sqlite3"
    shutil.copyfile(fixture, target)
    with sqlite3.connect(target) as db:
        before = db.execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0]
    store = SQLiteStore(target)
    assert store.active_risk_context()["version"] == "2"
    with sqlite3.connect(target) as db:
        assert db.execute("SELECT COUNT(*) FROM analysis_runs").fetchone()[0] == before
        assert db.execute("SELECT DISTINCT modality FROM relationships").fetchall() == [
            ("unspecified",)
        ]
    store.save_risk_context(CATALOG, store.active_risk_context()["revision_id"])
    assert store.active_risk_context()["version"] == "3"
    with sqlite3.connect(target) as db:
        prior = json.loads(
            db.execute("SELECT data FROM analysis_runs LIMIT 1").fetchone()[0]
        )
    assert prior["policy_version"] == "2"


@pytest.mark.asyncio
async def test_signal_repair_and_decision_share_immutable_submission_policy(tmp_path):
    import copy

    settings = Settings(
        database_path=str(tmp_path / "runs.sqlite3"),
        bootstrap_database_path="",
        llm_max_retries=1,
    )
    store = SQLiteStore(settings.path(settings.database_path))
    mid, _ = store.ingest(normalize("Send now privately"))

    class Provider:
        calls = 0

        async def generate_structured(
            self, instructions, input, output_schema, timeout
        ):
            if "extraction" not in input:
                return json.dumps(
                    {
                        "sender": None,
                        "recipients": [],
                        "date": None,
                        "subject": None,
                        "summary": "A concealed urgent payment request",
                        "facts": [],
                    }
                ), {}
            self.calls += 1

            def output(*ids):
                risk = findings(*ids).model_dump()
                for signal in risk["signals"]:
                    signal["evidence"][0]["source_id"] = input["sources"][0]["id"]
                return json.dumps(
                    {"risk": risk, "entities": [], "relationships": []}
                ), {}

            if self.calls == 1:
                changed = copy.deepcopy(CATALOG)
                changed["version"] = "edited-during-run"
                for rule in changed["rules"]:
                    rule["suggested_level"] = "low"
                store.save_risk_context(
                    changed, store.active_risk_context()["revision_id"]
                )
                return output("invented_signal")
            assert input["risk_policy_context"]["version"] == "3"
            assert input["repair_context"]["errors"][0]["code"] == "unknown_signal"
            return output("payment_request", "urgency", "secrecy")

    service = AnalysisService(store, Provider(), settings)
    run_id = service.submit(mid)
    await service.process(run_id)
    run = store.run(run_id)
    assert run["status"] == "completed"
    assert run["risk"]["level"] == "high"
    assert run["policy_version"] == "3"
    assert store.active_risk_context()["version"] == "edited-during-run"
