"""Typed analysis contracts and evidence invariants, independent of delivery/storage."""

import re
from decimal import Decimal, InvalidOperation
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(StrictModel):
    source_id: str
    quote: str = Field(min_length=1)


class Fact(StrictModel):
    kind: Literal[
        "amount",
        "date",
        "duration",
        "account",
        "reference",
        "url",
        "document",
        "identity",
        "request",
        "allegation",
        "event",
        "other",
    ]
    value: str = Field(min_length=1, max_length=500)
    evidence: list[Evidence] = Field(min_length=1)


class Extraction(StrictModel):
    sender: str | None
    recipients: list[str]
    date: str | None
    subject: str | None
    summary: str = Field(min_length=1)
    facts: list[Fact] = Field(max_length=40)


class ObservedSignal(StrictModel):
    id: str = Field(min_length=1, max_length=64)
    evidence: list[Evidence] = Field(min_length=1, max_length=4)


class RiskFindings(StrictModel):
    # The model identifies evidence-bearing signals; application policy assigns severity.
    signals: list[ObservedSignal] = Field(max_length=32)


class RiskSignal(StrictModel):
    id: str = Field(min_length=1, max_length=64)
    description: str = Field(min_length=1, max_length=500)
    examples: list[str] = Field(default_factory=list, max_length=3)
    counterexamples: list[str] = Field(default_factory=list, max_length=3)


class RiskGuidanceRule(StrictModel):
    id: str = Field(min_length=1, max_length=64)
    required_signals: list[str] = Field(min_length=1, max_length=6)
    suggested_level: Literal["none", "low", "medium", "high"]
    explanation: str = Field(min_length=1, max_length=500)


class RiskContext(StrictModel):
    version: str = Field(min_length=1, max_length=32)
    description: str = Field(min_length=1, max_length=500)
    levels: dict[Literal["none", "low", "medium", "high"], str]
    signals: list[RiskSignal] = Field(min_length=1, max_length=32)
    rules: list[RiskGuidanceRule] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def validate_catalog(self):
        if set(self.levels) != {"none", "low", "medium", "high"} or any(
            not value.strip() for value in self.levels.values()
        ):
            raise ValueError("All four risk levels require definitions.")
        signal_ids = [signal.id for signal in self.signals]
        rule_ids = [rule.id for rule in self.rules]
        if len(set(signal_ids)) != len(signal_ids) or len(set(rule_ids)) != len(
            rule_ids
        ):
            raise ValueError("Signal and rule IDs must be unique within each group.")
        for rule in self.rules:
            if len(set(rule.required_signals)) != len(rule.required_signals) or not set(
                rule.required_signals
            ).issubset(signal_ids):
                raise ValueError("Rules require distinct existing signal IDs.")
        return self


class Entity(StrictModel):
    id: str = Field(min_length=1)
    type: Literal[
        "person",
        "organization",
        "amount",
        "account",
        "location",
        "email",
        "date",
        "duration",
        "document",
        "url",
        "phone",
        "other",
    ]
    label: str = Field(min_length=1, max_length=200)
    evidence: list[Evidence] = Field(min_length=1)


class Relationship(StrictModel):
    source_id: str
    target_id: str
    type: Literal[
        "mentions",
        "claims_identity",
        "employed_by",
        "requests_transfer_to",
        "replaces_account",
        "requests_forwarding_to",
        "associated_with",
        "requests_action_from",
        "alleges_against",
        "located_at",
    ]
    modality: Literal["asserted", "claimed", "alleged", "requested"]
    evidence: list[Evidence] = Field(min_length=1)


class Assessment(StrictModel):
    risk: RiskFindings
    entities: list[Entity] = Field(max_length=40)
    relationships: list[Relationship] = Field(max_length=60)


class AppError(Exception):
    def __init__(
        self, code: str, message: str, retryable: bool = False, status: int = 422
    ):
        self.code, self.message, self.retryable, self.status = (
            code,
            message,
            retryable,
            status,
        )
        super().__init__(message)

    def payload(self):
        return {"code": self.code, "message": self.message, "retryable": self.retryable}


class LLMProvider(Protocol):
    async def generate_structured(
        self, instructions: str, input: dict, output_schema: dict, timeout: float
    ) -> tuple[str, dict]: ...


class Store(Protocol):
    def active_risk_context(self) -> dict | None: ...
    def ensure_risk_context(self, path) -> dict: ...
    def message(self, message_id: str) -> dict: ...
    def run(self, run_id: str) -> dict: ...
    def new_run(self, message_id: str, provenance: dict) -> str: ...
    def update_run(self, run_id: str, **fields) -> None: ...
    def complete(self, run_id: str, assessment: dict) -> None: ...


class OutputValidationError(AppError):
    def __init__(self, errors: list[dict]):
        super().__init__(
            "invalid_output", "Model evidence or references are invalid.", True
        )
        self.validation_errors = errors


def evidence_items(result: Extraction | Assessment):
    groups = (
        [("facts", result.facts)]
        if isinstance(result, Extraction)
        else [("entities", result.entities), ("relationships", result.relationships)]
    )
    if isinstance(result, Assessment):
        groups.append(("risk.signals", result.risk.signals))
    for group, items in groups:
        for index, item in enumerate(items):
            for offset, evidence in enumerate(item.evidence):
                yield group.split(".") + [index, "evidence", offset], evidence


