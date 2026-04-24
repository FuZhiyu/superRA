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

Load `references/codebase-integration.md` for the checklist, reviewer verdict protocol, and implementer Final Diff Self-Check. For data-analysis integration, also load `econ-data-analysis/references/integration.md`.

---

## Minimum Net Diff

- `[BLOCKING]` **Minimum net diff to the governing baseline.** Touch only what approved task objectives, codebase-coherence checklist items, handoff-doc coherence, documentation currency, logged user decisions, or supplied Sync impact context justify. No unrelated cleanup, broad reformatting, defensive edits, speculative abstractions, or helper extraction that is not required by the current task.

Use `git diff <BASE_HEAD_SHA>..HEAD` after workflow Sync. In standalone refactor work, use the caller's governing git range or touched-file diff.

Review the governing diff line by line. Any hunk without a current justification is out of scope; revert it or record the justification before return. A no-change diff still requires the Final Diff Self-Check trail in `references/codebase-integration.md`.
