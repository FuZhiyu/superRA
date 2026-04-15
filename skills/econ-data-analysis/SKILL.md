---
name: econ-data-analysis
description: >
  Use PROACTIVELY whenever performing data analysis on economic,
  financial, or panel datasets — importing raw data, cleaning,
  merging, filtering, constructing variables, aggregating, computing
  summary statistics, producing regression inputs, building figures,
  or writing analysis scripts. Also use when about to transform data
  you have not yet described; when merging two datasets; when
  filtering by a condition you have not yet profiled; when a number
  "looks off"; when outputs fail to match literature or intuition;
  when a script was just refactored and needs re-validation. Triggers
  include CRSP / Compustat / WRDS / panel data, "merge these datasets",
  "clean this data", "construct variable X", "check the summary stats",
  "why is this number so large", "I'll just filter and move on",
  or any data file with unknown structure. Language-agnostic (Python,
  Julia, R, Stata). Auto-loaded by implementer and reviewer subagents
  at dispatch time when the stage touches analysis code; the
  auto-load is configured in `agents/implementer.md` and
  `agents/reviewer.md`, not in the workflow skills themselves.
user-invocable: true
---

# Economic Data Analysis

superRA's flagship domain skill. Carries the cross-cutting discipline that applies at every stage of a data analysis — the Iron Law, the three concurrent disciplines (Describe, Analyze, Validate), the pitfalls catalog, and the Red Flags. Main body is loaded by implementer and reviewer subagents at every analysis-touching dispatch.

## Stage-Scoped References

Two companion reference files carry content that applies at exactly one phase. Load them per stage; do not load them at every dispatch:

| Reference | Load when |
|---|---|
| `references/planning.md` | PLAN phase — covers the **Data Inventory hard gate** and **Sensitivity Analysis Design**. Loaded by `planning-workflow` when the analysis involves data work. |
| `references/integrate-drift-tests.md` | INTEGRATE phase — identifies key results worth protecting, sets econ-specific tolerances, and catalogs data-analysis failure modes drift tests catch. Loaded by `integration-workflow` Stage 1 (drift-test creation + review). |
| `references/data-robustness-checklist.md` | PLAN phase (design) and IMPLEMENT phase (execution of sensitivity tasks) — menu of robustness checks. |

The main body below is everything else — everything that applies whenever data is being touched, which is most of the time. The §Review & Self-Check Discipline section below loads with the main body at every stage — it is the shared gating both implementer and reviewer walk.

## The Iron Law

```
NO TRANSFORMATION WITHOUT PRIOR DESCRIPTION
```

Transformed data without describing it first? Undo the transformation. Start over.

**No exceptions:**
- Don't keep the merged result as "it looks fine"
- Don't "check it later at the end"
- Don't rely on a description from a previous session
- Undo means undo

Describe fresh from the current data state. Period.

**Violating the letter of the rules is violating the spirit of the rules.**

---

## Three Concurrent Disciplines: Describe-Analyze-Validate

Three disciplines underpin rigorous data work. They are **concurrent, not sequential** — every analysis step exercises all three. Describe runs both before and after every transformation; Analyze is the transformation itself done with integrity; Validate is the sanity check against priors, literature, and alternatives. Documentation is a cross-cutting writing practice that runs throughout (see the short section after Analyze).

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
`superRA:script-to-notebook`.

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
stated once here and referenced elsewhere — see Pitfalls for operation-specific
details.

**Sort discipline for time-series**: sort by panel ID + time before any lag,
lead, diff, or cumsum. Joins destroy sort order — re-sort after every merge.
See Pitfalls §Time-series for operator-specific guidance.

**Join-type discipline**: decide 1:1, m:1, or 1:m before writing the merge;
many-to-many is almost always a bug. See Pitfalls §Merges.

## Documentation — cross-cutting writing practice

