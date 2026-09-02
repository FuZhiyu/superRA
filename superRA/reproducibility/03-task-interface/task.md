---
title: "Surface Reproduction State in the Task CLI"
status: not-started
depends_on: [01-section-contract, 02-runner]
---

## Objective

Make the reproduction graph visible and checkable through the commands agents already use, so a task reader sees its steps' state without loading the runner.

- **`task read <path>`** appends a `Reproduction` block after the inherited context: the task's tier, then one line per owned step with state, reason, and outs; then derived task-level edges (`feeds on: <task>`, `feeds: <task>`). State comes from `repro status --json` when pytask is available and degrades to "unknown (runner unavailable)" otherwise. JSON output gains the same fields.
- **`task check`** gains the `reproduction` category wired to the validation findings of [01-section-contract](../01-section-contract/task.md) and runs it by default.
- **`task tree`** marks `canon` tasks with a badge and accepts `--tier canon|task` to filter.
- **Validation criteria:** CLI tests for each command on a fixture tree with registered and unregistered tasks; `task read` and `task tree` pass with pytask absent.

## Details

- Injection point: [task_read.py](../../../skills/task-tree/scripts/task_read.py) `render_human` / `render_json`; comments are injected the same way, so mirror that pattern.
- `task check` categories are enumerated in [task_check.py](../../../skills/task-tree/scripts/task_check.py) `parse_args`; the dashboard and hook read the same findings.

## Results
