"""
OFAC SDN (Specially Designated Nationals) sanctions list lookup.
Data source: US Treasury — public domain, no T&S restrictions.
"""
import hashlib
import httpx
import xml.etree.ElementTree as ET

from .base import (
    BaseModule, Entity, EntityType, ModuleMetadata, ModuleResult,
    Relationship, TosRisk, UseCase,
)

OFAC_SDN_URL = "https://www.treasury.gov/ofac/downloads/sdn.xml"


class OFACModule(BaseModule):
    metadata = ModuleMetadata(
        name="ofac_sdn",
        display_name="OFAC Sanctions Check",
        description="Checks the US Treasury OFAC Specially Designated Nationals list.",
        version="1.0.0",
        author="nexus-osint",
        data_source="US Treasury OFAC",
        data_source_url="https://home.treasury.gov/policy-issues/financial-sanctions/sdn-list",
        legal_uses=[UseCase.RESEARCH, UseCase.FRAUD_PREVENTION, UseCase.DUE_DILIGENCE],
        prohibited_uses=[],
        tos_risk=TosRisk.NONE,
        requires_api_key=False,
        pii_returned=True,
        input_types=[EntityType.PERSON, EntityType.COMPANY],
        output_types=[EntityType.PERSON, EntityType.COMPANY],
    )

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        query = entity.label.lower()
        results: list[Entity] = []
        relationships: list[Relationship] = []

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(OFAC_SDN_URL)
                response.raise_for_status()

            root = ET.fromstring(response.text)
            ns = {"ofac": "https://sanctionslistservice.ofac.treas.gov/api/PublicationsService/Sdn"}

            for entry in root.findall(".//sdnEntry", ns):
                last = entry.findtext("lastName", namespaces=ns) or ""
                first = entry.findtext("firstName", namespaces=ns) or ""
                full_name = f"{first} {last}".strip().lower()

                if query not in full_name and query not in last.lower():
                    continue

                uid = entry.findtext("uid", namespaces=ns) or ""
                sdn_type = entry.findtext("sdnType", namespaces=ns) or ""
                program = entry.findtext(".//program", namespaces=ns) or ""

                entity_id = f"ofac_{hashlib.md5(uid.encode()).hexdigest()[:8]}"
                matched = Entity(
                    id=entity_id,
                    type=EntityType.COMPANY if sdn_type == "Entity" else EntityType.PERSON,
                    label=f"{first} {last}".strip(),
                    properties={
                        "ofac_uid": uid,
                        "sdn_type": sdn_type,
                        "program": program,
                        "sanctioned": True,
                    },
                    source_module=self.metadata.name,
                    source_url=f"https://sanctionssearch.ofac.treas.gov/Details.aspx?id={uid}",
                )
                results.append(matched)
                relationships.append(Relationship(
                    source_id=entity.id,
                    target_id=entity_id,
                    type="MATCHES_SANCTIONS_ENTRY",
                    properties={"program": program},
                    source_module=self.metadata.name,
                ))

        except Exception as e:
            return ModuleResult(error=str(e))

        return ModuleResult(entities=results, relationships=relationships)
