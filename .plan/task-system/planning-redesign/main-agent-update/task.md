---
title: "Update main-agent.md for .plan/-native operations"
status: not-started
review_status: ~
integration_status: ~
depends_on: 
  - skill-rewrite

tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Rewrite `skills/using-superRA/references/main-agent.md` to replace all PLAN.md/RESULTS.md references with `.plan/` task-tree operations.

### Session Start Actions (lines 5–16)
- Check for `.plan/task.md` instead of `PLAN.md`
- Detect incomplete plans via `task_query.py --tree` (tasks with non-approved status) instead of checking for unchecked `- [ ]` steps
- Summary format: "Found in-progress analysis: `.plan/` (N tasks approved, K with issues). Resume?"
- If user confirms: read `.plan/` task tree, check git log, run §Workflow Frontier Resolver
- Keep backward compatibility: if PLAN.md found without `.plan/`, offer migration via `plan_migrate.py`

### Workflow Frontier Resolver (lines 22–66)
- Read facts from `.plan/` task files (frontmatter `status`, `review_status`, `integration_status`) instead of PLAN.md checkboxes
- Use `task_query.py --frontier` to find dispatchable tasks
- Compute affected frontier using task dependencies (`depends_on:` frontmatter) instead of PLAN.md step references
- Remove references to `## Workflow Status` checkboxes — status lives in task frontmatter rollup
- Remove "check `## Decisions` for unlogged user decisions" — `## Decisions` is being dropped (see `revision-notes` sibling task)

### Changes of the Plan (line 70)
- Reference `.plan/` task files instead of "inline-edit PLAN.md"
- Point to `planning-workflow §User Feedback and Changing Plans` (already updated)

### Direct Mode (lines 124–134)
- Task context comes from `.plan/` task files (via `task_read.py` or direct read), not PLAN.md/RESULTS.md
- Point to direct-mode references (which will be regenerated separately)

### Decisions → Revision Notes (in this file only)
Since this task is already rewriting `main-agent.md`, also handle the `## Decisions` → `## Revision Notes` language changes in this file:
- §Log Before You Act: replace "written into relevant task.md `## Decisions`" with the new mechanism (fold decisions into objective text, optionally add revision note)
- §Three Pause Classes: drop "log per User Decisions Log" language — replace with "fold the answer into the task objective before acting"
- §Safety Invariants: replace "logged in PLAN.md" with "reflected in `.plan/` task objectives"

The `revision-notes` sibling task handles the same concept change in all OTHER files (task-system, agents, orchestration).

## Results

