"""
FEC political contribution search.
Free API — DEMO_KEY works for testing; register at api.data.gov for production.
https://api.open.fec.gov/developers
"""
import hashlib
import httpx

from .base import (
    BaseModule, Entity, EntityType, ModuleMetadata, ModuleResult,
    Relationship, TosRisk, UseCase,
)

API_BASE = "https://api.open.fec.gov/v1"
DEFAULT_KEY = "DEMO_KEY"


class FecModule(BaseModule):
    metadata = ModuleMetadata(
        name="fec",
        display_name="FEC Political Donations",
        description="Search federal campaign contributions by donor name via the FEC API.",
        version="1.0.0",
        author="nexus-osint",
        data_source="Federal Election Commission",
        data_source_url="https://www.fec.gov/data/",
        legal_uses=[UseCase.RESEARCH, UseCase.JOURNALISM, UseCase.DUE_DILIGENCE],
        prohibited_uses=[],
        tos_risk=TosRisk.NONE,
        requires_api_key=False,
        api_key_env_var="FEC_API_KEY",
        pii_returned=True,
        input_types=[EntityType.PERSON],
        output_types=[EntityType.PERSON, EntityType.COMPANY, EntityType.ADDRESS],
    )

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        key = api_key or DEFAULT_KEY
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(
                    f"{API_BASE}/schedules/schedule_a/",
                    params={
                        "contributor_name": entity.label,
                        "api_key": key,
                        "per_page": 20,
                        "sort": "-contribution_receipt_date",
                    },
                )
                r.raise_for_status()
                results = r.json().get("results", [])

            seen_committees: set[str] = set()

            for contrib in results:
                employer = contrib.get("contributor_employer") or ""
                occupation = contrib.get("contributor_occupation") or ""
                amount = contrib.get("contribution_receipt_amount", 0)
                date = contrib.get("contribution_receipt_date", "")
                committee_id = contrib.get("committee_id") or ""
                committee_name = contrib.get("committee", {}).get("name") or committee_id

                if committee_id and committee_id not in seen_committees:
                    seen_committees.add(committee_id)
                    uid = f"fec_cmte_{hashlib.md5(committee_id.encode()).hexdigest()[:8]}"
                    committee_entity = Entity(
                        id=uid,
                        type=EntityType.COMPANY,
                        label=committee_name,
                        properties={"committee_id": committee_id, "type": "political_committee"},
                        source_module=self.metadata.name,
                        source_url=f"https://www.fec.gov/data/committee/{committee_id}/",
                    )
                    entities.append(committee_entity)
                    relationships.append(Relationship(
                        source_id=entity.id,
                        target_id=uid,
                        type="DONATED_TO",
                        properties={"amount": amount, "date": date, "occupation": occupation},
                        source_module=self.metadata.name,
                    ))

                addr = contrib.get("contributor_city") or ""
                state = contrib.get("contributor_state") or ""
                if addr and state:
                    addr_str = f"{addr}, {state}"
                    addr_id = f"addr_{hashlib.md5(addr_str.encode()).hexdigest()[:8]}"
                    addr_entity = Entity(
                        id=addr_id,
                        type=EntityType.ADDRESS,
                        label=addr_str,
                        properties={
                            "city": addr,
                            "state": state,
                            "zip": contrib.get("contributor_zip"),
                        },
                        source_module=self.metadata.name,
                    )
                    if addr_entity not in entities:
                        entities.append(addr_entity)
                    relationships.append(Relationship(
                        source_id=entity.id,
                        target_id=addr_id,
                        type="LISTED_ADDRESS",
                        properties={},
                        source_module=self.metadata.name,
                    ))

                if employer:
                    emp_id = f"emp_{hashlib.md5(employer.lower().encode()).hexdigest()[:8]}"
                    if not any(e.id == emp_id for e in entities):
                        entities.append(Entity(
                            id=emp_id,
                            type=EntityType.COMPANY,
                            label=employer,
                            properties={"type": "employer"},
                            source_module=self.metadata.name,
                        ))
                        relationships.append(Relationship(
                            source_id=entity.id,
                            target_id=emp_id,
                            type="EMPLOYED_BY",
                            properties={"occupation": occupation},
                            source_module=self.metadata.name,
                        ))

        except Exception as e:
            return ModuleResult(error=str(e))

        return ModuleResult(entities=entities, relationships=relationships)
