"""
CourtListener federal court docket search.
Free REST API — no key required.
https://www.courtlistener.com/api/rest/v4/
"""
import hashlib
import httpx

from .base import (
    BaseModule, Entity, EntityType, ModuleMetadata, ModuleResult,
    Relationship, TosRisk, UseCase,
)

API_BASE = "https://www.courtlistener.com/api/rest/v4"


class CourtListenerModule(BaseModule):
    metadata = ModuleMetadata(
        name="courtlistener",
        display_name="CourtListener Federal Cases",
        description="Search federal court dockets and opinions by name or company.",
        version="1.0.0",
        author="nexus-osint",
        data_source="CourtListener / RECAP",
        data_source_url="https://www.courtlistener.com",
        legal_uses=[UseCase.RESEARCH, UseCase.DUE_DILIGENCE, UseCase.FRAUD_PREVENTION],
        prohibited_uses=[],
        tos_risk=TosRisk.NONE,
        requires_api_key=False,
        pii_returned=True,
        input_types=[EntityType.PERSON, EntityType.COMPANY],
        output_types=[EntityType.DOCUMENT],
    )

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(
                    f"{API_BASE}/search/",
                    params={"q": f'"{entity.label}"', "type": "r", "page_size": 10},
                    headers={"User-Agent": "nexus-osint/1.0"},
                )
                r.raise_for_status()
                data = r.json()

            for result in data.get("results", []):
                uid = f"case_{hashlib.md5(str(result.get('id', '')).encode()).hexdigest()[:8]}"
                doc = Entity(
                    id=uid,
                    type=EntityType.DOCUMENT,
                    label=result.get("caseName") or result.get("case_name") or "Unknown Case",
                    properties={
                        "court": result.get("court_id") or result.get("court"),
                        "date_filed": result.get("dateFiled") or result.get("date_filed"),
                        "docket_number": result.get("docketNumber") or result.get("docket_number"),
                        "nature_of_suit": result.get("nature_of_suit"),
                        "status": result.get("status"),
                    },
                    source_module=self.metadata.name,
                    source_url=f"https://www.courtlistener.com{result.get('absolute_url', '')}",
                )
                entities.append(doc)
                relationships.append(Relationship(
                    source_id=entity.id,
                    target_id=uid,
                    type="NAMED_IN_CASE",
                    properties={},
                    source_module=self.metadata.name,
                ))

        except Exception as e:
            return ModuleResult(error=str(e))

        return ModuleResult(entities=entities, relationships=relationships)
