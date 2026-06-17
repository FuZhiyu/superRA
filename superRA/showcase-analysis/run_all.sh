#!/usr/bin/env bash
# Reproduce every showcase-analysis output in dependency order. Fails fast.
# Raw CSVs and the intermediate parquet are gitignored and rebuilt here.
set -euo pipefail

cd "$(dirname "$0")"

echo "== [1/2] Download Ken French source data =="
uv run --script data/download.py

echo "== [2/2] Build the monthly panel =="
uv run --script analysis/01_build_panel.py

echo "== run_all complete =="
