"""
FAA aircraft registry and airmen certificate lookup.
Public government records — no API key required.
Aircraft N-number lookup via FAA registry.
Airmen lookup via FAA airmen inquiry service.
"""
import hashlib
import httpx
from urllib.parse import quote

from .base import (
    BaseModule, Entity, EntityType, ModuleMetadata, ModuleResult,
    Relationship, TosRisk, UseCase,
)

AIRCRAFT_URL = "https://registry.faa.gov/aircraftinquiry/Search/NNumberResult"
AIRMEN_URL = "https://amsrvs.registry.faa.gov/airmeninquiry/Main.aspx"
HEADERS = {
    "User-Agent": "nexus-osint/1.0 (OSINT research; github.com/nexus-osint)",
    "Accept": "text/html,application/xhtml+xml",
}


class FaaRegistryModule(BaseModule):
    metadata = ModuleMetadata(
        name="faa_registry",
        display_name="FAA Aircraft & Airmen Registry",
        description=(
            "Looks up FAA aircraft registration by N-number (e.g. N12345) "
            "or airmen certificate by last name. Input an N-number for aircraft, "
            "or a person name for pilot certificates."
        ),
        version="1.0.0",
        author="nexus-osint",
        data_source="FAA Aircraft Registry / Airmen Inquiry",
        data_source_url="https://registry.faa.gov",
        legal_uses=[UseCase.RESEARCH, UseCase.DUE_DILIGENCE],
        prohibited_uses=[],
        tos_risk=TosRisk.LOW,
        requires_api_key=False,
        pii_returned=True,
        input_types=[EntityType.PERSON, EntityType.AIRCRAFT],
        output_types=[EntityType.AIRCRAFT, EntityType.PERSON, EntityType.COMPANY, EntityType.ADDRESS],
    )

    async def _lookup_aircraft(self, entity: Entity) -> ModuleResult:
        """N-number → aircraft registration details."""
        n_number = entity.label.upper().lstrip("N")
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        try:
            async with httpx.AsyncClient(timeout=15, headers=HEADERS, follow_redirects=True) as client:
                r = await client.get(AIRCRAFT_URL, params={"nNumberTxt": n_number})
                r.raise_for_status()
                html = r.text

            def extract(label: str) -> str:
                marker = label
                idx = html.find(marker)
                if idx == -1:
                    return ""
                start = html.find(">", idx) + 1
                end = html.find("<", start)
                return html[start:end].strip()

            owner = extract("Registrant Name")
            street = extract("Street")
            city = extract("City")
            state = extract("State")
            serial = extract("Serial Number")
            mfr = extract("Manufacturer Name")
            model = extract("Model")
            aircraft_type = extract("Type Aircraft")

            uid = f"ac_{hashlib.md5(n_number.encode()).hexdigest()[:8]}"
            aircraft = Entity(
                id=uid,
                type=EntityType.AIRCRAFT,
                label=f"N{n_number}",
                properties={
                    "n_number": f"N{n_number}",
                    "manufacturer": mfr,
                    "model": model,
                    "serial_number": serial,
                    "aircraft_type": aircraft_type,
                    "owner": owner,
                },
                source_module=self.metadata.name,
                source_url=f"https://registry.faa.gov/aircraftinquiry/Search/NNumberResult?nNumberTxt={n_number}",
            )
            entities.append(aircraft)
            relationships.append(Relationship(
                source_id=entity.id,
                target_id=uid,
                type="AIRCRAFT_REGISTRATION",
                properties={},
                source_module=self.metadata.name,
            ))

            if owner:
                owner_id = f"owner_{hashlib.md5(owner.encode()).hexdigest()[:8]}"
                entities.append(Entity(
                    id=owner_id,
                    type=EntityType.PERSON,
                    label=owner,
                    properties={},
                    source_module=self.metadata.name,
                ))
                relationships.append(Relationship(
                    source_id=uid,
                    target_id=owner_id,
                    type="REGISTERED_OWNER",
                    properties={},
                    source_module=self.metadata.name,
                ))

            if city and state:
                addr_str = f"{street}, {city}, {state}".strip(", ")
                addr_id = f"addr_{hashlib.md5(addr_str.encode()).hexdigest()[:8]}"
                entities.append(Entity(
                    id=addr_id,
                    type=EntityType.ADDRESS,
                    label=addr_str,
                    properties={"city": city, "state": state, "street": street},
                    source_module=self.metadata.name,
                ))
                relationships.append(Relationship(
                    source_id=uid,
                    target_id=addr_id,
                    type="REGISTERED_ADDRESS",
                    properties={},
                    source_module=self.metadata.name,
                ))

        except Exception as e:
            return ModuleResult(error=str(e))

        return ModuleResult(entities=entities, relationships=relationships)

    async def _lookup_airmen(self, entity: Entity) -> ModuleResult:
        """Person name → airmen certificate records."""
        parts = entity.label.split()
        last = parts[-1] if parts else entity.label
        first = parts[0] if len(parts) > 1 else ""
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        try:
            async with httpx.AsyncClient(timeout=20, headers=HEADERS, follow_redirects=True) as client:
                r = await client.post(
                    AIRMEN_URL,
                    data={
                        "LastName": last,
                        "FirstName": first,
                        "state": "",
                        "region": "",
                        "action": "Search",
                    },
                )
                r.raise_for_status()
                html = r.text

            rows = html.split("<tr")[2:]
            for row in rows[:10]:
                if "<td" not in row:
                    continue
                cells = [c.split(">")[-1].split("<")[0].strip() for c in row.split("<td")[1:]]
                if len(cells) < 3:
                    continue
                name = cells[0]
                city = cells[1] if len(cells) > 1 else ""
                state = cells[2] if len(cells) > 2 else ""
                if not name or name.lower() == "name":
                    continue

                uid = f"airman_{hashlib.md5(f'{name}{city}{state}'.encode()).hexdigest()[:8]}"
                airman = Entity(
                    id=uid,
                    type=EntityType.PERSON,
                    label=name,
                    properties={"city": city, "state": state, "certificate_type": "FAA Airman"},
                    source_module=self.metadata.name,
                    source_url="https://amsrvs.registry.faa.gov/airmeninquiry/",
                )
                entities.append(airman)
                relationships.append(Relationship(
                    source_id=entity.id,
                    target_id=uid,
                    type="FAA_AIRMAN_MATCH",
                    properties={"city": city, "state": state},
                    source_module=self.metadata.name,
                ))

        except Exception as e:
            return ModuleResult(error=str(e))

        return ModuleResult(entities=entities, relationships=relationships)

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        if entity.type == EntityType.AIRCRAFT or entity.label.upper().startswith("N"):
            return await self._lookup_aircraft(entity)
        return await self._lookup_airmen(entity)
