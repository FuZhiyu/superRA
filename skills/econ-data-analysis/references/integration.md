# Integration Discipline for Data Analysis

> This reference is the single source of truth for data-analysis integration discipline at the `integration` stage. The implementer walks it as pre-handoff self-check; the reviewer walks it as verification criteria. Same content, two perspectives — no drift possible. `[BLOCKING]` items must be fixed to earn APPROVE; `[ADVISORY]` items are suggestions the reviewer MAY flag as MINOR and do not block APPROVE. The verdict protocol is the same as `econ-data-analysis/SKILL.md` §Three Concurrent Disciplines — two verdicts (APPROVE / REVISE).

Generic cross-cutting code-integration concerns (naming consistency, utility reuse, PR-friendly diffs, documentation currency) live in `refactor-and-integrate/references/codebase-integration.md`. Load both files at the `integration` stage — this one owns the data-analysis-specific gates; the generic file owns the cross-cutting code-quality gates.

## Consistency with the codebase

- `[BLOCKING]` **No redundant intermediary datasets.** If an intermediate dataset already exists for a similar purpose, reuse or extend it; do not create a parallel near-duplicate with minor variations. Same applies to intermediate code modules — consolidate rather than fork.
- `[BLOCKING]` **Variable-construction consistency.** If the codebase constructs a variable a specific way (log growth, Davis-Haltiwanger growth, 1/99 winsorization), new code follows the same definition unless there is a documented, justified deviation. Cross-reference the nearest `CLAUDE.md` / `AGENTS.md` / `README.md` and any shared utility module before writing a new construction.
- `[BLOCKING]` **Transformation-pattern consistency.** Winsorization thresholds, outlier treatment, sample filters, and control variables align with established codebase patterns — or the deviation is documented with reason.
- `[BLOCKING]` **Variable naming consistency.** Names match existing conventions for the same economic concept (e.g., if the codebase uses `ret_vw` for value-weighted returns, new code does not introduce `vw_return`).
- `[BLOCKING]` **Sample construction preserved** unless the researcher has authorized a change. Sample filters, exclusions, and the panel scope used in the new analysis match prior usage in the codebase, or the deviation is documented.
- `[BLOCKING]` **Document-code consistency.** If the analysis results feed into papers, slides, notes, or long-standing downstream artifacts in the repo (or in the researcher's named location), reconcile numerical and methodological inconsistencies between the refactored code and those artifacts. If reconciliation is out of scope for this refactor, flag unreconciled inconsistencies in `RESULTS.md` §Limitations.

## Data discipline preserved through refactoring

**Refactored code must be re-validated, not just carried forward.** Refactoring can silently change data flow, merge order, floating-point accumulation, or sample composition — the same safeguards that the original code needed, the refactored code needs again.

- `[BLOCKING]` **Describe steps survive the refactor.** Panel-structure diagnostics, variable diagnostics, and missing-value patterns described before the first transformation still run on the refactored code, not just copied over from the original. Never silently dropped.
- `[BLOCKING]` **Row-count prints at every sample-changing operation survive.** Every merge, filter, drop, deduplication, or sample restriction prints `before → after` counts in the refactored code, and the logged counts match the pre-refactor counts (or any change is explained).
- `[BLOCKING]` **Validation checks survive.** Sanity checks, distribution-shift comparisons, and economic-sense checks from §Validate are present in the refactored code and were re-executed successfully after refactoring.
- `[BLOCKING]` **Drift tests pass post-refactor.** Where drift tests exist, they pass on the refactored code; failures are adjudicated per `references/integrate-drift-tests.md`, never silently re-expected.
- `[BLOCKING]` **Jupytext/markdown documentation cells describe what the refactored code actually does** — not what the pre-refactor code did.
- `[BLOCKING]` **No data discipline artifact** (description, row count log, validation check, markdown justification) has been deleted during refactoring. Reorganize freely; delete nothing.

## Utility reuse and documented deviations

- `[BLOCKING]` **Shared transformations refactored into utilities.** Similar data transformations across the codebase consolidate into utility functions rather than re-implementation per analysis. If a helper already exists, call it; if the new code would create a helper duplicated elsewhere, lift it to the shared utility module.
- `[BLOCKING]` **Documented deviations.** Any intentional departure from codebase patterns (different winsorization threshold, different control set, different sample filter, alternative variable construction) carries a markdown-cell or comment explaining why (e.g., "use 5/95 here because the outer tails are the subject of study"). Undocumented deviation is a REVISE finding even when the deviation itself is defensible.
- `[ADVISORY]` **Migration pointers on consolidation.** When replacing a pattern with a newer/better-documented implementation, prefer the newer location; if other code still references the old location, leave a one-line migration pointer (e.g., a comment in the old file or a note in the nearest module doc) so follow-on analyses do not silently re-fork the old version.

## Reviewer verdict protocol

Same as `econ-data-analysis/SKILL.md` §Three Concurrent Disciplines: **walk this file and `codebase-integration.md` top to bottom. Never halt on a failure.** One comprehensive pass per dispatch.

Two verdicts:

- **APPROVE** — no `[BLOCKING]` findings.
- **REVISE** — at least one `[BLOCKING]` finding.

When a finding's assessment depends on an earlier `[BLOCKING]` item being fixed first, note that dependency in plain prose alongside the finding. On re-dispatch after REVISE, the reviewer verifies each fix and re-checks any finding annotated as depending on an upstream fix — everything else is accepted from the first pass.
