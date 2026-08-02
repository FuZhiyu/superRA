---
name: econ-data-analysis
description: Economic data-analysis discipline. Use for importing, cleaning, merging, filtering, variables, aggregation, summary stats, regressions, or figures on economic, financial, or panel data.
user-invocable: true
---

# Economic Data Analysis

Domain skill for rigorous economic data work; body carries §Three Concurrent Disciplines, §Pitfalls, §Common Rationalizations.

## Stage-Scoped References

Load per stage; do not load them all at every dispatch:

| Reference | Load when |
|---|---|
| `references/planning.md` | PLAN phase — Data Inventory hard gate and Sensitivity Analysis Design. |
| `references/data-robustness-checklist.md` | PLAN (design) and IMPLEMENT (execution of sensitivity tasks) — menu of robustness checks. |
| `references/integrate-drift-tests.md` | protection stage — data-analysis key-result identification, econ-specific tolerances, data-analysis failure modes for drift/regression tests. |
| `references/integration.md` | INTEGRATE stage — data-specific refactor-integrity gates. |
| `references/notebook-format.md` | IMPLEMENT stage (for implementer) — cell organization, narrative, output idioms, Python jupytext / Julia Quarto rendering. Companions: `jupytext-guide.md`, `julia-quarto-guide.md`. |

## The Iron Law

```
NO TRANSFORMATION WITHOUT PRIOR DESCRIPTION
```

Transformed data without describing it first? Undo the transformation and describe fresh from the current data state — not from a previous session, not "later at the end." (The excuses that precede this violation are catalogued in §Common Rationalizations.)

---

## Three Concurrent Disciplines: Describe–Analyze–Validate

Three disciplines underpin rigorous data work. They are **concurrent, not sequential** — every analysis step exercises all three. Documentation runs continuously alongside them, not as a fourth phase.

Shared checklist for the implementer (before DONE) and the reviewer (within its focus). Items apply to every analysis task; operation-conditional items live in §Pitfalls, walked only when the task performs the operation.

- `[BLOCKING]` — must fix to earn APPROVE.
- `[ADVISORY]` — recorded; never blocks APPROVE.

**The committed diagnostics, row-count logs, and output files are the evidence in data work.** A missing diagnostic is a finding, not a prompt to generate it yourself. When fixing, re-run the changed step and its downstream dependents; unaffected upstream outputs stand as committed.

### Describe

The most common analytical error is transforming data you do not understand. Describe thoroughly and often — both before and after every transformation. Post-transformation describe is not a separate phase; it is the same discipline applied a second time, now as a validation tool fed into Sanity checks (below).

**After loading any dataset:**

- `[BLOCKING]` Every input described before the first transformation on it.
- `[BLOCKING]` **Panel structure** (first priority for panel/longitudinal data — the common case): panel ID (firm, fund, country, individual) and time ID (year, quarter, month, day) identified; unique IDs and unique time periods counted and verified against expectations; date range (min, max) noted; balancedness characterized — periods-per-unit distribution (mean, median, min, max) and balanced ratio (actual rows / N_ids × T_periods). If unbalanced, pattern characterized (entry/exit, mid-panel gaps, expanding coverage). For pure cross-sections, note it and skip panel diagnostics.
- `[BLOCKING]` **Variable diagnostics** on key variables — do NOT blanket-`describe()` all columns:
  - Continuous (returns, prices, GDP, weights): mean, median, std, min, max, and tail percentiles (p1, p5, p95, p99) — tails detect outliers.
  - Categorical/binary (sector codes, indicators, country): value counts and shares; check unexpected categories or near-zero frequencies.
  - Identifiers: panel ID × time uniquely identifies rows; check duplicates.
- `[BLOCKING]` **Data types and missing values**: column types correct (dates as dates, numerics as numerics, not object/string); missing values counted and share per variable; missingness pattern (random vs systematic) — interpretation in §Validate §Missing-data as signal.

When data was already imported and validated upstream, read existing diagnostics rather than re-running full validation.

**Outlier flagging:**

- `[BLOCKING]` Observations beyond p1/p99 flagged and assessed — data errors vs genuine extremes. For naturally skewed variables (firm size, wealth, trade volumes), extremes may be real. Decision to keep, winsorize, or trim documented.
- `[ADVISORY]` If winsorizing, cutoff documented; robustness with alternatives considered (see `references/data-robustness-checklist.md`).

**After every major transformation (re-describe):**

- `[BLOCKING]` Descriptive statistics re-run on affected variables after merges, filters, variable construction, aggregations, reshaping, deduplication, and compared against the pre-transformation values. An unexplained distribution shift is silent corruption; nothing downstream uses the variable until the shift is understood.

**Visualization for key variables:**

