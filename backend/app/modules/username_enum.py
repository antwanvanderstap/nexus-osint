"""
Username existence enumeration across public platforms.
Sherlock-style: single HTTP GET per site, no login, no content extraction.
Checks existence only — does not scrape profile content.
"""
import asyncio
import hashlib
import httpx

from .base import (
    BaseModule, Entity, EntityType, ModuleMetadata, ModuleResult,
    Relationship, TosRisk, UseCase,
)

# Each entry: (site_name, url_template, expected_status_on_found)
PLATFORMS: list[tuple[str, str, int]] = [
    ("GitHub", "https://github.com/{}", 200),
    ("Reddit", "https://www.reddit.com/user/{}/about.json", 200),
    ("HackerNews", "https://hacker-news.firebaseio.com/v0/user/{}.json", 200),
    ("Gravatar", "https://en.gravatar.com/{}", 200),
    ("Keybase", "https://keybase.io/{}", 200),
    ("Mastodon (mastodon.social)", "https://mastodon.social/@{}", 200),
    ("GitLab", "https://gitlab.com/{}", 200),
    ("Codecademy", "https://www.codecademy.com/profiles/{}", 200),
    ("dev.to", "https://dev.to/{}", 200),
    ("Twitch", "https://www.twitch.tv/{}", 200),
]

HEADERS = {"User-Agent": "nexus-osint/1.0 (OSINT research tool; github.com/nexus-osint)"}


class UsernameEnumModule(BaseModule):
    metadata = ModuleMetadata(
        name="username_enum",
        display_name="Username Presence Check",
        description=(
            "Checks if a username exists across public platforms. "
            "Existence only — no profile content is extracted."
        ),
        version="1.0.0",
        author="nexus-osint",
        data_source="Multiple public platforms",
        data_source_url="",
        legal_uses=[UseCase.RESEARCH, UseCase.SECURITY],
        prohibited_uses=[UseCase.HOUSING, UseCase.EMPLOYMENT, UseCase.FCRA_DECISION],
        tos_risk=TosRisk.LOW,
        requires_api_key=False,
        pii_returned=False,
        input_types=[EntityType.USERNAME],
        output_types=[EntityType.USERNAME],
    )

    async def _check(self, client: httpx.AsyncClient, username: str, platform: str, url: str, expected: int) -> Entity | None:
        try:
            r = await client.get(url.format(username), timeout=8, follow_redirects=True)
            if r.status_code == expected:
                uid = f"uname_{hashlib.md5(f'{platform}{username}'.encode()).hexdigest()[:8]}"
                return Entity(
                    id=uid,
                    type=EntityType.USERNAME,
                    label=platform,
                    properties={"platform": platform, "url": url.format(username), "username": username},
                    source_module=self.metadata.name,
                    source_url=url.format(username),
                )
        except Exception:
            pass
        return None

    async def execute(self, entity: Entity, api_key: str | None = None) -> ModuleResult:
        username = entity.label.strip()
        found: list[Entity] = []
        relationships: list[Relationship] = []

        async with httpx.AsyncClient(headers=HEADERS) as client:
            tasks = [self._check(client, username, p, u, s) for p, u, s in PLATFORMS]
            results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                found.append(result)
                relationships.append(Relationship(
                    source_id=entity.id,
                    target_id=result.id,
                    type="USERNAME_FOUND_ON",
                    properties={"platform": result.properties["platform"]},
                    source_module=self.metadata.name,
                ))

        return ModuleResult(entities=found, relationships=relationships)
