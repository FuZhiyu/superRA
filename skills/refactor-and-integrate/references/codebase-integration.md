# Codebase Integration Standards

Cross-cutting reference for codebase-coherence refactoring and integration review. Implementer (refactorer) and reviewer both walk the gated checklist; the how-to sections give the procedures and decision trees the checklist encodes.

---

## How-To

### Handling inconsistencies — decision tree

When you find inconsistencies between new code and existing codebase:

- **Clear convention exists:** Follow the convention.
- **Ambiguous or conflicting conventions:** Use best judgment and document the choice.
- **Methodological question** (e.g., different control variable set, different variable definition): Do NOT resolve — flag for the user. This is a research decision, not a code quality decision. 

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

### Sync impact context

When PLAN.md task blocks contain `**Sync impact:**`, use those fields as evidence for why a hunk already exists in the governing diff. Follow the referenced Sync Map cluster only when needed to evaluate that hunk.

Sync impact justifies existing hunks only when it is already present; it does not create new refactor targets or excuse unrelated codebase changes.

## Reviewer Verdict Protocol

Every reviewer walks top-to-bottom through the Minimum Net Diff section in `SKILL.md` plus this checklist. **Never halt on a failure** — one comprehensive pass every time; halting early forces a full re-review on the next pass.

Two verdicts:

- **APPROVE** — no `[BLOCKING]` findings.
- **REVISE** — at least one `[BLOCKING]` finding.

**Handling dependent findings.** When a later finding's assessment depends on an earlier `[BLOCKING]` item being fixed first, say so in plain prose alongside the finding. No separate verdict, no formal tag.

**Re-review after REVISE.** Implementer fixes all `[BLOCKING]` findings and re-dispatches. Reviewer then (1) verifies each fix is correct, and (2) re-checks any finding the first pass annotated as depending on an upstream fix. Everything else is accepted from the first pass — no third full walk. APPROVE once all `[BLOCKING]` findings are resolved.

**Implementer Final Diff Self-Check.** Run immediately before every return or commit, including no-change cases:

1. **Recompute the governing diff.** In integration-workflow after Sync, use `git diff <BASE_HEAD_SHA>..HEAD`. In standalone refactor work, use the caller-provided git range or touched-file diff.
2. **Leave a compact trail.** In the assigned PLAN.md task block when one exists, write or refresh `**Final diff self-check:** <command/range>; <no surviving hunks OR surviving-change classes>; <suspicious hunk justifications or none>`. Without PLAN.md, put the same line in the status return.
3. **Summarize ordinary hunks by class.** Examples: "utility reuse in task scripts", "module README currency", "test contract wording". Do not justify every line when the class is already covered by the task objective or checklist.
4. **Justify suspicious hunks by file and line/hunk.** Suspicious cases are: `skills/*` or `agents/*` instruction edits, prior overprescription or scope-creep findings, base-side restorations or relocations, touched tasks already marked `Integration status: APPROVED`, broad formatting or rewrite hunks, and changes justified only by Sync impact. Apply any local instruction-prose gate only to files that local guidance covers.
5. **Prune or record.** Any hunk without a current justification is out of scope. Revert it, or record the underlying need where the reviewer can verify it.
6. **Respect the dispatch's scope list.** Refactor implementer and integration reviewer operate only on tasks whose `Integration status` is unset or `REVISE` and tasks explicitly reopened by accepted review findings.
7. **Stage only files you touched this turn** (per `superRA:using-superra` §Commit Hygiene); `git diff --cached` before `git commit`.

The integration reviewer recomputes the same governing diff and compares it with the self-check trail. A missing or stale trail is `[BLOCKING]`, including when no code changed.

---

## Gated Checklist

Walk every item. `[BLOCKING]` items must be satisfied for APPROVE; `[ADVISORY]` items MAY be flagged as MINOR but do not block APPROVE.

**Code integration:**

- `[BLOCKING]` **Final Diff Self-Check present and fresh:** The trail names the governing command/range, records no-change outcomes or surviving-change classes, and gives file/hunk justification for suspicious cases.
- `[BLOCKING]` **Governing-diff pruning performed line by line:** Every surviving hunk in the governing diff ties to an approved task objective, supplied Sync impact context, logged user decision, or checklist requirement; unrelated cleanup, formatting churn, and stale branch-side restorations are removed.
- `[BLOCKING]` **Base-current deletions / relocations honored by default:** Restorations exist only when an approved task objective, supplied Sync impact context, logged user decision, or checklist requirement requires them.
- `[BLOCKING]` **Naming consistency:** Variable names, function names, and file names follow codebase conventions.
- `[BLOCKING]` **Utility usage:** Existing utility functions are used where appropriate instead of hand-rolled equivalents.
- `[BLOCKING]` **No debug artifacts:** No leftover debug prints, commented-out experiments, or temporary variables.
- `[BLOCKING]` **Minimal existing-file changes:** Modifications to files outside the analysis scope are minimal and justified (adding an import to a shared module is fine; restructuring a shared module is not).
- `[ADVISORY]` **Code simplification:** Redundant code removed, repeated patterns consolidated, readability improved — only where the refactor task or codebase-coherence review demanded the touch.
- `[ADVISORY]` **PR-friendly diffs:** Changes produce clean, reviewable diffs — avoid unnecessary reformatting that obscures substantive changes.

**Handling inconsistencies (decision tree in §How-To → Handling inconsistencies):**

- `[BLOCKING]` **Methodological questions escalated, not resolved.** Different control variable sets, different variable definitions, different sample filters — these are research decisions, not code-quality decisions. Flag for the user; do not choose silently.
- `[ADVISORY]` **Clear convention exists:** follow the convention. **Ambiguous or conflicting conventions:** use best judgment and document the choice.

**PR quality:**

- `[BLOCKING]` **Focused diff:** Changes limited to analysis scope; no unrelated formatting or restructuring. (Reinforced by the governing-baseline minimum-net-diff top item in SKILL.md.)
- `[BLOCKING]` **Self-contained:** The analysis can be understood from the code and its documentation without external context.
- `[ADVISORY]` **Clean commits:** Commit history is logical and messages are descriptive.

**Documentation currency:**

- `[BLOCKING]` **Module CLAUDE.md / AGENTS.md / README.md** do not reference files, functions, outputs, or methodology that no longer exist or have been superseded by the refactored code.
- `[BLOCKING]` **No stale output lists:** Every output file mentioned in documentation is actually produced by the current code.
- `[BLOCKING]` **Dates and version claims** ("as of ...") reflect the current commit, not a prior state.

**Project Doc Audit (walk-up algorithm in §How-To → Project Doc Audit):**

- `[BLOCKING]` Walk-up executed for every file in the diff `<BASE_SHA>..<HEAD_SHA>`; repo-root `README.md` and root `CLAUDE.md` also checked. Stale claims updated, new patterns added at the correct level, parent-level content not duplicated, missing `CLAUDE.md` + `AGENTS.md` pair created for new module directories, and docs above the affected area left alone unless stale.
