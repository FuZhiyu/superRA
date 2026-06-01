---
title: "Worktree Selector"
status: approved
depends_on: []
tags: []
created: 2026-05-26
---

## Objective

Add worktree discovery and switching to the dashboard. The server discovers all git worktrees of the current repo, identifies which have valid `.plan/` directories, and presents them in a header dropdown. Switching worktrees hot-swaps the in-memory task tree, restarts the filesystem watcher, and triggers a `full-reload` SSE event so the browser updates. Port derivation changes from plan-root-based to repo-based (hash the git common dir) so all worktrees of the same repo share one dashboard port.

**Design decisions:**
- Repo-based port: `_default_port()` hashes `git rev-parse --git-common-dir` instead of `PLAN_ROOT`. Launching from any worktree of the same repo reaches the same port.
- All worktrees with `.plan/` are shown, including agent worktrees. The `is_agent` flag is available for UI labeling but does not filter by default. Prunable worktrees are excluded.
- Worktrees are ordered by last activity time (most recent first). Activity is measured by the last commit time on the worktree's branch.
- Graceful degradation: if not in a git repo, the dashboard works as before with no dropdown.

**Relationship to `multi-plan-subtree`:** That task is about subtree focus/zoom within one `.plan/` directory. This task is about switching between different `.plan/` directories across git worktrees. They are complementary.
