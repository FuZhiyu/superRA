---
name: refactor-and-integrate
description: Utility skill (any phase). Use when refactoring analysis code for codebase integration, reviewing post-sync branch quality, auditing project docs, pruning a governing diff to minimum net diff, or using task-local Sync impact context as justification evidence. Carries the Codebase Integration checklist shared by implementer (self-check before commit) and reviewer (verification). Standalone-invokable outside the full integration workflow for any refactor that needs consistent quality gates.
---

# Refactor and Integrate

Tool skill for **codebase coherence**: convention fit, utility reuse, Project Doc Audit, PR-friendly diffs, and minimum net diff against the governing baseline.

Techniques:

1. **Codebase-fit refactoring** — align names and utility reuse with host conventions, walk up project docs, and keep diffs reviewable.
2. **Governing-diff pruning** — minimize the surviving diff against the caller's baseline or range.
3. **Sync impact as evidence** — when task-local Sync impact exists, use it to justify existing post-sync hunks; it does not create new refactor targets.

The active domain skill's stage-load table routes any domain-specific integration reference at the `integration` stage; load it per that table.

---

## Minimum Net Diff

- `[BLOCKING]` **Minimum net diff to the governing baseline.** Touch only what approved task objectives, codebase-coherence checklist items, handoff-doc coherence, documentation currency, logged user decisions, or supplied Sync impact context justify. No unrelated cleanup, broad reformatting, defensive edits, speculative abstractions, or helper extraction that is not required by the current task.

Use `git diff <BASE_HEAD_SHA>..HEAD` in normal integration-workflow after Sync, or the caller-provided range when a dispatch explicitly overrides the baseline. In standalone refactor work, use the caller's governing git range or touched-file diff.

Review the governing diff line by line. Any hunk without a current justification is out of scope; revert it or record the justification before return. A no-change diff still requires the Final Diff Self-Check trail below.

## Project Doc Audit

Integrate-step refactoring and integration review both cover project-level docs reachable from the diff.

For every file in the diff `<BASE_SHA>..<HEAD_SHA>`, walk up from its directory to the repo root and collect every `CLAUDE.md` / `AGENTS.md` / `README.md` encountered. Always also check the repo-root `README.md` and root `CLAUDE.md`.

For each doc in the set:

- update stale claims contradicted by the diff;
- add new patterns at the nearest appropriate level;
- link rather than duplicate parent-level content;
- create a missing `CLAUDE.md` + relative `AGENTS.md -> CLAUDE.md` pair for new module directories.

Leave docs above the affected area alone unless they are stale.

## Sync Impact Context

When PLAN.md task blocks contain `**Sync impact:**`, use those fields as evidence for why a hunk already exists in the governing diff. Follow the referenced Sync Map cluster only when needed to evaluate that hunk.

Sync impact justifies existing hunks only when it is already present; it does not create new refactor targets or excuse unrelated codebase changes.

## Final Diff Self-Check

Implementers run this immediately before every return or commit, including no-change cases:

1. **Recompute the governing diff.** In integration-workflow after Sync, use `git diff <BASE_HEAD_SHA>..HEAD`. In standalone refactor work, use the caller-provided git range or touched-file diff.
2. **Leave a compact trail.** In the assigned PLAN.md task block when one exists, write or refresh `**Final diff self-check:** <command/range>; <no surviving hunks OR surviving-change classes>; <suspicious hunk justifications or none>`. Without PLAN.md, put the same line in the status return.
3. **Summarize ordinary hunks by class.** Examples: "utility reuse in task scripts", "module README currency", "test contract wording". Do not justify every line when the class is already covered by the task objective or checklist.
4. **Justify suspicious hunks by file and line/hunk.** Suspicious cases are: `skills/*` or `agents/*` instruction edits, prior overprescription or scope-creep findings, base-side restorations or relocations, touched tasks already marked `Integration status: APPROVED`, broad formatting or rewrite hunks, and changes justified only by Sync impact. Apply any local instruction-prose gate only to files that local guidance covers.
5. **Prune or record.** Any hunk without a current justification is out of scope. Revert it, or record the underlying need where the reviewer can verify it.
6. **Respect the dispatch scope.** Refactor implementer and integration reviewer operate only on tasks whose `Integration status` is unset or `REVISE` and tasks explicitly reopened by accepted review findings.

The integration reviewer recomputes the same governing diff and compares it with the self-check trail. A missing or stale trail is `[BLOCKING]`, including when no code changed.

## Checklist

Walk every item. `[BLOCKING]` items must be satisfied for APPROVE; `[ADVISORY]` items may be flagged as MINOR.

**Code integration:**

- `[BLOCKING]` **Final Diff Self-Check present and fresh:** The trail names the governing command/range, records no-change outcomes or surviving-change classes, and gives file/hunk justification for suspicious cases.
- `[BLOCKING]` **Governing-diff pruning performed line by line:** Every surviving hunk ties to an approved task objective, supplied Sync impact context, logged user decision, or checklist requirement; unrelated cleanup, formatting churn, and stale branch-side restorations are removed.
- `[BLOCKING]` **Base-current deletions / relocations honored by default:** Restorations exist only when an approved task objective, supplied Sync impact context, logged user decision, or checklist requirement requires them.
- `[BLOCKING]` **Naming consistency:** variable names, function names, and file names follow codebase conventions.
- `[BLOCKING]` **Utility usage:** existing utility functions are used where appropriate instead of hand-rolled equivalents.
- `[BLOCKING]` **No debug artifacts:** no leftover debug prints, commented-out experiments, or temporary variables.
- `[BLOCKING]` **Minimal existing-file changes:** modifications outside the analysis scope are minimal and justified.
- `[ADVISORY]` **Code simplification:** redundant code removed and repeated patterns consolidated only where the task or codebase-coherence review demanded the touch.
- `[ADVISORY]` **PR-friendly diffs:** avoid unnecessary reformatting that obscures substantive changes.

**Handling inconsistencies:**

- `[BLOCKING]` **Methodological questions escalated, not resolved.** Different control variable sets, variable definitions, sample filters, equilibrium concepts, or normalization choices are research decisions.
- `[ADVISORY]` **Clear convention exists:** follow it. **Ambiguous or conflicting conventions:** use judgment and document the choice.

**PR quality:**

- `[BLOCKING]` **Focused diff:** changes are limited to analysis scope.
- `[BLOCKING]` **Self-contained:** the analysis can be understood from the code and documentation.
- `[ADVISORY]` **Clean commits:** commit history is logical and messages are descriptive.

**Documentation currency:**

- `[BLOCKING]` Module `CLAUDE.md` / `AGENTS.md` / `README.md` files do not reference files, functions, outputs, or methodology that no longer exist or have been superseded.
- `[BLOCKING]` Every output file mentioned in documentation is produced by the current code.
- `[BLOCKING]` Dates and version claims reflect the current commit.

**Project Doc Audit:**

- `[BLOCKING]` The walk-up audit above was executed for every file in the governing diff; stale claims were updated, new patterns were added at the correct level, parent-level content was not duplicated, missing module guidance pairs were created for new module directories, and docs above the affected area were left alone unless stale.
