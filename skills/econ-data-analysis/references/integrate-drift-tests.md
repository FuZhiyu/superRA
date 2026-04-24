# Drift Tests for Data-Analysis Results

Load at the **INTEGRATE phase** when preparing drift tests that guard a data analysis's key results.

Answers the data-analysis-specific questions: what should a drift test protect, how to set econ tolerances, and how to pull candidate invariants out of `RESULTS.md`.

For the implementation-level quality checklist (coverage, independence, clarity, robustness, test format, cross-cutting integrity Red Flags), also load `skills/refactor-and-integrate/references/drift-test-quality.md`.

---

## Why Drift Tests Are Part of Data-Analysis Discipline

Econ results are fragile. A coefficient can drift because floating-point sums reorder after a merge, a winsorization cutoff is recomputed on a slightly different sample, a join key is cleaned more aggressively, or an unrelated refactor changes the order a panel is sorted in. None of these are "bugs" per se, and most review steps will not catch them. Drift tests catch them, and they catch the worst failure mode — silent result drift that looks like it was always that way.

The Iron Law protects the analysis from unknown data during implementation. Drift tests protect the finalized analysis from unknown transformations (refactors, merges, future edits) after implementation is complete. They are the integration-phase analogue.

Drift tests are not a substitute for the one-pass review or the describe-analyze-validate discipline. They are a safety net that guards the specific numbers the researcher has chosen as the headline results.

---

## Identifying Key Results from `RESULTS.md`

Drift tests should protect **headline findings**, not every number in the analysis. Before writing tests, read `RESULTS.md` and extract candidates:

**Strong candidates** (should get a test):
- Coefficients and standard errors of the main regression(s) — at minimum the sign, magnitude, and significance of the headline coefficient(s)
- Portfolio sort returns, factor premia, or similar aggregated moments that appear in a results table
- Sample statistics that define the study's scope (N observations, N unique units, date range) — these anchor every other number
- Any number the researcher would read aloud when presenting the analysis

**Weak candidates** (probably skip):
- Intermediate merge row counts (covered by the describe-analyze-validate audit trail in PLAN.md / RESULTS.md)
- Descriptive statistics on raw inputs (upstream, not load-bearing for conclusions)
- Sensitivity-analysis numbers (these are already robustness themselves — testing a robustness check against itself adds little)

**Always ask the researcher to confirm the candidate list** before writing tests. Drift-test coverage is a researcher-owned decision because it encodes what counts as a "key result." `integration-workflow` Phase A Step 2 bakes this question into the workflow via `AskUserQuestion`.

---

## Tolerance Conventions for Econ Results

Set tolerances based on **economic reasoning**, not arbitrary thresholds.

**Point estimates** (coefficients, means, portfolio returns):
- Allow minor variation from data ordering, floating-point arithmetic, rounding.
- Typical tolerance: 1-5% of estimate magnitude, or a few units in the last reported decimal place.

**Standard errors:**
- Wider tolerance than point estimates — sensitive to small changes in sample composition, clustering, numerical precision.
- Typical tolerance: 5-10% of the standard error.

**Counts and categoricals** (observations, firms, periods):
- Exact or near-exact — should not change unless sample construction changes.
- Tolerance: 0 or very small integer.

**Signs and significance:**
- Write directional tests ("coefficient is positive", "t-statistic exceeds 1.96") in addition to magnitude tests.
- These catch the most important drift — sign flip or significance loss.

**Too tight** → false positives on harmless changes (merge order, floating-point platform differences).
**Too loose** → misses real drift. Use economic judgment.

**Document every tolerance choice** with a comment explaining why:
```
# Coefficient on market_cap: 0.035 +/- 0.002
# Tolerance: ~5% of estimate. Allows for floating-point variation
# in OLS solver but catches meaningful coefficient drift.
```

---

## Data-Analysis-Specific Failure Modes

When a drift test fails after a refactor or merge, the three common causes in econ code are:

1. **Sort-order drift.** Joins, groupbys, and reshapes do not preserve panel sort order. If a downstream operation depends on order (lag/lead, cumsum, rank), the coefficient will drift after an innocent-looking refactor. Fix: re-sort explicitly before every time-series operation; the main `econ-data-analysis` SKILL.md covers this in Pitfalls § Time-series operations.

2. **Sample-boundary drift.** Filters that depend on derived variables can shift the sample if the derivation changes numerically. A `winsorize at p99` cutoff computed on a very slightly different sample passes or rejects a handful of observations. Fix: compute sample-defining cutoffs once, save, and reuse — do not recompute inside refactors.

3. **Missing-value drift.** `.fillna()` / `coalesce` changes, or a switch from implicit to explicit NA handling, can shift means, counts, and correlations without any code looking wrong. Fix: make NA handling explicit at every aggregation; the main SKILL.md covers this in Pitfalls § Missing data handling.

If a failure matches one of these, the test is almost certainly correct and the refactor is almost certainly the cause. If a failure does not match any of these, escalate to the researcher — it may be a real result change that warrants a research conversation, not a silent tolerance bump.

---

## Cross-Cutting Integrity Rules

See `refactor-and-integrate/references/drift-test-quality.md` §Cross-cutting Red Flags — drift test integrity.
