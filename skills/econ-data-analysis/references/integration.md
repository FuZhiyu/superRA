# Integration Discipline for Data Analysis

> Data-analysis integration discipline at the `integration` stage. Implementer walks it as self-check; reviewer walks it as verification. Severity markers and verdict mechanics per `econ-data-analysis/SKILL.md` §Three Concurrent Disciplines.

Generic code-integration concerns (naming, utility reuse, PR-friendly diffs, docs matching the code) live in `refactor-and-integrate/SKILL.md`. Load both at the `integration` stage.

## Consistency with the codebase

- `[BLOCKING]` **No redundant intermediary datasets.** An intermediate dataset already serving a similar purpose gets reused or extended, not near-duplicated with minor variations. Same for intermediate code modules — consolidate, don't fork.
- `[BLOCKING]` **Variable-construction consistency.** New code follows the codebase's existing definition (log growth, Davis-Haltiwanger growth, 1/99 winsorization) unless the deviation is documented and justified. Check the nearest `CLAUDE.md` / `AGENTS.md` / `README.md` and any shared utility module before writing a new construction.
- `[BLOCKING]` **Transformation-pattern consistency.** Winsorization thresholds, outlier treatment, sample filters, and control variables align with established codebase patterns — or the deviation is documented with reason.
- `[BLOCKING]` **Variable naming consistency.** Names match existing conventions for the same economic concept — a codebase using `ret_vw` does not gain a `vw_return`.
- `[BLOCKING]` **Sample construction preserved** unless the researcher authorized a change. Sample filters, exclusions, and panel scope match prior usage, or the deviation is documented.
- `[BLOCKING]` **Document-code consistency.** Results feeding papers, slides, notes, or long-standing downstream artifacts (in the repo or the researcher's named location): reconcile numerical and methodological inconsistencies between the refactored code and those artifacts. Reconciliation out of scope for this refactor: flag the unreconciled inconsistencies in the task's `## Results` §Limitations.

## Data discipline preserved through refactoring

**Refactored code is re-validated, not carried forward.** Refactoring silently changes data flow, merge order, floating-point accumulation, or sample composition.

- `[BLOCKING]` **Every data-discipline artifact survives and still runs on the refactored code** — describe steps (panel structure, variable diagnostics, missing-value patterns), `before → after` row-count prints at every sample-changing operation, and the §Validate sanity, distribution-shift, and economic-sense checks. Logged counts match pre-refactor counts or the change is explained. Copying the output forward is not survival; reorganize freely, delete nothing.
- `[BLOCKING]` **Drift tests pass post-refactor.** Where drift tests exist, they pass on the refactored code; failures are adjudicated per `references/integrate-drift-tests.md`, never silently re-expected.
- `[BLOCKING]` **Jupytext/markdown documentation cells describe what the refactored code actually does** — not what the pre-refactor code did.

## Utility reuse and documented deviations

- `[BLOCKING]` **Shared transformations refactored into utilities.** Similar transformations across the codebase consolidate into utility functions instead of per-analysis re-implementation. Helper exists: call it. New code would duplicate a helper elsewhere: lift it to the shared utility module.
- `[BLOCKING]` **Documented deviations.** Any intentional departure from codebase patterns (winsorization threshold, control set, sample filter, variable construction) carries a markdown-cell or comment explaining why — "use 5/95 here because the outer tails are the subject of study". Undocumented deviation is a REVISE finding even when defensible.
- `[ADVISORY]` **Migration pointers on consolidation.** Replacing a pattern with a newer/better-documented implementation: prefer the newer location, and if other code still references the old one, leave a one-line migration pointer (comment in the old file, note in the nearest module doc) so follow-on analyses do not re-fork the old version.
