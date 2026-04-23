# Codebase Integration Standards

Shared cross-cutting code-quality reference for post-sync code refactoring and integration review. Both the implementer (refactorer) and reviewer walk the gated checklist at the bottom; the how-to sections above give the procedures and decision trees the checklist items encode. Loaded whenever `Stage:` is `integration` (per `superRA:using-superra` §Skill-Load Manifest).

> **Primary reference for data-analysis work:** load `econ-data-analysis/references/integration.md` for the data-analysis-specific integration gates (codebase consistency, data discipline preserved through refactoring, utility reuse, documented deviations — with `[BLOCKING]` / `[ADVISORY]` markers and its own reviewer verdict protocol). This file covers the generic cross-cutting code-quality companion (naming, utility reuse, PR-friendly diffs, debug-artifact cleanup, documentation currency) that applies regardless of domain.

---

## How-To

### Handling inconsistencies — decision tree

When you find inconsistencies between new code and existing codebase:

- **Clear convention exists:** Follow the convention.
- **Ambiguous or conflicting conventions:** Use best judgment and document the choice.
- **Methodological question** (e.g., different control variable set, different variable definition): Do NOT resolve — flag for the user. This is a research decision, not a code quality decision. Domain-specific gates for data analysis live in the domain integration reference cited in the blockquote above.

### Project Doc Audit — walk-up algorithm

Integrate-step refactoring and integration review both cover project-level documentation reachable from the diff — the nested guidance docs that superRA deliberately places near code and that the harness does NOT auto-surface. The goal is to catch stale module-level claims, document new patterns at the right level, and keep the CLAUDE.md / AGENTS.md pair in sync before Finish.

For every file in the diff `<BASE_SHA>..<HEAD_SHA>`, walk up from its directory to the repo root and collect every `CLAUDE.md` / `AGENTS.md` / `README.md` encountered. Always also check the repo-root `README.md` and root `CLAUDE.md` regardless of the diff (stale skill counts and top-level claims live there).

For each doc in the set:

- **Update stale claims** — command names, file paths, architectural notes, skill counts, any statement contradicted by the diff.
- **Add new patterns or modules** — if the diff introduced a new module directory, feature, or command, document it at the correct level (nearest CLAUDE.md to the new code, not blasted into parent docs).
- **Do not duplicate parent-level content** — link instead. Module-level docs should carry module-specific conventions, not repeat what repo-root docs already cover.
- **Create missing CLAUDE.md + AGENTS.md pair for new modules** — if a new module directory has no guidance doc, create `CLAUDE.md` with purpose/conventions, then create a relative symlink `AGENTS.md -> CLAUDE.md` (just the filename, not an absolute path). If only one of the pair exists in an existing directory, unify them via symlink (keep the richer file).

Do **not** propagate upward for the sake of it: leave `CLAUDE.md` / `AGENTS.md` above the affected area alone unless something in them is stale.

The refactorer applies this as part of the refactoring pass; the integration reviewer verifies it as part of integration review. Results-level documentation (`RESULTS.md` itself) is a separate concern — it matures during `integration-workflow` Document via the doc-writer + doc-reviewer pair.

---

### Sync Map obligations

When PLAN.md contains `## Sync Map`, treat its `Post-sync obligations` entries as review evidence. The integration reviewer turns open obligations into task-local review notes, and the refactor implementer satisfies accepted obligations during the Integrate step. The orchestrator removes `## Sync Map` only after integration review APPROVES and the full drift-test suite passes.

## Reviewer Verdict Protocol

Every reviewer walks top-to-bottom through the Minimum-net-diff top item (in SKILL.md) plus every discipline's checklist that the task touches. **Never halt on a failure** — one comprehensive pass every time; halting early forces a full re-review on the next pass, and reviewer dispatches are costly.

Two verdicts:

- **APPROVE** — no `[BLOCKING]` findings.
- **REVISE** — at least one `[BLOCKING]` finding.

**Handling dependent findings.** When a later finding's assessment depends on an earlier `[BLOCKING]` item being fixed first (e.g., "couldn't fully assess the refactor until the drift tests are passing"), say so in plain prose alongside the finding. No separate verdict, no formal tag.

**Re-review after REVISE.** Implementer fixes all `[BLOCKING]` findings and re-dispatches. Reviewer then (1) verifies each fix is correct, and (2) re-checks any finding the first pass annotated as depending on an upstream fix. Everything else is accepted from the first pass — no third full walk. APPROVE once all `[BLOCKING]` findings are resolved.

**Implementer self-check (before every commit).** Run before every commit on the integration branch:

