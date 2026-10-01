---
title: "Register the Showcase Study's Reproduction Graph"
status: revise
depends_on: []
---

## Objective

Register [showcase-analysis](../../../showcase-analysis/task.md) in the reproduction graph so every retained output rebuilds through `superra repro build showcase-analysis`, and retire `run_all.sh`.

- **One step per analysis script,** each declared in the `## Reproduction` of the task that owns it: `analysis/01_build_panel.py` (01-data), `analysis/02_analysis.py` (02-analysis). Scripts keep their behavior; edit them only where the graph cannot describe them.
- **Add one `kind: check` step** that guards a headline result (e.g., the GRS statistics in `data/grs_results.csv`), so the export shows a check alongside builds.
- **The showcase data is frozen and committed.** The two raw Ken French CSVs (the 202608 release) are a committed external input; `download.py` stays as an unregistered refresh helper, and its zips are not kept. The panel and estimates parquet files are committed too, so a clean checkout — and the deployed docs export — reads every step `fresh` and the recorded numbers never move without a deliberate data refresh.
- `superra repro status showcase-analysis` shows every step `fresh` after a real build; commit `repro-lock.json`.
- `superRA/showcase-analysis` task `## Results` that cite `run_all.sh` now cite the graph.
- The live export (`docs/build_site.sh` → `showcase-analysis-tree.html`) renders the graph and step freshness; confirm by opening it.

## Revision Notes

Substantive: the researcher chose to freeze and commit the showcase data instead of registering `download` as a step, so the docs export reads fresh and the numbers stop drifting with Ken French releases.

## Details

- `run_all.sh` order is download → build panel → analysis; the raw CSVs and the parquet are gitignored.
- This makes the repo register steps again. [tmp-v05-integrate-refactor](../../../tmp-v05-integrate-refactor/task.md) records "no registered reproduction steps" as its Protect decision; that line now holds for everything except the showcase.
- Load `superRA:reproducibility` ([designing-the-graph.md](../../../../skills/reproducibility/references/designing-the-graph.md)).

## Results

The showcase study now rebuilds through four registered steps, all `fresh` in the committed [repro-lock.json](../../../../repro-lock.json), and `run_all.sh` is gone. The rebuild pulled a newer Ken French vintage, so every number in the showcase changed slightly. The verdict did not change.

### The graph

