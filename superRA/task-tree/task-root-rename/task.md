---
title: "Rename Task Root to superRA"
status: approved
depends_on:  []
tags: []
created: 2026-06-01
---

## Objective

Rename the default on-disk task-tree directory from `.plan/` to `superRA/` throughout active superRA behavior. Update workflow skills, task-tree docs, hooks, CLI defaults/help, dashboard/worktree discovery, tests, generated Codex role references, and the live task tree so new and resumed workflows look for `superRA/task.md` first. Preserve internal variable names such as `plan_root` when they mean a generic task-root path, and preserve clearly historical/archive prose such as old process notes unless it controls current behavior. Maintain compatibility where practical by allowing explicit `--plan-root` overrides and migration outputs, but make `superRA/` the documented and auto-detected default. Verification must include task-tree tests, dashboard/worktree tests, generated-agent sync tests, and task-tree integrity checks against the renamed root. Generated files affected by skill/agent edits must be regenerated with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` rather than hand-edited: `skills/using-superra/references/direct-mode-implementer.md`, `skills/using-superra/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, and `.codex/agents/superra_reviewer.toml`.

## Results

### Key Findings
- Renamed the live task tree from `.plan/` to `superRA/` and added `superRA/serve`.
- Updated active workflow skills, task-tree docs, hooks, dashboard/worktree discovery, CLI defaults/help, tests, generated Codex implementer artifacts, and current user-facing docs to prefer `superRA/`.
- Preserved explicit legacy `.plan/` compatibility in task-root discovery, worktree discovery, hook path recognition, and dashboard absolute-link handling.
- Reviewer pass found and fixed a `task_read.py` autodetection gap from ordinary repo subdirectories; added a regression for that path.
- Integration review fix made `task_update.py`, `task_add_result.py`, `task_link.py`, `task_rename.py`, and `task_check.py` auto-detect the task root when `--plan-root` is omitted, preferring `superRA/`, while preserving explicit overrides and legacy `.plan/` detection.

### Verification
- `uv run pytest skills/task-tree/scripts/test_task_tree.py skills/task-tree/scripts/test_dashboard.py skills/task-tree/scripts/test_worktree_selector.py skills/task-tree/scripts/tests/test_state_preservation.py` — 356 passed.
- `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py` — 6 passed.
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` — generated project agents and direct-mode references are up to date.
- `python3 skills/task-tree/scripts/task_check.py --plan-root superRA` — all checks passed.
- `uv run pytest skills/task-tree/scripts/test_task_tree.py -k 'ReviewedCliTaskRootDefaults or TestTaskCheck or TestPropagateAll'` — 19 passed.
- `uv run pytest skills/task-tree/scripts/test_task_tree.py` — 193 passed.
- `python3 skills/task-tree/scripts/task_check.py` — all checks passed with task-root auto-detection.

**Final diff self-check:** `git diff 981715dbb01eb99085d664778a121ce1a0d09f2c..HEAD`; surviving branch-local change classes are the approved `.plan/` -> `superRA/` task-root materialization (`.plan/task.md` deletion, `superRA/task.md`, `superRA/serve`, and 100%-similarity task-file renames), active-behavior/docs/hooks/dashboard/worktree updates for the new root, CLI default/autodetection fixes plus tests, generated implementer artifacts from the required generator path, and root/task documentation for the post-sync state. Suspicious hunks are instruction edits under `skills/` and `agents/`, generated direct-mode/Codex agent artifacts, the broad task-tree rename, and Sync Map/task-doc additions; they are justified by the objective's active-behavior rename, the generated-artifact requirement, and the approved post-sync context. Surviving overlap with Sync cluster `dashboard-self-contained-export` is limited to branch-local `superRA` adaptation on cluster-touched paths: `CLAUDE.md` task-tree terminology, `plan_dashboard.py` default-root/help wording, `base.html` task-root comments/internal-link prefix handling, `test_dashboard.py` and `test_task_tree.py` fixture/default updates, and the carried approved task record at `superRA/task-tree/dashboard/self-contained-export/task.md`; cluster assets such as `skills/task-tree/scripts/vendor/**` and `.gitattributes` have no branch-local hunk in this governing range. No unrelated hunks identified.

## Review Notes

Retrospective audit note (MINOR; status unchanged per orchestrator instruction):

> 1. [MINOR] Results ([task.md:16](task.md#L16)) record "added `superRA/serve`" with no pointer that [cli-scripts/wrappers-and-hooks](../cli-scripts/wrappers-and-hooks/task.md) later removed the wrapper deliberately (no replacement launcher); a reader following this approved record could resurrect it. Add a brief supersession note.
