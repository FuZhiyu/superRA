---
title: "Task-Hook Runtime E2E Coverage"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Add optional runtime end-to-end tests proving that real Codex and Claude Code CLI sessions trigger the task-tree PostToolUse task hook when an agent edits task files. Keep these tests outside default CI because they require authenticated CLIs and model/API budget.

## Planner Guidance

Use the existing optional CLI E2E scripts under tests/hooks as the durable home. Prefer structural JSONL/NDJSON event assertions and filesystem state checks over assertions on assistant prose.

## Results