| Step | Task | Reads | Writes |
|---|---|---|---|
| [download](../../../showcase-analysis/01-data/task.md#step-download) | 01-data | the Ken French website | `data/raw/`: two zips and two CSVs |
| [build-panel](../../../showcase-analysis/01-data/task.md#step-build-panel) | 01-data | the two raw CSVs | `data/ff_panel.parquet` |
| [estimate-test-plot](../../../showcase-analysis/02-analysis/task.md#step-estimate-test-plot) | 02-analysis | the panel | `data/regression_estimates.parquet`, [grs_results.csv](../../../showcase-analysis/data/grs_results.csv), the four figures in `02-analysis/attachments/` |
| [check-grs-headline](../../../showcase-analysis/02-analysis/task.md#step-check-grs-headline) (`kind: check`) | 02-analysis | `grs_results.csv` | — |

- **Evidence.** `superra repro build showcase-analysis` ran all four steps and none was accepted. The selection covers the whole chain, so it has no saved inputs. `superra repro status showcase-analysis --upstream` reports 4 `fresh`, `superra task check` is clean, and the check step passed: both models are rejected at 1%, FF3's GRS is below CAPM's, and FF3's mean |α| is 0.44 of CAPM's.
- **Reruns reproduce the outputs byte for byte.** After a `--force` rebuild every PNG, parquet, and raw file had the same hash and the lock was unchanged. After the fig3 title fix, only `estimate-test-plot` reran, and `check-grs-headline` stayed unchanged because `grs_results.csv` had not moved.
- **One runner.** [superRA/config.yaml](../../../config.yaml) adds `runners: uv: uv run --script {script}`, and every step uses it. Script dependencies are unpinned PEP 723 lists, so a rerun on a machine with newer packages can change output bytes, such as the matplotlib version stamped in each PNG.

### The raw CSVs are the download step's outputs

They are declared as `download`'s `outs` rather than as an external input, so `superra repro build showcase-analysis` rebuilds everything from a checkout that lacks them. The true external input is the remote library, which the graph cannot hash, and which serves only the current vintage.

- **Consequence: any rerun of `download` fetches the latest vintage.** It reruns when `data/raw/` is absent (a fresh clone) or when its script changes. The changed `grs_results.csv` and figures then show up in `git diff`.
- **A fixed sample end would not freeze the numbers either.** Ken French revised history between vintages: cutting the 202608 file at 2026-04 gives CAPM GRS 4.099, against the recorded 4.104. The 202604 files exist nowhere on this machine.

### The 202608 vintage moved the showcase numbers

| | Old (202604 vintage) | New (202608 vintage) |
|---|---|---|
| Sample | 754 months, 1963-07 → 2026-04 | 758 months, 1963-07 → 2026-08 |
| CAPM GRS | $F(25,728)=4.10$ | $F(25,732)=4.20$ |
| FF3 GRS | $F(25,726)=3.55$ | $F(25,730)=3.64$ |
| mean \|α\| CAPM → FF3 (%/mo) | 0.195 → 0.089 | 0.197 → 0.087 |
| `SMALL LoBM` FF3 α | −0.472, $t=-5.1$ | −0.465, $t=-5.1$ |

Both models are still rejected, FF3 still halves the mean |α|, and the loading gradients and sign guards still hold. Each number in the `## Results` of [showcase-analysis](../../../showcase-analysis/task.md), [01-data](../../../showcase-analysis/01-data/task.md), [02-analysis](../../../showcase-analysis/02-analysis/task.md), and [03-writeup](../../../showcase-analysis/03-writeup/task.md) now comes from the build logs. Each of those sections cites the steps in place of `run_all.sh`.

### Changes beyond the step declarations

- **[02_analysis.py](../../../showcase-analysis/analysis/02_analysis.py): fig3's title had `1963-07 -> 2026-04` hardcoded.** The title now takes the panel's own date range, and a header comment no longer states the panel length. No other script changed behavior.
- **03-writeup embeds its two figures from `../02-analysis/attachments/`.** Its byte copies were deleted. A hand copy has no producer step and would go stale on every rebuild. The export inlines the cross-task images.
- **The root task's `### Constraints` line about `run_all.sh`** now names the graph. That line is planner-owned. I changed it because retiring `run_all.sh` made it false.
- **New check script:** [check_grs.py](../../../showcase-analysis/analysis/check_grs.py), stdlib only.

### The deployed export will show three steps `missing`

`docs/build_site.sh` exits 0. In the local export, opened headless, the Graph view shows 01-data and 02-analysis as `fresh 2`, and the 03-writeup figures load. The deployed site builds from a clean checkout, though, where the gitignored `data/raw/`, `ff_panel.parquet`, and `regression_estimates.parquet` are absent. I simulated this by moving those files aside: status reports `download`, `build-panel`, and `estimate-test-plot` as `missing`, and `check-grs-headline` as `stale`. The Quickstart and reproducibility pages that link to the live export will show this state unless one of these is chosen:

- **Commit the outputs** (about 3.2 MB: 2.9 MB raw, 0.2 MB panel) and drop the matching [.gitignore](../../../showcase-analysis/.gitignore) lines. The deployed export then shows all four steps `fresh`. This reverses the root constraint that raw files stay gitignored.
- **Have CI run `superra repro build` before the export.** This would fetch a newer vintage in CI, so the rendered figures could disagree with the committed Results text. Not recommended.
- **Accept `missing` on the deployed page** and describe it there as the state of a fresh clone.
