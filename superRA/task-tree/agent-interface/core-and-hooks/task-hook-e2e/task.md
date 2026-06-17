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

## Review Notes

1. **MAJOR — [task.md:17-19](task.md#L17-L19) has no integration final-diff self-check trail.** The integration-stage checklist requires a fresh `Final diff self-check` in the assigned task's `## Results` naming the governing command/range, the surviving change classes, and hunk-level justification for suspicious hunks. The assigned parent `## Results` is empty, and the surviving range includes task files plus two hook E2E scripts, so the reviewer has no task-local trail to compare against `git diff 58e4ac0da790cfe526c86d14d46d5b16d75197cf..HEAD`. Fill this parent result with the final-diff self-check, Project Doc Audit outcome, and verification evidence, including justification or pruning for the root-task whitespace-only hunk.

2. **MAJOR — [test-codex-e2e-cli.sh:122-151](../../../../../tests/hooks/test-codex-e2e-cli.sh#L122-L151) can fail without failing the script.** The script still runs with `set -uo pipefail` rather than `set -e`, and after the first Python assertion exits nonzero, execution continues into the task-hook scenario at [test-codex-e2e-cli.sh:153-255](../../../../../tests/hooks/test-codex-e2e-cli.sh#L153-L255). If the second scenario passes, the script exits with the last Python command's status and can report an overall green run while silently missing the UserPromptSubmit hook evidence. Wrap the first assertion in an explicit `if ! python3 ...; then exit 1; fi` or otherwise make each assertion contribute to the final exit status.
