# The Three Concurrent Disciplines: Describe-Analyze-Validate

> Stage-scoped reference of `superRA:econ-data-analysis`. Loaded by the implementer subagent (and by the orchestrator in-session) at every analysis-touching implementation dispatch. Carries the full operational content of the three concurrent disciplines that underpin every data-analysis step. The reviewer does NOT load this file — the reviewer walks `SKILL.md` §Review & Self-Check Discipline, whose gates cite the relevant subsections here by name.

## How to read this file

This reference expands on the three-paragraph summary in `SKILL.md`. Every analysis step exercises all three disciplines simultaneously: you **Describe** the inputs before you touch them (and re-describe affected variables after), you **Analyze** (transform) with integrity, and you **Validate** the output against priors, literature, and alternatives. Documentation is a cross-cutting writing practice that runs alongside all three — written continuously, not retrofitted (see `SKILL.md` §Three Concurrent Disciplines and `references/notebook-format.md` for the mechanics).

The anchor is the Iron Law in `SKILL.md`: **no transformation without prior description.** If you find yourself reading this file after transforming data you have not described, stop, undo the transformation, describe fresh, and start that step over. Everything below assumes you are working *with* the Iron Law, not around it.

## Describe

The most common analytical error is transforming data you do not understand. **Describe thoroughly and often — both before and after every transformation.** Post-transformation describe is not a separate "phase"; it is the same discipline applied a second time, now as a validation tool (see Validate §Sanity checks).

### After loading any dataset

**Panel structure** (first priority for panel/longitudinal data — the common case):
- Identify the **panel ID** (firm, fund, country, individual) and **time ID**
  (year, quarter, month, day)
- Count unique IDs and unique time periods; verify against expectations
- Date range: min and max; any expected periods absent?
- **Balancedness**: compute periods-per-unit distribution (mean, median, min, max).
  Balanced ratio = actual rows / (N_ids × T_periods). If unbalanced, characterize
  the pattern — entry/exit, mid-panel gaps, or expanding coverage?
- For pure cross-sections, note it and skip panel diagnostics

**Variable diagnostics** — tailor to type, focus on key variables:
- **Continuous** (returns, prices, GDP, weights): mean, median, std, min, max,
  and tail percentiles (p1, p5, p95, p99) — tails detect outliers
- **Categorical/binary** (sector codes, indicators, country): value counts and
  shares; check for unexpected categories or near-zero frequencies
- **Identifiers**: does panel ID × time uniquely identify rows? Check for duplicates
- Do NOT run blanket `describe()` on all columns — select key variables explicitly

**Data types and missing values**:
- Column types: dates as dates, numerics as numerics (not object/string)
- Missing values: count and share per variable; is missingness random or
  systematic? (See Validate §Missing-data-as-signal for interpretation.)
- Compare to source documentation if expected sample size is stated

When data was already imported and validated upstream, read existing diagnostics
rather than re-running full validation.

### Before a merge

Also describe the **join keys** in both tables — unique values, overlap, type
compatibility. A merge without join-key inspection on both sides is a Red Flag.

### Outlier flagging

- Flag observations beyond p1/p99 — are they data errors or genuine extremes?
- For naturally skewed variables (firm size, wealth, trade volumes), extreme
  values may be real — document the decision to keep, winsorize, or trim
- If winsorizing, document cutoff and consider robustness with alternatives
  (see `references/data-robustness-checklist.md`)

### After every major transformation (re-describe)

Re-run descriptive statistics on affected variables. Major transformations
include: merges, filters, variable construction, aggregations, reshaping,
deduplication. This is the same Describe discipline applied a second time — the
output is fed directly into Validate §Sanity checks (distribution-shift check).

**Rule: if something looks unexpected, investigate before proceeding.**
Do not use a variable downstream until its distribution is understood.

### Visualization for key variables

Supplement summary statistics with diagnostic plots. These are part of
describing data — create them alongside the statistics they complement.

- **Distributions**: histograms for continuous variables — reveals skew, modes,
  and outliers that summary stats miss. Use for any variable you're about to
  transform, winsorize, or filter on.
- **Relationships**: scatter plots for variable pairs — shows nonlinearity,
  clusters, and influential observations that correlations hide.
- **Temporal patterns**: line plots of variable vs time — detects structural
  breaks, trends, and seasonality. Essential for any time-series variable.

Not publication quality. Clear axis labels, informative titles, readable scales.
Save to the output directory alongside notebook renders. For rendering, see
`references/notebook-format.md`.

## Analyze

Transform data with integrity. This is the shortest of the three disciplines —
most of the work is in getting Describe right before and Validate right after.

