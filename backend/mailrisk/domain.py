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


def validate_evidence(result: Extraction | Assessment, sources: list[dict]):
    texts = {source["id"]: source["text"] for source in sources}
    evidence = (
        [item for fact in result.facts for item in fact.evidence]
        if isinstance(result, Extraction)
        else [item for relation in result.relationships for item in relation.evidence]
        + [item for entity in result.entities for item in entity.evidence]
    )
    if any(
        item.source_id not in texts or item.quote not in texts[item.source_id]
        for item in evidence
    ):
        raise AppError(
            "invalid_output", "Model evidence does not match the source text.", True
        )
    if isinstance(result, Assessment):
        ids = [entity.id for entity in result.entities]
        if len(ids) != len(set(ids)) or any(
            r.source_id not in ids or r.target_id not in ids
            for r in result.relationships
        ):
            raise AppError(
                "invalid_output",
                "Model relationships reference invalid entities.",
                True,
            )
