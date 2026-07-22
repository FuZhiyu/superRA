---
title: "Worktree-Scoped Relative Image Assets"
status: not-started
depends_on:  []
---

## Objective

Preserve the active canonical worktree selector when live-dashboard Markdown rendering rewrites relative image sources to /files/ URLs. Add regression coverage proving the rendered URL retains the exact collision-safe selector and that fetching it returns bytes from the selected worktree rather than the launch worktree. Preserve launch-worktree rendering without a selector, standalone exports, absolute/root-relative image sources, and relative-image query strings.

## Planner Guidance

[Issue #47](https://github.com/FuZhiyu/superRA/issues/47) identifies the bypass in [dashboard.js:295](../../../../../skills/task-tree/scripts/templates/dashboard.js#L295): `renderMarkdown()` constructs `/files/` directly instead of routing it through `wtUrl()`. Existing node-backed `renderMarkdown()` tests in [test_dashboard.py:2599](../../../../../skills/task-tree/scripts/test_dashboard.py#L2599) exercise the rewrite; the two-worktree fixture in [test_dashboard.py:619](../../../../../skills/task-tree/scripts/test_dashboard.py#L619) exercises server-side `WorktreeState` selection. Audit other client-generated `/files/` URLs in the same pass.

## Results
