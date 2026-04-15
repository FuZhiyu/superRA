# Codebase Integration Standards

Shared domain reference for code refactoring and integration review. Both the implementer (refactorer) and reviewer use this checklist.

## Code Integration

- [ ] **Naming consistency:** Variable names, function names, and file names follow codebase conventions
- [ ] **Utility usage:** Existing utility functions are used where appropriate instead of hand-rolled equivalents
- [ ] **Code simplification:** Redundant code removed, repeated patterns consolidated, readability improved
- [ ] **No debug artifacts:** No leftover debug prints, commented-out experiments, or temporary variables
- [ ] **Minimal existing-file changes:** Modifications to files outside the analysis scope are minimal and justified (e.g., adding an import to a shared module is fine; restructuring a shared module is not)
- [ ] **PR-friendly diffs:** Changes produce clean, reviewable diffs — avoid unnecessary reformatting that obscures substantive changes

## Economic Integration

- [ ] **Specification consistency:** Control variables, time periods, sample restrictions align with existing codebase conventions — or differences are documented and justified
- [ ] **Transformation consistency:** Data transformations (winsorization, outlier treatment, variable construction) use codebase-standard approaches — or differences are documented
- [ ] **Justified inconsistencies:** Any intentional deviations from codebase patterns have clear documentation explaining why

## Data Discipline Through Refactoring

**CRITICAL: Refactored code must be re-validated, not just carried forward.** Refactoring can silently change data flow, merge order, floating-point accumulation, or sample composition — the same safeguards that the original code needed, the refactored code needs again.

- [ ] Data description steps are present in the refactored code and were re-run against the refactored output (not just copied over from the original).
- [ ] Row count is logged at every sample-changing step in the refactored code, and the logged counts match the pre-refactor counts (or any change is explained).
- [ ] Validation checks are present in the refactored code and were re-executed successfully after refactoring.
- [ ] Jupytext documentation cells are present and describe what the refactored code actually does — not what the pre-refactor code did.
- [ ] No data discipline artifact (description, row count log, validation check) has been deleted during refactoring. Reorganize freely; delete nothing.

See the loaded `econ-data-analysis` skill for the full list of data discipline artifacts and the three concurrent disciplines (Describe / Analyze / Validate) that every refactored step must re-run through.

## Handling Inconsistencies

When you find inconsistencies between new analysis code and existing codebase:

- **Clear convention exists:** Follow the convention (e.g., codebase always winsorizes at 1/99 but new code uses 5/95)
- **Ambiguous or conflicting conventions:** Use best judgment and document the choice
- **Methodological question** (e.g., different control variable set): Do NOT resolve — flag for the user. This is a research decision, not a code quality decision.

## PR Quality

- [ ] **Focused diff:** Changes limited to analysis scope; no unrelated formatting or restructuring
- [ ] **Clean commits:** Commit history is logical and messages are descriptive
- [ ] **Self-contained:** The analysis can be understood from the code and its documentation without external context
- [ ] **Drift tests exist and pass** on the refactored code
- [ ] **Appropriate tolerances** documented and economically reasonable

## Documentation Currency

- [ ] **Module CLAUDE.md / AGENTS.md / README.md** do not reference files, functions, outputs, or methodology that no longer exist or have been superseded by the refactored code
- [ ] **No stale output lists:** Every output file mentioned in documentation is actually produced by the current code
- [ ] **Dates and version claims** ("as of ...") reflect the current commit, not a prior state
