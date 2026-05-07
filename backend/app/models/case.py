from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, Field
from uuid import uuid4

from app.modules.base import UseCase


class CaseCreate(BaseModel):
    name: str
    description: str = ""
    declared_purpose: UseCase


class Case(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    declared_purpose: UseCase
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []


# In-memory store for v1 — replace with PostgreSQL in v2
_cases: dict[str, Case] = {}


def create_case(data: CaseCreate) -> Case:
    case = Case(**data.model_dump())
    _cases[case.id] = case
    return case


def get_case(case_id: str) -> Case | None:
    return _cases.get(case_id)


def list_cases() -> list[Case]:
    return list(_cases.values())


def upsert_graph(case_id: str, entities: list[dict], relationships: list[dict]) -> Case | None:
    case = _cases.get(case_id)
    if not case:
        return None

    existing_ids = {e["id"] for e in case.entities}
    for e in entities:
        if e["id"] not in existing_ids:
            case.entities.append(e)
            existing_ids.add(e["id"])

    existing_rels = {(r["source_id"], r["target_id"], r["type"]) for r in case.relationships}
    for r in relationships:
        key = (r["source_id"], r["target_id"], r["type"])
        if key not in existing_rels:
            case.relationships.append(r)
            existing_rels.add(key)

    case.updated_at = datetime.now(timezone.utc)
    return case
