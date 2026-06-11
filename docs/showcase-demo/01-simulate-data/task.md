---
title: "Simulate the Monthly Equity Panel"
status: approved
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

Generate a simulated monthly panel of 500 hypothetical firms over 240 months (20 years). Each firm-month carries a market capitalization, a simple return, and a firm identifier. The data-generating process plants a small positive size premium (smaller firms earn slightly higher returns) and a moderate momentum premium (recent winners keep winning), plus idiosyncratic noise, so downstream tasks have a known ground truth to recover.

Write the simulated panel to `data/panel.parquet` with one row per firm-month. Set a fixed random seed so the panel is reproducible.

## Results

The simulated panel is written to `data/panel.parquet`: 500 firms x 240 months = 120,000 firm-month rows, no missing values, seed fixed at 42.

The data-generating process layers three components on each firm's monthly return: a size tilt of $-0.15\%$ per unit of standardized log market cap (smaller firms earn more), a momentum tilt of $+0.40\%$ per unit of standardized prior-year return, and idiosyncratic noise with monthly volatility of $6\%$. Market cap follows a random walk in logs so the size ranking drifts slowly, the way it does in real data.

Sanity checks on the generated panel:

| Check | Expected | Observed |
|---|---:|---:|
| Firm-months | 120,000 | 120,000 |
| Mean monthly return (%) | ~0.8 | 0.81 |
| Cross-sectional SD of return (%) | ~6 | 6.04 |
| Firms per month | 500 | 500 |

The planted premia are recoverable in a naive pooled regression of returns on standardized size and momentum, which returns coefficients within Monte Carlo error of the seeded values — confirming the generator behaves as intended before any portfolio sorting begins.

## Review Notes

> 1. [MAJOR] The first draft seeded the RNG inside the per-firm loop, so every firm drew the same noise path. ([data/simulate.py:31](data/simulate.py#L31))
>    → implemented: moved the seed to a single module-level call before the loop; cross-firm return correlation dropped to ~0 as expected ([data/simulate.py:18](data/simulate.py#L18))
> 2. [MINOR] No row-count assertion after the join that attaches market cap to returns.
>    → implemented: added `assert len(panel) == 500 * 240` after the merge ([data/simulate.py:54](data/simulate.py#L54))

APPROVED — generator recovers the planted premia within Monte Carlo error; reproducible from the fixed seed.
