# Integration Discipline for Data Analysis

> This reference is the single source of truth for data-analysis integration discipline at the `refactoring` and `integration review` stages. The implementer walks it as pre-handoff self-check; the reviewer walks it as verification criteria. Same content, two perspectives — no drift possible. `[GATING]` items block unconditional APPROVE; `[STANDARD]` items become REVISE findings; `[ADVISORY]` items are suggestions the reviewer MAY flag as MINOR. The verdict protocol is the same as `econ-data-analysis/SKILL.md` §Review & Self-Check Discipline (APPROVE / REVISE / CONDITIONAL APPROVE).

Generic cross-cutting code-integration concerns (naming consistency, utility reuse, PR-friendly diffs, documentation currency) live in `refactor-and-integrate/references/codebase-integration.md`. Load both files at the `refactoring` and `integration review` stages — this one owns the data-analysis-specific gates; the generic file owns the cross-cutting code-quality gates.

## Consistency with the codebase

- `[GATING]` **No redundant intermediary datasets.** If an intermediate dataset already exists for a similar purpose, reuse or extend it; do not create a parallel near-duplicate with minor variations. Same applies to intermediate code modules — consolidate rather than fork.
- `[GATING]` **Variable-construction consistency.** If the codebase constructs a variable a specific way (log growth, Davis-Haltiwanger growth, 1/99 winsorization), new code follows the same definition unless there is a documented, justified deviation. Cross-reference the nearest `CLAUDE.md` / `AGENTS.md` / `README.md` and any shared utility module before writing a new construction.
- `[GATING]` **Transformation-pattern consistency.** Winsorization thresholds, outlier treatment, sample filters, and control variables align with established codebase patterns — or the deviation is documented with reason.
- `[STANDARD]` **Variable naming consistency.** Names match existing conventions for the same economic concept (e.g., if the codebase uses `ret_vw` for value-weighted returns, new code does not introduce `vw_return`).
- `[STANDARD]` **Sample construction preserved** unless the researcher has authorized a change. Sample filters, exclusions, and the panel scope used in the new analysis match prior usage in the codebase, or the deviation is documented.
- `[STANDARD]` **Document-code consistency.** If the analysis results feed into papers, slides, notes, or long-standing downstream artifacts in the repo (or in the researcher's named location), reconcile numerical and methodological inconsistencies between the refactored code and those artifacts. If reconciliation is out of scope for this refactor, flag unreconciled inconsistencies in `RESULTS.md` §Limitations.

## Data discipline preserved through refactoring

**Refactored code must be re-validated, not just carried forward.** Refactoring can silently change data flow, merge order, floating-point accumulation, or sample composition — the same safeguards that the original code needed, the refactored code needs again.

- `[GATING]` **Describe steps survive the refactor.** Panel-structure diagnostics, variable diagnostics, and missing-value patterns described before the first transformation still run on the refactored code, not just copied over from the original. Never silently dropped.
- `[GATING]` **Row-count prints at every sample-changing operation survive.** Every merge, filter, drop, deduplication, or sample restriction prints `before → after` counts in the refactored code, and the logged counts match the pre-refactor counts (or any change is explained).
- `[GATING]` **Validation checks survive.** Sanity checks, distribution-shift comparisons, and economic-sense checks from §Validate are present in the refactored code and were re-executed successfully after refactoring.
- `[GATING]` **Drift tests pass post-refactor.** Where drift tests exist, they pass on the refactored code; failures are adjudicated per `references/integrate-drift-tests.md`, never silently re-expected.
- `[STANDARD]` **Jupytext/markdown documentation cells describe what the refactored code actually does** — not what the pre-refactor code did.
- `[STANDARD]` **No data discipline artifact** (description, row count log, validation check, markdown justification) has been deleted during refactoring. Reorganize freely; delete nothing.

## Utility reuse and documented deviations

- `[STANDARD]` **Shared transformations refactored into utilities.** Similar data transformations across the codebase consolidate into utility functions rather than re-implementation per analysis. If a helper already exists, call it; if the new code would create a helper duplicated elsewhere, lift it to the shared utility module.
- `[STANDARD]` **Documented deviations.** Any intentional departure from codebase patterns (different winsorization threshold, different control set, different sample filter, alternative variable construction) carries a markdown-cell or comment explaining why (e.g., "use 5/95 here because the outer tails are the subject of study"). Undocumented deviation is a REVISE finding even when the deviation itself is defensible.
- `[ADVISORY]` **Migration pointers on consolidation.** When replacing a pattern with a newer/better-documented implementation, prefer the newer location; if other code still references the old location, leave a one-line migration pointer (e.g., a comment in the old file or a note in the nearest module doc) so follow-on analyses do not silently re-fork the old version.

## Reviewer verdict protocol

Same as `econ-data-analysis/SKILL.md` §Review & Self-Check Discipline: **walk the entire file top to bottom even when a gating item fails.** One comprehensive pass per dispatch.

- **APPROVE** — no findings at any severity.
- **REVISE** — only `[STANDARD]` items failed.
- **CONDITIONAL APPROVE** — one or more `[GATING]` items failed; the reviewer walked the rest of this file and of `codebase-integration.md` anyway, and those downstream items look correct conditional on the gating fix not invalidating them. The review-notes blockquote lists the failed `[GATING]` item(s) first, then states "downstream items reviewed and currently correct; approval contingent on the gating fix not changing downstream results."

On a re-dispatch following a CONDITIONAL APPROVE, the reviewer's second pass is narrow: (1) verify the gating fix is correct, (2) verify the cited downstream items still hold under the fix.
