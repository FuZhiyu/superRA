---
title: "Worktree Selector"
status: approved
depends_on: []
tags: []
created: 2026-05-26
---

## Objective

Add worktree discovery and switching to the dashboard. The server discovers all git worktrees of the current repo, identifies which have valid task-root directories, and presents them in a header dropdown. Switching worktrees is client navigation to a `?wt=<wt_id>` URL with per-request worktree resolution — selecting an entry navigates the browser to that worktree's view without a server-wide swap, so two tabs can view different worktrees on one shared port (the original global hot-swap design, `POST /api/worktree/switch`, was superseded by [multi-worktree-serving](../multi-worktree-serving/task.md) task 03). Port derivation changes from plan-root-based to repo-based (hash the git common dir) so all worktrees of the same repo share one dashboard port.

**Design decisions:**
- Repo-based port: `_default_port()` hashes `git rev-parse --git-common-dir` instead of `PLAN_ROOT`. Launching from any worktree of the same repo reaches the same port.
- All worktrees with `.plan/` are shown, including agent worktrees. The `is_agent` flag is available for UI labeling but does not filter by default. Prunable worktrees are excluded.
- Worktrees are ordered by last activity time (most recent first). Activity is measured by the last commit time on the worktree's branch.
- Graceful degradation: if not in a git repo, the dashboard works as before with no dropdown.

## Results

Worktree discovery and selection shipped across the children below; the final switching model is **client navigation to `?wt=<wt_id>`** with per-request resolution (the global hot-swap endpoint was retired by [multi-worktree-serving](../multi-worktree-serving/task.md) task 03 — see that subtree for the per-request server). Port derivation is repo-based (hash of the git common dir), so every worktree of a repo shares one dashboard server/port, and the dashboard degrades to no-dropdown outside a git repo.

- **[discovery](discovery/task.md)** — `discover_worktrees()` enumerates the repo's worktrees, identifies those with a valid task root, orders them by last branch-commit activity, and exposes the `is_agent`/`is_locked` labels. (The discovery layer still computes an `is_current` flag with its own test coverage; the dashboard no longer consumes it — see Review Note 3.)
- **[server-routes](server-routes/task.md)** — `/api/worktrees` lists the discovered worktrees (now with `launch_wt_id` + per-entry `wt_id`/`plan_root`), feeding the selector and the per-`?wt=` resolution.
- **[selector-ui](selector-ui/task.md)** — the header dropdown that navigates the browser to the chosen worktree's `?wt=` view.
- **[tests](tests/task.md)** — discovery/route/selector coverage, including the retirement of the old `is_current`/`switch` surface from `/api/worktrees`.

