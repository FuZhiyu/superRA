---
title: "PostToolUse Validation Hooks"
status: implemented
review_status: approved
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

### 1. Hook script ([`skills/task-system/scripts/task_hook.py`](skills/task-system/scripts/task_hook.py))

Reads PostToolUse JSON from stdin. Fast path exits immediately for non-Edit/Write tools, non-`task.md` filenames, and paths not under `.plan/`. On a matching edit:

- Calls `_find_plan_root()` from `_task_io.py` to locate the plan root.
- Calls `validate_plan(plan_root)` and prints any warnings to stderr (prefixed `[task-hook] WARNING:`).
- Calls `generate_dashboard(plan_root)` best-effort (try/except, non-fatal).
- Always exits 0.

Import approach: adds the `scripts/` directory to `sys.path` at runtime rather than using `importlib.util.spec_from_file_location`, which fails with `@dataclass` under Python 3.14 when the module is loaded outside `sys.modules`.

### 2. Hook configuration ([`hooks/hooks.json`](hooks/hooks.json))

Added a `PostToolUse` entry matching `Edit|Write` to the plugin's tracked `hooks/hooks.json`. Hook command: `python3 "${CLAUDE_PLUGIN_ROOT}/skills/task-system/scripts/task_hook.py"`, using the same `${CLAUDE_PLUGIN_ROOT}` convention as all other plugin hooks.

Note: `.claude/` is gitignored in this project. The task spec's "add to `.claude/settings.json`" would be a local-only runtime config. The tracked deliverable is `hooks/hooks.json`, which is installed by the plugin system and picked up by Claude Code.

### Verification

- Fast-path cases (Bash tool, non-task.md edit, task.md outside `.plan/`): all exit 0 with no output.
- Valid plan edit (`.plan/task.md`): runs validation silently, rebuilds dashboard, exits 0.
- Invalid-status task.md: prints validation warning to stderr, dashboard rebuild catches the parse error non-fatally, exits 0.
- All 53 existing `test_task_system.py` tests pass.
