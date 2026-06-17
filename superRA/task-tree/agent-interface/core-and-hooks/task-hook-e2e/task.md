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
