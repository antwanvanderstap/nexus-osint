"""
OpenCorporates business entity lookup.
Official API — free tier supports ~500 requests/month.
https://api.opencorporates.com
"""
import hashlib
import httpx

from .base import (
    BaseModule, Entity, EntityType, ModuleMetadata, ModuleResult,
    Relationship, TosRisk, UseCase,
)

API_BASE = "https://api.opencorporates.com/v0.4"


class OpenCorporatesModule(BaseModule):
    metadata = ModuleMetadata(
        name="opencorporates",
        display_name="OpenCorporates Business Lookup",
        description="Search global company registries via the OpenCorporates API.",
        version="1.0.0",
        author="nexus-osint",
        data_source="OpenCorporates",
        data_source_url="https://opencorporates.com",
        legal_uses=[UseCase.RESEARCH, UseCase.DUE_DILIGENCE, UseCase.FRAUD_PREVENTION],
        prohibited_uses=[],
        tos_risk=TosRisk.NONE,
        requires_api_key=False,
        api_key_env_var="OPENCORPORATES_API_KEY",
        pii_returned=False,
        input_types=[EntityType.COMPANY, EntityType.PERSON],
        output_types=[EntityType.COMPANY, EntityType.ADDRESS],
    )

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        params: dict = {"q": entity.label, "format": "json"}
        if api_key:
            params["api_token"] = api_key

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(f"{API_BASE}/companies/search", params=params)
                response.raise_for_status()
                data = response.json()

            companies = data.get("results", {}).get("companies", [])
            entities: list[Entity] = []
            relationships: list[Relationship] = []

            for item in companies[:10]:
                co = item.get("company", {})
                uid = f"oc_{hashlib.md5(co.get('company_number', co['name']).encode()).hexdigest()[:8]}"

                company_entity = Entity(
                    id=uid,
                    type=EntityType.COMPANY,
                    label=co.get("name", "Unknown"),
                    properties={
                        "jurisdiction": co.get("jurisdiction_code"),
                        "company_number": co.get("company_number"),
                        "status": co.get("current_status"),
                        "incorporated": co.get("incorporation_date"),
                        "company_type": co.get("company_type"),
                    },
                    source_module=self.metadata.name,
                    source_url=co.get("opencorporates_url"),
                )
                entities.append(company_entity)
                relationships.append(Relationship(
                    source_id=entity.id,
                    target_id=uid,
                    type="ASSOCIATED_COMPANY",
                    properties={},
                    source_module=self.metadata.name,
                ))

                if co.get("registered_address"):
                    addr = co["registered_address"]
                    addr_id = f"addr_{hashlib.md5(str(addr).encode()).hexdigest()[:8]}"
                    entities.append(Entity(
                        id=addr_id,
                        type=EntityType.ADDRESS,
                        label=addr.get("street_address", ""),
                        properties=addr,
                        source_module=self.metadata.name,
                    ))
                    relationships.append(Relationship(
                        source_id=uid,
                        target_id=addr_id,
                        type="REGISTERED_AT",
                        properties={},
                        source_module=self.metadata.name,
                    ))

            return ModuleResult(entities=entities, relationships=relationships)

        except Exception as e:
            return ModuleResult(error=str(e))
