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

## Project Doc Audit

Stage 2 refactoring and integration review both cover project-level documentation reachable from the diff — the nested guidance docs that superRA deliberately places near code and that the harness does NOT auto-surface. The goal is to catch stale module-level claims, document new patterns at the right level, and keep the CLAUDE.md / AGENTS.md pair in sync before merge.

For every file in the diff `<BASE_SHA>..<HEAD_SHA>`, walk up from its directory to the repo root and collect every `CLAUDE.md` / `AGENTS.md` / `README.md` encountered. Always also check the repo-root `README.md` and root `CLAUDE.md` regardless of the diff (stale skill counts and top-level claims live there).

For each doc in the set:

- **Update stale claims** — command names, file paths, architectural notes, skill counts, any statement contradicted by the diff.
- **Add new patterns or modules** — if the diff introduced a new module directory, feature, or command, document it at the correct level (nearest CLAUDE.md to the new code, not blasted into parent docs).
- **Do not duplicate parent-level content** — link instead. Module-level docs should carry module-specific conventions, not repeat what repo-root docs already cover.
- **Create missing CLAUDE.md + AGENTS.md pair for new modules** — if a new module directory has no guidance doc, create `CLAUDE.md` with purpose/conventions, then create a relative symlink `AGENTS.md -> CLAUDE.md` (just the filename, not an absolute path). If only one of the pair exists in an existing directory, unify them via symlink (keep the richer file).

Do **not** propagate upward for the sake of it: leave `CLAUDE.md` / `AGENTS.md` above the affected area alone unless something in them is stale.

The refactorer applies this as part of the refactoring pass; the integration reviewer verifies it as part of integration review. Results-level documentation (`RESULTS.md` itself) is a separate concern — it matures at `integration-workflow` Step 3 via the doc-writer + doc-reviewer pair.
