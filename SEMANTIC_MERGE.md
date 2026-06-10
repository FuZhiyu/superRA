# Semantic Merge Record

**Operation:** `merge --no-ff`
**Current branch:** `better-handoff`
**Incoming ref:** `better-handoff-impl/semantic-move-hook-json-agent/parallel/posttooluse-empty-json`
**Governing baseline:** `8f5dd1d5b22954294b22651e41f95751a2e69466`
**Merge commit:** `1533d06a`
**Propagation commits:** Record update containing this SHA

## Current Branch Intent

`better-handoff` already carried the approved Codex task-hook integration: decision-reminder hook removal, Codex task-system `PostToolUse` wiring, `updated` metadata removal, stable hook-wrapper packaging, and approved task-tree evidence under `superRA/task-system/codex-task-hooks`.

## Incoming Intent

The incoming parallel branch fixes a Codex harness edge case: no-feedback task-hook paths that emitted empty stdout must emit parseable empty hook JSON (`{}`) for Codex, while Claude-compatible no-feedback paths stay silent and feedback paths still return `additionalContext`.

## Resolution Thesis

The merge keeps current branch packaging and approved hook-task structure while taking the incoming parseable-empty-output behavior. The temporary update task is folded into the durable `codex-task-hooks` parent per the update-task lifecycle, and the active internals reference is updated so no stale "silent no-feedback" claim remains.

## File / Script Impact Map

| Path or path cluster | Incoming intent | Resolution | Codebase context |
|---|---|---|---|
| `hooks/hooks-codex.json` | Export Codex empty-JSON mode for task-hook commands and fail open with `{}` when no plugin root exists. | Kept incoming manifest behavior. | Preserves current `run-hook.cmd task-hook` packaging. |
| `skills/task-system/scripts/task_hook.py` | Add `SUPERRA_TASK_HOOK_EMPTY_JSON` and a shared success-exit helper so no-feedback Codex paths emit `{}`. | Kept incoming behavior, including automatic empty-JSON mode for `apply_patch`; feedback JSON remains unchanged. | Existing hook remains best-effort and non-blocking. |
| `skills/task-system/scripts/test_task_system.py` | Cover parseable empty JSON for Codex no-feedback Edit/Write, Bash, empty stdin, manifest fallback, and `apply_patch`. | Preserved incoming regression coverage and Claude silent no-op checks. | Protects the harness-specific output contract. |
| `skills/task-system/references/internals.md` | Avoid stale documentation that all valid/ignored no-feedback paths stay silent. | Updated the active hook architecture reference to distinguish Claude silence from Codex `{}` output. | Scope-limited stale-reference fix. |
| `superRA/task-system/codex-task-hooks/**`, `superRA/task.md` | Record the implemented update task. | Folded the temporary `06-posttooluse-empty-json` task into the durable approved parent and recorded the merge in the root Sync Map. | Prunes integration-stage update-task structure. |

## User Decisions

None.

## Checks

- `python3 -m json.tool hooks/hooks-codex.json` — pass.
- `uv run --script skills/task-system/scripts/cli.py task check --root superRA` — pass.
- `rg -n "^(<<<<<<<|=======|>>>>>>>)" hooks skills/task-system superRA SEMANTIC_MERGE.md` — pass.
- `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-system/scripts/test_task_system.py -v` — pass, 328 tests.
- `bash tests/hooks/test-codex-hooks.sh` — pass, 15/15 after updating stale no-feedback assertions for Codex `{}`.
- `git diff --check` — pass.
- `bash tests/check-harness-compatibility.sh` — fails on the pre-existing assertion `using-superRA manifest must reference theory-modeling`; `skills/using-superRA/SKILL.md` is outside this merge's touched hook-output surface, and the same residual check failure was already recorded in the previous semantic merge record.

## Codebase Context

This merge intentionally synthesizes the incoming Codex hook-output fix with the current branch's packaged hook-wrapper design and approved task-tree structure.
