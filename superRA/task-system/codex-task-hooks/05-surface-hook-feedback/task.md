---
title: "Surface Hook Feedback to Agents"
status: not-started
depends_on: 
  - 04-docs-tests-and-compat

tags: []
created: 2026-06-03
---

## Objective

Fix the task-system PostToolUse hook so validation warnings and non-fatal reconcile failures are injected back into the agent context for both Claude Code and Codex while preserving the hook as a non-blocking passive reconciler. Invalid task statuses must become model-visible immediately after a task.md edit or Codex apply_patch edit, without relying on stderr visibility. The implementation must keep exit code 0 for passive reconcile behavior, emit harness-compatible JSON on stdout only when there is feedback to inject, and keep silent fast paths silent. Update the active task-hook internals documentation and focused tests for Claude Edit/Write and Codex apply_patch/manifest-wrapper behavior. Validate that invalid enum edits produce additionalContext/hookSpecificOutput feedback, that dashboard rebuild failures no longer hide the warning from the agent, and that valid edits still rebuild/propagate normally.

## Results

