---
title: ".plan/-Native Implementation"
status: not-started
review_status: ~
integration_status: ~
depends_on: 
  - agent-protocols
  - handoff-doc

tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Update `skills/implementation-workflow/SKILL.md` for `.plan/` hierarchy.

### Key changes

- **Frontier computation:** use `task_query.py --frontier` to find dispatchable tasks instead of manual dependency traversal through PLAN.md task blocks
- **Task dispatch:** path in dispatch prompt `Task: data-preparation/merge` instead of "Task 3 in PLAN.md"
- **Implementer context:** implementer runs `task_read.py --path <path>` to get ancestor context + sibling deps (replaces "read the full task block and PLAN.md header context")
- **No RESULTS.md management:** results live in task.md `## Results`. No pre-allocated stubs. No "find your section and replace its content" — each task.md is self-contained
- **Status updates:** implementer edits `status:` and `review_status:` in frontmatter directly. Hooks validate
- **Atomic commits:** `git add <code-files> <task-path>/task.md` (not `git add code PLAN.md RESULTS.md`)
- **Review loop:** reviewer reads task.md via `task_read.py`, writes `## Review Notes` with same severity/citation/fix format, edits `review_status:` in frontmatter
- **Completion check:** `task_query.py --tree` shows all tasks approved (root effective_status = approved), or check root task's rolled-up status
- **Reproducibility verification:** unchanged — pipeline runs all scripts in order
- **Step 4 completion disposition:** unchanged but references `.plan/` paths

### Remove

- RESULTS.md pre-allocation at planning time
- "Find your pre-allocated RESULTS.md section" guidance
- Step-checkbox tracking (`- [ ]` / `- [x]` step completion)
- References to PLAN.md task block anatomy

## Results

