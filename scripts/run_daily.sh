#!/usr/bin/env bash
set -euo pipefail

# Usage: bash scripts/run_daily.sh
# Fetch reports and generate per-ticker summaries.

cd "$(dirname "$0")/../backend"
source .venv/bin/activate

python -m app.jobs.run_daily
