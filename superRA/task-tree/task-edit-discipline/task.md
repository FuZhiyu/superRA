---
title: "Task Edit Discipline — Manual Move + Edit-Path Guidance"
status: approved
depends_on: []
---

## Objective

Make the PostToolUse hook the single mechanism that keeps the `superRA/` tree consistent under direct edits and shell operations, and make the task-tree guidance on *how* to mutate a task unambiguous. Three coupled changes:

1. **Move hook** — generalize the hook so a shell command that restructures `superRA/` (chiefly `mv`, also `rm`/`cp`/`mkdir` of task directories) triggers the same validate → propagate-status reconcile that an `Edit`/`Write` on a `task.md` already triggers.
2. **Skill guidance** — state the settled canonical path in SKILL.md: agents mutate a task (including `status`) by editing frontmatter directly while hooks enforce invariants; the mutation CLIs are scaffolding/bulk tools, not co-equal per-field commands; manual `mv` is a supported reorganization path.
3. **Revision-note warning** — surface the stale-revision-note leak (approved tasks still carrying `## Revision Notes`) without mutating anything, via a `validate_plan` rule that warns through the existing hook channel. An earlier auto-mutation design (flip-to-`revise` on note add, delete-on-approve) was abandoned as too error-prone — a stateless post-hoc hook can destroy planner-owned content in the uncommitted-approval window. The reviewer keeps owning revision-note removal.

### Rationale

- Direct edit is the canonical agent mutation path; the CLIs (`task_update.py`, `task_add_result.py`, `task_link.py`, `task_rename.py`) are convenience/scaffolding.
- Everything a task owns lives inside its directory (`task.md`, `comments.yaml`, child task dirs), so a plain `mv` of a task directory carries the whole subtree and its comments — nothing keyed by external path is orphaned.
- `depends_on` is sibling-slug-scoped; the only thing a move can break is a dependency edge crossing the move boundary, which `validate_plan` already reports as a dangling-dep warning.
- `task_rename.py` refuses cross-parent moves, so manual `mv` is already the only re-parenting path — this work makes it safe and documented rather than silent.

Scope: `task_hook.py`, `_task_io.py` (the new `validate_plan` warning rule), `hooks/hooks.json`, the task-tree test suite, and `skills/task-tree/SKILL.md`. No generated artifacts are affected — with the revision-note work reduced to a warning, `agents/reviewer.md` is untouched.

## Results

All three changes shipped and are approved.

- **Move hook.** `task_hook.py` handles Bash shell mutations of the `superRA/` tree (chiefly `mv`): a manual move prints the dangling-dep warning, propagates parent status, and exits 0.
- **Skill guidance.** `skills/task-tree/SKILL.md §How to Edit a Task` names direct `task.md` edit as the canonical mutation path for status and all body sections, reframes the CLIs as scaffolding tools, and documents manual `mv` as the supported re-parenting path.
- **Revision-note warning.** The abandoned auto-mutation design is replaced by a stateless `validate_plan` rule: an `approved` task carrying a `## Revision Notes` section produces a hook warning, with no auto-mutation symbols remaining.
