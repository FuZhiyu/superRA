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
  Julia, R, Stata). Loaded by implementer and reviewer subagents
  at dispatch time when the stage touches analysis code, per the
  `superRA:using-superRA` §Skill-Load Manifest.
user-invocable: true
---

# Economic Data Analysis

superRA's flagship domain skill. Carries the cross-cutting discipline that applies at every stage of a data analysis — the Iron Law, the three concurrent disciplines (Describe, Analyze, Validate) with inline severity markers, the pitfalls catalog, and the common rationalizations. Main body is loaded by implementer and reviewer subagents at every analysis-touching dispatch.

## Stage-Scoped References

Companion reference files carry content that applies at a specific phase or operation. Load per stage; do not load them all at every dispatch:

| Reference | Load when |
|---|---|
| `references/planning.md` | PLAN phase — covers the **Data Inventory hard gate** and **Sensitivity Analysis Design**. Loaded by `planning-workflow` when the analysis involves data work. |
| `references/integrate-drift-tests.md` | INTEGRATE phase — identifies key results worth protecting, sets econ-specific tolerances, and catalogs data-analysis failure modes drift tests catch. Loaded by `integration-workflow` Stage 1 (drift-test creation + review). |
| `references/integration.md` | INTEGRATE phase — data-specific refactor-integrity gates (variable-construction consistency, transformation-pattern consistency, preserved describe steps / row-count prints / validation checks, drift-test pass-through). Loaded at the `integration` stage. |
| `references/data-robustness-checklist.md` | PLAN phase (design) and IMPLEMENT phase (execution of sensitivity tasks) — menu of robustness checks. |
| `references/notebook-format.md` | IMPLEMENT + VALIDATE phase — cell organization, markdown narrative, writing discipline (major-vs-minor-decision rule, figure placement), output idioms, and language-specific rendering (Python via jupytext, Julia via QuartoNotebookRunner). Loaded by the **implementer** alongside the main body whenever analysis scripts are being written or rendered. Companion guides: `jupytext-guide.md`, `julia-quarto-guide.md`. |

The main body below is the shared base that both implementer and reviewer load — it carries §Three Concurrent Disciplines (teaching + inline severity-marked checklist), §Pitfalls (operation-specific correctness), §Common Rationalizations, and §Key References. The implementer additionally loads `references/notebook-format.md` for analysis-script stages (per the manifest). The reviewer loads SKILL.md only.

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

## Three Concurrent Disciplines: Describe–Analyze–Validate

Three disciplines underpin rigorous data work. They are **concurrent, not sequential** — every analysis step exercises all three. Documentation runs continuously alongside them as a cross-cutting writing practice, not a fourth phase.

This section is both **teaching content** (how to do the work) and the **shared checklist**. The implementer walks it before returning DONE; the reviewer walks the same items as verification. The items below apply to every analysis task; operation-conditional items (merges, time-series shifts, aggregations, etc.) live in §Pitfalls and are walked only when the task performs the corresponding operation.

- `[BLOCKING]` — must fix to earn APPROVE. Encodes the Iron Law, handoff-doc discipline, and other required items.
- `[ADVISORY]` — best-practice. The reviewer MAY flag as MINOR; does not block APPROVE.

### Reviewer verdict protocol

**Walk §Three Concurrent Disciplines top to bottom, plus any §Pitfalls subsections matching operations performed in this task. Never halt on a failure.** One comprehensive pass every time — halting early forces a full re-review on the next pass, and reviewer dispatches are costly.

Two verdicts:

- **APPROVE** — no `[BLOCKING]` findings.
- **REVISE** — at least one `[BLOCKING]` finding.

**Handling dependent findings.** When a later finding's assessment depends on an earlier `[BLOCKING]` item being fixed first (e.g., "couldn't fully assess the merge because the pre-merge describe was missing — re-check after the describe is added"), say so in plain prose alongside the finding. No separate verdict, no formal tag.

**Re-review after REVISE.** Implementer fixes all `[BLOCKING]` findings and re-dispatches. The reviewer then (1) verifies each fix is correct, and (2) re-checks any finding the first pass annotated as depending on an upstream fix. Everything else is accepted from the first pass — no third full walk. APPROVE once all `[BLOCKING]` findings are resolved.

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

- `[BLOCKING]` Descriptive statistics re-run on affected variables after merges, filters, variable construction, aggregations, reshaping, deduplication. Output fed into §Validate §Sanity checks (distribution-shift check).
- `[BLOCKING]` Variables not used downstream until their post-transformation distribution is understood. If something looks unexpected, investigated before proceeding.

**Visualization for key variables:**

Supplement summary statistics with diagnostic plots — part of Describe, created alongside the statistics they complement. Not publication quality; clear axis labels, informative titles, readable scales. Save to the output directory alongside notebook renders; for rendering see `references/notebook-format.md`.

