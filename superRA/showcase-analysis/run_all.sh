#!/usr/bin/env bash
# Reproduce every showcase-analysis output in dependency order. Fails fast.
# Raw CSVs and the intermediate parquet are gitignored and rebuilt here.
set -euo pipefail

cd "$(dirname "$0")"

echo "== [1/3] Download Ken French source data =="
uv run --script data/download.py

echo "== [2/3] Build the monthly panel =="
uv run --script analysis/01_build_panel.py

echo "== [3/3] Estimate, test (GRS), and visualize: CAPM vs FF3 =="
uv run --script analysis/02_analysis.py

echo "== run_all complete =="
