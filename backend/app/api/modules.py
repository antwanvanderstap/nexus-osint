import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.audit_logger import log_execution
from app.core.plugin_bus import plugin_bus
from app.models.case import get_case, upsert_graph
from app.modules.base import Entity, EntityType, ModuleMetadata, UseCase

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get("/", response_model=list[ModuleMetadata])
def list_modules() -> list[ModuleMetadata]:
    return [m.metadata for m in plugin_bus.all()]


@router.get("/for/{entity_type}", response_model=list[ModuleMetadata])
def modules_for_entity(entity_type: EntityType) -> list[ModuleMetadata]:
    return [m.metadata for m in plugin_bus.for_entity_type(entity_type)]


class ExecuteRequest(BaseModel):
    case_id: str
    module_name: str
    entity_type: EntityType
    entity_label: str
    api_key: str | None = None
    session_id: str = ""


class ExecuteResponse(BaseModel):
    entity_count: int
    relationship_count: int
    error: str | None = None


@router.post("/execute", response_model=ExecuteResponse)
async def execute_module(req: ExecuteRequest) -> ExecuteResponse:
    case = get_case(req.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    module = plugin_bus.get(req.module_name)
    if not module:
        raise HTTPException(status_code=404, detail=f"Module '{req.module_name}' not found")

    if not module.is_permitted_for(case.declared_purpose):
        raise HTTPException(
            status_code=403,
            detail=f"Module '{req.module_name}' is not permitted for purpose '{case.declared_purpose}'",
        )

    if not module.accepts(req.entity_type):
        raise HTTPException(
            status_code=400,
            detail=f"Module '{req.module_name}' does not accept entity type '{req.entity_type}'",
        )

    entity = Entity(
        id=f"input_{uuid.uuid4().hex[:8]}",
        type=req.entity_type,
        label=req.entity_label,
        source_module="user",
    )

    result = await module.execute(entity, api_key=req.api_key)

    log_execution(
        session_id=req.session_id or "unknown",
        case_id=req.case_id,
        module_name=req.module_name,
        entity_type=req.entity_type,
        entity_label=req.entity_label,
        declared_purpose=case.declared_purpose,
        result_count=len(result.entities),
        error=result.error,
    )

    if result.error:
        return ExecuteResponse(entity_count=0, relationship_count=0, error=result.error)

    all_entities = [entity] + result.entities
    upsert_graph(
        req.case_id,
        [e.model_dump() for e in all_entities],
        [r.model_dump() for r in result.relationships],
    )

    return ExecuteResponse(
        entity_count=len(result.entities),
        relationship_count=len(result.relationships),
    )
