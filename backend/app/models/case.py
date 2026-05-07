import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, select


class CaseCreate(BaseModel):
    name: str
    description: str = ""
    declared_purpose: str


class CaseDB(SQLModel, table=True):
    __tablename__ = "case"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str
    description: str = ""
    declared_purpose: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    entities_json: str = Field(default="[]")
    relationships_json: str = Field(default="[]")


class Case(BaseModel):
    id: str
    name: str
    description: str
    declared_purpose: str
    created_at: datetime
    updated_at: datetime
    entities: list[dict[str, Any]]
    relationships: list[dict[str, Any]]

    @classmethod
    def from_db(cls, db: CaseDB) -> "Case":
        return cls(
            id=db.id,
            name=db.name,
            description=db.description,
            declared_purpose=db.declared_purpose,
            created_at=db.created_at,
            updated_at=db.updated_at,
            entities=json.loads(db.entities_json),
            relationships=json.loads(db.relationships_json),
        )


def create_case(data: CaseCreate, session: Session) -> Case:
    db = CaseDB(**data.model_dump())
    session.add(db)
    session.commit()
    session.refresh(db)
    return Case.from_db(db)


def get_case(case_id: str, session: Session) -> Case | None:
    db = session.get(CaseDB, case_id)
    return Case.from_db(db) if db else None


def list_cases(session: Session) -> list[Case]:
    return [Case.from_db(db) for db in session.exec(select(CaseDB).order_by(CaseDB.updated_at.desc())).all()]


def upsert_graph(case_id: str, entities: list[dict], relationships: list[dict], session: Session) -> Case | None:
    db = session.get(CaseDB, case_id)
    if not db:
        return None

    existing_entities: list[dict] = json.loads(db.entities_json)
    existing_ids = {e["id"] for e in existing_entities}
    for e in entities:
        if e["id"] not in existing_ids:
            existing_entities.append(e)
            existing_ids.add(e["id"])

    existing_rels: list[dict] = json.loads(db.relationships_json)
    existing_rel_keys = {(r["source_id"], r["target_id"], r["type"]) for r in existing_rels}
    for r in relationships:
        key = (r["source_id"], r["target_id"], r["type"])
        if key not in existing_rel_keys:
            existing_rels.append(r)
            existing_rel_keys.add(key)

    db.entities_json = json.dumps(existing_entities)
    db.relationships_json = json.dumps(existing_rels)
    db.updated_at = datetime.now(timezone.utc)

    session.add(db)
    session.commit()
    session.refresh(db)
    return Case.from_db(db)


def delete_case(case_id: str, session: Session) -> bool:
    db = session.get(CaseDB, case_id)
    if not db:
        return False
    session.delete(db)
    session.commit()
    return True
