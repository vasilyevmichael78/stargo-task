"""Load bounded local risk guidance; examples are not evidence or benchmark labels."""

import hashlib
import json

from .domain import AppError, RiskContext


def parse_risk_context(raw):
    try:
        catalog = RiskContext.model_validate_json(raw)
        content = catalog.model_dump()
        canonical = json.dumps(
            content, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        if len(canonical) > 16_000:
            raise ValueError("Catalog exceeds the 16 KB limit.")
    except ValueError:
        raise AppError(
            "configuration",
            "Provide a valid risk catalog of at most 16 KB with unique IDs, all four levels, and valid rule references.",
        ) from None
    return content, hashlib.sha256(canonical).hexdigest()


def load_risk_context(path):
    try:
        with path.open("rb") as stream:
            raw = stream.read(16_001)
        if len(raw) > 16_000:
            raise ValueError()
    except (OSError, ValueError):
        raise AppError(
            "configuration",
            "Configure a readable risk catalog of at most 16 KB at RISK_CONTEXT_PATH.",
        ) from None
    return parse_risk_context(raw)
