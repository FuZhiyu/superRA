---
title: "Construct Size and Momentum Sorting Variables"
status: approved
depends_on: 
  - 01-simulate-data

tags: []
created: 2026-06-11
---

## Objective

From the simulated panel, construct the two firm-month sorting variables the portfolio sorts will use:

- **Size:** log market capitalization at the end of month $t-1$.
- **Momentum:** the cumulative simple return from month $t-12$ to month $t-2$, skipping the most recent month $t-1$ to avoid the short-term reversal effect.

Each firm-month gets a size decile and a momentum decile, assigned cross-sectionally within each month. Drop the first 12 months, which have no momentum history. Write the augmented panel to `data/panel_factors.parquet`.

## Results

The augmented panel is at `data/panel_factors.parquet`: 114,000 firm-month rows survive after dropping the 12-month momentum burn-in (500 firms x 228 months). Each row carries `size_decile` and `mom_decile`, both integers 1–10, assigned within-month.

Two construction choices that matter, both verified against the panel:

- **The momentum window skips month $t-1$.** Including the most recent month contaminates momentum with short-term reversal; the $t-12$ to $t-2$ window is the standard convention. The per-firm return correlation between the skipped month and the momentum signal is near zero by construction, confirming the skip.
- **Deciles are within-month, not pooled.** Sorting cross-sectionally each month keeps the portfolios balanced (≈50 firms per decile per month) even as the overall return level drifts. A pooled sort would let high-volatility months dominate the extreme deciles.

| Decile | Mean log mktcap | Mean momentum (%) | Firm-months |
|---:|---:|---:|---:|
| 1 (small / loser) | 4.21 | -18.3 | 11,400 |
| 5 | 6.05 | -0.4 | 11,400 |
| 10 (large / winner) | 8.11 | 21.6 | 11,400 |

The monotone decile means confirm the sort separates firms as intended.

## Review Notes

> 1. [MAJOR] Momentum was computed over $t-12$ to $t-1$, including the most recent month. ([data/factors.py:27](data/factors.py#L27))
>    → implemented: shifted the window to $t-12$ to $t-2$ so month $t-1$ is skipped, per the project convention ([data/factors.py:27](data/factors.py#L27))

APPROVED — both sorting variables match the conventions; decile means are monotone and balanced.
