"""
GDELT 2.0 adverse media and news article search.
Free API, no key required.
https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
"""
import hashlib
import httpx
from urllib.parse import quote

from .base import (
    BaseModule, Entity, EntityType, ModuleMetadata, ModuleResult,
    Relationship, TosRisk, UseCase,
)

API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


class GdeltModule(BaseModule):
    metadata = ModuleMetadata(
        name="gdelt",
        display_name="GDELT Adverse Media",
        description="Searches global news via GDELT for mentions of a person or company.",
        version="1.0.0",
        author="nexus-osint",
        data_source="GDELT Project",
        data_source_url="https://www.gdeltproject.org",
        legal_uses=[UseCase.RESEARCH, UseCase.DUE_DILIGENCE, UseCase.JOURNALISM, UseCase.FRAUD_PREVENTION],
        prohibited_uses=[],
        tos_risk=TosRisk.NONE,
        requires_api_key=False,
        pii_returned=False,
        input_types=[EntityType.PERSON, EntityType.COMPANY],
        output_types=[EntityType.DOCUMENT],
    )

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        entities: list[Entity] = []
        relationships: list[Relationship] = []

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(API_URL, params={
                    "query": f'"{entity.label}"',
                    "mode": "artlist",
                    "maxrecords": "15",
                    "format": "json",
                    "sort": "datedesc",
                })
                r.raise_for_status()
                data = r.json()

            articles = data.get("articles", [])
            for article in articles:
                url = article.get("url", "")
                title = article.get("title", "Unknown Article")
                uid = f"art_{hashlib.md5(url.encode()).hexdigest()[:8]}"

                doc = Entity(
                    id=uid,
                    type=EntityType.DOCUMENT,
                    label=title[:80] + ("…" if len(title) > 80 else ""),
                    properties={
                        "url": url,
                        "source": article.get("domain"),
                        "published": article.get("seendate"),
                        "language": article.get("language"),
                        "sentiment_tone": article.get("tone"),
                        "source_country": article.get("sourcecountry"),
                    },
                    source_module=self.metadata.name,
                    source_url=url,
                )
                entities.append(doc)
                relationships.append(Relationship(
                    source_id=entity.id,
                    target_id=uid,
                    type="MENTIONED_IN",
                    properties={"published": article.get("seendate"), "source": article.get("domain")},
                    source_module=self.metadata.name,
                ))

        except Exception as e:
            return ModuleResult(error=str(e))

        return ModuleResult(entities=entities, relationships=relationships)
