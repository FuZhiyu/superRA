---
title: "Warn (don't mutate) on stale revision notes in approved tasks"
status: approved
depends_on:
  - move-hook
tags: []
created: 2026-05-30
---

## Objective

The hook must **not** auto-mutate task content or status for revision notes. Auto-deletion proved too error-prone: a stateless post-hoc hook cannot reliably tell a planner *adding* a note (wants the task reopened) from a reviewer *approving* a task that still carried an old note (wants it cleaned), and a wrong guess silently destroys planner-owned content (decision 2026-05-31: warn only, no mutation; see Revision Notes). Replace the abandoned auto-mutation with one non-destructive validation warning.

### 1. Remove the auto-mutation added for the old design

From `skills/task-tree/scripts/task_hook.py`, delete the revnote auto-mutation machinery committed in `21f5948`: the `_reconcile_revision_notes` function and its helpers (`_recover_prior_status`, `_strip_revision_notes`, `_body_has_revision_notes` and any associated regexes), and the call to it in `_handle_edit_write`. From `skills/task-tree/scripts/test_task_tree.py`, remove the `TestRevisionNoteSync` cases that assert mutation. The `move-hook` Bash/Edit reconcile (`_reconcile`: validate → propagate → dashboard) and all other hook behavior stay exactly as they were before `21f5948`.

### 2. Add a validation warning in `validate_plan`

In `skills/task-tree/scripts/_task_io.py`, add a per-task validation rule (walked by `validate_plan`, alongside `validate_frontmatter`) that emits a warning when a task's `status == "approved"` **and** it has a non-empty `## Revision Notes` section. The message names the task path and states that an approved task still carries a revision note that should be removed (the reviewer owns revision-note removal at approval). Because `validate_plan` runs inside the existing hook reconcile on every edit and every shell move, this surfaces through the existing `[task-hook]` warning channel and flags *all* stale revision notes across the tree — directly addressing the leak that motivated this work.

Constraints:
- **Only `approved` warns.** `implemented` + a revision note is a legitimate mid-state (a reopened task, reworked, awaiting review) — do not warn on it. `not-started` / `in-progress` never warn.
- **Fence-aware detection.** Detect `## Revision Notes` only as a real section header, not when the line appears inside a fenced ```` ``` ```` code block (Results/objective sections in this very tree quote the header). The `Task.revision_notes` field comes from the fence-blind `parse_body_sections`, so do not simply trust it non-empty; use a fence-aware scan of `task.body` for the header. Do not broadly rewrite the shared `parse_body_sections` (it has many consumers) unless a localized check is genuinely impractical — prefer a small local helper.

### 3. Minimal docs

Add one accurate line where the revision-note lifecycle is described (`skills/task-tree/references/planning.md`, and `skills/task-tree/SKILL.md` if it describes the section): `validate_plan` warns when an `approved` task still carries a `## Revision Notes` section, and the reviewer remains responsible for removing it at approval. **Do not change `agents/reviewer.md`** — the reviewer keeps the removal duty, so there is no generated-artifact (`direct-mode-reviewer.md`, `superra_reviewer.toml`) regeneration in this task.

## Validation

- `validate_plan` warns for an `approved` task with a non-empty `## Revision Notes` section; does **not** warn for: `not-started` / `in-progress` / `implemented` + revnote, `approved` without a revnote, or a `## Revision Notes` header that appears only inside a fenced code block in another section.
- The auto-mutation code and its mutation tests are gone; `git grep` finds no `_reconcile_revision_notes` / `_strip_revision_notes` references; the hook no longer changes status or removes content for revision notes.
- Full task-tree suite green (`uv run --with pytest python -m pytest test_task_tree.py`). Manual: an `approved` task.md carrying a revnote produces the warning on the next reconcile; a `not-started` one does not; a fenced `## Revision Notes` header does not.

## Results

All three parts implemented; full suite green (163 passed) and `git grep` finds no auto-mutation symbols.

**Part 1 — auto-mutation removed.** Deleted from [task_hook.py](../../../../skills/task-tree/scripts/task_hook.py): `_reconcile_revision_notes`, `_recover_prior_status`, `_strip_revision_notes`, `_body_has_revision_notes`, the `_COMPLETED_STATES` / `_REVNOTE_SECTION_RE` constants, the call in `_handle_edit_write`, and the now-unused `import subprocess`. The `re` import stays (used by the move-hook `_MUTATING_RE` / `_PLAN_TOKEN_RE`). The move-hook `_reconcile` (validate → propagate → dashboard) and all other hook behavior are untouched. Removed `TestRevisionNoteSync` (and its `_make_git_plan` / git-recovery scaffolding) from [test_task_tree.py](../../../../skills/task-tree/scripts/test_task_tree.py).

**Part 2 — non-destructive warning.** Added two functions to [_task_io.py](../../../../skills/task-tree/scripts/_task_io.py): `_has_nonempty_section(body, section)` — a small local fence-aware scanner that skips `## ` headers inside ``` ``` ``` / `~~~` fenced blocks and treats a section as non-empty only when a non-blank line follows the header before the next top-level `## `; and `validate_revision_notes(task)` — warns only when `status == "approved"` and the fence-aware scan finds a non-empty `## Revision Notes` section. Wired into `validate_plan` alongside `validate_frontmatter` at both the per-task level and the root task. `Task.revision_notes` (fence-blind) is deliberately not trusted; `parse_body_sections` is left unchanged. The warning rides the existing `[task-hook]` channel, so it flags every stale revision note tree-wide on each reconcile.

**Part 3 — docs.** One line added to [planning.md](../../../../skills/task-tree/references/planning.md) §Revision Notes lifecycle and the `## Revision Notes` row of the section table in [SKILL.md](../../../../skills/task-tree/SKILL.md): `validate_plan` warns (never mutates) when an `approved` task still carries the section; the reviewer keeps the removal duty. `agents/reviewer.md` untouched; no Codex/direct-mode regeneration.

**Tests.** Replaced the mutation tests with `TestHasNonemptySection` (real header, empty section, missing header, ``` and `~~~` fenced headers ignored, real header after a fenced quote still detected), `TestValidateRevisionNotes` (approved+revnote warns; approved-without / implemented / not-started / in-progress / fenced / empty do not), and `TestValidatePlanRevisionNotes` (end-to-end `validate_plan` warns on approved+revnote, silent on implemented+revnote and on a fenced header). Manual hook run on a temp `.plan/`: approved+revnote emits the warning with content byte-identical before/after; not-started+revnote and fenced-only produce zero revnote warnings.

## Notes

Code (`task_hook.py` removal, `_task_io.py` warning rule) + tests + a one-line doc note only. No `agents/reviewer.md` change, no Codex/direct-mode regeneration. Standalone — no longer has a dependent doc task.

## Review Notes

> 1. [MINOR] The objective points to "see Revision Notes" for the 2026-05-31 warn-only decision, but that section was (correctly) removed at approval — a dangling internal pointer. Inline the one-line rationale in the objective.
> 2. [MINOR] `## Results` cite the doc line added to `planning.md §Revision Notes lifecycle`; that file is gone — the surviving rule lives in [task-file-contract.md](../../../../skills/task-tree/references/task-file-contract.md) (`validate_plan` warning noted there). Repoint the citation.