- `[ADVISORY]` **Distributions**: histograms for continuous variables — reveal skew, modes, outliers that summary stats miss. Use for any variable about to be transformed, winsorized, or filtered on.
- `[ADVISORY]` **Relationships**: scatter plots for variable pairs — show nonlinearity, clusters, influential observations that correlations hide.
- `[ADVISORY]` **Temporal patterns**: line plots of variable vs time — detect structural breaks, trends, seasonality. Essential for any time-series variable.

### Analyze

Transform data with integrity. This is the shortest of the three disciplines — most of the work is in getting Describe right before and Validate right after. Operation-specific traps live in §Pitfalls below — walk the subsections matching the operations this task actually performs.

- `[BLOCKING]` **One logical operation per step.** Don't chain merge + filter + construct in a single step. Each Analyze step corresponds to one verb: merge, filter, construct, aggregate, reshape, deduplicate.
- `[BLOCKING]` **Row-count logging at every sample-changing operation.** Print `before → after` for every merge, filter, drop, deduplication, or sample restriction. Major operations typically warrant their own cell; minor operations can share a cell as long as the count is printed.

### Validate

Numbers must make economic sense. Sanity-check against priors, literature, cross-variable relationships, and alternative specifications. Validate is not a "final" phase — it runs on the output of every Analyze step, using Describe's post-transformation output as one of its tools.

**Sanity checks** (run after every Analyze step; minimum bar before proceeding):

- `[BLOCKING]` **Row count matches expectation.** Left join: row count matches left table (if right side is m:1). Inner join: expect fewer rows — how many dropped? Filter: how many rows removed? Drop rate reasonable?
- `[BLOCKING]` **Distribution shift vs pre-transformation values.** Re-run describe on affected variables (Describe applied a second time) and compare. Unexpected shifts flag silent corruption.
- `[BLOCKING]` **Economic sense.** Magnitudes plausible (GDP growth of 300% is wrong); signs correct; correlations match known stylized facts.
- `[BLOCKING]` **Spot-check a few observations by hand** — especially for constructed variables and growth rates.
- `[BLOCKING]` **PLAN.md expectations comparison.** When the plan states Expected Results or Hypotheses, findings compared explicitly and divergences flagged before moving on.

If something looks unexpected, STOP and investigate before proceeding.

**Multi-source validation** (for key variables and headline numbers, go beyond sanity checks):

- `[BLOCKING]` **Scale check.** Magnitude matches economic intuition and published benchmarks (IMF WEO, World Bank, central-bank data, prior literature).
- `[BLOCKING]` **Property check.** Variable behavior consistent with priors or literature. For constructed variables, spot-check observations by hand; for growth rates, verify against published figures for well-known cases.
- `[BLOCKING]` **Relationship check.** Correlations between new variables and known related measures are meaningful (e.g., two proxies for financial conditions should be meaningfully correlated); signs and magnitudes consistent with stylized facts (e.g., GDP growth positively correlated with employment growth); conditional means across subgroups (developed vs emerging, pre/post crisis) behave as expected.
- `[BLOCKING]` **Reference verification.** For key variables, at least one external reference found. A surprising relationship is a signal to investigate, not to explain away.

**Missing-data as signal** (missingness is data; interrogate before handling — operational how-to in §Pitfalls §Missing data handling):

- `[BLOCKING]` **Systematic missingness** (concentrated in time, geography, or correlated with other variables) investigated — true absence vs construction error.
- `[BLOCKING]` **"Missing" meaning disambiguated.** No position (→ zero) vs didn't report (→ truly missing). Missing returns treated as zero is almost always wrong.
- `[BLOCKING]` Missingness passed through the pipeline where possible; fill/coalesce only with explicit justification.

**Sensitivity analysis** (planning-side design in `references/planning.md`; menu of checks in `references/data-robustness-checklist.md`):

- `[ADVISORY]` Sensitivity checks run on robustness-sensitive tasks — rerun the headline analysis under one alternative specification at a time (different sample cutoff, alternative variable definition, different winsorization, leave-one-out). One variation per check; bundling makes divergence untraceable.
- `[ADVISORY]` "Robust enough" judged by economic reasoning, not mechanical pass/fail. A coefficient that moves 5% under a sensible alternative is usually fine; one that flips sign or loses significance is not. Relevant question: "would the researcher tell the same story under this alternative?"
- `[BLOCKING]` **Divergence escalated.** If a sensitivity check produces a meaningfully different result (sign flip, lost significance on a headline coefficient, magnitude change large enough to change the interpretation), STOP and `AskUserQuestion`. Divergence is a methodology question, not an RA decision.

### Implementation standards

