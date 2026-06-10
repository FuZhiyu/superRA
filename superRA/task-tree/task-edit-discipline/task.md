---
title: "Task Edit Discipline — Manual Move + Edit-Path Guidance"
status: revise
depends_on: []
tags: []
created: 2026-05-30
---

## Objective

Make the PostToolUse hook the single mechanism that keeps the `.plan/` tree consistent under direct edits and shell operations, and make the task-tree guidance on *how* to mutate a task unambiguous. Three coupled changes, each a subtask:

1. **`move-hook`** — generalize the hook so a shell command that restructures `.plan/` (chiefly `mv`, also `rm`/`cp`/`mkdir` of task directories) triggers the same validate → propagate-status → rebuild-dashboard reconcile that an `Edit`/`Write` on a `task.md` already triggers.
2. **`skill-guidance`** — rewrite the SKILL.md "How to Edit a Task" guidance so it states the settled canonical path (agents mutate a task, including `status`, by editing frontmatter directly while hooks enforce invariants), reframes the mutation CLIs as scaffolding/bulk tools rather than co-equal per-field commands, and documents manual `mv` as a supported reorganization path.
3. **`revnote-warning`** — surface the stale-revision-note leak (approved tasks still carrying `## Revision Notes`) without mutating anything: add a `validate_plan` rule that warns when an `approved` task still has a `## Revision Notes` section, surfaced tree-wide through the existing hook warning channel. An earlier auto-mutation design (flip-to-`revise` on note add, delete-on-approve) was abandoned as too error-prone — a stateless post-hoc hook can destroy planner-owned content in the uncommitted-approval window (decision 2026-05-31: warn only). The reviewer keeps owning revision-note removal, so `agents/reviewer.md` is not touched and no Codex/direct-mode regeneration is needed.

## Context / Rationale

This is superRA self-development (skill + hook engineering); no data/theory/writing domain vertical applies. Contributor discipline in the repo `CLAUDE.md` governs — load `skill-creator` before editing `skills/task-tree/SKILL.md`, and self-apply the DRY + Necessity tests to every instruction line touched.

Background facts that motivate the change, already established:
- Direct edit is the canonical agent mutation path (decided in `task-tree/agent-interface` — "Agents edit task.md directly using Read/Edit/Write. PostToolUse hooks handle validation … and dashboard rebuild"). The CLIs (`task_update.py`, `task_add_result.py`, `task_link.py`, `task_rename.py`) are convenience/scaffolding, not the prescribed mutation method. SKILL.md currently presents both side by side, with a standalone "Update task status" CLI example that invites agents to reach for the CLI for a single status flip.
- Everything a task owns lives inside its directory (`task.md`, `comments.yaml`, child task dirs), so a plain `mv` of a task directory carries the whole subtree and its comments with it — nothing keyed by external path is orphaned.
- `depends_on` is sibling-slug-scoped (`_task_io.py` `validate_dependencies`). The only thing a move can break is a dependency edge that crosses the move boundary; `validate_plan` already reports these as dangling-dep warnings. A self-contained subtree with no boundary-crossing deps moves cleanly.
- `task_rename.py` deliberately refuses cross-parent moves, so manual `mv` is already the only path for re-parenting — this work makes that path safe and documented rather than silent.

## Scope boundary

In scope: `skills/task-tree/scripts/task_hook.py`, `skills/task-tree/scripts/_task_io.py` (the new `validate_plan` warning rule), `hooks/hooks.json`, the task-tree test suite, `skills/task-tree/SKILL.md`, and `skills/task-tree/references/planning.md` (one-line doc note). Out of scope and explicitly NOT to be expanded into here: the static `dashboard.html` generation cleanup, and bringing Codex/Cursor hook variants to task-validation parity (those variants do not wire `task_hook.py` at all today — see `move-hook` task).

**No generated artifacts are affected.** With the revision-note work reduced to a non-destructive warning, `agents/reviewer.md` is no longer touched (the reviewer keeps the removal duty), so the generated reviewer references (`direct-mode-reviewer.md`, `.codex/agents/superra_reviewer.toml`) need no regeneration.

## Review Notes

> 1. [MAJOR] This approved parent of a closed 3-child workstream has no `## Results` section at all (body is Objective / Context / Scope boundary only) — zero recorded outcome violates the Results lifecycle in [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) §Results Shape. Add a rollup linking the three children.
> 2. [MINOR] `## Context / Rationale` and `## Scope boundary` are top-level sections, so children never inherited them via `superra task read` (which injects only the ancestor `## Objective` and its nested `###` subsections); nest them as `###` under `## Objective` or fold them in.
> 3. [MINOR] Stale claims stated as current: `.plan/` as the tree root; `skills/task-tree/SKILL.md` "How to Edit a Task" / command-surface sections that the later agent-surface redesign removed; "those variants do not wire `task_hook.py` at all today" — Codex now wires it ([hooks-codex.json](../../../hooks/hooks-codex.json)), only Cursor ([hooks-cursor.json](../../../hooks/hooks-cursor.json)) still lacks task-hook parity; and the objective's "validate → propagate-status → rebuild-dashboard reconcile" overstates the hook, which no longer rebuilds the dashboard ([task_hook.py:6](../../../skills/task-tree/scripts/task_hook.py#L6)). Rewrite in place.
