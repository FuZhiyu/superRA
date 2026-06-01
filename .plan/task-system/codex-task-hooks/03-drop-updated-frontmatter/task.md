---
title: "Drop updated frontmatter field"
status: not-started
depends_on: []
tags: [task-system, schema, metadata]
script: ""
input: [skills/task-system/scripts/_task_io.py, skills/task-system/scripts/task_create.py, skills/task-system/scripts/task_update.py, skills/task-system/scripts/task_add_result.py, skills/task-system/scripts/task_link.py, skills/task-system/scripts/task_rename.py, skills/task-system/scripts/task_query.py, skills/task-system/scripts/task_read.py, skills/task-system/scripts/plan_dashboard.py, skills/task-system/scripts/templates/summary_bar.html, skills/task-system/SKILL.md, skills/task-system/references/internals.md, skills/task-system/scripts/test_task_system.py, skills/task-system/scripts/test_dashboard.py, skills/task-system/scripts/tests/test_state_preservation.py, .plan]
output: [same files with active updated-field behavior removed]
created: 2026-06-01
updated: 2026-06-01
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
