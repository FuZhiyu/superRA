---
title: "Codex Exec Task-Hook E2E"
status: approved
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Extend the optional Codex CLI end-to-end test so a real codex exec session edits a temporary task tree and the test verifies that the PostToolUse task-hook ran for that task edit. The test must assert hook evidence from Codex JSONL and resulting task-tree state, not assistant prose.

## Planner Guidance

Start from tests/hooks/test-codex-e2e-cli.sh. Build a minimal superRA/ tree in TMPROOT, install project-local hooks, prompt Codex to make a deterministic task edit, and assert a PostToolUse task-hook response plus status propagation or hook feedback evidence.

## Results

Implemented optional Codex runtime task-hook coverage in [test-codex-e2e-cli.sh:33-74](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L33-L74), [test-codex-e2e-cli.sh:89-95](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L89-L95), and [test-codex-e2e-cli.sh:136-236](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L136-L236). The script now builds a temporary `superRA/` tree, installs PostToolUse task-hook commands with Codex empty-JSON mode, runs `codex exec` with current noninteractive bypass flags, asks it to edit `superRA/01-child/task.md`, and asserts parsed JSONL hook evidence plus task-tree state. The propagation assertion now first requires the unique mutating task-file path set to be exactly `superRA/01-child/task.md`, so a direct root edit or extra task-file edit fails before root status is used as propagation evidence.

Verification run in this implementation pass:

- `bash -n tests/hooks/test-codex-e2e-cli.sh` passed.
- `bash tests/hooks/test-codex-hooks.sh` passed: 15 passed, 0 failed.
- `codex exec --json --ephemeral --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox --dangerously-bypass-hook-trust --help` passed, verifying the revised noninteractive flags get through CLI parsing without starting a paid session.

The authenticated paid runtime command `bash tests/hooks/test-codex-e2e-cli.sh` was not run in this pass.
