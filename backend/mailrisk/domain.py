"""Typed analysis contracts and evidence invariants, independent of delivery/storage."""

from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(StrictModel):
    source_id: str
    quote: str = Field(min_length=1)


class Fact(StrictModel):
    kind: str
    value: str
    evidence: list[Evidence] = Field(min_length=1)


class Extraction(StrictModel):
    sender: str | None
    recipients: list[str]
    date: str | None
    subject: str | None
    summary: str = Field(min_length=1)
    facts: list[Fact]


class Risk(StrictModel):
    level: Literal["none", "low", "medium", "high"]
    rationale: str = Field(min_length=1)
    tags: list[str]


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
        "person", "organization", "amount", "account", "location", "email", "other"
    ]
    label: str = Field(min_length=1)
    evidence: list[Evidence] = Field(min_length=1)


class Relationship(StrictModel):
    source_id: str
    target_id: str
    type: str
    evidence: list[Evidence] = Field(min_length=1)


class Assessment(StrictModel):
    risk: Risk
    entities: list[Entity]
    relationships: list[Relationship]


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


def validate_evidence(result: Extraction | Assessment, sources: list[dict]):
    texts = {source["id"]: source["text"] for source in sources}
    errors = []
    groups = (
        [("facts", result.facts)]
        if isinstance(result, Extraction)
        else [("entities", result.entities), ("relationships", result.relationships)]
    )
    for group, items in groups:
        for index, item in enumerate(items):
            for offset, evidence in enumerate(item.evidence):
                path = [group, index, "evidence", offset]
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
        for index, relation in enumerate(result.relationships):
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
