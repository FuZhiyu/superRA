---
title: "PostToolUse Validation Hooks"
status: not-started
review_status: ~
integration_status: ~
depends_on: 
  - task-io-enhancements

tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Create PostToolUse hooks that fire when an agent edits or writes a `task.md` file within `.plan/`. Two components:

### 1. Hook script (`skills/task-system/scripts/task_hook.py`)

- Receives the tool name and file path from the hook environment variables
- Checks if the file is a `task.md` under a `.plan/` directory
- If not a task.md edit: exit 0 immediately (fast path)
- If yes: find plan root by walking up from the file path
- Run `validate_plan(plan_root)` from `_task_io.py`, print any warnings to stderr
- Run `generate_dashboard(plan_root)` best-effort (try/except, never fail)
- Exit 0 always — never block the agent

The hook uses `_find_plan_root()` from `_task_io.py` to locate the plan root. It imports `validate_plan` and `generate_dashboard` from the same module.

### 2. Hook configuration

Add to project `.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "python3 skills/task-system/scripts/task_hook.py"
      }
    ]
  }
}
```

The hook reads `$CLAUDE_TOOL_NAME` and `$CLAUDE_FILE_PATH` (or equivalent) from the environment. Check the Claude Code hook documentation for the exact env var names available to PostToolUse hooks.

The hook provides immediate feedback: validation warnings appear as hook output visible to the agent, dashboard is silently rebuilt. The agent sees warnings and can fix issues on the next edit.

## Results

