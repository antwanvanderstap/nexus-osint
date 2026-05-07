# Nexus OSINT

A free, open-source, self-hosted OSINT investigation platform for small businesses and independent researchers.

Built as a community alternative to expensive commercial tools — visual graph-based investigation using only legal, public data sources.

---

## What It Is

- **Graph-based** — relationships between entities visualized as a network
- **Module-driven** — each data source is an isolated, auditable plugin
- **Self-hosted** — your data never leaves your machine
- **Legally considered** — every module carries T&S risk and prohibited-use metadata
- **Small-business focused** — designed for landlords, SMB due diligence, fraud prevention

## What It Is Not

Nexus OSINT is **not** a consumer reporting agency and **may not** be used to make decisions
about employment, housing, credit, or insurance eligibility (FCRA-regulated purposes).
See [LEGAL.md](LEGAL.md) for full operator guidance.

---

## Quick Start

**Requirements:** Docker and Docker Compose.

```bash
git clone https://github.com/YOUR_ORG/nexus-osint.git
cd nexus-osint
cp .env.example .env
docker compose up
```

Open [http://localhost:3000](http://localhost:3000).

---

## Built-in Modules (v0.1)

| Module | Data Source | T&S Risk | API Key |
|---|---|---|---|
| OFAC Sanctions Check | US Treasury | None | No |
| OpenCorporates Business Lookup | OpenCorporates | None | Optional |
| WHOIS Domain Lookup | ICANN/WHOIS | None | No |
| Username Presence Check | Multiple platforms | Low | No |

---

## Roadmap

### v0.2
- [ ] Property record lookups (US county assessors — top 10 states)
- [ ] CourtListener federal case search
- [ ] SEC EDGAR filings
- [ ] FEC political donations
- [ ] PDF report export

### v0.3
- [ ] GDELT adverse media search
- [ ] FAA pilot/aircraft registry
- [ ] Case sharing (local team, read-only)
- [ ] PostgreSQL persistence (replace in-memory store)

### v0.4
- [ ] Module marketplace (community-contributed modules)
- [ ] Shodan integration
- [ ] Multi-user support

---

## Architecture

```
frontend/     React + Vite + Cytoscape.js
backend/      FastAPI (Python 3.12)
  modules/    Pluggable data source integrations
  core/       Plugin bus, audit logger
```

Deployed via Docker Compose. No cloud dependency. Audit logs stored locally.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Module contributions are the highest-impact way to help.

New modules require a T&S and legal assessment before merging — the bar is intentional.

---

## Legal

See [LEGAL.md](LEGAL.md) for FCRA, GDPR, CFAA, and T&S guidance for operators.

---

## License

MIT — see [LICENSE](LICENSE).
