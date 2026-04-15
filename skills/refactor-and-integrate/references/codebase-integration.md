# Codebase Integration Standards

Shared cross-cutting code-quality reference for code refactoring and integration review. Both the implementer (refactorer) and reviewer use this checklist.

> **Primary references for data-analysis work:** load BOTH the active domain skill's §Refactor integrity — for data analysis that is `econ-data-analysis/SKILL.md` §Review & Self-Check Discipline §Refactor integrity — AND `econ-data-analysis/references/integration.md` for the data-analysis-specific integration gates (no redundant intermediaries, variable-construction consistency, transformation-pattern consistency, data discipline preserved through refactoring, documented deviations). This file then covers the generic cross-cutting code-quality companion (naming, utility reuse, PR-friendly diffs, debug-artifact cleanup, documentation currency) that applies regardless of domain.

## Code Integration

- [ ] **Naming consistency:** Variable names, function names, and file names follow codebase conventions
- [ ] **Utility usage:** Existing utility functions are used where appropriate instead of hand-rolled equivalents
- [ ] **Code simplification:** Redundant code removed, repeated patterns consolidated, readability improved
- [ ] **No debug artifacts:** No leftover debug prints, commented-out experiments, or temporary variables
- [ ] **Minimal existing-file changes:** Modifications to files outside the analysis scope are minimal and justified (e.g., adding an import to a shared module is fine; restructuring a shared module is not)
- [ ] **PR-friendly diffs:** Changes produce clean, reviewable diffs — avoid unnecessary reformatting that obscures substantive changes

## Handling Inconsistencies

When you find inconsistencies between new code and existing codebase:

- **Clear convention exists:** Follow the convention.
- **Ambiguous or conflicting conventions:** Use best judgment and document the choice.
- **Methodological question** (e.g., different control variable set, different variable definition): Do NOT resolve — flag for the user. This is a research decision, not a code quality decision. Domain-specific gates for data analysis live in the domain integration reference cited in the blockquote above.

## PR Quality

- [ ] **Focused diff:** Changes limited to analysis scope; no unrelated formatting or restructuring
- [ ] **Clean commits:** Commit history is logical and messages are descriptive
- [ ] **Self-contained:** The analysis can be understood from the code and its documentation without external context
- [ ] **Appropriate tolerances** documented and economically reasonable (where drift tests exist)

## Documentation Currency

- [ ] **Module CLAUDE.md / AGENTS.md / README.md** do not reference files, functions, outputs, or methodology that no longer exist or have been superseded by the refactored code
- [ ] **No stale output lists:** Every output file mentioned in documentation is actually produced by the current code
- [ ] **Dates and version claims** ("as of ...") reflect the current commit, not a prior state
