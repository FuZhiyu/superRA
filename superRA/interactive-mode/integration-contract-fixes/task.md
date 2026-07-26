---
title: "Close Interactive Integration Contract Gaps"
status: approved
depends_on: []
---

## Objective

Resolve the integration review blockers as one coherent execution-contract repair: keep review now/defer/skip on the existing status lifecycle; wire superimplement to per-task main/subagent seat selection; make canonical role specs resolvable for main-filled and forced-inline seats in installed cross-repo use; add a minimal domain-neutral interactive self-review; remove DRY/Necessity duplication; and correct the conservative cleanup's narrow reproducibility accounting. Success: every recorded integration finding is accepted and fixed, current docs and tests reflect the same contract, packaged/generated access works, and full integration verification passes.

## Planner Guidance

The findings in superRA/interactive-mode/task.md and superRA/interactive-mode/prose-test-cleanup/task.md at review commit f88a42f5 are inputs except for the superseded durable-disposition finding: defer / skip leaves the task `implemented`, and the normal review gates remain unchanged. Reuse the existing status enum; do not add a review-status field. Keep role behavior in agents/*, harness resolution in the Codex adapter/setup owner, and changing-tree behavior in its reference. Load skill-creator before skills/* edits. Apply DRY/Necessity line by line and keep the diff bounded to these findings.

## Results

Resolved the integration-review findings:

- [interactive-mode.md](../../../skills/superplan/references/interactive-mode.md)
  performs a domain-neutral self-review and leaves deferred or skipped review
  at `implemented`.
- [superimplement/SKILL.md](../../../skills/superimplement/SKILL.md) selects
  the per-task seat structure and executes each filler through a structured
  main-role or dispatch route. [agent-orchestration/SKILL.md](../../../skills/agent-orchestration/SKILL.md)
  retains one seat-choice table and only the orchestration delta.
- [canonical-role.md](../../../skills/using-superra/references/canonical-role.md)
  and [resolve_role.py](../../../skills/using-superra/scripts/resolve_role.py)
  provide the shared packaged-role resolver. The
  [Claude adapter](../../../skills/using-superra/references/claude-instructions.md)
  and [Codex adapter](../../../skills/using-superra/references/codex-instructions.md)
  both route main-filled and forced-inline seats through it, and
  [test_resolve_role.py](../../../skills/using-superra/scripts/test_resolve_role.py)
  verifies both roles from a foreign project against a copied plugin layout.
- [superplan/SKILL.md](../../../skills/superplan/SKILL.md) points to
  `changing-the-tree.md` without paraphrasing its drift, tracker, protocol, or
  stop rules.
- [prose-test-cleanup/task.md](../prose-test-cleanup/task.md) now records the
  reproducible narrow accounting: range `6be18283..64440306`, pathspecs
  `tests`, `:(glob)skills/**/test*.py`, and
  `:(glob)skills/**/tests/**`, with 349 additions, 2,386 deletions, and 43
  files.

Verification:

- Focused contract tests: `13 passed`.
- Task-tree and harness suites: `824 passed`, with four expected warnings.
- Harness compatibility and generated-agent equality: exit `0`.
- Codex hook suite: `15/15`.
- Zotero shell suite: `18/18`.
- Skill validation, Markdown integrity, Python compilation, and
  `git diff --check`: clean.

Accepted-fix verification:

- Shared packaged-role resolver: `1 passed`; Codex agent generation: `3 passed`.
- Focused execution-contract tests: `32 passed`.
- Full CI-safe harness suite: `126 passed`.
- Harness compatibility and generated-agent equality: exit `0`.
- Five edited skill directories passed `quick_validate.py`; Markdown integrity
  and `git diff --check` were clean.

**Final diff self-check:** `git diff 84d451deff42cab17944fd8ab038ca8d092428d1 --cached`
against the complete staged candidate tree; surviving-change classes are the
interactive execution-mode contract and docs, shared packaged canonical-role
resolution, task-tree/harness contract coverage, conservative prose-test
cleanup, and task records. Suspicious hunk justifications: the cross-repo role
resolution edits in `skills/using-superra/` and the two harness adapters close
Review Note 1; the domain-neutral interactive self-review and main/subagent
seat-execution edits implement this task's objective; the `superplan` and
`superimplement` deletions remove the Review Note 3 DRY/Necessity echoes; the
deleted generated direct-mode references are authorized by
[drop-direct-generated](../drop-direct-generated/task.md); and the broad test
deletions retain only structured contract coverage per
[prose-test-cleanup](../prose-test-cleanup/task.md). Project-doc walk-up found
no stale claim in the root `CLAUDE.md`, root `README.md`, or harness
[README.md](../../../tests/harness-instruction-following/README.md). No
unjustified or scope-ambiguous hunk remains.

## Revision Notes

The researcher confirmed that this integration update task folds into
`interactive-mode`: move the durable lifecycle, cross-harness role-resolution,
and DRY/Necessity outcomes into a short parent Results subsection, then remove
this temporary task directory.
