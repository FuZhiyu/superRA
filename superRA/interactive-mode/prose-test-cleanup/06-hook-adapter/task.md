---
title: "Replace Hook-Adapter Prose Oracles"
status: not-started
depends_on:  []
---

## Objective

Replace Codex hook tests that assert exact Stop reasons, invalid-status wording, or phrase-based plan detection with adapter JSON shape, block decisions, structured proposed-plan/permission-mode signals, and structured status identities. Success: hook behavior remains covered without prose heuristics or diagnostic wording oracles.

## Planner Guidance

Own tests/hooks/test-codex-hooks.sh and codex-plan-stop adapter surfaces. Coordinate any required structured task-hook contract with 03-task-tree-core; do not duplicate core changes.

## Results