Documentation is not a fourth phase. It runs continuously alongside Describe,
Analyze, and Validate. The goal is a human-readable document that interleaves
code, narrative, and outputs so a fresh reader (or the next session) can
reconstruct what was done and why.

**Script categories:**
- **Analysis scripts** (loading, cleaning, merging, construction, diagnostics):
  format for notebook rendering — see `superRA:script-to-notebook` for cell
  organization and rendering details (Python jupytext, Julia
  QuartoNotebookRunner).
- **Runner/utility/pipeline scripts**: standard script format, no notebook
  formatting needed.

**Writing discipline:**
- **Markdown cells** frame each block: what, why, expected result.
- **Inline comments** for minor decisions (winsorization percentile, filter
  threshold).
- **Markdown cells with reasoning** for major decisions (excluding countries,
  choosing sample period, variable definition).
- **Figures**: save alongside notebook renders; see Describe §Visualization for
  what to plot and `superRA:script-to-notebook` for rendering.

**Short checklist per step:**
- [ ] Markdown cell stating what this step does and why
- [ ] Row-count log visible in output (if sample-changing)
- [ ] Decision justifications written *as decisions are made*, not retrofitted

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
(Operational how-to-write-the-code lives in Pitfalls §Missing data handling.)

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

## Review & Self-Check Discipline — shared gating for implementer and reviewer

Single source of truth for pre-handoff self-check and reviewer verification. The implementer walks this section before returning DONE; the reviewer walks the same items as verification criteria. No parallel checklist lives elsewhere — any drift between "what the implementer checks" and "what the reviewer checks" is a bug in this section, not a reason to fork it.

**Severity markers** appear inline on each item:

- `[GATING]` — load-bearing non-negotiable. Failure blocks an unconditional APPROVE. These encode the Iron Law and the handoff-doc discipline; no task ships with a failed gating item unresolved.
- `[STANDARD]` — required. A missed item becomes a REVISE finding from the reviewer.
- `[ADVISORY]` — best-practice. The reviewer MAY flag as MINOR; resolution is optional unless the task's specifics elevate it.

### Reviewer verdict protocol (CONDITIONAL APPROVE)

**Walk the entire section top to bottom even when a gating item fails.** Halting early on gating failure forces a full re-review on the next pass — reviewer dispatches are costly. One comprehensive pass, every time.

Three verdicts:

- **APPROVE** — no findings at any severity.
- **REVISE** — only `[STANDARD]` items failed (no `[GATING]` failures). Implementer fixes the flagged items and re-dispatches.
- **CONDITIONAL APPROVE** — one or more `[GATING]` items failed. The reviewer walked the rest of the checklist anyway and those downstream items look correct **conditional on the gating fix not invalidating them**. The review-notes blockquote lists the failed `[GATING]` item(s) first, then states "downstream items reviewed and currently correct; approval contingent on the gating fix not changing downstream results."

On a re-dispatch following a CONDITIONAL APPROVE, the reviewer's second pass is narrow: (1) verify the gating fix is correct, (2) verify the cited downstream items still hold under the fix. If both, CONDITIONAL → unconditional APPROVE.

### Gating — the Iron Law applied per step

- `[GATING]` Every input described before the first transformation on it — panel structure, variable diagnostics, missing-value pattern. See §Describe.
- `[GATING]` Every sample-changing operation logs before/after row counts. See §Analyze.
- `[GATING]` Every merge describes join keys on both sides before execution. See §Pitfalls §Merges and joins.

### Implementation standards

- `[STANDARD]` Each step implements what `PLAN.md` specifies; deviations are rewritten into the step text, not layered on top.
- `[STANDARD]` Analysis scripts follow the notebook-compatible format per `superRA:script-to-notebook`.
- `[STANDARD]` Major decisions (filter threshold, join type, variable definition, sample period) carry a markdown-cell justification; minor decisions carry an inline comment.
- `[STANDARD]` Outputs (tables, figures) are generated from committed code, not ad-hoc REPL state.

