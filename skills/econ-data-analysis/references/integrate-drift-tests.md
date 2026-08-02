# Drift Tests for Data-Analysis Results

Load during Protect when preparing drift tests that guard a data analysis's key results.

---

## Identifying Key Results from Task Results

Drift tests protect **headline findings**, not every number. Extract candidates from task `## Results` sections first.

**Strong candidates** (get a test):
- Coefficients and standard errors of the main regression(s) — at minimum sign, magnitude, and significance of the headline coefficient(s)
- Portfolio sort returns, factor premia, or similar aggregated moments appearing in a results table
- Sample statistics defining the study's scope (N observations, N unique units, date range) — they anchor every other number
- Any number the researcher would read aloud when presenting

**Weak candidates** (usually skip):
- Intermediate merge row counts — covered by the describe-analyze-validate audit trail in task files
- Descriptive statistics on raw inputs — upstream, not load-bearing for conclusions
- Sensitivity-analysis numbers — already robustness themselves

## Tolerance Conventions for Econ Results

Set tolerances from **economic reasoning**, not arbitrary thresholds.

- **Point estimates** (coefficients, means, portfolio returns) — allow minor variation from data ordering, floating-point arithmetic, rounding. Typical: 1-5% of estimate magnitude, or a few units in the last reported decimal place.
- **Standard errors** — wider than point estimates; sensitive to small changes in sample composition, clustering, numerical precision. Typical: 5-10% of the standard error.
- **Counts and categoricals** (observations, firms, periods) — exact or near-exact; they change only when sample construction changes. Tolerance: 0 or a very small integer.
- **Signs and significance** — write directional tests ("coefficient is positive", "t-statistic exceeds 1.96") alongside magnitude tests. They catch sign flip and significance loss.

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

Three common causes when a drift test fails after a refactor or merge:

1. **Sort-order drift.** Joins, groupbys, and reshapes do not preserve panel sort order, so any order-dependent downstream operation (lag/lead, cumsum, rank) drifts after an innocent-looking refactor. Fix: re-sort explicitly before every time-series operation (`econ-data-analysis` SKILL.md §Pitfalls, Time-series operations).

2. **Sample-boundary drift.** Filters on derived variables shift the sample when the derivation changes numerically — a `winsorize at p99` cutoff on a slightly different sample keeps or drops a handful of observations. Fix: compute sample-defining cutoffs once, save, reuse; never recompute inside refactors.

3. **Missing-value drift.** `.fillna()` / `coalesce` changes, or a switch from implicit to explicit NA handling, shift means, counts, and correlations with no code looking wrong. Fix: make NA handling explicit at every aggregation (SKILL.md §Pitfalls, Missing data handling).

A failure matching one of these is usually the refactor, not the result — confirm before updating anything. A failure matching none: escalate to the researcher — possibly a real result change warranting a research conversation, not a silent tolerance bump.

---

## Generic Integrity Rules

See `result-protection/references/drift-test-quality.md` §Cross-Cutting Red Flags.
