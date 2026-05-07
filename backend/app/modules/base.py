from abc import ABC, abstractmethod
from enum import Enum
from typing import Any
from pydantic import BaseModel


class UseCase(str, Enum):
    RESEARCH = "research"
    FRAUD_PREVENTION = "fraud_prevention"
    DUE_DILIGENCE = "due_diligence"
    JOURNALISM = "journalism"
    SECURITY = "security"
    # Prohibited uses — modules declare these to trigger UI warnings
    FCRA_DECISION = "fcra_decision"
    EMPLOYMENT = "employment"
    HOUSING = "housing"
    CREDIT = "credit"


class TosRisk(str, Enum):
    NONE = "none"      # Official API or public domain
    LOW = "low"        # Existence check only, no content extraction
    MEDIUM = "medium"  # Gray area — public data, no official API
    HIGH = "high"      # Likely T&S violation — community use only, user accepts risk


class EntityType(str, Enum):
    PERSON = "person"
    COMPANY = "company"
    DOMAIN = "domain"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    IP = "ip"
    USERNAME = "username"
    DOCUMENT = "document"
    VESSEL = "vessel"
    AIRCRAFT = "aircraft"


class Entity(BaseModel):
    id: str
    type: EntityType
    label: str
    properties: dict[str, Any] = {}
    source_module: str
    source_url: str | None = None


class Relationship(BaseModel):
    source_id: str
    target_id: str
    type: str
    properties: dict[str, Any] = {}
    source_module: str


class ModuleResult(BaseModel):
    entities: list[Entity] = []
    relationships: list[Relationship] = []
    raw: dict[str, Any] = {}
    error: str | None = None


class ModuleMetadata(BaseModel):
    name: str
    display_name: str
    description: str
    version: str
    author: str
    data_source: str
    data_source_url: str
    legal_uses: list[UseCase]
    prohibited_uses: list[UseCase]
    tos_risk: TosRisk
    requires_api_key: bool
    api_key_env_var: str | None = None
    pii_returned: bool
    input_types: list[EntityType]
    output_types: list[EntityType]


class BaseModule(ABC):
    metadata: ModuleMetadata

    @abstractmethod
    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        """Run the module against an input entity and return graph data."""
        ...

    def is_permitted_for(self, declared_purpose: UseCase) -> bool:
        return declared_purpose not in self.metadata.prohibited_uses

    def accepts(self, entity_type: EntityType) -> bool:
        return entity_type in self.metadata.input_types