### Validation completeness

- `[STANDARD]` Distributions re-checked on affected variables after every major transformation; compared to pre-transformation values per §Validate §Sanity checks.
- `[STANDARD]` Economic sense checked: magnitudes plausible, signs as expected, benchmarks cross-checked where applicable. See §Validate §Multi-source validation.
- `[STANDARD]` When `PLAN.md` header states Expected Results / Hypotheses, findings are compared explicitly and divergences flagged.
- `[ADVISORY]` Sensitivity analysis run on robustness-sensitive tasks per `references/data-robustness-checklist.md`; divergence escalated per §Validate §Sensitivity analysis.

### Documentation and handoff

- `[GATING]` `RESULTS.md` updated in place for this task's section per `superRA:handoff-doc`. The doc is the record — findings live there before they appear in any status report.
- `[STANDARD]` Markdown cells explain what each block does and why; reasoning for major decisions sits alongside the code.
- `[STANDARD]` Figures saved under `results_attachments/` and embedded in `RESULTS.md` via relative paths per `superRA:report-in-markdown`.
- `[STANDARD]` No dangling TODO / placeholder / `XXX` strings shipped.

### Refactor integrity (applies at the `refactoring` and `integration review` stages)

- `[GATING]` All Describe steps preserved — or explicitly replaced by upstream-validated diagnostics the refactor relies on.
- `[GATING]` All row-count prints preserved at sample-changing operations.
- `[GATING]` All Validate checks preserved.
- `[GATING]` Drift tests (where they exist) pass post-refactor; failures adjudicated per `references/integrate-drift-tests.md`, never silently re-expected.
- `[STANDARD]` Variable definitions unchanged, or the change is documented and justified.
- `[STANDARD]` Sample construction unchanged, or the change is documented and justified.
- `[STANDARD]` Naming follows the nearest module-level `CLAUDE.md` / `AGENTS.md` / `README.md` conventions.
- `[STANDARD]` Existing utility functions reused; no reinvented helpers.

### Completion verification (applies at `execution-workflow` Step 3)

- `[GATING]` All code committed.
- `[GATING]` Multi-script pipeline runs end-to-end if the plan declares one.
- `[GATING]` Outputs exist and were generated from committed code (not ad-hoc REPL).
- `[STANDARD]` `PLAN.md` and `RESULTS.md` current, per the inline-edit rule in `superRA:handoff-doc`.
- `[STANDARD]` Deferred MINORs either resolved or documented in `RESULTS.md` as accepted limitations with rationale.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Data looks fine" | You haven't described it. You don't know. |
| "Just a simple merge" | Simple merges create the worst silent bugs. |
| "I'll validate at the end" | Can't isolate which step caused the problem. |
| "Already know this data" | Your memory ≠ current state. Describe it. |
| "It's the same as last session" | Files change. Upstream code changes. Describe fresh. |
| "Only filtering, not transforming" | Filters change your sample. Describe what you're losing. |
| "Quick exploration, not formal analysis" | If results inform decisions, they must be validated. |
| "Row counts match, so the merge is fine" | Row counts don't catch value corruption or key mismatches. |
| "I'll add descriptions when I write it up" | After-the-fact descriptions are biased by what you built. |
| "Describing is busywork" | 30 seconds of describing vs hours of debugging wrong results. |

## Red Flags - STOP and Start Over

- Transform before describe
- Merge without checking join keys in both tables
- No row count printed after sample-changing operation
- "Looks fine" without running diagnostics
- Descriptions added after the fact
- Skipping validation because "the numbers look right"
- Multiple transformations without intermediate validation
- Rationalizing "just this once"
- "I already checked this data in a previous session"
- "This is exploratory so it doesn't matter"
- Assume a merge, rebase, or refactor preserves analysis results without re-running describe on the affected variables. Floating-point order, row-count drift, and silent sample changes are common post-integration failures.
- Accept merged or refactored code without comparing pre- and post-change row counts and summary statistics on the key variables.

