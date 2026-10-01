---
title: "Register the Showcase Study's Reproduction Graph"
status: not-started
depends_on: []
---

## Objective

Register [showcase-analysis](../../../showcase-analysis/task.md) in the reproduction graph so every retained output rebuilds through `superra repro build showcase-analysis`, and retire `run_all.sh`.

- **One step per existing script,** each declared in the `## Reproduction` of the task that owns it: `data/download.py` (01-data), `analysis/01_build_panel.py` (01-data), `analysis/02_analysis.py` (02-analysis). Scripts keep their behavior; edit them only where the graph cannot describe them.
- **Add one `kind: check` step** that guards a headline result (e.g., the GRS statistics in `data/grs_results.csv`), so the export shows a check alongside builds.
- **The Ken French download is the only network step.** Agree in `## Results` whether the raw CSVs it writes are its `outs` or an external input.
- `superra repro status showcase-analysis` shows every step `fresh` after a real build; commit `repro-lock.json`.
- `superRA/showcase-analysis` task `## Results` that cite `run_all.sh` now cite the graph.
- The live export (`docs/build_site.sh` → `showcase-analysis-tree.html`) renders the graph and step freshness; confirm by opening it.

## Details

- `run_all.sh` order is download → build panel → analysis; the raw CSVs and the parquet are gitignored.
- This makes the repo register steps again. [tmp-v05-integrate-refactor](../../../tmp-v05-integrate-refactor/task.md) records "no registered reproduction steps" as its Protect decision; that line now holds for everything except the showcase.
- Load `superRA:reproducibility` ([designing-the-graph.md](../../../../skills/reproducibility/references/designing-the-graph.md)).
