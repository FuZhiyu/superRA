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

Implemented optional Codex runtime task-hook coverage in [test-codex-e2e-cli.sh:33-74](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L33-L74), [test-codex-e2e-cli.sh:89-95](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L89-L95), and [test-codex-e2e-cli.sh:136-236](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L136-L236). The script now builds a temporary `superRA/` tree, installs PostToolUse task-hook commands with Codex empty-JSON mode, runs `codex exec` with current noninteractive bypass flags, asks it to edit `superRA/01-child/task.md`, and asserts parsed JSONL hook evidence plus task-tree state. The propagation assertion now first requires the unique mutating task-file path set to be exactly `superRA/01-child/task.md`, so a direct root edit or extra task-file edit fails before root status is used as propagation evidence.

Verification run in this implementation pass:

- `bash -n tests/hooks/test-codex-e2e-cli.sh` passed.
- `bash tests/hooks/test-codex-hooks.sh` passed: 15 passed, 0 failed.
- `codex exec --json --ephemeral --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox --dangerously-bypass-hook-trust --help` passed, verifying the revised noninteractive flags get through CLI parsing without starting a paid session.

The authenticated paid runtime command `bash tests/hooks/test-codex-e2e-cli.sh` was not run in this pass.

## Review Notes

1. **MAJOR** [test-codex-e2e-cli.sh:94](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L94) and [test-codex-e2e-cli.sh:149](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L149) pass `--ask-for-approval never` to `codex exec`, but the current local `codex-cli 0.140.0` rejects that flag before any session starts. I reproduced this with `bash tests/hooks/test-codex-e2e-cli.sh`, which exits at argument parsing with `unexpected argument '--ask-for-approval'`; the optional runtime E2E therefore cannot currently exercise PostToolUse behavior. Update the script to the current noninteractive approval/sandbox flags and verify the script gets past CLI parsing before relying on it as E2E coverage.
   → implemented: replaced the rejected approval/sandbox arguments with `--dangerously-bypass-approvals-and-sandbox` on both `codex exec` invocations ([test-codex-e2e-cli.sh:89-95](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L89-L95), [test-codex-e2e-cli.sh:143-149](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L143-L149)).

2. **MAJOR** [test-codex-e2e-cli.sh:199-220](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L199-L220) does not prove the task hook propagated the root status from the child edit. It accepts any string containing `PostToolUse`, any event mentioning a child task edit, and a final root status of `approved`; it never rejects an `Edit`/`Write`/`apply_patch` that directly edits `superRA/task.md`. A model that edits both child and root would pass even if the task hook failed to propagate status. Tighten the assertion to identify a structural PostToolUse task-hook response for the task-edit turn and require that the only mutating task-file path is `superRA/01-child/task.md` before using root status as propagation evidence.
   → implemented: the JSONL assertion now extracts task-file paths from tool-shaped events, requires child edit/apply-patch evidence, and requires the unique mutating task-file path set to equal only `superRA/01-child/task.md` before checking propagated root status ([test-codex-e2e-cli.sh:201-236](../../../../../../tests/hooks/test-codex-e2e-cli.sh#L201-L236)).