**All of these mean: Undo the transformation. Describe first. Start over from that step.**

## Verification Checklist

For pre-handoff self-check and reviewer verification, see §Review & Self-Check Discipline above.

## Pitfalls

Concise checklists for common data manipulation errors. Consult when performing
the relevant operation.

### Merges and joins

- **Before**: check row counts and unique join-key values in both tables
- **Join type**: 1:1, m:1, or 1:m. Many-to-many is almost always a bug —
  it creates a Cartesian product that silently inflates row counts
- **After**: row count should match left table for left join (unless right
  has dupes on the join key — the many-to-many trap)
- **Unmatched**: log how many rows from each side did not match; assess whether
  non-matching is random or systematic

### Time-series operations (lag, lead, diff, cumsum, fill)

- **Sort first**: sort by panel ID + time before any time-series operation.
  Joins destroy sort order — always re-sort after any merge
- **Check for gaps** before applying lags/leads/diffs. If unit `i` is missing
  period `t`, a naive `shift(1)` treats period `t+1`'s lag as `t-1`'s value —
  silently wrong. Diagnose gaps per unit before proceeding
- **Use time-aware operators** when available: in Julia, `PanelShift.jl`
  handles gaps correctly; in Python, merge on lagged time index or `reindex`
  to a full time grid before shifting. If the framework only supports positional
  shift, verify there are no gaps first, or fill gaps explicitly (with NaN,
  not interpolation) so shifts are correct
- **After**: spot-check a few units to confirm the lag/lead aligns with the
  correct time period, especially near panel entry/exit

### Reshaping

- After pivot: unique IDs × unique time periods should match original shape
- Check for unintended NAs from unbalanced panels going wide

### Aggregations

- **Function**: sum dollar amounts, average rates — never the reverse.
  Averaging dollars or summing rates are common silent errors
- **Group-by keys**: verify they match intended level (country-year, not
  country-month)
- **Weights**: if weighted average, verify weights sum to expected values
- **Duplicates**: handle before aggregating — dupes cause double-counting

### Deduplication

- Check uniqueness before operations that assume it (merges, index-setting)
- Document which duplicate kept and why (first, last, highest value, etc.)

### Filtering

- Log rows dropped: count, reason, before/after
- Check non-randomness: are drops concentrated in certain countries, periods,
  or variable ranges? This may introduce sample selection bias
- Verify boolean logic: `&` vs `|` errors are a common silent bug
- Watch chained filters for unintended cumulative effects

### Variable construction

- **Transformation order**: log → winsorize → standardize
  (log after standardize fails because standardized values can be negative)
- **Ratio denominators**: check for zero/near-zero; extreme ratios often come
  from small denominators
- **Growth rates**: compare to published benchmarks for spot checks; first
  differences amplify measurement error — inspect for implausible spikes
- **Standardization**: verify mean ≈ 0, std ≈ 1 within the relevant sample;
  be clear about cross-sectional vs time-series vs pooled

### Missing data handling

Operational how-to (for *interpretation* of missingness, see
Validate §Missing-data-as-signal):

- **Explicit** handling (`.fillna(0)`, `.dropna()`, filters) is visible and
  auditable
- **Implicit** handling (package defaults silently ignoring NaN in
  aggregations) is easy to miss — check alignment with analytical objective
- Prefer passing missing through the pipeline over filling silently; use
  fill/coalesce only with explicit justification

## Key References

- `superRA:script-to-notebook` — cell organization, rendering (Python jupytext, Julia QuartoNotebookRunner)
- `references/data-robustness-checklist.md` — sensitivity analysis: outlier
  alternatives, alternative definitions, sample restrictions, leave-one-out
- Gentzkow & Shapiro (2014), "Code and Data for the Social Sciences"
- AEA Data Editor, "Guidance for Replication Packages"