- `[ADVISORY]` Plot what summary statistics hide: histograms before transforming, winsorizing, or filtering on a continuous variable; scatter plots for a pair whose correlation you are about to rely on; a line plot against time for any time-series variable, where structural breaks and seasonality live.

### Analyze

Transform data with integrity. Operation-specific traps live in §Pitfalls below — walk the subsections matching the operations this task actually performs.

- `[BLOCKING]` **One logical operation per step.** Don't chain merge + filter + construct in a single step. Each Analyze step corresponds to one verb: merge, filter, construct, aggregate, reshape, deduplicate.
- `[BLOCKING]` **Row-count logging at every sample-changing operation.** Print `before → after` for every merge, filter, drop, deduplication, or sample restriction. Major operations typically warrant their own cell; minor operations can share a cell as long as the count is printed.

### Validate

Numbers must make economic sense. Sanity-check against priors, literature, cross-variable relationships, and alternative specifications. Validate is not a "final" phase — it runs on the output of every Analyze step, using Describe's post-transformation output as one of its tools.

**Sanity checks** (run after every Analyze step; minimum bar before proceeding):

- `[BLOCKING]` **Row count matches a stated expectation**, not just logged: left join matches the left table when the right side is m:1; inner join and filter drop counts are explained and the drop rate is defensible.
- `[BLOCKING]` **Economic sense.** Magnitudes plausible (GDP growth of 300% is wrong); signs correct; correlations match known stylized facts. Constructed variables and growth rates spot-checked by hand on a few observations.
- `[BLOCKING]` **Task objective expectations comparison.** When the task objective states Expected Results or Hypotheses, findings compared explicitly and divergences flagged before moving on.

If something looks unexpected, STOP and investigate before proceeding.

**Multi-source validation** (for key variables and headline numbers, go beyond sanity checks):

- `[BLOCKING]` Every key variable and headline number checked against **at least one external reference** — a published benchmark (IMF WEO, World Bank, central-bank data), prior literature, or a known related measure — for scale, sign, and relationship. Two proxies for the same construct should correlate; conditional means across obvious subgroups (developed vs emerging, pre/post crisis) should behave as expected. A surprising relationship is a signal to investigate, not to explain away.

**Missing-data as signal** (missingness is data; interrogate before handling — operational how-to in §Pitfalls §Missing data handling):

- `[BLOCKING]` **Systematic missingness** (concentrated in time, geography, or correlated with other variables) investigated — true absence vs construction error.
- `[BLOCKING]` **"Missing" meaning disambiguated.** No position (→ zero) vs didn't report (→ truly missing). Missing returns treated as zero is almost always wrong.

**Sensitivity analysis** (planning-side design in `references/planning.md`; menu of checks in `references/data-robustness-checklist.md`):

- `[ADVISORY]` Sensitivity checks run on robustness-sensitive tasks — one alternative specification at a time (sample cutoff, variable definition, winsorization, leave-one-out), since bundling makes divergence untraceable. "Robust enough" is an economic judgment: a coefficient that moves 5% is usually fine, one that flips sign is not. The question is whether the researcher would tell the same story under the alternative.
- `[BLOCKING]` **Divergence escalated.** If a sensitivity check produces a meaningfully different result (sign flip, lost significance on a headline coefficient, magnitude change large enough to change the interpretation), STOP and `AskUserQuestion`. Divergence is a methodology question, not an RA decision.

### Implementation standards

- `[BLOCKING]` Analysis scripts follow the notebook-compatible format per `references/notebook-format.md`.
- `[BLOCKING]` Major decisions (filter threshold, join type, variable definition, sample period) carry a markdown-cell justification; minor decisions carry an inline comment.
- `[BLOCKING]` Outputs (tables, figures) are generated from committed code, not ad-hoc REPL state.

### Documentation and handoff

- `[BLOCKING]` Markdown cells explain what each block does and why; reasoning for major decisions sits alongside the code.
- `[BLOCKING]` **Headline findings presented visually.** Show each headline result as a figure — a distribution, a relationship, or a time path — unless a figure would not clarify it (a lone scalar, or a small table that already reads clearly).
- `[BLOCKING]` Figures saved under the task's `attachments/` directory and embedded in task `## Results` as `attachments/fig.png` per `superRA:report-in-markdown`.

### Stage-scoped discipline (not walked at every implementation dispatch)

- **`integration` stage** — `references/integration.md` (codebase consistency, data discipline preserved through refactoring, utility reuse, documented deviations).
- **End-of-workflow completion verification** — owned by the orchestrator, not dispatched subagents. In superRA, see `superimplement` §Step 3 (reproducibility gate).

## Pitfalls

Operation-conditional checklist — walk a subsection only when the task performs that operation. Severity markers match the main checklist.

