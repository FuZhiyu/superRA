---
title: "Download and Build the Monthly Panel"
status: not-started
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

*(filled during implementation)*