def align_evidence_whitespace(result: Extraction | Assessment, sources: list[dict]):
    """Recover an exact source span only from an unambiguous whitespace variant."""
    texts = {source["id"]: source["text"] for source in sources}
    alignments = []
    for path, evidence in evidence_items(result):
        text = texts.get(evidence.source_id)
        if text is None or evidence.quote in text:
            continue
        words = evidence.quote.split()
        if not words:
            continue
        pattern = r"\s+".join(re.escape(word) for word in words)
        # Lookahead includes overlapping matches; even those must be unambiguous.
        matches = re.finditer(f"(?=({pattern}))", text)
        first = next(matches, None)
        if first is None or next(matches, None) is not None:
            continue
        evidence.quote = text[first.start(1) : first.end(1)]
        alignments.append(
            {"path": path + ["quote"], "method": "unique_whitespace_span"}
        )
    return alignments


RELATION_ROLES = {
    "claims_identity": ({"person"}, {"email"}),
    "employed_by": ({"person"}, {"organization"}),
    "requests_transfer_to": (
        {"person", "organization", "email"},
        {"organization", "person", "account"},
    ),
    "replaces_account": ({"account"}, {"account"}),
    "requests_forwarding_to": (
        {"person", "organization", "email"},
        {"person", "organization", "email"},
    ),
    "requests_action_from": (
        {"person", "organization", "email"},
        {"person", "organization", "email"},
    ),
    "alleges_against": (
        {"person", "organization", "email"},
        {"person", "organization"},
    ),
    "located_at": ({"person", "organization"}, {"location"}),
}


def numeric_values(text: str):
    values = set()
    pattern = r"(?<![\w])(-?\d+(?:[.,]\d+)*)(?:\s*(million|thousand|[kKmM]))?(?![\w])"
    for match in re.finditer(pattern, text):
        try:
            value = Decimal(match[1].replace(",", ""))
            unit = (match[2] or "").lower()
            factor = {
                "m": 1_000_000,
                "million": 1_000_000,
                "k": 1000,
                "thousand": 1000,
            }.get(unit, 1)
            values.add(value * factor)
        except InvalidOperation:
            continue
    return values


def validate_evidence(result: Extraction | Assessment, sources: list[dict]):
    texts = {source["id"]: source["text"] for source in sources}
    errors = []
    for path, evidence in evidence_items(result):
        if evidence.source_id not in texts:
            errors.append(
                {
                    "path": path + ["source_id"],
                    "code": "unknown_source",
                    "message": "Use an existing source ID.",
                }
            )
        elif evidence.quote not in texts[evidence.source_id]:
            errors.append(
                {
                    "path": path + ["quote"],
                    "code": "quote_mismatch",
                    "message": "Copy an exact substring from the referenced source.",
                }
            )
    if isinstance(result, Assessment):
        ids = [entity.id for entity in result.entities]
        for index, entity_id in enumerate(ids):
            if entity_id in ids[:index]:
                errors.append(
                    {
                        "path": ["entities", index, "id"],
                        "code": "duplicate_entity",
                        "message": "Entity IDs must be unique.",
                    }
                )
        by_id = {entity.id: entity for entity in result.entities}
        for index, entity in enumerate(result.entities):
            if entity.type == "amount":
                values = numeric_values(entity.label)
                supported = numeric_values(
                    " ".join(item.quote for item in entity.evidence)
                )
                if not values or not values <= supported:
                    errors.append(
                        {
                            "path": ["entities", index, "label"],
                            "code": "unsupported_amount",
                            "message": "Copy a source-supported monetary value; do not represent absence as zero.",
                        }
                    )
            if entity.type == "email" and (
                not re.fullmatch(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", entity.label)
                or not any(
                    entity.label.casefold() in item.quote.casefold()
                    for item in entity.evidence
                )
            ):
                errors.append(
                    {
                        "path": ["entities", index, "label"],
                        "code": "unsupported_email",
                        "message": "Use a complete source-cited email address as the label, without decorations.",
                    }
                )
        for index, relation in enumerate(result.relationships):
            endpoints = [by_id.get(relation.source_id), by_id.get(relation.target_id)]
            roles = RELATION_ROLES.get(relation.type)
            if (
                roles
                and all(endpoints)
                and any(
                    entity.type not in allowed
                    for entity, allowed in zip(endpoints, roles, strict=True)
                )
            ):
                errors.append(
                    {
                        "path": ["relationships", index, "type"],
                        "code": "invalid_relation_roles",
                        "message": "Use endpoint types compatible with the relationship, or omit it.",
                    }
                )
            required_modality = (
                "requested"
                if relation.type.startswith("requests_")
                else {"claims_identity": "claimed", "alleges_against": "alleged"}.get(
                    relation.type
                )
            )
            if required_modality and relation.modality != required_modality:
                errors.append(
                    {
                        "path": ["relationships", index, "modality"],
                        "code": "invalid_modality",
                        "message": "Preserve the request/claim/allegation status of this relationship.",
                    }
                )
            for field in ("source_id", "target_id"):
                if getattr(relation, field) not in ids:
                    errors.append(
                        {
                            "path": ["relationships", index, field],
                            "code": "unknown_entity",
                            "message": "Reference an entity ID from this output or omit the unsupported relationship.",
                        }
                    )
    if errors:
        raise OutputValidationError(errors[:20])
