---
title: "Codex Exec Task-Hook E2E"
status: implemented
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Extend the optional Codex CLI end-to-end test so a real codex exec session edits a temporary task tree and the test verifies that the PostToolUse task-hook ran for that task edit. The test must assert hook evidence from Codex JSONL and resulting task-tree state, not assistant prose.

## Planner Guidance

Start from tests/hooks/test-codex-e2e-cli.sh. Build a minimal superRA/ tree in TMPROOT, install project-local hooks, prompt Codex to make a deterministic task edit, and assert a PostToolUse task-hook response plus status propagation or hook feedback evidence.

## Results

Implemented optional Codex runtime task-hook coverage in [test-codex-e2e-cli.sh:33-74](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L33-L74) and [test-codex-e2e-cli.sh:137-221](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L137-L221). The script now builds a temporary `superRA/` tree, installs PostToolUse task-hook commands with Codex empty-JSON mode, asks a real `codex exec` run to edit `superRA/01-child/task.md`, and asserts parsed JSONL hook evidence plus task-tree state: child status `approved`, root status propagated to `approved`, and no generated dashboard.

Verification run in this implementation pass:

- `bash -n tests/hooks/test-codex-e2e-cli.sh` passed.
- `bash tests/hooks/test-codex-hooks.sh` passed: 15 passed, 0 failed.

The authenticated paid runtime command `bash tests/hooks/test-codex-e2e-cli.sh` was not run in this pass.
