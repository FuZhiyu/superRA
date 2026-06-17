---
title: "Claude Code Task-Hook E2E"
status: approved
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Extend the optional Claude Code CLI end-to-end hook suite so a real Claude Code session edits a temporary task tree and the test verifies that the PostToolUse task-hook ran for that task edit. The test must assert hook evidence from the CLI event stream and resulting task-tree state, not assistant prose.

## Planner Guidance

Use tests/hooks/test-e2e-cli.sh conventions for isolated temp dirs, session cleanup, and structural hook_response assertions. Add a narrow scenario for task-hook PostToolUse coverage without broadening default CI.

## Results

Implemented optional Claude Code runtime task-hook coverage in [test-e2e-cli.sh:249-277](../../../../../../tests/hooks/test-e2e-cli.sh#L249-L277), [test-e2e-cli.sh:423-505](../../../../../../tests/hooks/test-e2e-cli.sh#L423-L505), and [test-e2e-cli.sh:687-712](../../../../../../tests/hooks/test-e2e-cli.sh#L687-L712). The S7 scenario builds an isolated temporary `superRA/` tree, runs Claude Code with `Read,Edit` and `acceptEdits`, and asserts the NDJSON event stream contains a PostToolUse hook response. The propagation assertion now canonicalizes temp paths before collecting every mutating `Edit`/`Write` task-file target under the temp tree and requires the unique path set to be exactly `superRA/01-child/task.md`, so a direct root edit or extra task-file edit fails before root status is used as propagation evidence. The default one-click suite now skips the brittle S4/S5 workflow-skill gate probes unless `CLAUDE_E2E_FULL=1`, matching the script's mode banner.

Verification run in this implementation pass:

- `bash -n tests/hooks/test-e2e-cli.sh` passed.
- `bash tests/hooks/test-codex-hooks.sh` passed: 15 passed, 0 failed.
- `bash tests/hooks/test-e2e-cli.sh` passed in default mode with a real authenticated Claude Code session: S1, S2 setup/check, S3, S6, and S7 passed; S4/S5 were skipped because `CLAUDE_E2E_FULL` was not set.
