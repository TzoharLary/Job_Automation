#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

# Activate venv if present and prefer its uvicorn
if [[ -f "$DIR/.venv/bin/activate" ]]; then
  source "$DIR/.venv/bin/activate"
fi

# If port is already taken, open browser and exit gracefully
if lsof -iTCP:8000 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Server already running on port 8000. Opening browser..."
  if command -v open >/dev/null 2>&1; then
    open "http://localhost:8000"
  else
    printf 'Open http://localhost:8000 in your browser.\n'
  fi
  exit 0
fi

if [[ -x "$DIR/.venv/bin/uvicorn" ]]; then
  UVICORN="$DIR/.venv/bin/uvicorn"
else
  UVICORN="uvicorn"
fi

# Start server
exec $UVICORN src.app.main:app --host 0.0.0.0 --port 8000
