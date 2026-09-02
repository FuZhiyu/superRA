---
title: "PostToolUse Reminder When a Producer Changes Without Its Step"
status: not-started
depends_on: [01-section-contract]
---

## Objective

Extend the task hook so an edit to a maintained producer that leaves the graph untouched gets a non-blocking reminder in the same turn.

- **Trigger:** the edited or written file is a dep or script of a registered step, or lies under a configured `code_roots` directory, and no `## Reproduction` section changed in the same tool call.
- **Message:** names the file, the owning step(s) if any, and the duty: update the step's deps/outs or register a new step, then run `superra repro status`. One reminder per turn.
- **Parity:** the Claude hook and the Codex hook manifest emit the same reminder; both remain fail-open when the tree has no reproduction config.
- **Validation criteria:** hook fixture tests for edit-under-code-root, edit-of-registered-dep, edit-with-section-change (no reminder), and no-config (silent); existing hook tests stay green.

## Details

- The hook entry is [task_hook.py](../../../skills/task-tree/scripts/task_hook.py) via `hooks/task-hook`; Codex wiring lives in `hooks/hooks-codex.json`. Reuse the graph model from [01-section-contract](../01-section-contract/task.md) for the dep lookup.

## Results
