---
title: "Task-Tree Agent Interface"
status: approved
depends_on: []
---

## Objective

Make the task tree the primary handoff mechanism, replacing the monolithic PLAN.md + RESULTS.md pair. Every agent role (planner, implementer, reviewer, orchestrator) interacts with the `superRA/` task tree — reading tasks with context, editing body sections, and recording decisions.

### Design Decisions

**Indexing: path, not UUID.** The relative path within `superRA/` is the canonical task identifier (e.g. `data-preparation/merge`). Directory names are descriptive slugs; display and execution order derive from a DAG topological sort of `depends_on`.

**Hooks + convenience CLI.** Agents edit `task.md` directly with Read/Edit/Write; PostToolUse hooks handle validation (frontmatter, dep references, cycle detection) and status propagation. The `superra task ...` CLI stays for scaffolding, bulk edits, and read-path context injection.

**Flexible body sections.** Any `## Heading` is valid and becomes a foldable dashboard layer; the recommended defaults are `## Objective`, `## Results`, `## Review Notes`.

**Progressive skill revelation.** Consumer tier (`using-superra` §Task Interface: read, edit), planner tier (`task-tree` + `superplan` references: objectives, splitting, retroactive), contributor tier (`task-tree` internals: data layer, hooks).

## Results

The task tree is the primary handoff mechanism for the superRA workflow. The monolithic PLAN.md + RESULTS.md pair is gone; each task owns a `task.md` with planner-owned `## Objective` and implementer-owned `## Results`, read with ancestor context through `superra task read`.

What shipped across this workstream:

- The universal task interface is folded into `using-superra` §Task Interface; role specs share a parallel skeleton; the reporting model collapsed onto commit = summary / return = status + SHA, and a coverage audit confirmed no knowledge was lost.
- Researcher-pinned dashboard comments surface in `skills/task-tree/scripts/task_read.py`, so every dispatched agent sees them.
- Topological sort, validation functions, and PostToolUse hook parity for Codex shell mutations landed in the data layer and hook.
- The `handoff-doc` skill is deprecated; its content merged into `task-tree` and the role specs.
- `superplan` outputs a `superRA/` task tree instead of PLAN.md, and `superintegrate` matures results into the highest touched task. The [task-edit-discipline](../task-edit-discipline/task.md) sibling aligns the move hook and edit guidance with direct task mutation.
