---
title: "Task Edit Discipline — Manual Move + Edit-Path Guidance"
status: in-progress
depends_on: []
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Make the PostToolUse hook the single mechanism that keeps the `.plan/` tree consistent under direct edits and shell operations, and make the task-system guidance on *how* to mutate a task unambiguous. Three coupled changes, each a subtask:

1. **`move-hook`** — generalize the hook so a shell command that restructures `.plan/` (chiefly `mv`, also `rm`/`cp`/`mkdir` of task directories) triggers the same validate → propagate-status → rebuild-dashboard reconcile that an `Edit`/`Write` on a `task.md` already triggers.
2. **`skill-guidance`** — rewrite the SKILL.md "How to Edit a Task" guidance so it states the settled canonical path (agents mutate a task, including `status`, by editing frontmatter directly while hooks enforce invariants), reframes the mutation CLIs as scaffolding/bulk tools rather than co-equal per-field commands, and documents manual `mv` as a supported reorganization path.
3. **`revnote-status-sync` + `revnote-docs`** — automate the `## Revision Notes` lifecycle in the hook so it no longer depends on a reviewer remembering a manual side-duty (the leak that left stale revision notes in approved tasks). Adding a `## Revision Notes` section to a completed (approved/implemented) task flips it to `revise`; setting a task to `approved` removes its `## Revision Notes`. Reconcile the now-redundant manual instructions in `agents/reviewer.md` and `planning.md`, and regenerate the Codex/direct-mode reviewer artifacts.

## Context / Rationale

This is superRA self-development (skill + hook engineering); no data/theory/writing domain vertical applies. Contributor discipline in the repo `CLAUDE.md` governs — load `skill-creator` before editing `skills/task-system/SKILL.md`, and self-apply the DRY + Necessity tests to every instruction line touched.

Background facts that motivate the change, already established:
- Direct edit is the canonical agent mutation path (decided in `task-system/agent-interface` — "Agents edit task.md directly using Read/Edit/Write. PostToolUse hooks handle validation … and dashboard rebuild"). The CLIs (`task_update.py`, `task_add_result.py`, `task_link.py`, `task_rename.py`) are convenience/scaffolding, not the prescribed mutation method. SKILL.md currently presents both side by side, with a standalone "Update task status" CLI example that invites agents to reach for the CLI for a single status flip.
- Everything a task owns lives inside its directory (`task.md`, `comments.yaml`, child task dirs), so a plain `mv` of a task directory carries the whole subtree and its comments with it — nothing keyed by external path is orphaned.
- `depends_on` is sibling-slug-scoped (`_task_io.py` `validate_dependencies`). The only thing a move can break is a dependency edge that crosses the move boundary; `validate_plan` already reports these as dangling-dep warnings. A self-contained subtree with no boundary-crossing deps moves cleanly.
- `task_rename.py` deliberately refuses cross-parent moves, so manual `mv` is already the only path for re-parenting — this work makes that path safe and documented rather than silent.

## Scope boundary

In scope: `skills/task-system/scripts/task_hook.py`, `hooks/hooks.json`, the task-system test suite, `skills/task-system/SKILL.md`, and — for the revision-note automation — `agents/reviewer.md`, `skills/task-system/references/planning.md`, and the regenerated reviewer artifacts. Out of scope and explicitly NOT to be expanded into here: the static `dashboard.html` generation cleanup, and bringing Codex/Cursor hook variants to task-validation parity (those variants do not wire `task_hook.py` at all today — see `move-hook` task).

**Generated artifacts (revnote-docs subtask only).** Editing `agents/reviewer.md` regenerates two files via `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py`: `skills/using-superRA/references/direct-mode-reviewer.md` and `.codex/agents/superra_reviewer.toml`. These are generated, not hand-edited — `revnote-docs` must run the generator (and its `--check` mode / `test_sync_codex_agents.py`) after editing the source spec. The `move-hook` and `skill-guidance` subtasks touch no agent specs and need no regeneration.

## Revision Notes

Substantive scope addition (2026-05-30, after `move-hook` and `skill-guidance` were approved and integrated): added the revision-note lifecycle automation as two new subtasks (`revnote-status-sync`, `revnote-docs`) and rewrote the scope boundary to bring revision-note cleanup *in* scope (it was previously excluded) and to surface the newly-affected generated reviewer artifacts. `move-hook` and `skill-guidance` are unchanged and remain approved; only the parent objective and scope boundary changed. This note is cleaned when the parent's new children are approved.
