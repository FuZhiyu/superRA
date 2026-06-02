# Semantic Merge Record

**Operation:** `merge --squash`
**Current branch:** `better-handoff`
**Incoming ref:** `analysis/codex-task-hooks`
**Governing baseline:** `9ca25479f7cb588aec3d758f0bb27d66e4c8aded`
**Merge commit:** Squash commit containing this record
**Propagation commits:** `None`

## Current Branch Intent

`better-handoff` already carried the lean task-system skill surface, packaged `superra` CLI, and stable `hooks/task-hook` wrapper for task-tree reconciliation.

## Incoming Intent

`analysis/codex-task-hooks` removes the decision-reminder hook, wires Codex task-tree `PostToolUse` reconciliation for task edits and structural shell changes, teaches `task_hook.py` to handle Codex `apply_patch` payloads and `.plan` roots, updates hook docs, and adds regression coverage.

## Resolution Thesis

The squash keeps current branch packaging conventions while taking the incoming Codex hook behavior. Claude and Codex manifests both use stable hook entry points; Codex `PostToolUse` now routes through `hooks/run-hook.cmd task-hook` instead of pointing directly at source scripts. The deprecated `ask-user-question-logger` hook is removed from manifests, tests, docs, and the hook directory.

## File / Script Impact Map

| Path or path cluster | Incoming intent | Resolution | Codebase context |
|---|---|---|---|
| `hooks/hooks-codex.json` | Add Codex `PostToolUse` task-tree reconcile hooks. | Added `Edit|Write` and `Bash` matchers, routed through `run-hook.cmd task-hook`. | Preserves current packaged-wrapper convention. |
| `hooks/hooks.json`, `hooks/hooks-cursor.json`, `hooks/ask-user-question-logger` | Remove decision-reminder hook. | Removed `AskUserQuestion` / Cursor entries and deleted the script. | User-decision logging remains workflow discipline, not hook reminder behavior. |
| `skills/task-system/scripts/task_hook.py` | Accept Codex `apply_patch` payloads and `.plan` structural shell references. | Kept incoming parser and handler additions. | Existing hook remains best-effort and non-blocking. |
| `skills/task-system/SKILL.md`, `skills/task-system/references/internals.md` | Document Codex task-hook coverage. | Kept `SKILL.md` lean; documented details in `internals.md §Hook Architecture`. | Matches DRY/Necessity gate for skill text. |
| `tests/**`, `skills/task-system/scripts/test_task_system.py` | Cover Codex task hook wiring and behavior. | Preserved incoming behavior tests and adapted manifest assertions to the stable wrapper. | Avoids stale direct-script path expectations. |
| `superRA/task-system/codex-task-hooks/**`, `superRA/task.md` | Carry task-tree implementation, integration, and documentation evidence. | Preserved Codex hook task evidence; dropped stale incoming Sync Map block from an older base-sync. | Root integration notes remain current-branch history plus Codex hook closure evidence. |

## User Decisions

None.

## Checks

- `python3 -m json.tool hooks/hooks-codex.json`, `hooks/hooks.json`, `hooks/hooks-cursor.json` — pass.
- `bash tests/hooks/test-codex-hooks.sh` — pass, 14/14.
- `uv run pytest skills/task-system/scripts/test_task_system.py` — pass, 233 tests.
- `python3 skills/task-system/scripts/task_check.py --plan-root superRA` — pass.
- `git diff --cached --check` — pass.
- Anchored conflict-marker sweep — pass for merge markers.
- `bash tests/check-harness-compatibility.sh` — fails on the pre-existing assertion `using-superRA manifest must reference theory-modeling`; `skills/using-superRA/SKILL.md` is outside this squash's touched hook surface.

## Codebase Context

This squash intentionally synthesizes the incoming Codex hook implementation with the current branch's packaged hook-wrapper design.
