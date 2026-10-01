---
title: "Register the Showcase Study's Reproduction Graph"
status: implemented
depends_on: []
---

## Objective

Register [showcase-analysis](../../../showcase-analysis/task.md) in the reproduction graph so every retained output rebuilds through `superra repro build showcase-analysis`, and retire `run_all.sh`.

- **One step per analysis script,** each declared in the `## Reproduction` of the task that owns it: `analysis/01_build_panel.py` (01-data), `analysis/02_analysis.py` (02-analysis). Scripts keep their behavior; edit them only where the graph cannot describe them.
- **Add one `kind: check` step** that guards a headline result (e.g., the GRS statistics in `data/grs_results.csv`), so the export shows a check alongside builds.
- **The showcase data is frozen and committed.** The two raw Ken French CSVs (the 202608 release) are a committed external input; `download.py` stays as an unregistered refresh helper, and its zips are not kept. The panel and estimates parquet files are committed too, so a clean checkout — and the deployed docs export — reads every step `fresh` and the recorded numbers never move without a deliberate data refresh.
- `superra repro status showcase-analysis` shows every step `fresh` after a real build; commit `repro-lock.json`.
- `superRA/showcase-analysis` task `## Results

The showcase study rebuilds through three registered steps from a committed, frozen copy of the Ken French data, and `run_all.sh` is gone. All three steps are `fresh` in the committed [repro-lock.json](../../../../repro-lock.json), on this checkout and on a clean clone.

### The graph

| Step | Task | Reads | Writes |
|---|---|---|---|
| [build-panel](../../../showcase-analysis/01-data/task.md#step-build-panel) | 01-data | the two raw CSVs (external input) | `data/ff_panel.parquet` |
| [estimate-test-plot](../../../showcase-analysis/02-analysis/task.md#step-estimate-test-plot) | 02-analysis | the panel | `data/regression_estimates.parquet`, [grs_results.csv](../../../showcase-analysis/data/grs_results.csv), the four figures in `02-analysis/attachments/` |
| [check-grs-headline](../../../showcase-analysis/02-analysis/task.md#step-check-grs-headline) (`kind: check`) | 02-analysis | `grs_results.csv` | — |

- **Evidence.** `superra repro build showcase-analysis --force` ran all three steps and none was accepted. The selection covers the whole chain, so it has no saved inputs; its one external input is the two committed CSVs. The rebuilt parquets, `grs_results.csv`, and PNGs matched the committed bytes. `superra repro status showcase-analysis --upstream` reports 3 `fresh`, `superra task check` is clean, and the check step passed: both models are rejected at 1%, FF3's GRS is below CAPM's, and FF3's mean |α| is 0.44 of CAPM's.
- **One runner.** [superRA/config.yaml](../../../config.yaml) adds `runners: uv: uv run --script {script}`, and every step uses it. Script dependencies are unpinned PEP 723 lists, so a rerun on a machine with newer packages can change output bytes, such as the matplotlib version stamped in each PNG.

### The data is frozen at the 202608 release

The raw CSVs ([F-F_Research_Data_Factors.csv](../../../showcase-analysis/data/raw/F-F_Research_Data_Factors.csv), [25_Portfolios_5x5.csv](../../../showcase-analysis/data/raw/25_Portfolios_5x5.csv), 2.4 MB together), the panel, and the estimates parquet are committed. Only the download zips stay gitignored, in the narrowed [.gitignore](../../../showcase-analysis/.gitignore).

- **`download.py` is an unregistered refresh helper.** Running it replaces the CSVs with the current release and stales every step. Its docstring now says so.
- **Freezing is the only way to keep the numbers.** The Ken French library serves only the current release and revises past months: cutting the 202608 release at 2026-04 gives CAPM GRS 4.099, against 4.104 from the 202604 release.

### The 202608 release moved the showcase numbers

The 202604 files behind the earlier numbers no longer exist, so the first build used the 202608 release.

| | Old (202604 release) | New (202608 release) |
|---|---|---|
| Sample | 754 months, 1963-07 → 2026-04 | 758 months, 1963-07 → 2026-08 |
| CAPM GRS | $F(25,728)=4.10$ | $F(25,732)=4.20$ |
| FF3 GRS | $F(25,726)=3.55$ | $F(25,730)=3.64$ |
| mean \|α\| CAPM → FF3 (%/mo) | 0.195 → 0.089 | 0.197 → 0.087 |
| `SMALL LoBM` FF3 α | −0.472, $t=-5.1$ | −0.465, $t=-5.1$ |

Both models are still rejected, FF3 still halves the mean |α|, and the loading gradients and sign guards still hold. Each number in the `## Results` of [showcase-analysis](../../../showcase-analysis/task.md), [01-data](../../../showcase-analysis/01-data/task.md), [02-analysis](../../../showcase-analysis/02-analysis/task.md), and [03-writeup](../../../showcase-analysis/03-writeup/task.md) comes from the build logs. Each of those sections cites the steps in place of `run_all.sh`.

### Changes beyond the step declarations

- **[02_analysis.py](../../../showcase-analysis/analysis/02_analysis.py): fig3's title had `1963-07 -> 2026-04` hardcoded.** The title now takes the panel's own date range, and a header comment no longer states the panel length. No other script changed behavior.
- **03-writeup embeds its two figures from `../02-analysis/attachments/`.** Its byte copies were deleted. A hand copy has no producer step and would go stale on every rebuild. The export inlines the cross-task images.
- **The root task's `### Context` data-inventory line and two `### Constraints` lines** now describe the committed data and the graph. Those lines are planner-owned. I changed them because the old text said `run_all.sh` and gitignored raw files.
- **The 01-data `## Objective` still says gitignored `data/raw/` and panel.** I left it because it records the original task.
- **New check script:** [check_grs.py](../../../showcase-analysis/analysis/check_grs.py), stdlib only.

### The export reads every step fresh from a clean checkout

I cloned the commit into a scratch directory, with no `.superra-repro/` and no untracked files. `superra repro status showcase-analysis` reports 3 `fresh` there. `docs/build_site.sh` exits 0 in the clone. Its `showcase-analysis-tree.html`, opened headless, shows 01-data as `fresh 1` and 02-analysis as `fresh 2` in the Graph view, and the 03-writeup figures load.
