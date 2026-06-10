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

## Review Notes

1. **MAJOR** — approved branch task with no `## Results` section at all, despite five approved children (discovery, server-routes, selector-ui, tests — each with its own Results). The task-file contract requires every task to carry `## Results` substantive enough for approval; add a parent rollup linking down to the children.
2. **MAJOR** — the Objective describes the retired switching model as current: "Switching worktrees hot-swaps the in-memory task tree, restarts the filesystem watcher, and triggers a `full-reload` SSE event". That global-switch design (`POST /api/worktree/switch`) was removed by [multi-worktree-serving](../multi-worktree-serving/task.md) task 03 — switching is now client navigation to a `?wt=<wt_id>` URL with per-request resolution ([plan_dashboard.py:1220-1223](../../../../skills/task-tree/scripts/plan_dashboard.py#L1220)). Per the stale-content checklist (sibling objectives assuming a superseded approach), rewrite the switching sentence in place; the discovery, dropdown, and repo-based-port decisions remain accurate.
3. **MINOR** — `WorktreeInfo.is_current` and its `_get_current_worktree_path()` probe ([_worktree_discovery.py:59](../../../../skills/task-tree/scripts/_worktree_discovery.py#L59)) survive the switch retirement with no dashboard consumer (`/api/worktrees` no longer emits `is_current`), costing one `git rev-parse` subprocess per discovery for dead data. Drop the field or note the remaining consumer.
