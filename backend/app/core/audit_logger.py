"""
Audit logger — records every module execution for operator compliance.
Query values for PII entity types are hashed before storage.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from app.modules.base import EntityType

PII_TYPES = {EntityType.PERSON, EntityType.EMAIL, EntityType.PHONE, EntityType.ADDRESS}

LOG_DIR = Path("/data/audit")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _hash_if_pii(entity_type: EntityType, value: str) -> str:
    if entity_type in PII_TYPES:
        return "sha256:" + hashlib.sha256(value.encode()).hexdigest()
    return value


def log_execution(
    session_id: str,
    case_id: str,
    module_name: str,
    entity_type: EntityType,
    entity_label: str,
    declared_purpose: str,
    result_count: int,
    error: str | None = None,
) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "case_id": case_id,
        "module": module_name,
        "entity_type": entity_type,
        "query": _hash_if_pii(entity_type, entity_label),
        "purpose": declared_purpose,
        "result_count": result_count,
        "error": error,
    }
    log_file = LOG_DIR / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
    with log_file.open("a") as f:
        f.write(json.dumps(entry) + "\n")
