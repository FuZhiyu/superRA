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

## Data Discipline Preservation

**CRITICAL: Never remove data discipline artifacts during refactoring.**

- [ ] Data description steps preserved
- [ ] Row count logging preserved
- [ ] Validation checks preserved
- [ ] Jupytext documentation cells preserved
- [ ] You may reorganize these artifacts but never delete them

See the loaded `econ-data-analysis` skill for the full list of data discipline artifacts.

## Handling Inconsistencies

When you find inconsistencies between new analysis code and existing codebase:

- **Clear convention exists:** Follow the convention (e.g., codebase always winsorizes at 1/99 but new code uses 5/95)
- **Ambiguous or conflicting conventions:** Use best judgment and document the choice
- **Methodological question** (e.g., different control variable set): Do NOT resolve — flag for the user. This is a research decision, not a code quality decision.

## Drift Assessment

After refactoring, run drift tests. If all pass, proceed.

If any fail:
- **Identify what changed** — compare before/after values
- **Minor variation** (floating-point differences from reordered operations, trivially different rounding): Update test expectation with a comment explaining the change. Proceed.
- **Meaningful change** (coefficient changes direction, significance changes, sample size changes, economically different magnitude): **STOP.** Do not update the test. Report the drift to the orchestrator so the user can be consulted.

## PR Quality

- [ ] **Focused diff:** Changes limited to analysis scope; no unrelated formatting or restructuring
- [ ] **Clean commits:** Commit history is logical and messages are descriptive
- [ ] **Self-contained:** The analysis can be understood from the code and its documentation without external context
- [ ] **Drift tests exist and pass** on the refactored code
- [ ] **Appropriate tolerances** documented and economically reasonable
