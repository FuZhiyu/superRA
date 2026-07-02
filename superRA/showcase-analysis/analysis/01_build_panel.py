# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "pyarrow"]
# ///
# %% [markdown]
# # Build the monthly FF panel
#
# Assemble one tidy monthly panel from Ken French's research factors and his
# 25 size x book-to-market portfolios. The output feeds the CAPM-vs-FF3
# regression tasks downstream.
#
# Pipeline: parse each multi-panel CSV (keep only the value-weighted **monthly**
# portfolio panel), merge portfolios onto factors on the month index, build the
# 25 portfolio **excess returns** (`portfolio - RF`), restrict to the baseline
# sample (1963-07 -> latest complete month), and write `data/ff_panel.parquet`.
#
# Returns are kept in **percent per month** as published, so downstream alphas
# come out in percent per month (the asset-pricing convention). Missing codes
# `-99.99` and `-999` are recoded to `NaN`.

# %%
from pathlib import Path

import numpy as np
import pandas as pd

# Resolve paths relative to this script so it runs from any working directory.
DATA = Path(__file__).resolve().parents[1] / "data"
RAW = DATA / "raw"
FACTORS_CSV = RAW / "F-F_Research_Data_Factors.csv"
PORT_CSV = RAW / "25_Portfolios_5x5.csv"
OUT = DATA / "ff_panel.parquet"

BASELINE_START = "1963-07"  # standard B/M test-asset start; pre-1963 BE coverage thin
MISSING_CODES = [-99.99, -999.0]

# %% [markdown]
# ## Parse a single panel out of a multi-panel Ken French CSV
#
# Each CSV stacks several panels (monthly value-weighted, monthly equal-weighted,
# annual variants, firm counts, ...) under text markers. We locate the panel by
# its marker line, take the column header on the next line, then read the
# contiguous block of `YYYYMM,...` monthly rows until the first blank / non-monthly
# line. Keying on the marker text (not hardcoded line numbers) keeps the parser
# correct as Ken French appends new months.

