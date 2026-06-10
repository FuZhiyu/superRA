---
title: "Drop updated frontmatter field"
status: approved
depends_on: []
tags: [task-tree, schema, metadata]
script: ""
input: [skills/task-tree/scripts/_task_io.py, skills/task-tree/scripts/task_create.py, skills/task-tree/scripts/task_update.py, skills/task-tree/scripts/task_add_result.py, skills/task-tree/scripts/task_link.py, skills/task-tree/scripts/task_rename.py, skills/task-tree/scripts/task_query.py, skills/task-tree/scripts/task_read.py, skills/task-tree/scripts/plan_dashboard.py, skills/task-tree/scripts/templates/summary_bar.html, skills/task-tree/SKILL.md, skills/task-tree/references/internals.md, skills/task-tree/scripts/test_task_tree.py, skills/task-tree/scripts/test_dashboard.py, skills/task-tree/scripts/tests/test_state_preservation.py, .plan]
output: [same files with active updated-field behavior removed]
created: 2026-06-01
---

## Objective

Remove `updated` from the active task-tree frontmatter schema. Git history is the source of truth for last modification time, and auto-bumping `updated` creates noisy metadata-only diffs whenever hooks or CLIs touch parent tasks.

Implementation requirements:

- Stop generating `updated:` in new tasks.
- Stop parsing `updated` into the public `Task` dataclass / JSON outputs unless a short compatibility shim is needed for legacy reads.
- Stop writing or bumping `updated` in mutation scripts and status propagation.
- Remove dashboard summary/UI use of latest `updated`.
- Remove `updated` from task-tree docs, examples, and tests.
- Migrate active `.plan/` task files in this worktree to remove `updated:` lines so the repository's own task tree matches the new schema.

Keep `created:` for this task unless the implementer records a stronger reason to drop it too. `created` is not a substitute for git history; it is a stable task-inception date for human scanning, including before the task's first commit and after a task directory is moved. If the implementer proposes dropping `created`, record the tradeoff in `## Results` before making that broader schema change.

Validation: run the task-tree pytest suite and a grep over active task-tree code/docs/tests for `updated:` and task `.updated` access. Remaining uses of the word "updated" as ordinary prose or variable names for function return values are acceptable when they do not represent the frontmatter field.

## Results

Implemented the task metadata cleanup while keeping `created` as the stable task-inception date.

- Removed `updated` from the `Task` dataclass, parser/writer field order, JSON outputs, task creation/migration templates, task mutation scripts, status propagation, and dashboard summary surfaces.
- Updated task-tree docs and internals references so the active schema documents `created` but no longer documents `updated`.
- Updated task-tree test fixtures and expectations to generate/read task files without `updated`.
- Migrated this worktree's `.plan/**/task.md` files to remove `updated:` frontmatter lines.

Validation:

- `uv run pytest skills/task-tree/scripts/test_task_tree.py skills/task-tree/scripts/test_dashboard.py skills/task-tree/scripts/tests/test_state_preservation.py` passed: 280 tests.
- `rg -n "updated:|\\.updated|\\\"updated\\\"|stat-updated|updated_date" skills/task-tree .plan/task-tree/codex-task-hooks` has no active schema hits; remaining hits are this task's own prose, the legacy-read stale-field suppression entry, and local status-propagation count variables.
- `python3 skills/task-tree/scripts/task_check.py --plan-root .plan` passed.

Integration fix after `better-handoff` sync:

- Clarified the root Sync Map: the sync preserved the base branch's committed template-backed dashboard exporter, but did not commit unrelated in-flight subtree Share/export work. That dirty work was stashed before revalidation so the metadata integration checks run against the committed tree.
- Final Diff Self-Check for the integration range `f0c103664dc9e987a5c4bf6475aa2d5a910a21c4..HEAD`: surviving hunks are limited to the `codex-task-hooks` task tree, removal of `updated:` frontmatter from `.plan/**/task.md`, task-tree schema/writer/query/read/update/link/rename/result/migration cleanup, dashboard summary removal in `templates/summary_bar.html`, docs/examples/tests for the new schema, review/sync notes, and the approved task status. No exporter/share implementation hunks are part of this integration; that code belongs to the separate subtree-export workstream.
- Clean-tree validation after stashing unrelated subtree Share/export work: `uv run pytest skills/task-tree/scripts/test_task_tree.py skills/task-tree/scripts/test_dashboard.py skills/task-tree/scripts/tests/test_state_preservation.py` passed: 288 tests; `python3 skills/task-tree/scripts/task_check.py --plan-root .plan` passed.

## Review Notes

> 1. [MINOR] `output:` frontmatter is a prose sentence ("same files with active updated-field behavior removed"), not file paths — scope-defining fields should be machine-meaningful; list the actual files or drop the field (planner-owned; flagging for the orchestrator).
> 2. [MINOR] `.plan`-rooted phrasing stated as current (objective and Results); same terminology fix as the parent's item 2.