**One logical operation per step.** Don't chain merge + filter + construct in a
single step. Each Analyze step should correspond to one verb: merge, filter,
construct, aggregate, reshape, deduplicate.

**Row-count logging is MANDATORY at every sample-changing operation.** Print
`before → after` row counts for every merge, filter, drop, deduplication, or
sample restriction. Major operations typically warrant their own cell; minor
operations can share a cell as long as the count is printed. This rule is
stated once here and referenced elsewhere — see `SKILL.md` §Pitfalls for
operation-specific details.

**Sort discipline for time-series**: sort by panel ID + time before any lag,
lead, diff, or cumsum. Joins destroy sort order — re-sort after every merge.
See `SKILL.md` §Pitfalls §Time-series for operator-specific guidance.

**Join-type discipline**: decide 1:1, m:1, or 1:m before writing the merge;
many-to-many is almost always a bug. See `SKILL.md` §Pitfalls §Merges.

## Validate

Numbers must make economic sense. Sanity-check against priors, literature,
cross-variable relationships, and alternative specifications. Validate is not
a "final" phase — it runs on the output of every Analyze step, using Describe's
post-transformation output as one of its tools.

### Sanity checks

Run after every Analyze step; these are the minimum bar before proceeding.

- **Row count matches join/filter expectation**:
  - Left join: row count should match left table (if right side is m:1)
  - Inner join: expect fewer rows — how many dropped?
  - Filter: how many rows removed? Is the drop rate reasonable?
- **Distribution shift vs. pre-transformation values**: re-run describe on the
  affected variables (that's the second application of Describe) and compare
  to the pre-transformation values. Unexpected shifts flag silent corruption.
- **Economic sense**: magnitudes plausible? GDP growth of 300% is wrong. Signs
  correct? Correlations match known stylized facts?
- **Spot-check a few observations by hand** — especially for constructed
  variables and growth rates.
- **PLAN.md expectations comparison**: when the plan states expected results or
  hypotheses, compare findings to them explicitly. Flag and investigate
  divergences before moving on.

**If something looks unexpected: STOP. Investigate before proceeding.**

### Multi-source validation

For key variables and headline numbers, go beyond sanity checks and cross-check
against external references.

- **Scale check**: does the magnitude match economic intuition and published
  benchmarks (IMF WEO, World Bank, central bank data, prior literature)?
- **Property check**: is the variable's behavior consistent with priors or what
  the literature has found? For constructed variables, spot-check a few
  observations by hand. For growth rates, verify against published figures for
  well-known cases.
- **Relationship check**:
  - Compute correlations between new variables and known related measures
    (e.g., two different proxies for financial conditions should be meaningfully correlated)
  - Signs and magnitudes consistent with published stylized facts?
    (e.g., GDP growth positively correlated with employment growth)
  - Conditional means across subgroups behave as expected?
    (e.g., developed vs. emerging, pre/post crisis)
- **Reference verification**: for key variables, find at least one external
  reference to verify alignment. A surprising relationship is a signal to
  investigate, not to explain away.

### Missing-data as signal

Missingness is data. Interrogate the pattern before deciding how to handle it.
(Operational how-to-write-the-code lives in `SKILL.md` §Pitfalls §Missing data handling.)

- **Systematic missingness** (concentrated in time, geography, or correlated
  with other variables) is informative — investigate whether it reflects true
  data absence or a construction error.
- **What does "missing" mean here?** No position (→ zero) vs didn't report
  (→ truly missing) — the correct treatment depends on the data source and
  research question.
- **Missing returns treated as zero is almost always wrong.**
- Prefer passing missingness through the pipeline over silently filling it;
  fill/coalesce only with explicit justification.

### Sensitivity analysis

Validation against alternative specifications. Planning-side design is in
`references/planning.md §Sensitivity Analysis Design`; the menu of checks is in
`references/data-robustness-checklist.md`. This section covers **execution-side
discipline** — how to run a sensitivity check during implementation.

**How to run**: rerun the headline analysis under one alternative specification
at a time (different sample cutoff, alternative variable definition, different
winsorization, leave-one-out). One variation per check — bundling changes makes
divergence untraceable.

**What counts as "robust enough"**: use economic reasoning, not mechanical
pass/fail. A coefficient that moves 5% under a sensible alternative is usually
fine; one that flips sign or loses significance is not. The relevant question
is "would the researcher tell the same story under this alternative?" — not
"does the number round to the same value?"

**When to escalate**: if a sensitivity check produces a meaningfully different
result (sign flip, lost significance on a headline coefficient, magnitude
change large enough to change the interpretation), **stop and
`AskUserQuestion`**. Divergence is a methodology question, not an RA decision —
the researcher chooses whether to revise the headline, report both, or
investigate further.
