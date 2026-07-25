---
title: "Delete Low-Value Wording Assertions"
status: not-started
depends_on:  []
---

## Objective

Delete exact diagnostic, warning, UI-label, heading-count, and remediation-copy assertions across the audited test surfaces. Keep an existing behavioral assertion when it already exposes a cheap important outcome such as exit status, unchanged files, JSON shape, event order, or secret absence. Do not modify production code or add helper APIs. Success: the test diff is net-negative, no new execution cost is introduced, and the remaining assertions protect stable behavior rather than wording.

## Planner Guidance

Use the completed audit as navigation across harness contract/diagnostics, task-tree CLI/dashboard/comments, worktree-data-sync, hook adapter, Zotero CLI, and report-in-markdown. Replacements are allowed only when they reuse an existing result/state in a few local assertions; otherwise delete. Preserve the branch-specific interactive transcript/seat behavioral checks already present before this task.

## Results
