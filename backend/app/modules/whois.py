"""
WHOIS domain registration lookup.
Uses python-whois — no API key, no T&S issues.
"""
import hashlib

import whois as pywhois

from .base import (
    BaseModule, Entity, EntityType, ModuleMetadata, ModuleResult,
    Relationship, TosRisk, UseCase,
)


class WhoisModule(BaseModule):
    metadata = ModuleMetadata(
        name="whois",
        display_name="WHOIS Domain Lookup",
        description="Retrieves domain registration data (registrar, dates, nameservers).",
        version="1.0.0",
        author="nexus-osint",
        data_source="WHOIS",
        data_source_url="https://www.icann.org/resources/pages/whois-2018-01-17-en",
        legal_uses=[UseCase.RESEARCH, UseCase.SECURITY, UseCase.DUE_DILIGENCE],
        prohibited_uses=[],
        tos_risk=TosRisk.NONE,
        requires_api_key=False,
        pii_returned=True,
        input_types=[EntityType.DOMAIN],
        output_types=[EntityType.DOMAIN, EntityType.EMAIL, EntityType.COMPANY],
    )

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        try:
            w = pywhois.whois(entity.label)
        except Exception as e:
            return ModuleResult(error=str(e))

        entities: list[Entity] = []
        relationships: list[Relationship] = []

        domain_id = f"domain_{hashlib.md5(entity.label.encode()).hexdigest()[:8]}"
        domain_entity = Entity(
            id=domain_id,
            type=EntityType.DOMAIN,
            label=entity.label,
            properties={
                "registrar": w.registrar,
                "creation_date": str(w.creation_date),
                "expiration_date": str(w.expiration_date),
                "updated_date": str(w.updated_date),
                "name_servers": w.name_servers,
                "status": w.status,
                "dnssec": w.dnssec,
            },
            source_module=self.metadata.name,
        )
        entities.append(domain_entity)
        relationships.append(Relationship(
            source_id=entity.id,
            target_id=domain_id,
            type="WHOIS_RECORD",
            properties={},
            source_module=self.metadata.name,
        ))

        for email in (w.emails or []):
            email_id = f"email_{hashlib.md5(email.encode()).hexdigest()[:8]}"
            entities.append(Entity(
                id=email_id,
                type=EntityType.EMAIL,
                label=email,
                properties={},
                source_module=self.metadata.name,
            ))
            relationships.append(Relationship(
                source_id=domain_id,
                target_id=email_id,
                type="REGISTERED_BY_EMAIL",
                properties={},
                source_module=self.metadata.name,
            ))

        if w.org:
            org_id = f"org_{hashlib.md5(w.org.encode()).hexdigest()[:8]}"
            entities.append(Entity(
                id=org_id,
                type=EntityType.COMPANY,
                label=w.org,
                properties={},
                source_module=self.metadata.name,
            ))
            relationships.append(Relationship(
                source_id=domain_id,
                target_id=org_id,
                type="REGISTERED_BY_ORG",
                properties={},
                source_module=self.metadata.name,
            ))

        return ModuleResult(entities=entities, relationships=relationships)
