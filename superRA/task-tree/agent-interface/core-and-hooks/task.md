---
title: "Core Library + Hooks"
status: approved
depends_on: []
tags: []
created: 2026-05-24
---

## Objective

Enhance _task_io.py with validation functions and topological sort. Build PostToolUse hooks for automatic validation and dashboard rebuild on task.md edits.

## Results

[task-io-enhancements](task-io-enhancements/task.md) added validation (`validate_frontmatter`, `validate_dependencies`, `detect_cycles`, tree-wide `validate_plan`) and dependency-aware topological sibling ordering to `_task_io.py`. [validation-hooks](validation-hooks/task.md) built the PostToolUse hook (`task_hook.py` + `hooks/hooks.json` entry) that runs that validation automatically on `task.md` edits, never blocking (always exit 0).

## Review Notes

> 1. [MINOR] `## Results` is empty on this approved branch — no rollup of the two children's outcomes. Add a one-to-two-line summary linking the children.
>    → implemented: added a two-line rollup linking both children ([core-and-hooks/task.md](task.md))
