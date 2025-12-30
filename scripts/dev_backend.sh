#!/usr/bin/env bash
set -euo pipefail

# Usage: bash scripts/dev_backend.sh
# Runs FastAPI backend with auto-reload.

cd "$(dirname "$0")/../backend"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create data directory
mkdir -p data

# Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
