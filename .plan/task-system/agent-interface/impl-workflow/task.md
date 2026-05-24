---
title: ".plan/-Native Implementation"
status: implemented
review_status: approved
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

Updated `skills/implementation-workflow/SKILL.md` for `.plan/`-native operation. All changes applied:

- **Frontmatter description:** updated triggers and references from `PLAN.md` to `.plan/` task tree
- **Execution Modes §1:** "Load plan from `.plan/` task tree" replaces "Load plan from `PLAN.md`"
- **Step 0b:** renamed "Task Tree Existence Check"; checks `.plan/task.md` existence and clean worktree instead of `PLAN.md` + `RESULTS.md`
- **Step 1:** reads root `.plan/task.md` + `task_query.py --tree` instead of `PLAN.md` + `RESULTS.md`; references root task.md `## Conventions` instead of `## Project Conventions`
- **Step 2:** frontier computed via `task_query.py --frontier`; `Task:` field uses path; implementer commits code + task.md (not PLAN.md + RESULTS.md); reviewer reads via `task_read.py`, writes `## Review Notes` in task.md, sets `review_status:` in frontmatter
- **Step 3:** verification uses `task_query.py --tree` for status check; results confirmed per-task in `## Results`; deferred MINORs checked in task `## Review Notes`; workflow-status checkbox in root task.md
- **Step 4:** notation/assumption promotion scans task `## Results` ledgers against root task.md; decision logging points to root task.md `## Decisions`
- **Red Flags:** pointer-based dispatch references task path and `task_read.py`; status references use lowercase frontmatter values

Removed: all RESULTS.md management, step-checkbox tracking, PLAN.md task block references, "find your pre-allocated section" guidance.
