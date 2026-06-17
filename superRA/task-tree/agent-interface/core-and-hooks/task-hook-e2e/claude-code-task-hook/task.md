---
title: "Claude Code Task-Hook E2E"
status: implemented
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Extend the optional Claude Code CLI end-to-end hook suite so a real Claude Code session edits a temporary task tree and the test verifies that the PostToolUse task-hook ran for that task edit. The test must assert hook evidence from the CLI event stream and resulting task-tree state, not assistant prose.

## Planner Guidance

Use tests/hooks/test-e2e-cli.sh conventions for isolated temp dirs, session cleanup, and structural hook_response assertions. Add a narrow scenario for task-hook PostToolUse coverage without broadening default CI.

## Results

Implemented optional Claude Code runtime task-hook coverage in [test-e2e-cli.sh:249-277](../../../../../../tests/hooks/test-e2e-cli.sh#L249-L277), [test-e2e-cli.sh:423-496](../../../../../../tests/hooks/test-e2e-cli.sh#L423-L496), and [test-e2e-cli.sh:670-712](../../../../../../tests/hooks/test-e2e-cli.sh#L670-L712). The new S7 scenario builds an isolated temporary `superRA/` tree, runs Claude Code with `Read,Edit` and `acceptEdits`, and asserts the NDJSON event stream contains a PostToolUse hook response plus an actual `Edit`/`Write` tool use for `superRA/01-child/task.md`. It then checks filesystem state: child status `approved`, root status propagated to `approved`, and no generated dashboard.

Verification run in this implementation pass:

- `bash -n tests/hooks/test-e2e-cli.sh` passed.
- `bash tests/hooks/test-codex-hooks.sh` passed: 15 passed, 0 failed.

The authenticated paid runtime command `bash tests/hooks/test-e2e-cli.sh` was not run in this pass.
