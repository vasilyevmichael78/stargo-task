"""Typed analysis contracts and evidence invariants, independent of delivery/storage."""

from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field


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
