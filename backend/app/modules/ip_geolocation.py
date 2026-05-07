"""
IP address geolocation using ip-api.com.
Free tier: 45 requests/minute, no API key required.
No T&S restrictions for non-commercial use.
https://ip-api.com/docs
"""
import hashlib
import httpx

from .base import (
    BaseModule, Entity, EntityType, ModuleMetadata, ModuleResult,
    Relationship, TosRisk, UseCase,
)

API_URL = "http://ip-api.com/json/{ip}"
FIELDS = "status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"


class IpGeolocationModule(BaseModule):
    metadata = ModuleMetadata(
        name="ip_geolocation",
        display_name="IP Geolocation",
        description="Geolocates an IP address and returns country, city, ISP, ASN, and org.",
        version="1.0.0",
        author="nexus-osint",
        data_source="ip-api.com",
        data_source_url="https://ip-api.com",
        legal_uses=[UseCase.RESEARCH, UseCase.SECURITY, UseCase.FRAUD_PREVENTION],
        prohibited_uses=[],
        tos_risk=TosRisk.NONE,
        requires_api_key=False,
        pii_returned=False,
        input_types=[EntityType.IP],
        output_types=[EntityType.IP, EntityType.COMPANY, EntityType.ADDRESS],
    )

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        ip = entity.label.strip()
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(API_URL.format(ip=ip), params={"fields": FIELDS})
                r.raise_for_status()
                data = r.json()

            if data.get("status") == "fail":
                return ModuleResult(error=data.get("message", "IP lookup failed"))

            uid = f"ip_{hashlib.md5(ip.encode()).hexdigest()[:8]}"
            enriched_ip = Entity(
                id=uid,
                type=EntityType.IP,
                label=ip,
                properties={
                    "country": data.get("country"),
                    "country_code": data.get("countryCode"),
                    "region": data.get("regionName"),
                    "city": data.get("city"),
                    "zip": data.get("zip"),
                    "lat": data.get("lat"),
                    "lon": data.get("lon"),
                    "timezone": data.get("timezone"),
                    "isp": data.get("isp"),
                    "org": data.get("org"),
                    "asn": data.get("as"),
                },
                source_module=self.metadata.name,
                source_url=f"https://ip-api.com/#{ip}",
            )
            entities.append(enriched_ip)
            relationships.append(Relationship(
                source_id=entity.id,
                target_id=uid,
                type="GEOLOCATED",
                properties={},
                source_module=self.metadata.name,
            ))

            if data.get("org"):
                org_id = f"org_{hashlib.md5(data['org'].encode()).hexdigest()[:8]}"
                entities.append(Entity(
                    id=org_id,
                    type=EntityType.COMPANY,
                    label=data["org"],
                    properties={"isp": data.get("isp"), "asn": data.get("as")},
                    source_module=self.metadata.name,
                ))
                relationships.append(Relationship(
                    source_id=uid,
                    target_id=org_id,
                    type="HOSTED_BY",
                    properties={},
                    source_module=self.metadata.name,
                ))

            if data.get("city"):
                loc = f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}"
                loc_id = f"loc_{hashlib.md5(loc.encode()).hexdigest()[:8]}"
                entities.append(Entity(
                    id=loc_id,
                    type=EntityType.ADDRESS,
                    label=loc,
                    properties={"lat": data.get("lat"), "lon": data.get("lon"), "timezone": data.get("timezone")},
                    source_module=self.metadata.name,
                ))
                relationships.append(Relationship(
                    source_id=uid,
                    target_id=loc_id,
                    type="LOCATED_IN",
                    properties={},
                    source_module=self.metadata.name,
                ))

        except Exception as e:
            return ModuleResult(error=str(e))

        return ModuleResult(entities=entities, relationships=relationships)
