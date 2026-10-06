"""Deterministic advisory risk policy over validated, model-extracted signals."""

from .domain import OutputValidationError, RiskFindings

LEVEL_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}
# These observations alone do not indicate a concern; combinations may still escalate.
NEUTRAL_SIGNALS = {"payment_request", "departure"}


def validate_signal_catalog(findings: RiskFindings, catalog: dict):
    allowed = {signal["id"] for signal in catalog["signals"]}
    seen = set()
    errors = []
    for index, signal in enumerate(findings.signals):
        if signal.id not in allowed or signal.id in seen:
            errors.append(
                {
                    "path": ["risk", "signals", index, "id"],
                    "code": "unknown_signal"
                    if signal.id not in allowed
                    else "duplicate_signal",
                    "message": "Use a distinct signal ID from the supplied policy catalog.",
                }
            )
        seen.add(signal.id)
    if errors:
        raise OutputValidationError(errors[:20])


def decide_risk(findings: RiskFindings, catalog: dict):
    validate_signal_catalog(findings, catalog)
    ids = {signal.id for signal in findings.signals}
    matches = [
        rule for rule in catalog["rules"] if set(rule["required_signals"]) <= ids
    ]
    if matches:
        level = max((rule["suggested_level"] for rule in matches), key=LEVEL_ORDER.get)
        strongest = [rule for rule in matches if rule["suggested_level"] == level]
        rationale = " ".join(rule["explanation"] for rule in strongest)
    elif ids - NEUTRAL_SIGNALS:
        level = "low"
        rationale = "Extracted concerns do not match an escalation rule; analyst review is needed."
    else:
        level = "none"
        rationale = "No escalation rule or concerning signal was identified; this is not proof of safety."
    return {
        "level": level,
        "rationale": rationale,
        "tags": [signal.id for signal in findings.signals],
        "signals": [signal.model_dump() for signal in findings.signals],
        "matched_rule_ids": [rule["id"] for rule in matches],
        "decision_engine_version": "1",
    }
