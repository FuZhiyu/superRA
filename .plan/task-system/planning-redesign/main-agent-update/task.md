---
title: "Update main-agent.md for .plan/-native operations"
status: approved
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

### Files Modified

- [`skills/using-superRA/references/main-agent.md`](skills/using-superRA/references/main-agent.md) — Complete rewrite of all PLAN.md/RESULTS.md references to `.plan/` task-tree operations.

### Changes by Section

**§Session Start Actions:** Check for `.plan/task.md` instead of `PLAN.md`. Use `task_query.py --tree` for status summary. Simplified incomplete-plan detection to frontmatter status checks (no more checkbox counting). Added backward-compatibility clause for legacy `PLAN.md` migration. Changed "no plan file" to "no task tree."

**§Workflow Frontier Resolver:** Replaced all five "Read facts" bullet points — removed PLAN header/Workflow Status/Decisions/RESULTS.md references; now reads `.plan/` task tree existence, root task.md sections, per-task frontmatter via `task_query.py --frontier`, and per-task body sections including `## Revision Notes`. Removed "Invalidated milestones" from the return decision (no more `## Workflow Status` boxes). Simplified step 3 (downstream via `depends_on:` edges, exemption noted in revision note instead of `## Decisions`). Removed step 4 (`## Workflow Status` checkbox rollup logic). Updated canonical workflow order to drop `Execution complete` box flip. Updated safety invariants: "reflected in `.plan/` task objectives" instead of "logged in PLAN.md," and "changed task's downstream" instead of "rollup milestone."

**§Changes of the Plan:** Renamed to "§Changes of the Task Tree." Protocol steps now reference `.plan/` task files and `planning-workflow §User Feedback and Changing the Task Tree` (matching the renamed section in the rewritten SKILL.md).

**§Three Pause Classes:** Replaced "logging the researcher's answer per User Decisions Log" with "fold the researcher's answer into the relevant task objective."

**§Log Before You Act:** Replaced `## Decisions` log language with fold-into-objective + `## Revision Notes` mechanism.

**§Banned Phrasings:** Updated the AskUserQuestion guidance to say "fold the answer into the task objective" instead of referencing the User Decisions Log.

**§Direct Mode:** Task context now from `.plan/` task files via `task_read.py` instead of PLAN.md/RESULTS.md.

### Verification

- `grep -n 'PLAN\.md\|RESULTS\.md\|User Decisions Log\|## Decisions\|## Workflow Status\|Changing Plans' main-agent.md` returns only the backward-compatibility migration line (intentional).
- No checkbox, unchecked, or "plan file" references remain.
- All cross-references to planning-workflow use the updated section name (`§User Feedback and Changing the Task Tree`).
