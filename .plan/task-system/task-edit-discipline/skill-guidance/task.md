---
title: "SKILL.md edit-path guidance: direct-edit canonical, CLI as scaffolding, manual move documented"
status: not-started
depends_on:
  - move-hook
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Rewrite the "How to Edit a Task" guidance in `skills/task-system/SKILL.md` so the canonical mutation path is stated once and unambiguously, the mutation CLIs are reframed as scaffolding/bulk tools rather than co-equal per-field commands, and manual `mv` is documented as a supported way to reorganize the tree (relying on the `move-hook` behavior). Load `skill-creator` before editing, and self-apply the DRY + Necessity tests from the repo `CLAUDE.md` to every line touched — add a line only if removing it would change what an agent *does*.

### 1. State the canonical path once, in "How to Edit a Task"

The section already says "Edit `task.md` directly with Read/Edit tools." Make explicit, in one place, that this includes `status` and all task content: agents mutate a task by editing frontmatter/body directly; the PostToolUse hook is what validates the frontmatter (enum values, dependency references, cycles), propagates parent status, and rebuilds the dashboard — so direct edit is the path the safety net is built around, not an unsafe shortcut. One line is enough; do not restate the hook's internals (they live in the validation-hooks task / references).

### 2. Reframe the mutation CLIs in the Command Surface

The Command Surface currently documents `task_create.py`, `task_update.py`, `task_add_result.py`, `task_link.py`, `task_rename.py` as a flat list, including a standalone "### Update task status" example (`task_update.py --status approved`) that reads as a co-equal path for a single status flip. Change the framing, not the inventory:
- Add one orienting line that the mutation CLIs are convenience/scaffolding and for bulk or scripted changes (`task_create.py` scaffolds a new task with template + dates; `task_update.py --propagate-all` / `--cascade` do bulk status work), not the way to set a single field on one task.
- Demote or remove the standalone single-flip "Update task status" example so it no longer competes with the direct-edit guidance. Keep the genuinely-CLI-only operations (bulk/cascade, scaffolding) documented.
- Do not delete the CLIs or their bulk flags from the docs; the goal is correct precedence, not removal.

### 3. Document manual move as supported

Add a short "moving / reorganizing tasks" note to the editing guidance: a task directory may be moved with a plain `mv` (it carries its `task.md`, `comments.yaml`, and whole subtree); the PostToolUse hook revalidates the tree, propagates status, and rebuilds the dashboard after the move (per the `move-hook` task). Call out the one caveat in plain terms: because `depends_on` references same-level sibling slugs, a move that crosses a dependency boundary leaves a dangling dependency that validation will flag — re-wire it with `task_link.py` or a direct edit. State that `task_rename.py` remains the convenience for an atomic same-parent rename that also cascades sibling `depends_on`, but is no longer required for the tree to stay consistent after a manual move. Keep this tight — a few sentences, not an essay; the behavior is authoritative in the hook, so the doc points and trusts.

## Validation

Re-read the edited section end to end: the canonical mutation path is unambiguous, no CLI example competes with it for single-field edits, and the move note matches the behavior the `move-hook` task actually shipped (including the dangling-dep caveat and the no-auto-cascade reality). Confirm no line fails the DRY/Necessity tests (no restating hook internals, no "here is what you will receive" description of the command shape). Confirm the inventory of CLIs is unchanged — only their framing/precedence moved.

## Notes

Depends on `move-hook` so the documented move behavior matches what shipped (the doc must not claim auto-cascade or any behavior the hook does not implement). This task changes documentation/instruction text only; no code, no generated artifacts.
