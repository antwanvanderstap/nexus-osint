"""
DNS record lookup for a domain.
Uses dnspython — no external API, no T&S concerns.
"""
import hashlib
import dns.resolver
import dns.exception

from .base import (
    BaseModule, Entity, EntityType, ModuleMetadata, ModuleResult,
    Relationship, TosRisk, UseCase,
)

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]


class DnsLookupModule(BaseModule):
    metadata = ModuleMetadata(
        name="dns_lookup",
        display_name="DNS Record Lookup",
        description="Retrieves A, AAAA, MX, NS, TXT, and CNAME records for a domain.",
        version="1.0.0",
        author="nexus-osint",
        data_source="Public DNS",
        data_source_url="https://www.icann.org",
        legal_uses=[UseCase.RESEARCH, UseCase.SECURITY, UseCase.DUE_DILIGENCE],
        prohibited_uses=[],
        tos_risk=TosRisk.NONE,
        requires_api_key=False,
        pii_returned=False,
        input_types=[EntityType.DOMAIN],
        output_types=[EntityType.IP, EntityType.DOMAIN, EntityType.COMPANY],
    )

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        domain = entity.label.strip().lower()
        entities: list[Entity] = []
        relationships: list[Relationship] = []
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 8

        for rtype in RECORD_TYPES:
            try:
                answers = resolver.resolve(domain, rtype)
                for rdata in answers:
                    value = rdata.to_text().strip().rstrip(".")

                    if rtype in ("A", "AAAA"):
                        uid = f"ip_{hashlib.md5(value.encode()).hexdigest()[:8]}"
                        ent = Entity(
                            id=uid,
                            type=EntityType.IP,
                            label=value,
                            properties={"record_type": rtype},
                            source_module=self.metadata.name,
                        )
                        rel_type = "RESOLVES_TO"

                    elif rtype == "MX":
                        parts = value.split()
                        mx_host = parts[-1] if parts else value
                        uid = f"mx_{hashlib.md5(mx_host.encode()).hexdigest()[:8]}"
                        ent = Entity(
                            id=uid,
                            type=EntityType.DOMAIN,
                            label=mx_host,
                            properties={"record_type": "MX", "priority": parts[0] if len(parts) > 1 else ""},
                            source_module=self.metadata.name,
                        )
                        rel_type = "MAIL_HANDLED_BY"

                    elif rtype == "NS":
                        uid = f"ns_{hashlib.md5(value.encode()).hexdigest()[:8]}"
                        ent = Entity(
                            id=uid,
                            type=EntityType.DOMAIN,
                            label=value,
                            properties={"record_type": "NS"},
                            source_module=self.metadata.name,
                        )
                        rel_type = "NAMESERVER"

                    elif rtype == "CNAME":
                        uid = f"cname_{hashlib.md5(value.encode()).hexdigest()[:8]}"
                        ent = Entity(
                            id=uid,
                            type=EntityType.DOMAIN,
                            label=value,
                            properties={"record_type": "CNAME"},
                            source_module=self.metadata.name,
                        )
                        rel_type = "CNAME_TARGET"

                    else:
                        uid = f"txt_{hashlib.md5(value.encode()).hexdigest()[:8]}"
                        ent = Entity(
                            id=uid,
                            type=EntityType.DOCUMENT,
                            label=value[:60] + ("…" if len(value) > 60 else ""),
                            properties={"record_type": "TXT", "full_value": value},
                            source_module=self.metadata.name,
                        )
                        rel_type = "TXT_RECORD"

                    if not any(e.id == uid for e in entities):
                        entities.append(ent)
                    relationships.append(Relationship(
                        source_id=entity.id,
                        target_id=uid,
                        type=rel_type,
                        properties={"record_type": rtype},
                        source_module=self.metadata.name,
                    ))

            except (dns.exception.DNSException, dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                continue
            except Exception:
                continue

        return ModuleResult(entities=entities, relationships=relationships)
