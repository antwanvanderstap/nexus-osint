"""
SEC EDGAR company and filing search.
Public API — no key required.
https://www.sec.gov/developer
"""
import hashlib
import httpx
import xml.etree.ElementTree as ET

from .base import (
    BaseModule, Entity, EntityType, ModuleMetadata, ModuleResult,
    Relationship, TosRisk, UseCase,
)

EDGAR_SEARCH = "https://www.sec.gov/cgi-bin/browse-edgar"
EDGAR_SUBMISSIONS = "https://data.sec.gov/submissions"
HEADERS = {"User-Agent": "nexus-osint research@nexus-osint.dev"}


class SecEdgarModule(BaseModule):
    metadata = ModuleMetadata(
        name="sec_edgar",
        display_name="SEC EDGAR Filings",
        description="Search SEC EDGAR for company filings, officers, and registered addresses.",
        version="1.0.0",
        author="nexus-osint",
        data_source="SEC EDGAR",
        data_source_url="https://www.sec.gov/edgar",
        legal_uses=[UseCase.RESEARCH, UseCase.DUE_DILIGENCE, UseCase.FRAUD_PREVENTION],
        prohibited_uses=[],
        tos_risk=TosRisk.NONE,
        requires_api_key=False,
        pii_returned=False,
        input_types=[EntityType.COMPANY, EntityType.PERSON],
        output_types=[EntityType.COMPANY, EntityType.ADDRESS, EntityType.DOCUMENT],
    )

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        try:
            async with httpx.AsyncClient(timeout=20, headers=HEADERS) as client:
                r = await client.get(EDGAR_SEARCH, params={
                    "company": entity.label,
                    "action": "getcompany",
                    "owner": "include",
                    "count": "10",
                    "output": "atom",
                })
                r.raise_for_status()

            ns = {"atom": "http://www.w3.org/2005/Atom"}
            root = ET.fromstring(r.text)

            for entry in root.findall("atom:entry", ns):
                title = entry.findtext("atom:title", namespaces=ns) or ""
                link_el = entry.find("atom:link", ns)
                url = link_el.get("href", "") if link_el is not None else ""
                content = entry.findtext("atom:content", namespaces=ns) or ""

                cik = ""
                for part in content.split():
                    if part.isdigit() and len(part) >= 7:
                        cik = part
                        break

                uid = f"edgar_{hashlib.md5(title.encode()).hexdigest()[:8]}"
                co = Entity(
                    id=uid,
                    type=EntityType.COMPANY,
                    label=title.split("(")[0].strip(),
                    properties={"cik": cik, "edgar_content": content[:200]},
                    source_module=self.metadata.name,
                    source_url=url,
                )
                entities.append(co)
                relationships.append(Relationship(
                    source_id=entity.id,
                    target_id=uid,
                    type="EDGAR_MATCH",
                    properties={},
                    source_module=self.metadata.name,
                ))

                if cik:
                    try:
                        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
                            sub = await client.get(f"{EDGAR_SUBMISSIONS}/CIK{cik.zfill(10)}.json")
                            sub.raise_for_status()
                            sub_data = sub.json()

                        addr = sub_data.get("addresses", {}).get("business", {})
                        if addr.get("street1"):
                            addr_str = f"{addr.get('street1')}, {addr.get('city')}, {addr.get('stateOrCountry')} {addr.get('zipCode')}"
                            addr_id = f"addr_{hashlib.md5(addr_str.encode()).hexdigest()[:8]}"
                            entities.append(Entity(
                                id=addr_id,
                                type=EntityType.ADDRESS,
                                label=addr_str,
                                properties=dict(addr),
                                source_module=self.metadata.name,
                            ))
                            relationships.append(Relationship(
                                source_id=uid,
                                target_id=addr_id,
                                type="BUSINESS_ADDRESS",
                                properties={},
                                source_module=self.metadata.name,
                            ))
                    except Exception:
                        pass

        except Exception as e:
            return ModuleResult(error=str(e))

        return ModuleResult(entities=entities, relationships=relationships)
