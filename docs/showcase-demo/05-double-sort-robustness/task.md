---
title: "Size x Momentum Double-Sort Robustness"
status: in-progress
depends_on: 
  - 03-size-sort-returns
  - 04-momentum-sort-returns

tags: []
created: 2026-06-11
---

## Objective

Check that the size and momentum premia are not the same effect in disguise. Independently double-sort firms into a 3 (size) × 3 (momentum) grid each month, form value-weighted portfolios in the nine cells, and report the average return surface. The size premium should survive within momentum terciles, and the momentum premium should survive within size terciles. Report the within-tercile spreads.

## Results

Work in progress — the size dimension is estimated; the momentum dimension is blocked on the upstream re-estimate.

The size premium survives within each momentum tercile: holding momentum fixed, the small-tercile portfolio out-earns the large-tercile portfolio by 0.22%–0.29% per month across the three momentum bins. This is consistent with `03-size-sort-returns` and confirms the size effect is not a momentum artifact.

The momentum dimension of the surface is **not yet final**: it depends on `04-momentum-sort-returns`, which is in `revise` because its spread was estimated on the wrong weighting scheme. Re-running the within-size momentum spreads against the corrected value-weighted portfolios is the remaining step before this task can move to review.
