"""
HaveIBeenPwned email breach lookup.
Requires a paid API key (~$3.50/mo hobbyist tier).
https://haveibeenpwned.com/API/v3
"""
import hashlib
import httpx

from .base import (
    BaseModule, Entity, EntityType, ModuleMetadata, ModuleResult,
    Relationship, TosRisk, UseCase,
)

API_BASE = "https://haveibeenpwned.com/api/v3"


class HibpModule(BaseModule):
    metadata = ModuleMetadata(
        name="hibp",
        display_name="HaveIBeenPwned Breach Check",
        description="Check if an email address appears in known data breaches.",
        version="1.0.0",
        author="nexus-osint",
        data_source="HaveIBeenPwned",
        data_source_url="https://haveibeenpwned.com",
        legal_uses=[UseCase.SECURITY, UseCase.FRAUD_PREVENTION, UseCase.RESEARCH],
        prohibited_uses=[UseCase.HOUSING, UseCase.EMPLOYMENT, UseCase.FCRA_DECISION],
        tos_risk=TosRisk.NONE,
        requires_api_key=True,
        api_key_env_var="HIBP_API_KEY",
        pii_returned=True,
        input_types=[EntityType.EMAIL],
        output_types=[EntityType.DOCUMENT],
    )

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        if not api_key:
            return ModuleResult(error="HIBP requires an API key. Get one at https://haveibeenpwned.com/API/Key")

        entities: list[Entity] = []
        relationships: list[Relationship] = []

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(
                    f"{API_BASE}/breachedaccount/{entity.label}",
                    params={"truncateResponse": "false"},
                    headers={
                        "hibp-api-key": api_key,
                        "user-agent": "nexus-osint",
                    },
                )

                if r.status_code == 404:
                    return ModuleResult(entities=[], relationships=[], raw={"result": "No breaches found"})

                r.raise_for_status()
                breaches = r.json()

            for breach in breaches:
                uid = f"breach_{hashlib.md5(breach['Name'].encode()).hexdigest()[:8]}"
                doc = Entity(
                    id=uid,
                    type=EntityType.DOCUMENT,
                    label=breach.get("Name", "Unknown Breach"),
                    properties={
                        "breach_date": breach.get("BreachDate"),
                        "added_date": breach.get("AddedDate"),
                        "pwn_count": breach.get("PwnCount"),
                        "data_classes": breach.get("DataClasses", []),
                        "is_verified": breach.get("IsVerified"),
                        "is_sensitive": breach.get("IsSensitive"),
                        "domain": breach.get("Domain"),
                    },
                    source_module=self.metadata.name,
                    source_url=f"https://haveibeenpwned.com/PwnedWebsites#{breach.get('Name')}",
                )
                entities.append(doc)
                relationships.append(Relationship(
                    source_id=entity.id,
                    target_id=uid,
                    type="FOUND_IN_BREACH",
                    properties={"breach_date": breach.get("BreachDate")},
                    source_module=self.metadata.name,
                ))

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return ModuleResult(error="Invalid HIBP API key.")
            if e.response.status_code == 429:
                return ModuleResult(error="HIBP rate limit hit — wait 1 minute and retry.")
            return ModuleResult(error=str(e))
        except Exception as e:
            return ModuleResult(error=str(e))

        return ModuleResult(entities=entities, relationships=relationships)
