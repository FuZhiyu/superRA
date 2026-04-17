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

superRA's flagship domain skill. Carries the cross-cutting discipline that applies at every stage of a data analysis — the Iron Law, the three concurrent disciplines (Describe, Analyze, Validate), the pitfalls catalog, and the Red Flags. Main body is loaded by implementer and reviewer subagents at every analysis-touching dispatch.

## Stage-Scoped References

Companion reference files carry content that applies at a specific phase or operation. Load per stage; do not load them all at every dispatch:

| Reference | Load when |
|---|---|
| `references/disciplines.md` | IMPLEMENT + VALIDATE phase — full operational content of the three concurrent disciplines (Describe / Analyze / Validate) with every subsection (panel diagnostics, variable diagnostics, before-merge, outliers, post-transformation re-describe, visualization; row-count rule, sort discipline, join discipline; sanity checks, multi-source validation, missing-data, sensitivity analysis). Loaded by the **implementer** at every analysis-touching dispatch. The reviewer does NOT load this file — §Review & Self-Check Discipline below is self-sufficient for verification. |
| `references/planning.md` | PLAN phase — covers the **Data Inventory hard gate** and **Sensitivity Analysis Design**. Loaded by `planning-workflow` when the analysis involves data work. |
| `references/integrate-drift-tests.md` | INTEGRATE phase — identifies key results worth protecting, sets econ-specific tolerances, and catalogs data-analysis failure modes drift tests catch. Loaded by `integration-workflow` Stage 1 (drift-test creation + review). |
| `references/integration.md` | INTEGRATE phase — data-specific refactor-integrity gates (variable-construction consistency, transformation-pattern consistency, preserved describe steps / row-count prints / validation checks, drift-test pass-through). Loaded at `refactoring` and `integration-review` stages. |
| `references/data-robustness-checklist.md` | PLAN phase (design) and IMPLEMENT phase (execution of sensitivity tasks) — menu of robustness checks. |
| `references/notebook-format.md` | IMPLEMENT + VALIDATE phase — cell organization, markdown narrative, writing discipline (major-vs-minor-decision rule, figure placement), output idioms, and language-specific rendering (Python via jupytext, Julia via QuartoNotebookRunner). Loaded by the **implementer** alongside the main body whenever analysis scripts are being written or rendered. Companion guides: `jupytext-guide.md`, `julia-quarto-guide.md`. |

The main body below is the shared base that both implementer and reviewer load — it carries the three-disciplines summary, the §Review & Self-Check Discipline both walk, §Pitfalls (reviewer needs it to verify operation-specific correctness), Common Rationalizations, Red Flags, and Key References. The implementer additionally loads `references/disciplines.md` + `references/notebook-format.md` (per the manifest). The reviewer loads SKILL.md only.

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

Three disciplines underpin rigorous data work. They are **concurrent, not sequential** — every analysis step exercises all three. Documentation runs continuously alongside them as a cross-cutting writing practice, not a fourth phase.

**Describe.** The most common analytical error is transforming data you do not understand. Describe thoroughly and often — both before and after every transformation. Post-transformation describe is not a separate phase; it is the same discipline applied a second time, now as a validation tool fed into Sanity checks. Panel structure, variable diagnostics, missing-value pattern, join-key inspection (before any merge), outlier flagging, and diagnostic visualization all live here. For the full operational discipline see `references/disciplines.md` §Describe.

**Analyze.** Transform with integrity. One logical operation per step — no chaining merge + filter + construct. Row-count logging is MANDATORY at every sample-changing operation (`before → after` printed for every merge, filter, drop, deduplication, sample restriction). Sort by panel ID + time before any lag / lead / diff / cumsum; joins destroy sort order so re-sort after every merge. Decide 1:1 / m:1 / 1:m before writing a merge — many-to-many is almost always a bug. For the full operational discipline see `references/disciplines.md` §Analyze; operation-specific guidance lives in §Pitfalls below.

**Validate.** Numbers must make economic sense. Sanity-check against priors, literature, cross-variable relationships, and alternative specifications. Validate is not a "final" phase — it runs on the output of every Analyze step. Four subdisciplines: Sanity checks (row counts, distribution shift, economic sense, PLAN.md comparison), Multi-source validation (scale / property / relationship checks), Missing-data as signal (missingness is data), and Sensitivity analysis (alternative specifications; divergence is a methodology question to escalate via `AskUserQuestion`, not an RA call). For the full operational discipline see `references/disciplines.md` §Validate.

For writing mechanics — cell organization, markdown-cell narrative, major-vs-minor-decision rule, figure placement, language-specific rendering — see `references/notebook-format.md`.

## Review & Self-Check Discipline

The implementer walks this section before returning DONE; the reviewer walks the same items as verification criteria. 

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

- `[GATING]` Every input described before the first transformation on it — panel structure, variable diagnostics, missing-value pattern. See §Describe summary above; full operational discipline in `references/disciplines.md` §Describe.
  - *Why:* violations are silent corruption. Transforming data you haven't understood is the most common analytical error — the Iron Law encodes it. A skipped describe means you cannot tell whether a downstream anomaly is bad data or bad code.
- `[GATING]` Every sample-changing operation logs before/after row counts. See §Analyze summary above; full discipline in `references/disciplines.md` §Analyze.
  - *Why:* row-count drift is the canonical silent bug — Cartesian products, unexpected filter cascades, missing-key joins all surface first as an unexplained row count. Printing `before → after` makes drift visible at commit time, not weeks later.
