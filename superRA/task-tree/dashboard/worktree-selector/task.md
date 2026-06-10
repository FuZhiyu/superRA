---
title: "Worktree Selector"
status: implemented
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

## Review Notes

1. **MAJOR** — approved branch task with no `## Results` section at all, despite five approved children (discovery, server-routes, selector-ui, tests — each with its own Results). The task-file contract requires every task to carry `## Results` substantive enough for approval; add a parent rollup linking down to the children.
   → implemented: added a `## Results` rollup summarizing the final `?wt=` navigation model and repo-based port, with links down to each child ([task.md:19](task.md)).
2. **MAJOR** — the Objective describes the retired switching model as current: "Switching worktrees hot-swaps the in-memory task tree, restarts the filesystem watcher, and triggers a `full-reload` SSE event". That global-switch design (`POST /api/worktree/switch`) was removed by [multi-worktree-serving](../multi-worktree-serving/task.md) task 03 — switching is now client navigation to a `?wt=<wt_id>` URL with per-request resolution ([plan_dashboard.py:1220-1223](../../../../skills/task-tree/scripts/plan_dashboard.py#L1220)). Per the stale-content checklist (sibling objectives assuming a superseded approach), rewrite the switching sentence in place; the discovery, dropdown, and repo-based-port decisions remain accurate.
   → implemented: rewrote the switching sentence in §Objective to the `?wt=` client-navigation model with a supersession note, leaving discovery/dropdown/repo-port intact ([task.md:11](task.md)).
3. **MINOR** — `WorktreeInfo.is_current` and its `_get_current_worktree_path()` probe ([_worktree_discovery.py:59](../../../../skills/task-tree/scripts/_worktree_discovery.py#L59)) survive the switch retirement with no dashboard consumer (`/api/worktrees` no longer emits `is_current`), costing one `git rev-parse` subprocess per discovery for dead data. Drop the field or note the remaining consumer.
   → implemented (noted, not dropped): the discovery module still computes `is_current` and `test_worktree_selector.py:260` asserts it directly, so the field has a remaining consumer (the discovery layer + its tests); dropping it would cascade into discovery and its test files beyond this record-repair round. Recorded the dashboard-no-longer-consumes-it fact in the new `## Results` (discovery bullet) and flag the dead-data subprocess cost for a follow-up prune. No code change.
