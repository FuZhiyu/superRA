---
title: "Task-Hook Runtime E2E Coverage"
status: approved
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Add optional runtime end-to-end tests proving that real Codex and Claude Code CLI sessions trigger the task-tree PostToolUse task hook when an agent edits task files. Keep these tests outside default CI because they require authenticated CLIs and model/API budget.

## Planner Guidance

Use the existing optional CLI E2E scripts under tests/hooks as the durable home. Prefer structural JSONL/NDJSON event assertions and filesystem state checks over assertions on assistant prose.

## Results

Added optional runtime E2E coverage for the task-tree `PostToolUse` task hook in both supported CLI harnesses. The Codex script now installs hooks through a temporary Codex profile, preserves failed fixtures with `KEEP_TMPROOT=1`, runs a real `codex exec` edit of a temporary `superRA/01-child/task.md`, and verifies Codex JSONL `file_change` evidence plus filesystem status propagation. The Claude Code script now adds S7, which runs a real `Read`/`Edit` session against a temporary task tree, validates a `PostToolUse` hook response, canonicalizes temp paths before comparing task-file edits, and verifies root status propagation.

Project Doc Audit: touched files are under `tests/hooks/` and this `superRA/` task subtree. The repo-root [CLAUDE.md](../../../../../CLAUDE.md) / [AGENTS.md](../../../../../AGENTS.md) contributor rules were applied; no nearer `CLAUDE.md`, `AGENTS.md`, or `README.md` exists under `tests/` or this task subtree, and the root [README.md](../../../../../README.md) has no stale user-facing claim about these optional authenticated E2E scripts.

Verification on the synced integration branch:

- `bash -n tests/hooks/test-codex-e2e-cli.sh` passed.
- `bash -n tests/hooks/test-e2e-cli.sh` passed.
- `bash tests/hooks/test-codex-hooks.sh` passed: 15 passed, 0 failed.
- `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts` passed: 688 passed, 2 skipped.
- `bash tests/hooks/test-codex-e2e-cli.sh` passed with a real authenticated Codex session.
- `bash tests/hooks/test-e2e-cli.sh` passed with a real authenticated Claude Code session: 6 passed, 0 failed in default mode.

`./superRA/superra task check` reports only inherited base warnings outside this task-hook E2E scope: `task-tree/test-suite` depends on archived `auto-rebuild`, and `task-tree/dashboard/github-artifact-action` still carries an old temporary `## Sync Impact`.

**Final diff self-check:** `git diff 58e4ac0da790cfe526c86d14d46d5b16d75197cf..HEAD`; surviving change classes are the approved optional runtime E2E scripts, the new task-hook E2E task records, and the integration-review note/fix trail. Suspicious hunks: hook runtime script changes are justified by the task objective to exercise real `codex exec` and Claude Code sessions; task-file additions/statuses are justified by the approved task tree; the root `superRA/task.md` hunk is EOF-only normalization from sync propagation, and restoring the base's extra blank line fails `git diff --check`. No unrelated hunks remain.

## Review Notes

1. **MAJOR — [task.md:17-19](task.md#L17-L19) has no integration final-diff self-check trail.** The integration-stage checklist requires a fresh `Final diff self-check` in the assigned task's `## Results` naming the governing command/range, the surviving change classes, and hunk-level justification for suspicious hunks. The assigned parent `## Results` is empty, and the surviving range includes task files plus two hook E2E scripts, so the reviewer has no task-local trail to compare against `git diff 58e4ac0da790cfe526c86d14d46d5b16d75197cf..HEAD`. Fill this parent result with the final-diff self-check, Project Doc Audit outcome, and verification evidence, including justification or pruning for the root-task whitespace-only hunk.
   → implemented: filled the parent `## Results` with the final-diff self-check, Project Doc Audit outcome, verification evidence, and the root-task EOF-normalization justification.

2. **MAJOR — [test-codex-e2e-cli.sh:122-151](../../../../../tests/hooks/test-codex-e2e-cli.sh#L122-L151) can fail without failing the script.** The script still runs with `set -uo pipefail` rather than `set -e`, and after the first Python assertion exits nonzero, execution continues into the task-hook scenario at [test-codex-e2e-cli.sh:153-255](../../../../../tests/hooks/test-codex-e2e-cli.sh#L153-L255). If the second scenario passes, the script exits with the last Python command's status and can report an overall green run while silently missing the UserPromptSubmit hook evidence. Wrap the first assertion in an explicit `if ! python3 ...; then exit 1; fi` or otherwise make each assertion contribute to the final exit status.
   → implemented: wrapped both Codex Python assertion blocks so either failed structural check exits the script immediately.
