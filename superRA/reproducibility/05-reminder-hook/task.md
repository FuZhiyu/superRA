---
title: "PostToolUse Reminder When a Producer Changes Without Its Step"
status: not-started
depends_on: [01-section-contract]
---

## Objective

Extend the task hook so an edit to a maintained producer that leaves the graph untouched gets a non-blocking reminder in the same turn.

- **Trigger:** the edited or written file is a dep or script of a registered step, or lies under a configured `code_roots` directory. Task files never trigger.
- **Suppression:** one reminder per file per session, recorded as a marker in the runner's gitignored state directory keyed on the session id the hook payload carries (fallback: per process lifetime). Editing a `## Reproduction` section clears the markers for the files that section's steps name.
- **Message:** names the file, the owning step(s) if any, and the duty: update the step's deps/outs or register a new step, then run `superra repro status`.
- **Parity:** the Claude hook and the Codex hook manifest emit the same reminder; both remain fail-open when the tree has no reproduction config.
- **Validation criteria:** hook fixture tests for edit-under-code-root, edit-of-registered-dep, second edit of the same file in one session (silent), edit after the section was updated (reminder again), task-file edit (silent), and no-config (silent); existing hook tests stay green.

## Details

- The hook entry is [task_hook.py](../../../skills/task-tree/scripts/task_hook.py) via `hooks/task-hook`; Codex wiring lives in `hooks/hooks-codex.json`. Reuse the graph model from [01-section-contract](../01-section-contract/task.md) for the dep lookup.

## Results