### Merges and joins

- `[BLOCKING]` **Before — describe both sides.** Check row counts and unique join-key values in both tables; verify key overlap and type compatibility. A merge without join-key inspection on both sides is an Iron Law violation.
- `[BLOCKING]` **Join type declared.** Decide 1:1, m:1, or 1:m before writing the merge, and confirm the post-merge row count against it. Many-to-many is almost always a bug — a Cartesian product that silently inflates row counts, and the reason a left join can come back longer than its left table.
- `[BLOCKING]` **Unmatched rows logged.** How many rows from each side did not match; assess whether non-matching is random or systematic.

### Time-series operations (lag, lead, diff, cumsum, fill)

- `[BLOCKING]` **Sort first.** Sort by panel ID + time before any lag, lead, diff, or cumsum. Joins destroy sort order — always re-sort after any merge.
- `[BLOCKING]` **Check for gaps** before applying lags/leads/diffs. If unit `i` is missing period `t`, a naive `shift(1)` treats period `t+1`'s lag as `t-1`'s value — silently wrong. Diagnose gaps per unit first, then spot-check a few units after the shift, especially near panel entry and exit.
- `[BLOCKING]` **Use time-aware operators when available.** In Julia, `PanelShift.jl` handles gaps correctly; in Python, merge on lagged time index or `reindex` to a full time grid before shifting. If the framework only supports positional shift, verify there are no gaps first, or fill gaps explicitly (with NaN, not interpolation) so shifts are correct.

### Reshaping

- `[BLOCKING]` After pivot: unique IDs × unique time periods should match original shape.
- `[BLOCKING]` Check for unintended NAs from unbalanced panels going wide.

### Aggregations

- `[BLOCKING]` **Function matches content.** Sum dollar amounts, average rates — never the reverse. Averaging dollars or summing rates are common silent errors.
- `[BLOCKING]` **Group-by keys match intended level** (country-year, not country-month).
- `[BLOCKING]` **Weights verified.** If weighted average, verify weights sum to expected values.
- `[BLOCKING]` **Duplicates handled before aggregating** — dupes cause double-counting.

### Deduplication

- `[BLOCKING]` Check uniqueness before operations that assume it (merges, index-setting).
- `[BLOCKING]` Document which duplicate kept and why (first, last, highest value, etc.).

### Filtering

- `[BLOCKING]` Log rows dropped — count, reason, before/after.
- `[BLOCKING]` **Check non-randomness of drops.** Are drops concentrated in certain countries, periods, or variable ranges? Sample selection bias risk.
- `[BLOCKING]` **Verify boolean logic.** `&` vs `|` errors are a common silent bug; chained filters compound.

### Variable construction

- `[BLOCKING]` **Transformation order:** log → winsorize → standardize. Log after standardize fails because standardized values can be negative.
- `[BLOCKING]` **Ratio denominators checked** for zero/near-zero; extreme ratios often come from small denominators.
- `[BLOCKING]` **Growth rates:** compare to published benchmarks for spot checks; first differences amplify measurement error — inspect for implausible spikes.
- `[BLOCKING]` **Standardization:** verify mean ≈ 0, std ≈ 1 within the relevant sample; be clear about cross-sectional vs time-series vs pooled.

### Missing data handling

Operational how-to for *handling* missingness (for *interpretation* of missingness, see §Validate §Missing-data as signal):

- `[BLOCKING]` **Handling is visible and auditable** — `.fillna(0)`, `.dropna()`, and filters are explicit, and package defaults that silently ignore NaN in aggregations are checked against the analytical objective.
- `[BLOCKING]` **Prefer passing missing through the pipeline** over filling silently; fill or coalesce only with explicit justification.

## Common Rationalizations

LLM-specific excuses that precede Iron Law violations. When you catch yourself forming one of these, undo the transformation and describe first.

| Excuse | Reality |
|--------|---------|
| "Already know this data" / "Same as last session" | Your memory ≠ current state. Files and upstream code change. Describe fresh. |
| "Just a simple merge, I can skip the describe" | Simple merges create the worst silent bugs. |
| "Quick exploration, not formal analysis" | If results inform a decision, they need validation. |
| "I'll validate at the end" | Can't isolate which step caused the problem. |
| "Only filtering, not transforming" | Filters change your sample. Log what you're losing. |

## Key References

- `references/notebook-format.md` — cell organization, rendering (Python jupytext, Julia QuartoNotebookRunner)
- `references/data-robustness-checklist.md` — sensitivity analysis: outlier
  alternatives, alternative definitions, sample restrictions, leave-one-out
- Gentzkow & Shapiro (2014), "Code and Data for the Social Sciences"
- AEA Data Editor, "Guidance for Replication Packages"
