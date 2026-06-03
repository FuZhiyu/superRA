---
title: "Surface Hook Feedback to Agents"
status: implemented
depends_on: 
  - 04-docs-tests-and-compat

tags: []
created: 2026-06-03
---

## Objective

Fix the task-system PostToolUse hook so validation warnings and non-fatal reconcile failures are injected back into the agent context for both Claude Code and Codex while preserving the hook as a non-blocking passive reconciler. Invalid task statuses must become model-visible immediately after a task.md edit or Codex apply_patch edit, without relying on stderr visibility. The implementation must keep exit code 0 for passive reconcile behavior, emit harness-compatible JSON on stdout only when there is feedback to inject, and keep silent fast paths silent. Update the active task-hook internals documentation and focused tests for Claude Edit/Write and Codex apply_patch/manifest-wrapper behavior. Validate that invalid enum edits produce additionalContext/hookSpecificOutput feedback, that dashboard rebuild failures no longer hide the warning from the agent, and that valid edits still rebuild/propagate normally.

## Results

Implemented the task-system PostToolUse hook feedback surface. `task_hook.py` now collects validation warnings plus non-fatal status-propagation and dashboard-rebuild failures, emits a single PostToolUse JSON payload only when feedback exists, and keeps passive reconcile exit code 0. The payload carries both top-level `additionalContext` and Claude-compatible `hookSpecificOutput.additionalContext`, so invalid task statuses and dashboard failures become model-visible without depending on stderr ([task_hook.py:45](../../../../skills/task-system/scripts/task_hook.py#L45), [task_hook.py:69](../../../../skills/task-system/scripts/task_hook.py#L69)).

Silent paths remain silent: valid edits suppress dashboard-generator stdout while still propagating parent status and rebuilding dashboards, ignored payloads emit nothing, and the stable shell wrapper no longer replays `uvx` stderr or prints `{}` when it has no feedback to inject ([task_hook.py:99](../../../../skills/task-system/scripts/task_hook.py#L99), [hooks/task-hook:21](../../../../hooks/task-hook#L21), [hooks/hooks-codex.json:24](../../../../hooks/hooks-codex.json#L24)).

Updated the active task-hook internals documentation to describe the JSON feedback contract and added focused coverage for Claude Edit/Write, Codex `apply_patch`, Codex manifest wrapper execution, invalid enum feedback, dashboard-failure feedback, and valid apply_patch propagation ([internals.md:92](../../../../skills/task-system/references/internals.md#L92), [test_task_system.py:2126](../../../../skills/task-system/scripts/test_task_system.py#L2126), [test_task_system.py:2146](../../../../skills/task-system/scripts/test_task_system.py#L2146), [test_task_system.py:2170](../../../../skills/task-system/scripts/test_task_system.py#L2170), [test-codex-hooks.sh:200](../../../../tests/hooks/test-codex-hooks.sh#L200), [test-codex-hooks.sh:234](../../../../tests/hooks/test-codex-hooks.sh#L234)).

Verification passed:

| Command | Result |
|---|---|
| `uv run --with pytest --project skills/task-system pytest skills/task-system/scripts/test_task_system.py -q` | 224 passed, 11 skipped |
| `bash tests/hooks/test-codex-hooks.sh` | 15 passed, 0 failed |
| `python3 -m json.tool hooks/hooks-codex.json` | valid JSON |
