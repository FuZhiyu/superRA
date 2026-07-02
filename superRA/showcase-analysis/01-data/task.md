---
title: "Download and Build the Monthly Panel"
status: approved
depends_on: []
tags: []
script: analysis/01_build_panel.py
input: Ken French CSVs (downloaded by data/download.py)
output: data/ff_panel.parquet
created: 2026-06-17
---

## Objective

Acquire the source data and assemble a single tidy monthly panel that the regression tasks consume.

- **Download** the two Ken French zip files with a committed `data/download.py` (PEP 723, `uv run --script`): the research factors and the 25 size-B/M 5×5 portfolios. Extract the CSVs into a gitignored `data/raw/`.
- **Parse** each multi-panel CSV: strip the multi-line text header, keep only the value-weighted **monthly** portfolio panel (cut the equal-weighted and annual panels that follow it), parse the `YYYYMM` index into a month-end date, recode `-99.99` and `-999` to missing, and keep returns in percent.
- **Merge** the 25 portfolios with the factor series on the month index (declare the join type and verify it). Construct the 25 portfolio **excess returns** by subtracting `RF`.
- **Restrict** to the baseline sample (1963-07 → latest complete month).
- Write the result to `data/ff_panel.parquet` (gitignored): one row per month, columns for the four factors, `RF`, and the 25 excess-return series.

Apply the Describe gate before and after each transformation: report the panel shape (months × series), the date range, missingness per series, and summary statistics (mean, std, tail percentiles) for the factors and a spot-check of portfolio columns. Log row/column counts at the parse, merge, and sample-restriction steps. Confirm there are no within-sample month gaps before any downstream time-series use.

**Validation:** factor means and volatilities should match published Ken French magnitudes (e.g. the market risk premium averages on the order of 0.5% per month); the 25 excess-return series should be jointly non-missing over the baseline sample. Flag any divergence before marking done.

## Results

Built the baseline monthly panel end-to-end from public Ken French data. The full pipeline ([../run_all.sh](../run_all.sh), `set -euo pipefail`) runs download → build with no manual steps. Re-running `bash superRA/showcase-analysis/run_all.sh` reproduces every output.

**Scripts (committed):**
- [../data/download.py](../data/download.py) — downloads `F-F_Research_Data_Factors_CSV.zip` and `25_Portfolios_5x5_CSV.zip` from the [Ken French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) and extracts the CSVs into `data/raw/`.
- [../analysis/01_build_panel.py](../analysis/01_build_panel.py) — parses, merges, constructs excess returns, restricts the sample, and writes the panel. Jupytext percent format.

**Gitignored (rebuilt on demand):** `data/raw/` (zips + CSVs) and `data/ff_panel.parquet`, via [../.gitignore](../.gitignore).

### Output panel

`data/ff_panel.parquet`: **754 months × 29 columns**, indexed by month-end `date` over **1963-07 → 2026-04**. Columns: `Mkt-RF, SMB, HML, RF` (percent/month, as published) plus 25 portfolio **excess-return** series named `… (xs)` (portfolio return − `RF`). The source file was created from the `202604` CRSP database, so the latest complete month is April 2026.

### Parse, merge, restrict — row/column logging

The marker-keyed parser locates the value-weighted **monthly** panel by its header text (not hardcoded line numbers), reads the contiguous `YYYYMM` block, and stops at the first blank/non-monthly line — so the equal-weighted and annual panels that follow are cut, and the parser stays correct as new months are appended.

| Step | Result |
|---|---|
| Parse factors | 1198 months × 4 cols, 1926-07 → 2026-04, 0 missing |
| Parse 25 portfolios (VW-monthly only) | 1198 months × 25 cols, `SMALL LoBM … BIG HiBM`, 0 missing on full history |
| Merge (1:1 inner on month index) | 1198 × 1198 → **1198** rows; 0 unmatched on either side |
| Construct 25 excess returns | `portfolio − RF`; spot-check 1926-07 `SMALL LoBM`: 5.8276 − 0.22 = 5.6076 ✓ |
| Restrict to baseline (≥ 1963-07) | 1198 → **754** rows |

The merge is a 1:1 inner join on a unique month-end index; inner is intentional (keep only months in both files) and drops nothing because the two files share the same span. Missing codes `-99.99` / `-999` are recoded to `NaN` at parse; none appear over the full history of either file.

### Describe / validate (baseline sample)

**No within-sample month gaps** — the 754 baseline months form a contiguous monthly grid (754 grid months, 0 gaps), so downstream lag/diff operations are safe. **No missing values** in any of the 29 series over the baseline; all 25 excess-return series are jointly present in every one of the 754 months.

Factor magnitudes match published Ken French scales:

| Series (%/mo) | Mean | Std |
|---|---:|---:|
| Mkt-RF | 0.597 | 4.466 |
| SMB | 0.148 | — |
| HML | 0.296 | — |
| RF | 0.363 | — |

The market risk premium (0.597%/mo) and market volatility (4.47%/mo) sit squarely on the published modern-sample magnitudes (premium ~0.4–0.6%/mo, σ ~4.5%/mo); SMB and HML are both positive at the expected single-digit-tenths scale. An assertion in the script fails fast if the market premium leaves the 0.3–0.8 band.

Corner excess-return means (%/mo) preview the size/value spread the study turns on:

| Corner | Mean (%/mo) |
|---|---:|
| `SMALL LoBM` (small-growth) | 0.317 |
| `SMALL HiBM` (small-value) | 1.109 |
| `BIG LoBM` (big-growth) | 0.615 |
| `BIG HiBM` (big-value) | 0.767 |

Small-growth is the weakest corner and small-value the strongest — the classic value premium within small caps, consistent with the expected-results benchmark in the root task. (Factor *loading* signs are an 02-analysis check; here the raw means already line up.)

No divergences from published magnitudes or expected structure; nothing to flag.
