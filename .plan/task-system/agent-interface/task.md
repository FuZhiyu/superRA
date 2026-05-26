---
title: "Task-System Agent Interface"
status: approved
depends_on: []
tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Make the task system the primary handoff mechanism, replacing the monolithic PLAN.md + RESULTS.md pair. Every agent role (planner, implementer, reviewer, orchestrator) needs to know how to interact with `.plan/` — reading tasks with context, editing body sections, and recording decisions.

## Design Decisions

**Indexing: Path (not UUID).** The relative path within `.plan/` is the canonical task identifier (e.g., `data-preparation/merge`). Directory names are descriptive slugs — no numeric prefixes. Display and execution order derived from DAG topological sort of `depends_on`.

**Hooks + Convenience CLI.** Agents edit task.md directly using Read/Edit/Write. PostToolUse hooks handle validation (frontmatter, dep references, cycle detection) and dashboard rebuild. `task_create.py` kept for convenience (auto-fills template). Read-path CLI kept: `task_read.py` (context injection), `task_query.py` (tree/frontier/DAG).

**Flexible body sections.** No rigid structure enforced. Any `## Heading` is valid — each becomes a foldable layer in dashboard. Recommended defaults: `## Objective`, `## Results`, `## Decisions`, `## Review Notes`.

**User decisions in-task.** Decisions go in the relevant task's `## Decisions` section. Cross-cutting decisions in root task's `## Decisions`. No separate monolithic section.

**Progressive skill revelation (3 tiers).** Consumer (SKILL.md body: read, edit, query), Planner (references/planning.md: objectives, splitting, retroactive), Contributor (references/internals.md: data layer, hooks).

**What replaces what:**

| Old | New |
|---|---|
| PLAN.md header | Root task.md body sections |
| `## Project Conventions` | Root task.md `## Conventions` |
| `## Workflow Status` | Root task.md `## Workflow Status` |
| `### Task N:` block | `<path>/task.md` |
| RESULTS.md task section | Task's `## Results` |
| `**Review status:**` | `review_status:` in frontmatter |
| Review-notes blockquote | Task's `## Review Notes` |
| Steps with checkboxes | Subtasks or prose |
| Separate RESULTS.md | Gone — results in task.md body |

## Results

