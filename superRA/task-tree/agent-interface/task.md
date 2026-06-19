---
title: "Task-Tree Agent Interface"
status: revise
depends_on: []
tags: []
created: 2026-05-24
---

## Objective

Make the task tree the primary handoff mechanism, replacing the monolithic PLAN.md + RESULTS.md pair. Every agent role (planner, implementer, reviewer, orchestrator) needs to know how to interact with the `superRA/` task tree — reading tasks with context, editing body sections, and recording decisions.

### Design Decisions

**Indexing: Path (not UUID).** The relative path within `superRA/` is the canonical task identifier (e.g., `data-preparation/merge`). Directory names are descriptive slugs — no numeric prefixes. Display and execution order derived from DAG topological sort of `depends_on`.

**Hooks + Convenience CLI.** Agents edit task.md directly using Read/Edit/Write. PostToolUse hooks handle validation (frontmatter, dep references, cycle detection). `task_create.py` kept for convenience (auto-fills template). Read-path CLI kept: `task_read.py` (context injection), `task_query.py` (tree/frontier/DAG).

**Flexible body sections.** No rigid structure enforced. Any `## Heading` is valid — each becomes a foldable layer in dashboard. Recommended defaults: `## Objective`, `## Results`, `## Review Notes`.

**Progressive skill revelation (3 tiers).** Consumer (`using-superra` §Task Interface: read, edit), Planner (`task-tree` + `superplan` references: objectives, splitting, retroactive), Contributor (`task-tree/references/internals.md`: data layer, hooks).

**What replaces what:**

| Old | New |
|---|---|
| PLAN.md header | Root task.md body sections |
| `## Project Conventions` | Root task.md `## Conventions` |
| `## Workflow Status` | Root task.md `## Workflow Status` |
| `### Task N:` block | `<path>/task.md` |
| RESULTS.md task section | Task's `## Results` |
| Review-notes blockquote | Task's `## Review Notes` |
| Steps with checkboxes | Subtasks or prose |
| Separate RESULTS.md | Gone — results in task.md body |

## Results

The task tree is now the primary handoff mechanism for the superRA workflow. The monolithic PLAN.md + RESULTS.md pair has been replaced by the `superRA/` filesystem hierarchy where each task owns a `task.md` with planner-owned `## Objective` and implementer-owned `## Results`. All eleven child tasks in this workstream have been implemented and approved.

Key outcomes across the workstream:

- **[agent-surface-redesign](agent-surface-redesign/task.md):** The universal task interface was folded into `using-superra §Task Interface`; role specs were restructured to a parallel skeleton; the reporting model collapsed onto commit = summary / return = status + SHA. Nine subtasks; coverage audit confirmed no knowledge lost.
- **[comment-surfacing](comment-surfacing/task.md):** Researcher-pinned dashboard comments are now surfaced in `task_read.py`, visible to every dispatched agent.
- **[core-and-hooks](core-and-hooks/task.md):** Topological sort, validation functions, and PostToolUse hook parity for Codex shell mutations.
- **[handoff-doc](handoff-doc/task.md):** handoff-doc skill deprecated; content merged into task-tree + role specs.
- **[integ-workflow](integ-workflow/task.md):** `superintegrate` is `.plan/`-native, with gated consolidation assessment and results maturation into the highest-level touched task.
- **[planning-workflow](planning-workflow/task.md):** `superplan` outputs a `.plan/` task tree instead of PLAN.md.
- **[task-edit-discipline](../task-edit-discipline/task.md):** Move hook, skill guidance, and revision-note warning align the hook with direct task mutation.

## Revision Notes

2026-06-19: Added [agent-loading-tests](agent-loading-tests/task.md) as a new scoped test-design subtree. This reopens the approved agent-interface workstream only for instruction-following and file-loading verification; the earlier approved implementation results above remain historical rollup context.
