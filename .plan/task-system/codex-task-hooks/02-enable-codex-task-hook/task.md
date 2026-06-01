---
title: "Enable Codex task-system PostToolUse hook"
status: not-started
depends_on: []
tags: [hooks, codex, task-system]
script: ""
input: [hooks/hooks-codex.json, skills/task-system/scripts/task_hook.py, skills/task-system/scripts/test_task_system.py]
output: [hooks/hooks-codex.json, skills/task-system/scripts/task_hook.py, skills/task-system/scripts/test_task_system.py]
created: 2026-06-01
---

## Objective

Install the task-system reconcile hook for Codex and make the hook script understand Codex edit payloads.

Add `PostToolUse` registrations to `hooks/hooks-codex.json` for:

- `matcher: "Edit|Write"` so Codex file edits through `apply_patch` trigger task reconciliation.
- `matcher: "Bash"` so shell commands that structurally mutate `.plan/` trigger the same reconcile path as Claude Code.

Use plugin-root resolution consistent with the existing Codex manifest: prefer `PLUGIN_ROOT`, fall back to `CLAUDE_PLUGIN_ROOT`, and fail open with `{}` when no root is available. The command should invoke `skills/task-system/scripts/task_hook.py` from the plugin root.

Adapt `task_hook.py` for Codex `PostToolUse` edit events. Codex reports file edits as `tool_name: "apply_patch"` even when the matcher alias is `Edit|Write`; the relevant file paths are inside `tool_input.command`, not `tool_input.file_path`. The hook should parse apply-patch filenames touching `.plan/**/task.md`, reconcile each affected plan root once, and keep the existing Bash and Claude `Edit`/`Write` behavior intact. If validation warnings need to be visible in Codex, return a Codex-compatible JSON `hookSpecificOutput.additionalContext` while preserving non-blocking behavior.

Validation: extend `skills/task-system/scripts/test_task_system.py` or add a focused hook test so synthetic Codex `PostToolUse` payloads cover both `apply_patch` edits of `.plan/**/task.md` and Bash structural mutations. Confirm the hook exits 0 on irrelevant apply-patch payloads and no-root manifest execution.

## Results