# %%
def parse_ff_panel(path: Path, marker: str | None) -> pd.DataFrame:
    """Return the monthly panel under `marker` (or the first panel if marker is None)."""
    lines = path.read_text().splitlines()

    # Find the data block start: the header row beginning with ',' that follows
    # the marker (or the first such header in the file when marker is None).
    start = None
    if marker is None:
        for i, ln in enumerate(lines):
            if ln.startswith(","):
                start = i
                break
    else:
        for i, ln in enumerate(lines):
            if marker in ln:
                # header is the next non-empty line after the marker
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                start = j
                break
    if start is None:
        raise ValueError(f"Could not locate panel header (marker={marker!r}) in {path}")

    header = [c.strip() for c in lines[start].split(",")]
    header[0] = "date"  # the leading empty label is the YYYYMM index

    rows = []
    for ln in lines[start + 1:]:
        stripped = ln.strip()
        if not stripped:
            break  # blank line terminates the monthly block
        tok = stripped.split(",")[0].strip()
        if not (tok.isdigit() and len(tok) == 6):
            break  # next panel marker / annual rows (YYYY) -> stop
        rows.append([c.strip() for c in ln.split(",")])

    df = pd.DataFrame(rows, columns=header)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m") + pd.offsets.MonthEnd(0)
    for c in df.columns[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.set_index("date").sort_index()
    df = df.replace(MISSING_CODES, np.nan)
    return df


# %% [markdown]
# ## Parse the factor series (first / only monthly panel)
#
# The factors CSV has one monthly panel (`Mkt-RF, SMB, HML, RF`) followed by an
# annual panel. Expect ~1200 monthly rows from 1926-07 to the latest month.

# %%
factors = parse_ff_panel(FACTORS_CSV, marker=None)
print(f"Factors parsed: {factors.shape[0]} months x {factors.shape[1]} cols")
print(f"  columns: {list(factors.columns)}")
print(f"  date range: {factors.index.min():%Y-%m} -> {factors.index.max():%Y-%m}")
print("  missing per column:")
print(factors.isna().sum().to_string())

# %%
# Describe (pre-restriction): factor magnitudes over the full history.
factors.describe(percentiles=[0.01, 0.05, 0.95, 0.99]).round(3)

# %% [markdown]
# ## Parse the 25 portfolios (value-weighted **monthly** panel only)
#
# Keep only the "Average Value Weighted Returns -- Monthly" panel; the equal-
# weighted and annual panels that follow are cut by the marker-keyed parser.
# Expect 25 portfolio columns over the same ~1200-month span.

# %%
PORT_MARKER = "Average Value Weighted Returns -- Monthly"
ports = parse_ff_panel(PORT_CSV, marker=PORT_MARKER)
print(f"Portfolios parsed: {ports.shape[0]} months x {ports.shape[1]} cols")
print(f"  date range: {ports.index.min():%Y-%m} -> {ports.index.max():%Y-%m}")
assert ports.shape[1] == 25, f"expected 25 portfolios, got {ports.shape[1]}"
print(f"  first/last portfolio cols: {ports.columns[0]!r} ... {ports.columns[-1]!r}")
print("  missing per column (full history):")
print(ports.isna().sum().to_string())

# %%
# Describe (pre-restriction): spot-check a few portfolio columns. The corner
# portfolios (small-growth, small-value, big-growth, big-value) are the ones the
# asset-pricing story turns on, so we look at them explicitly.
spot = [ports.columns[0], ports.columns[4], ports.columns[20], ports.columns[24]]
print(f"Spot-check columns: {spot}")
ports[spot].describe(percentiles=[0.01, 0.05, 0.95, 0.99]).round(3)

# %% [markdown]
# ## Merge portfolios onto factors (month index, 1:1)
#
# Both frames are indexed by month-end date with unique months, so this is a
# **1:1 inner join** on the date index. Inner join is intentional: we keep only
# months present in both files (they share the 1926-07 -> latest span, so we
# expect ~0 dropped). Log the row counts on both sides and after.

# %%
assert factors.index.is_unique and ports.index.is_unique, "non-unique month index"
n_fac, n_port = len(factors), len(ports)
panel = factors.join(ports, how="inner")
print(f"Merge (1:1 inner on month): factors {n_fac} x portfolios {n_port} -> {len(panel)} rows")
print(f"  factor months not matched:    {n_fac - len(panel)}")
print(f"  portfolio months not matched: {n_port - len(panel)}")
print(f"  merged date range: {panel.index.min():%Y-%m} -> {panel.index.max():%Y-%m}")

# %% [markdown]
# ## Construct the 25 excess returns: `portfolio - RF`
#
# Every portfolio return is converted to an excess return by subtracting the
# risk-free rate `RF`. The factor series (`Mkt-RF`, `SMB`, `HML`) are already
# excess / long-short returns and are kept as published. We keep the raw `RF` and
# the four factor columns alongside the 25 excess-return series.

# %%
PORT_COLS = list(ports.columns)
FACTOR_COLS = ["Mkt-RF", "SMB", "HML", "RF"]
excess = panel[PORT_COLS].sub(panel["RF"], axis=0)
excess.columns = [f"{c} (xs)" for c in PORT_COLS]
panel_xs = pd.concat([panel[FACTOR_COLS], excess], axis=1)
print(f"Constructed excess returns for {len(PORT_COLS)} portfolios.")
print(f"Panel columns: {len(panel_xs.columns)} ({len(FACTOR_COLS)} factors/RF + {len(PORT_COLS)} excess)")

# Spot-check the construction by hand on the first available month.
chk_date = panel.index[0]
chk_port = PORT_COLS[0]
raw_val = panel.loc[chk_date, chk_port]
rf_val = panel.loc[chk_date, "RF"]
xs_val = panel_xs.loc[chk_date, f"{chk_port} (xs)"]
print(f"Spot-check {chk_date:%Y-%m} {chk_port!r}: {raw_val:.4f} - RF {rf_val:.4f} = {xs_val:.4f}")
assert np.isclose(xs_val, raw_val - rf_val), "excess-return construction mismatch"

# %% [markdown]
# ## Restrict to the baseline sample (1963-07 -> latest complete month)
#
# 1963-07 is the standard start for book-to-market test assets. The latest month
# is whatever the file ends on (the most recent complete month). Log the row
# count before and after the restriction.

# %%
n_before = len(panel_xs)
panel_base = panel_xs.loc[BASELINE_START:].copy()
print(f"Sample restriction (>= {BASELINE_START}): {n_before} -> {len(panel_base)} rows")
print(f"  baseline range: {panel_base.index.min():%Y-%m} -> {panel_base.index.max():%Y-%m}")

# %% [markdown]
# ## Describe (post-restriction) and validate
#
# Re-run describe on the baseline sample. Checks:
# - **No within-sample month gaps** (required before any downstream lag/diff).
# - **Factor magnitudes** match published Ken French scales (market premium on
#   the order of ~0.5%/month).
# - **25 excess-return series jointly non-missing** over the baseline sample.

# %%
# Gap check: the month-end index must be a contiguous monthly grid.
full_grid = pd.date_range(panel_base.index.min(), panel_base.index.max(), freq="ME")
missing_months = full_grid.difference(panel_base.index)
print(f"Baseline months: {len(panel_base)}; contiguous-grid months: {len(full_grid)}")
print(f"Within-sample month gaps: {len(missing_months)}")
assert len(missing_months) == 0, f"month gaps present: {list(missing_months)}"

# %%
# Missingness over the baseline sample, per series.
miss = panel_base.isna().sum()
print("Missing values per series (baseline):")
print(miss[miss > 0].to_string() if (miss > 0).any() else "  none — all series fully observed")

# %%
# Factor summary stats over the baseline sample.
factor_summary = panel_base[FACTOR_COLS].describe(percentiles=[0.01, 0.05, 0.95, 0.99]).round(3)
print("Factor summary (percent/month, baseline 1963-07 onward):")
factor_summary

# %%
# Validation: published-magnitude sanity check on the factor means.
mkt_mean = panel_base["Mkt-RF"].mean()
print(f"Mean Mkt-RF (market risk premium): {mkt_mean:.3f}% / month  [expect ~0.4-0.6]")
print(f"Mean SMB:                          {panel_base['SMB'].mean():.3f}% / month")
print(f"Mean HML:                          {panel_base['HML'].mean():.3f}% / month")
print(f"Mean RF:                           {panel_base['RF'].mean():.3f}% / month")
print(f"Std Mkt-RF:                        {panel_base['Mkt-RF'].std():.3f}% / month  [expect ~4.5]")
assert 0.3 < mkt_mean < 0.8, f"market premium {mkt_mean:.3f} off published scale"

# %%
# Validation: the 25 excess-return series are jointly non-missing over baseline.
xs_cols = [c for c in panel_base.columns if c.endswith("(xs)")]
xs_complete = panel_base[xs_cols].notna().all(axis=1)
print(f"Excess-return columns: {len(xs_cols)}")
print(f"Months with all 25 excess returns present: {xs_complete.sum()} / {len(panel_base)}")
assert xs_complete.all(), "some baseline months have missing excess returns"

# %%
# Spot-check excess-return magnitudes on the corner portfolios.
xs_corners = [c for c in xs_cols if any(k in c for k in
              ["SMALL LoBM", "SMALL HiBM", "BIG LoBM", "BIG HiBM"])]
print("Corner excess-return means (percent/month, baseline):")
panel_base[xs_corners].mean().round(3).to_frame("mean %/mo")

# %% [markdown]
# ## Write the panel
#
# One row per month; columns = four factor/RF series + 25 excess-return series.

# %%
OUT.parent.mkdir(parents=True, exist_ok=True)
panel_base.to_parquet(OUT)
print(f"Wrote {OUT} : {panel_base.shape[0]} months x {panel_base.shape[1]} columns")
print(f"  range: {panel_base.index.min():%Y-%m} -> {panel_base.index.max():%Y-%m}")
