---
title: "Update Agent Role Specs"
status: not-started
review_status: ~
integration_status: ~
depends_on: 
  - skill-restructure

tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Update `agents/implementer.md`, `agents/reviewer.md`, and dispatch templates in `skills/agent-orchestration/SKILL.md` for `.plan/`-native operation.

### Changes to `implementer.md`

- **§Before You Start:** "Read your task via `task_read.py --path <path>`" replaces "Read your task block from PLAN.md". This gives the implementer ancestor context + sibling dependency status automatically
- **§Before You Start:** "Read root task.md `## Conventions`" replaces "Read PLAN.md's `## Project Conventions`"
- **§Handoff:** Edit task.md body sections directly (Read + Edit tools). Hooks validate + rebuild dashboard. No separate RESULTS.md to manage
- **§What You Own:** body sections of your assigned task only — write `## Results`, respond in `## Review Notes` with `→ implemented:` annotations, record in `## Decisions`. You may add any `##` section that serves the task
- **§What You Don't Own:** other tasks' content, scope-defining frontmatter (title, depends_on, script, input, output — planner-owned)
- **§Pre-Commit Self-Check:** adapted for task.md. "Every edit is inside my assigned task.md" replaces "inside my PLAN.md task block". Remove RESULTS.md checklist items
- **§Report Format:** point at task path (e.g., "see `data-preparation/merge/task.md`") not "PLAN.md Task N" or "RESULTS.md Task N section"
- **Remove:** all references to RESULTS.md as a separate file, step-checkbox tracking (`- [ ]` / `- [x]`), "mark steps checked" guidance
- **§Update the Docs and Commit:** single atomic commit of code + task.md (not code + PLAN.md + RESULTS.md)

### Changes to `reviewer.md`

- Read task via `task_read.py` for context (gets ancestor chain + sibling deps)
- Write review in task's `## Review Notes` section (same blockquote format with severity, citation, fix guidance)
- Edit `review_status:` in frontmatter directly
- Reference task by path, not number
- On re-review: delete confirmed-fixed items from `## Review Notes`, remove section entirely when empty and set `review_status: approved`

### Changes to dispatch templates (`agent-orchestration/SKILL.md`)

- `Task:` field uses path: `Task: data-preparation/merge`
- Remove all references to "Task N in PLAN.md"
- The implementer/reviewer find their task by running `task_read.py --path <dispatch-task-path>`

## Results

