# ARGUS (Automated Real-time Geospatial Understanding System)

This repository contains a runnable MVP implementation of the Watch_Dogs-style live intelligence architecture described in `docs/ARGUS_RESEARCH_ARCHITECTURE.md`.

## What is implemented

- FastAPI backend with pluggable integration registry.
- Camera and events endpoints backed by mock adapters.
- AOI summary endpoint with situation score computation.
- Browser UI for AOI selection and signal display.
- Docker support for one-command local launch.
- **Offline stdlib runner** for Codex-like environments where pip/docker are unavailable.

## Quick start (Codex-friendly)

### Option A (recommended here): no dependencies

```bash
PORT=8000 ./scripts/run.sh
```

- If `uvicorn` is installed, this runs FastAPI.
- If `uvicorn` is missing, it automatically starts `scripts/run_local.py` (stdlib fallback with compatible API routes).
- You can change the listen port with `PORT=8765 ./scripts/run.sh`.

Open: `http://localhost:$PORT` (default `8000`).

### Option B: local Python (FastAPI)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./scripts/run.sh
```

### Option C: Docker Compose

```bash
docker compose up --build
```

## API endpoints

- `GET /health`
- `GET /api/cameras?minLat=...&maxLat=...&minLon=...&maxLon=...`
- `GET /api/events?minLat=...&maxLat=...&minLon=...&maxLon=...`
- `GET /api/aoi/summary?name=...`
