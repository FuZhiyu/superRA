# Drift Tests for Data-Analysis Results

Load at the **INTEGRATE phase** when preparing drift tests that guard a data analysis's key results before it is merged. `integration-workflow` Stage 1 invokes this reference alongside the quality checklist.

This reference answers the data-analysis-specific questions:

1. **What should a drift test for this analysis actually protect?**
2. **What are the conventions for setting tolerances on econ / panel-data results?**
3. **How do I pull candidate invariants out of `RESULTS.md`?**

For the implementation-level quality checklist (coverage, independence, clarity, robustness, test format, cross-cutting integrity Red Flags), load `skills/refactor-and-integrate/references/drift-test-quality.md`. This file and that checklist are both read at drift-test creation and at drift-test review.

---

## Why Drift Tests Are Part of Data-Analysis Discipline

Econ results are fragile. A coefficient can drift because floating-point sums reorder after a merge, a winsorization cutoff is recomputed on a slightly different sample, a join key is cleaned more aggressively, or an unrelated refactor changes the order a panel is sorted in. None of these are "bugs" per se, and most review steps will not catch them. Drift tests catch them, and they catch the worst failure mode — silent result drift that looks like it was always that way.

The Iron Law protects the analysis from unknown data during implementation. Drift tests protect the finalized analysis from unknown transformations (refactors, merges, future edits) after implementation is complete. They are the integration-phase analogue.

Drift tests are not a substitute for the two-stage review or the describe-analyze-doc cycle. They are a safety net that guards the specific numbers the researcher has chosen as the headline results.

---

## Identifying Key Results from `RESULTS.md`

Drift tests should protect **headline findings**, not every number in the analysis. Before writing tests, read `RESULTS.md` and extract candidates:

**Strong candidates** (should get a test):
- Coefficients and standard errors of the main regression(s) — at minimum the sign, magnitude, and significance of the headline coefficient(s)
- Portfolio sort returns, factor premia, or similar aggregated moments that appear in a results table
- Sample statistics that define the study's scope (N observations, N unique units, date range) — these anchor every other number
- Any number the researcher would read aloud when presenting the analysis

**Weak candidates** (probably skip):
- Intermediate merge row counts (covered by the describe-analyze-doc audit trail in PLAN.md / RESULTS.md)
- Descriptive statistics on raw inputs (upstream, not load-bearing for conclusions)
- Sensitivity-analysis numbers (these are already robustness themselves — testing a robustness check against itself adds little)

**Always ask the researcher to confirm the candidate list** before writing tests. Drift-test coverage is a researcher-owned decision because it encodes what counts as a "key result." `integration-workflow` Stage 1 Step 2 bakes this question into the workflow via `AskUserQuestion`.

---

## Tolerance Conventions for Econ Results

Set tolerances based on **economic reasoning**, not arbitrary thresholds. Summary (full rubric in `refactor-and-integrate/references/drift-test-quality.md`):

| Result type | Typical tolerance | Rationale |
|---|---|---|
| Point estimates (coefficients, portfolio returns, means) | 1–5% of estimate magnitude, or a few units in the last decimal | Allows FP reordering and merge-order variation, catches meaningful coefficient drift |
| Standard errors | 5–10% of SE | SEs are more sensitive to clustering and sample composition than point estimates |
| Counts (N obs, N firms, N periods) | 0 or very small integer | Should not change unless sample construction changes |
| Signs and significance | Exact (directional) | Sign flip or loss of significance is the failure mode drift tests most need to catch |

**Document every tolerance choice** with a one-line comment explaining the rationale in economic terms, not just a number. A drift test with an unexplained tolerance is easy to silently loosen later, defeating the purpose.

---

## Data-Analysis-Specific Failure Modes

When a drift test fails after a refactor or merge, the three common causes in econ code are:

1. **Sort-order drift.** Joins, groupbys, and reshapes do not preserve panel sort order. If a downstream operation depends on order (lag/lead, cumsum, rank), the coefficient will drift after an innocent-looking refactor. Fix: re-sort explicitly before every time-series operation; the main `econ-data-analysis` SKILL.md covers this in Pitfalls § Time-series operations.

2. **Sample-boundary drift.** Filters that depend on derived variables can shift the sample if the derivation changes numerically. A `winsorize at p99` cutoff computed on a very slightly different sample passes or rejects a handful of observations. Fix: compute sample-defining cutoffs once, save, and reuse — do not recompute inside refactors.

3. **Missing-value drift.** `.fillna()` / `coalesce` changes, or a switch from implicit to explicit NA handling, can shift means, counts, and correlations without any code looking wrong. Fix: make NA handling explicit at every aggregation; the main SKILL.md covers this in Pitfalls § Missing data handling.

If a failure matches one of these, the test is almost certainly correct and the refactor is almost certainly the cause. If a failure does not match any of these, escalate to the researcher — it may be a real result change that warrants a research conversation, not a silent tolerance bump.

---

## Cross-Cutting Integrity Rules

The Red Flags that protect drift-test integrity during creation, refactor, merge, and semantic-merge live in `refactor-and-integrate/references/drift-test-quality.md` §Drift Test Integrity — Cross-Cutting Red Flags. They apply wherever drift tests are in play. Do not restate them here; load that section and follow it.