1. **Compute the cumulative diff from the governing baseline.** In integration-workflow after Sync, use `git diff <BASE_HEAD_SHA>..HEAD`. In standalone refactor work, use the caller-provided git range or touched-file diff.
2. **Review every hunk** against the loaded references' checklists, approved task objectives, Sync Map obligations, and logged user decisions. For each hunk, ask: *which `[BLOCKING]` / `[ADVISORY]` item, approved objective, Sync Map obligation, or user decision justifies this change?*
3. **Any hunk without a justification is out of scope.** Revert it, OR re-justify it by adding the underlying need to the Sync Map, task-local review notes, or commit message so the reviewer can check the same evidence.
4. **Respect the post-sync baseline.** Base-current deletions and relocations are already represented in `BASE_HEAD_SHA`; do not restore or contradict them unless an approved objective, Sync Map obligation, or logged user decision requires it.
5. **Respect the dispatch's scope list.** Refactor implementer and integration reviewer operate only on tasks whose `Integration status` is unset or `REVISE` — named explicitly in the dispatch's `Task:` or `Tasks in scope:` field. `APPROVED`-integration tasks are out of scope unless the Sync Map or accepted reviewer finding names them.
6. **Stage only files you touched this turn** (per `superRA:using-superra` §Commit Hygiene); `git diff --cached` before `git commit`.

The integration reviewer runs the same governing diff as evidence and walks each hunk through the same reference checklists. One source of truth, two perspectives.

---

## Gated Checklist

Walk every item. `[BLOCKING]` items must be satisfied for APPROVE; `[ADVISORY]` items MAY be flagged as MINOR but do not block APPROVE.

**Code integration:**

- `[BLOCKING]` **Governing-diff pruning performed:** Every surviving hunk in the governing diff ties to an approved task objective, Sync Map obligation, logged user decision, or checklist requirement.
- `[BLOCKING]` **Base-current deletions / relocations honored by default:** Restorations exist only when an approved task objective, Sync Map obligation, or logged user decision requires them.
- `[BLOCKING]` **Naming consistency:** Variable names, function names, and file names follow codebase conventions.
- `[BLOCKING]` **Utility usage:** Existing utility functions are used where appropriate instead of hand-rolled equivalents.
- `[BLOCKING]` **No debug artifacts:** No leftover debug prints, commented-out experiments, or temporary variables.
- `[BLOCKING]` **Minimal existing-file changes:** Modifications to files outside the analysis scope are minimal and justified (adding an import to a shared module is fine; restructuring a shared module is not).
- `[ADVISORY]` **Code simplification:** Redundant code removed, repeated patterns consolidated, readability improved — only where the refactor task or Sync Map demanded the touch.
- `[ADVISORY]` **PR-friendly diffs:** Changes produce clean, reviewable diffs — avoid unnecessary reformatting that obscures substantive changes.

**Handling inconsistencies (decision tree in §How-To → Handling inconsistencies):**

- `[BLOCKING]` **Methodological questions escalated, not resolved.** Different control variable sets, different variable definitions, different sample filters — these are research decisions, not code-quality decisions. Flag for the user; do not choose silently. Domain-specific methodological gates for data analysis live in `econ-data-analysis/references/integration.md`.
- `[ADVISORY]` **Clear convention exists:** follow the convention. **Ambiguous or conflicting conventions:** use best judgment and document the choice.

**PR quality:**

- `[BLOCKING]` **Focused diff:** Changes limited to analysis scope; no unrelated formatting or restructuring. (Reinforced by the governing-baseline minimum-net-diff top item in SKILL.md.)
- `[BLOCKING]` **Self-contained:** The analysis can be understood from the code and its documentation without external context.
- `[ADVISORY]` **Clean commits:** Commit history is logical and messages are descriptive.
- `[ADVISORY]` **Appropriate tolerances** documented and economically reasonable (where drift tests exist).

**Documentation currency:**

- `[BLOCKING]` **Module CLAUDE.md / AGENTS.md / README.md** do not reference files, functions, outputs, or methodology that no longer exist or have been superseded by the refactored code.
- `[BLOCKING]` **No stale output lists:** Every output file mentioned in documentation is actually produced by the current code.
- `[BLOCKING]` **Dates and version claims** ("as of ...") reflect the current commit, not a prior state.

**Project Doc Audit (walk-up algorithm in §How-To → Project Doc Audit):**

- `[BLOCKING]` Walk-up executed for every file in the diff `<BASE_SHA>..<HEAD_SHA>`; repo-root `README.md` and root `CLAUDE.md` also checked. Stale claims updated, new patterns added at the correct level, parent-level content not duplicated, missing `CLAUDE.md` + `AGENTS.md` pair created for new module directories, and docs above the affected area left alone unless stale.
