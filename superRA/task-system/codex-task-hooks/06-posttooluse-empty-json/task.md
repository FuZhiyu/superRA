---
title: "Codex PostToolUse empty JSON fallback"
status: not-started
depends_on:  []
tags: []
created: 2026-06-09
---

## Objective

Fix the Codex task-hook failure where no-feedback PostToolUse paths emit empty stdout, which current Codex treats as invalid hook JSON. Make the task hook emit valid JSON on every Codex-facing no-feedback or ignored path, normally `{}`, while preserving the hook's non-blocking behavior and Claude compatibility. Also add the missing `hooks/hooks-codex.json` fallback so an unset plugin root prints `{}` like the other Codex hooks.

Outputs: `task_hook.py` and generated or manifest hook wiring changes as needed; regression tests proving no-feedback task-hook invocations return `rc=0` and parseable JSON, and that feedback paths still return `additionalContext`.

## Results
