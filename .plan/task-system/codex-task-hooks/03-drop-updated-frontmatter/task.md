---
title: "Drop updated frontmatter field"
status: revise
depends_on: []
tags: [task-system, schema, metadata]
script: ""
input: [skills/task-system/scripts/_task_io.py, skills/task-system/scripts/task_create.py, skills/task-system/scripts/task_update.py, skills/task-system/scripts/task_add_result.py, skills/task-system/scripts/task_link.py, skills/task-system/scripts/task_rename.py, skills/task-system/scripts/task_query.py, skills/task-system/scripts/task_read.py, skills/task-system/scripts/plan_dashboard.py, skills/task-system/scripts/templates/summary_bar.html, skills/task-system/SKILL.md, skills/task-system/references/internals.md, skills/task-system/scripts/test_task_system.py, skills/task-system/scripts/test_dashboard.py, skills/task-system/scripts/tests/test_state_preservation.py, .plan]
output: [same files with active updated-field behavior removed]
created: 2026-06-01
---

## Objective

Remove `updated` from the active task-system frontmatter schema. Git history is the source of truth for last modification time, and auto-bumping `updated` creates noisy metadata-only diffs whenever hooks or CLIs touch parent tasks.

Implementation requirements:

- Stop generating `updated:` in new tasks.
- Stop parsing `updated` into the public `Task` dataclass / JSON outputs unless a short compatibility shim is needed for legacy reads.
- Stop writing or bumping `updated` in mutation scripts and status propagation.
- Remove dashboard summary/UI use of latest `updated`.
- Remove `updated` from task-system docs, examples, and tests.
- Migrate active `.plan/` task files in this worktree to remove `updated:` lines so the repository's own task tree matches the new schema.

Keep `created:` for this task unless the implementer records a stronger reason to drop it too. `created` is not a substitute for git history; it is a stable task-inception date for human scanning, including before the task's first commit and after a task directory is moved. If the implementer proposes dropping `created`, record the tradeoff in `## Results` before making that broader schema change.

Validation: run the task-system pytest suite and a grep over active task-system code/docs/tests for `updated:` and task `.updated` access. Remaining uses of the word "updated" as ordinary prose or variable names for function return values are acceptable when they do not represent the frontmatter field.

## Results

Implemented the task metadata cleanup while keeping `created` as the stable task-inception date.

- Removed `updated` from the `Task` dataclass, parser/writer field order, JSON outputs, task creation/migration templates, task mutation scripts, status propagation, and dashboard summary surfaces.
- Updated task-system docs and internals references so the active schema documents `created` but no longer documents `updated`.
- Updated task-system test fixtures and expectations to generate/read task files without `updated`.
- Migrated this worktree's `.plan/**/task.md` files to remove `updated:` frontmatter lines.

Validation:

- `uv run pytest skills/task-system/scripts/test_task_system.py skills/task-system/scripts/test_dashboard.py skills/task-system/scripts/tests/test_state_preservation.py` passed: 280 tests.
- `rg -n "updated:|\\.updated|\\\"updated\\\"|stat-updated|updated_date" skills/task-system .plan/task-system/codex-task-hooks` has no active schema hits; remaining hits are this task's own prose, the legacy-read stale-field suppression entry, and local status-propagation count variables.
- `python3 skills/task-system/scripts/task_check.py --plan-root .plan` passed.

## Review Notes

1. MAJOR [../../../task.md:21](../../../task.md#L21), [../../../../skills/task-system/scripts/plan_dashboard.py:887](../../../../skills/task-system/scripts/plan_dashboard.py#L887), [../../../../skills/task-system/scripts/templates/base.html:1838](../../../../skills/task-system/scripts/templates/base.html#L1838), [../../../../skills/task-system/scripts/test_dashboard.py:234](../../../../skills/task-system/scripts/test_dashboard.py#L234), [../../../../skills/task-system/scripts/test_task_system.py:856](../../../../skills/task-system/scripts/test_task_system.py#L856): the merge record says the integration kept `better-handoff`'s newer template-backed standalone dashboard exporter, but the committed review range `f0c103664dc9e987a5c4bf6475aa2d5a910a21c4..73e4487a40aca64926ef326b71f5a7e18915dce9` has no `skills/task-system/scripts/plan_dashboard.py`, `skills/task-system/scripts/templates/base.html`, or exporter test hunks. The exporter/share implementation currently exists only as unstaged worktree changes, so the merge commit under review does not actually preserve the stated base-side behavior and the tests were run against a dirty tree. Commit the intended exporter/share hunks as part of the integration result, or remove the stale Sync Map claim if the exporter is intentionally out of scope.

2. MAJOR [task.md:38](task.md#L38): the assigned task's `## Results` validation trail has tests, grep, and `task_check`, but it does not include the required integration Final Diff Self-Check naming the governing range and surviving-change classes/suspicious hunk justifications. Add a fresh final-diff self-check for `git diff f0c103664dc9e987a5c4bf6475aa2d5a910a21c4..73e4487a40aca64926ef326b71f5a7e18915dce9`, including how the committed exporter/share hunks are justified once finding 1 is fixed.
