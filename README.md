# ARGUS (Automated Real-time Geospatial Understanding System)

This repository contains a runnable MVP implementation of the Watch_Dogs-style live intelligence architecture described in `docs/ARGUS_RESEARCH_ARCHITECTURE.md`.

## What is implemented

- FastAPI backend with pluggable integration registry.
- Camera and events endpoints backed by mock adapters.
- AOI summary endpoint with situation score computation.
- Browser UI for AOI selection and signal display.
- Docker support for one-command local launch.

## Quick start (Codex-friendly)

### Option A: local Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/run.sh
```

Open: http://localhost:8000

### Option B: Docker Compose

```bash
docker compose up --build
```

Open: http://localhost:8000

## API endpoints

- `GET /health`
- `GET /api/cameras?minLat=...&maxLat=...&minLon=...&maxLon=...`
- `GET /api/events?minLat=...&maxLat=...&minLon=...&maxLon=...`
- `GET /api/aoi/summary?name=...`
