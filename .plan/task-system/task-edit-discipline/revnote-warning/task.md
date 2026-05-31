---
title: "Warn (don't mutate) on stale revision notes in approved tasks"
status: not-started
depends_on:
  - move-hook
tags: []
created: 2026-05-30
updated: 2026-05-31
---

## Objective

The hook must **not** auto-mutate task content or status for revision notes. Auto-deletion proved too error-prone: a stateless post-hoc hook cannot reliably tell a planner *adding* a note (wants the task reopened) from a reviewer *approving* a task that still carried an old note (wants it cleaned), and a wrong guess silently destroys planner-owned content (decision 2026-05-31: warn only, no mutation; see Revision Notes). Replace the abandoned auto-mutation with one non-destructive validation warning.

### 1. Remove the auto-mutation added for the old design

From `skills/task-system/scripts/task_hook.py`, delete the revnote auto-mutation machinery committed in `21f5948`: the `_reconcile_revision_notes` function and its helpers (`_recover_prior_status`, `_strip_revision_notes`, `_body_has_revision_notes` and any associated regexes), and the call to it in `_handle_edit_write`. From `skills/task-system/scripts/test_task_system.py`, remove the `TestRevisionNoteSync` cases that assert mutation. The `move-hook` Bash/Edit reconcile (`_reconcile`: validate → propagate → dashboard) and all other hook behavior stay exactly as they were before `21f5948`.

### 2. Add a validation warning in `validate_plan`

In `skills/task-system/scripts/_task_io.py`, add a per-task validation rule (walked by `validate_plan`, alongside `validate_frontmatter`) that emits a warning when a task's `status == "approved"` **and** it has a non-empty `## Revision Notes` section. The message names the task path and states that an approved task still carries a revision note that should be removed (the reviewer owns revision-note removal at approval). Because `validate_plan` runs inside the existing hook reconcile on every edit and every shell move, this surfaces through the existing `[task-hook]` warning channel and flags *all* stale revision notes across the tree — directly addressing the leak that motivated this work.

Constraints:
- **Only `approved` warns.** `implemented` + a revision note is a legitimate mid-state (a reopened task, reworked, awaiting review) — do not warn on it. `not-started` / `in-progress` never warn.
- **Fence-aware detection.** Detect `## Revision Notes` only as a real section header, not when the line appears inside a fenced ```` ``` ```` code block (Results/objective sections in this very tree quote the header). The `Task.revision_notes` field comes from the fence-blind `parse_body_sections`, so do not simply trust it non-empty; use a fence-aware scan of `task.body` for the header. Do not broadly rewrite the shared `parse_body_sections` (it has many consumers) unless a localized check is genuinely impractical — prefer a small local helper.

### 3. Minimal docs

Add one accurate line where the revision-note lifecycle is described (`skills/task-system/references/planning.md`, and `skills/task-system/SKILL.md` if it describes the section): `validate_plan` warns when an `approved` task still carries a `## Revision Notes` section, and the reviewer remains responsible for removing it at approval. **Do not change `agents/reviewer.md`** — the reviewer keeps the removal duty, so there is no generated-artifact (`direct-mode-reviewer.md`, `superra_reviewer.toml`) regeneration in this task.

## Validation

- `validate_plan` warns for an `approved` task with a non-empty `## Revision Notes` section; does **not** warn for: `not-started` / `in-progress` / `implemented` + revnote, `approved` without a revnote, or a `## Revision Notes` header that appears only inside a fenced code block in another section.
- The auto-mutation code and its mutation tests are gone; `git grep` finds no `_reconcile_revision_notes` / `_strip_revision_notes` references; the hook no longer changes status or removes content for revision notes.
- Full task-system suite green (`uv run --with pytest python -m pytest test_task_system.py`). Manual: an `approved` task.md carrying a revnote produces the warning on the next reconcile; a `not-started` one does not; a fenced `## Revision Notes` header does not.

## Notes

Code (`task_hook.py` removal, `_task_io.py` warning rule) + tests + a one-line doc note only. No `agents/reviewer.md` change, no Codex/direct-mode regeneration. Standalone — no longer has a dependent doc task.

## Revision Notes

Substantive pivot (2026-05-31): the original design auto-mutated — flip a completed task to `revise` when a revision note was added, and delete the `## Revision Notes` section on approval. First-pass review found a CRITICAL data-loss path: in the uncommitted-approval window the status-based discriminator strips a planner's freshly added note. The researcher decided auto-deletion is too error-prone and chose warn-only, no mutation. This task is rewritten to remove the auto-mutation (committed in `21f5948`) and add a single non-destructive `validate_plan` warning instead. The former sibling `revnote-docs` (which moved the cleanup duty off the reviewer and regenerated Codex artifacts) was deleted: the reviewer keeps the removal duty, so no reviewer-spec change or regeneration is needed. The earlier review notes critiqued the discarded mutation design and are therefore moot. Cleaned when this task is approved.
