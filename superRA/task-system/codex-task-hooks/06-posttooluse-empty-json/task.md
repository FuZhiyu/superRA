---
title: "Codex PostToolUse empty JSON fallback"
status: implemented
depends_on:  []
tags: []
created: 2026-06-09
---

## Objective

Fix the Codex task-hook failure where no-feedback PostToolUse paths emit empty stdout, which current Codex treats as invalid hook JSON. Make the task hook emit valid JSON on every Codex-facing no-feedback or ignored path, normally `{}`, while preserving the hook's non-blocking behavior and Claude compatibility. Also add the missing `hooks/hooks-codex.json` fallback so an unset plugin root prints `{}` like the other Codex hooks.

Outputs: `task_hook.py` and generated or manifest hook wiring changes as needed; regression tests proving no-feedback task-hook invocations return `rc=0` and parseable JSON, and that feedback paths still return `additionalContext`.

## Results

Implemented the Codex empty-output JSON fallback for the task-system PostToolUse hook.

- [task_hook.py](../../../../skills/task-system/scripts/task_hook.py#L39) now has a `SUPERRA_TASK_HOOK_EMPTY_JSON` compatibility mode. In that mode, and automatically for `apply_patch` payloads, every no-feedback success path exits `0` and emits `{}` through the shared success helper while feedback paths still emit `additionalContext` JSON ([task_hook.py](../../../../skills/task-system/scripts/task_hook.py#L121), [task_hook.py](../../../../skills/task-system/scripts/task_hook.py#L502)).
- [hooks-codex.json](../../../../hooks/hooks-codex.json#L30) now exports that compatibility flag for task-hook PostToolUse commands and prints `{}` when no plugin root is available, matching the other Codex hook fail-open fallbacks.
- Regression coverage verifies Claude silent no-op compatibility, Codex `{}` no-feedback outputs for Edit/Write, Bash, empty stdin, and `apply_patch`, parseable manifest fallback output, and unchanged `additionalContext` feedback paths ([test_task_system.py](../../../../skills/task-system/scripts/test_task_system.py#L2418), [test_task_system.py](../../../../skills/task-system/scripts/test_task_system.py#L2590), [test_task_system.py](../../../../skills/task-system/scripts/test_task_system.py#L2995)).

Verification:

- `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-system/scripts/test_task_system.py -v` passed: 328 tests passed, 4 warnings.
