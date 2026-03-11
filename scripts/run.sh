#!/usr/bin/env bash
set -euo pipefail

if python -c 'import uvicorn' >/dev/null 2>&1; then
  echo "Starting ARGUS with FastAPI/uvicorn on :8000"
  exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
fi

echo "uvicorn not available; starting stdlib fallback runner on :8000"
exec python scripts/run_local.py
