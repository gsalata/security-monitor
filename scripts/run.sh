#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8000}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if "$PYTHON_BIN" -c 'import uvicorn' >/dev/null 2>&1; then
  echo "Starting ARGUS with FastAPI/uvicorn on :${PORT}"
  exec "$PYTHON_BIN" -m uvicorn src.api.main:app --host 0.0.0.0 --port "$PORT" --reload
fi

echo "uvicorn not available; starting stdlib fallback runner on :${PORT}"
exec "$PYTHON_BIN" scripts/run_local.py --port "$PORT"
