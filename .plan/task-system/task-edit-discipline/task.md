---
title: "Task Edit Discipline — Manual Move + Edit-Path Guidance"
status: not-started
depends_on: []
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Make manual `mv` a first-class way to reorganize the `.plan/` task tree, and make the task-system SKILL.md guidance on *how* to mutate a task unambiguous. Two coupled changes: (1) generalize the PostToolUse hook so a shell command that restructures `.plan/` (chiefly `mv`, also `rm`/`cp`/`mkdir` of task directories) triggers the same validate → propagate-status → rebuild-dashboard reconcile that an `Edit`/`Write` on a `task.md` already triggers; (2) rewrite the SKILL.md "How to Edit a Task" guidance so it states the settled canonical path — agents mutate a task, including `status`, by editing frontmatter directly while hooks enforce invariants — reframes the mutation CLIs as scaffolding/bulk tools rather than co-equal per-field commands, and documents manual `mv` as a supported reorganization path.

## Context / Rationale

This is superRA self-development (skill + hook engineering); no data/theory/writing domain vertical applies. Contributor discipline in the repo `CLAUDE.md` governs — load `skill-creator` before editing `skills/task-system/SKILL.md`, and self-apply the DRY + Necessity tests to every instruction line touched.

Background facts that motivate the change, already established:
- Direct edit is the canonical agent mutation path (decided in `task-system/agent-interface` — "Agents edit task.md directly using Read/Edit/Write. PostToolUse hooks handle validation … and dashboard rebuild"). The CLIs (`task_update.py`, `task_add_result.py`, `task_link.py`, `task_rename.py`) are convenience/scaffolding, not the prescribed mutation method. SKILL.md currently presents both side by side, with a standalone "Update task status" CLI example that invites agents to reach for the CLI for a single status flip.
- Everything a task owns lives inside its directory (`task.md`, `comments.yaml`, child task dirs), so a plain `mv` of a task directory carries the whole subtree and its comments with it — nothing keyed by external path is orphaned.
- `depends_on` is sibling-slug-scoped (`_task_io.py` `validate_dependencies`). The only thing a move can break is a dependency edge that crosses the move boundary; `validate_plan` already reports these as dangling-dep warnings. A self-contained subtree with no boundary-crossing deps moves cleanly.
- `task_rename.py` deliberately refuses cross-parent moves, so manual `mv` is already the only path for re-parenting — this work makes that path safe and documented rather than silent.

## Scope boundary

In scope: `skills/task-system/scripts/task_hook.py`, `hooks/hooks.json`, the task-system test suite, and `skills/task-system/SKILL.md`. Out of scope and explicitly NOT to be expanded into here: the static `dashboard.html` generation cleanup, the revision-note leftover cleanup, and bringing Codex/Cursor hook variants to task-validation parity (those variants do not wire `task_hook.py` at all today — see `move-hook` task).

No generated artifacts are affected. The generated role references (`skills/using-superRA/references/direct-mode-{implementer,reviewer}.md`) and `.codex/agents/*.toml` derive from `agents/implementer.md` / `agents/reviewer.md`, which this work does not touch — no `sync_codex_agents.py` run is required.
