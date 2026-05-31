---
title: "Hook: revision-note ↔ status automation"
status: not-started
depends_on:
  - move-hook
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Automate the `## Revision Notes` lifecycle inside the PostToolUse hook (`skills/task-system/scripts/task_hook.py`, the `Edit`/`Write` branch built in `move-hook`) so it no longer depends on a reviewer remembering a manual side-duty. Stale revision notes have leaked into approved tasks precisely because their removal was a forgettable secondary reviewer step; moving the lifecycle into the hook makes it deterministic. Two behaviors, both on an `Edit`/`Write` to a `task.md`, both via direct file I/O (best-effort, never block, always exit 0; the hook's own writes do not re-trigger PostToolUse):

### Behavior A — revision note added on a completed task → flip to `revise`

When, after an edit, a leaf `task.md` has a `## Revision Notes` section AND its status is a *completed* state (`approved` or `implemented`) AND the status field did **not** change to `approved` in this same edit (see disambiguation below), set its status to `revise`. Rationale: a revision note signals the objective changed and the task needs another implementation pass; `revise` routes it back to the implementer (decision 2026-05-30: `revise`, not `not-started`). Guards: never touch a task whose status is already `not-started`, `in-progress`, or `revise` (no-op); only de-approve completed states.

### Behavior B — flip to `approved` → remove revision notes

When an edit sets a task's status to `approved` and the task has a `## Revision Notes` section, remove that entire section (its rework is done; the delta signal is spent). Scope is revision notes only — `## Review Notes` stays owned by the reviewer's own loop and is NOT touched by the hook (decision 2026-05-30: keep the two note types separate, hook handles revision notes only).

### The disambiguation (the crux)

A stateless post-hoc hook sees an identical end-state — `{status: approved, ## Revision Notes present}` — for two opposite intents:
- a planner just *added* a revision note to a still-`approved` task to reopen it → wants Behavior A (flip to `revise`);
- a reviewer just *set* a previously-`revise`/`implemented` task to `approved` while a revision note was still present → wants Behavior B (remove the note).

The discriminator is **whether the status field changed to `approved` in this edit**. Recover the prior status best-effort from the last committed version (`git show :<relpath>` or `HEAD:<relpath>`, parsed via the existing frontmatter parser). Rule:
- prior status ≠ `approved` and new status == `approved` → **Behavior B** (approval transition; clean the note).
- new status == prior status (both `approved`/`implemented`) and a `## Revision Notes` section is now present → **Behavior A** (note added to a completed task; flip to `revise`).

If the prior status cannot be recovered (file not yet committed, not in a git tree, `git` unavailable), fall back to the **safe default: do nothing** for the revnote automation (validation/propagation/dashboard still run as before). Never block, never guess destructively — a missed automation self-heals on the next committed edit; a wrong guess could delete a planner's revision note.

### Placement and reuse

This logic lives in the `Edit`/`Write` reconcile path only (revision notes are edited via `Edit`/`Write`, not the shell) — do not add it to the `Bash` branch. Run it alongside the existing `_reconcile` (validate → propagate → dashboard); the status change or section removal must happen before propagation so parent rollup reflects the new state. Reuse `_task_io` frontmatter parse/write helpers; do not hand-roll YAML.

## Validation

Extend `TestTaskHook` in `skills/task-system/scripts/test_task_system.py`. Required cases:
- **A:** approved task, edit adds `## Revision Notes`, prior committed status was approved → hook sets `revise`, section preserved.
- **B:** task with `## Revision Notes` present, edit sets status `approved` (prior committed status was `revise` or `implemented`) → hook removes the section, status stays `approved`.
- **Disambiguation:** the same `{approved + revnote}` end-state resolves to A vs B based on the prior committed status (one fixture per branch).
- **No-ops:** `not-started`/`in-progress` task with a revnote → untouched; `approved` with no revnote → untouched; prior-status unrecoverable → no revnote automation (and no crash).
- **Invariants:** always exit 0; the hook's write does not loop; `## Review Notes` is never touched by the hook.

Full task-system suite green (`uv run --with pytest python -m pytest test_task_system.py`). Manual: in a scratch `.plan/`, add a revnote to an approved task.md committed at approved → confirm it flips to revise; separately, approve a task.md that carries a revnote → confirm the section is removed.

## Notes

`agents/reviewer.md` and `planning.md` currently assign revision-note removal to the reviewer; reconciling those instructions to point at this hook (and regenerating the Codex/direct-mode reviewer artifacts) is the sibling `revnote-docs` task, which depends on this one so its docs match shipped behavior. Code + tests only here; no doc or generated-artifact edits.
