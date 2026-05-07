# Local Deployment Guide

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac or Windows)
- 4 GB RAM available to Docker
- Ports 3000 and 8000 free

## Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_ORG/nexus-osint.git
cd nexus-osint

# 2. Copy and configure environment
cp .env.example .env
# Edit .env to add any optional API keys

# 3. Start the stack
docker compose up

# 4. Open the app
open http://localhost:3000
```

## Stopping

```bash
docker compose down
```

Audit logs are stored in a named Docker volume (`audit_data`) and persist between restarts.

## Updating

```bash
git pull
docker compose build
docker compose up
```

---

## Access from Other Devices on Your Network

To access from a phone or another computer on the same Wi-Fi:

1. Find your machine's local IP: `ipconfig getifaddr en0` (Mac) or `ipconfig` (Windows)
2. Open `http://YOUR_LOCAL_IP:3000` on the other device

For secure remote access from outside your network, see the [VPS deployment guide](vps.md)
and the Tailscale section.
