---
title: "Semantic task move CLI"
status: not-started
depends_on:  []
tags: []
created: 2026-06-09
---

## Objective

Make task path changes go through a first-class task-system CLI operation instead of raw `mv` / `git mv`. Add or document a canonical task move path that preserves task-tree invariants and is the place to preserve relative markdown hyperlinks using pre-move context. Keep `rename` as a same-parent alias or wrapper if retained for compatibility, but teach agents that intentional task path changes use the CLI move/rename surface, not plain filesystem moves; the PostToolUse hook remains a guardrail, not the canonical move mechanism.

Outputs: task-system CLI/docs updates, especially `SKILL.md` and `references/commands.md`, with clear instruction not to use raw `mv` / `git mv` for intentional task moves; focused tests for the move/rename command surface and link-preservation or validation behavior implemented.

## Results