- `[BLOCKING]` Each step implements what `PLAN.md` specifies; deviations are rewritten into the step text, not layered on top.
- `[BLOCKING]` Analysis scripts follow the notebook-compatible format per `references/notebook-format.md`.
- `[BLOCKING]` Major decisions (filter threshold, join type, variable definition, sample period) carry a markdown-cell justification; minor decisions carry an inline comment.
- `[BLOCKING]` Outputs (tables, figures) are generated from committed code, not ad-hoc REPL state.

### Documentation and handoff

- `[BLOCKING]` `RESULTS.md` updated in place for this task's section. The doc is the record — findings live there before they appear in any status report.
- `[BLOCKING]` Markdown cells explain what each block does and why; reasoning for major decisions sits alongside the code.
- `[BLOCKING]` Figures saved under `results_attachments/` and embedded in `RESULTS.md` via relative paths per `superRA:report-in-markdown`.
- `[BLOCKING]` No dangling TODO / placeholder / `XXX` strings shipped.

### Stage-scoped discipline (not walked at every implementation dispatch)

- **`integration` stage** — `references/integration.md` carries the full integration-stage checklist (codebase consistency, data discipline preserved through refactoring, utility reuse, documented deviations) with its own `[BLOCKING]` / `[ADVISORY]` markers and a two-verdict protocol. Loaded by implementer and reviewer at the `integration` stage per `superRA:using-superRA` §Skill-Load Manifest.
- **End-of-workflow completion verification** — `superRA:execution-workflow` §Step 3 carries the reproducibility gate (pipeline runs end-to-end, outputs generated from committed code, docs current, deferred MINORs resolved). Walked by the orchestrator, not by dispatched subagents.

## Pitfalls

Operation-conditional checklist. The universal checks live in §Three Concurrent Disciplines above and apply to every analysis task; the items here apply only when you perform the corresponding operation (merge, time-series shift, reshape, aggregation, dedupe, filter, variable construction, missing-data handling). The implementer walks the relevant subsections as part of self-check; the reviewer walks the same subsections as verification. Severity markers (`[BLOCKING]` / `[ADVISORY]`) have the same meaning as in the main checklist.

### Merges and joins

- `[BLOCKING]` **Before — describe both sides.** Check row counts and unique join-key values in both tables; verify key overlap and type compatibility. A merge without join-key inspection on both sides is an Iron Law violation.
- `[BLOCKING]` **Join type declared.** Decide 1:1, m:1, or 1:m before writing the merge. Many-to-many is almost always a bug — it creates a Cartesian product that silently inflates row counts.
- `[BLOCKING]` **After — row count matches expectation.** Left join: row count matches left table (unless right has dupes on the join key — the many-to-many trap). Inner join: expect fewer rows; log how many dropped.
- `[BLOCKING]` **Unmatched rows logged.** How many rows from each side did not match; assess whether non-matching is random or systematic.

### Time-series operations (lag, lead, diff, cumsum, fill)

- `[BLOCKING]` **Sort first.** Sort by panel ID + time before any lag, lead, diff, or cumsum. Joins destroy sort order — always re-sort after any merge.
- `[BLOCKING]` **Check for gaps** before applying lags/leads/diffs. If unit `i` is missing period `t`, a naive `shift(1)` treats period `t+1`'s lag as `t-1`'s value — silently wrong. Diagnose gaps per unit before proceeding.
- `[BLOCKING]` **Use time-aware operators when available.** In Julia, `PanelShift.jl` handles gaps correctly; in Python, merge on lagged time index or `reindex` to a full time grid before shifting. If the framework only supports positional shift, verify there are no gaps first, or fill gaps explicitly (with NaN, not interpolation) so shifts are correct.
- `[BLOCKING]` **After — spot-check a few units** to confirm the lag/lead aligns with the correct time period, especially near panel entry/exit.

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
- `[BLOCKING]` **Verify boolean logic.** `&` vs `|` errors are a common silent bug.
- `[ADVISORY]` Watch chained filters for unintended cumulative effects.

### Variable construction

- `[BLOCKING]` **Transformation order:** log → winsorize → standardize. Log after standardize fails because standardized values can be negative.
- `[BLOCKING]` **Ratio denominators checked** for zero/near-zero; extreme ratios often come from small denominators.
- `[BLOCKING]` **Growth rates:** compare to published benchmarks for spot checks; first differences amplify measurement error — inspect for implausible spikes.
- `[BLOCKING]` **Standardization:** verify mean ≈ 0, std ≈ 1 within the relevant sample; be clear about cross-sectional vs time-series vs pooled.

### Missing data handling

Operational how-to for *handling* missingness (for *interpretation* of missingness, see §Validate §Missing-data as signal):

- `[BLOCKING]` **Explicit handling** (`.fillna(0)`, `.dropna()`, filters) is visible and auditable.
- `[BLOCKING]` **Implicit handling audited** (package defaults silently ignoring NaN in aggregations) — check alignment with analytical objective.
- `[BLOCKING]` **Prefer passing missing through the pipeline** over filling silently; use fill/coalesce only with explicit justification.

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