- `[GATING]` Every merge describes join keys on both sides before execution. See §Pitfalls §Merges and joins.
  - *Why:* a merge against an unchecked join key is a bet, not an operation. Key type mismatches (int vs string), duplicate keys (many-to-many bugs), and incomplete overlap are invisible until they've corrupted the sample — and by then the describe you should have run first is contaminated by the merge you shouldn't have done.

### Implementation standards

- `[STANDARD]` Each step implements what `PLAN.md` specifies; deviations are rewritten into the step text, not layered on top.
  - *Why:* the handoff-doc principle "latest state only, no history" applies to plans too. A step whose recorded text no longer matches what was done cannot be audited.
- `[STANDARD]` Analysis scripts follow the notebook-compatible format per `references/notebook-format.md`.
- `[STANDARD]` Major decisions (filter threshold, join type, variable definition, sample period) carry a markdown-cell justification; minor decisions carry an inline comment.
  - *Why:* the major/minor split is load-bearing — markdown cells capture *the reasoning that led to the choice*, inline comments capture *the choice*. A reviewer tracing methodology reads the markdown cells first.
- `[STANDARD]` Outputs (tables, figures) are generated from committed code, not ad-hoc REPL state.

### Validation completeness

- `[STANDARD]` Distributions re-checked on affected variables after every major transformation; compared to pre-transformation values per `references/disciplines.md` §Validate §Sanity checks.
- `[STANDARD]` Economic sense checked: magnitudes plausible, signs as expected, benchmarks cross-checked where applicable. See `references/disciplines.md` §Validate §Multi-source validation.
- `[STANDARD]` When `PLAN.md` header states Expected Results / Hypotheses, findings are compared explicitly and divergences flagged.
  - *Why:* silent divergence from stated expectations is how wrong results ship — the comparison is forced explicit so divergence becomes a decision, not a drift.
- `[ADVISORY]` Sensitivity analysis run on robustness-sensitive tasks per `references/data-robustness-checklist.md`; divergence escalated per `references/disciplines.md` §Validate §Sensitivity analysis.

### Documentation and handoff

- `[GATING]` `RESULTS.md` updated in place for this task's section per `superRA:using-superRA` §Handoff Doc Discipline. The doc is the record — findings live there before they appear in any status report.
  - *Why:* Workflow Principle #2 — if a finding exists only in a chat message, it does not exist. It will be lost at the next session boundary. The committed doc is the authoritative record; the status report points at it.
- `[STANDARD]` Markdown cells explain what each block does and why; reasoning for major decisions sits alongside the code.
- `[STANDARD]` Figures saved under `results_attachments/` and embedded in `RESULTS.md` via relative paths per `superRA:report-in-markdown`.
- `[STANDARD]` No dangling TODO / placeholder / `XXX` strings shipped.

### Refactor integrity (applies at the `refactoring` and `integration-review` stages)

For integration-stage refactoring discipline (cross-codebase consistency, no redundant intermediaries, variable-construction consistency, transformation-pattern consistency, documented deviations, migration pointers), see `references/integration.md`. The items below are the data-discipline-preservation gates that apply inside this file regardless of codebase context.

- `[GATING]` All Describe steps preserved — or explicitly replaced by upstream-validated diagnostics the refactor relies on.
  - *Why:* a refactor that removes describe steps converts a transparent analysis into an opaque one. The Iron Law does not stop applying at the refactor boundary — if describe steps move upstream, the refactorer must cite the upstream diagnostics the new code depends on.
- `[GATING]` All row-count prints preserved at sample-changing operations.
  - *Why:* row-count visibility is the first-line drift detector. A refactor that drops the prints hides future drift from the reviewer and from post-merge integration review.
- `[GATING]` All Validate checks preserved.
  - *Why:* refactors silently change behavior more often than authors expect (floating-point ordering, sort-stability, merge semantics). Removed validation checks mean removed drift detection — a refactor without its validation checks is not the same analysis.
- `[GATING]` Drift tests (where they exist) pass post-refactor; failures adjudicated per `references/integrate-drift-tests.md`, never silently re-expected.
  - *Why:* "re-expect" silently changes the headline. A drift-test failure is a question for the researcher, not a number to relax.
- `[STANDARD]` Variable definitions unchanged, or the change is documented and justified.
- `[STANDARD]` Sample construction unchanged, or the change is documented and justified.
- `[STANDARD]` Naming follows the nearest module-level `CLAUDE.md` / `AGENTS.md` / `README.md` conventions.
- `[STANDARD]` Existing utility functions reused; no reinvented helpers.

### Completion verification (applies at `execution-workflow` Step 3)

- `[GATING]` All code committed.
  - *Why:* uncommitted state is unreproducible — the task is not done until `git status` is clean.
- `[GATING]` Multi-script pipeline runs end-to-end if the plan declares one.
  - *Why:* scripts that run individually but not as a pipeline are a reproducibility failure waiting for the next session to trigger it.
- `[GATING]` Outputs exist and were generated from committed code (not ad-hoc REPL).
  - *Why:* outputs generated from uncommitted REPL state are unreproducible — the commit does not reconstruct them.
- `[STANDARD]` `PLAN.md` and `RESULTS.md` current, per the inline-edit rule in `superRA:using-superRA` §Handoff Doc Discipline.
- `[STANDARD]` Deferred MINORs either resolved or documented in `RESULTS.md` as accepted limitations with rationale.

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

## Key References

- `references/notebook-format.md` — cell organization, rendering (Python jupytext, Julia QuartoNotebookRunner)
- `references/data-robustness-checklist.md` — sensitivity analysis: outlier
  alternatives, alternative definitions, sample restrictions, leave-one-out
- Gentzkow & Shapiro (2014), "Code and Data for the Social Sciences"
- AEA Data Editor, "Guidance for Replication Packages"
