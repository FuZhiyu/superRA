---
title: "Per-worktree state cache + request resolution"
status: not-started
depends_on:  []
tags: []
created: 2026-06-03
---

## Objective

Replace the dashboard's single global root with a **per-worktree state cache** and a **per-request resolver**, then thread that resolver through every read route so each request renders the worktree it names. This is the foundation the SSE (02) and URL-routing (03) tasks build on; deliver it so the server behaves identically to today when no worktree is named, and correctly serves any other discovered worktree when one is.

**Deliverables:**

1. A `WorktreeState` dataclass holding the per-worktree render state currently spread across globals: `root_task`, `task_index`, `project_root`, `plan_root`. Replace direct use of the module singletons `_root_task` / `_task_index` / `_project_root` / `PLAN_ROOT` / `_current_worktree_path` ([plan_dashboard.py:65-82](../../../../../skills/task-system/scripts/plan_dashboard.py#L65)) with lookups into a module-level `_worktree_cache: dict[str, WorktreeState]` keyed by the resolved worktree id (the worktree directory basename per the root task's design decision 2).
2. A `resolve_worktree(request) -> WorktreeState` helper that reads the `?wt=<name>` query param, maps it to a discovered worktree via `_worktree_discovery.discover_worktrees()` ([_worktree_discovery.py](../../../../../skills/task-system/scripts/_worktree_discovery.py)), lazily builds and caches its `WorktreeState` on first use, and **falls back to the launch worktree when `?wt=` is absent or unknown**. Return a clear 404 only when `?wt=` names a value that is neither the launch worktree nor any discovered worktree.
3. Every read handler resolves the worktree from the request and renders from the resolved `WorktreeState` instead of the globals: `/`, `/tree`, `/nav`, `/nav/{path}`, `/node/{path}`, `/task/{path}`, `/dag`, `/kanban`, `/export`, `/files/{path}`, and the comment routes `/api/task/{path}/*` + `/api/comments/summary`. The render helpers ([plan_dashboard.py:329-395](../../../../../skills/task-system/scripts/plan_dashboard.py#L329)) already take explicit `task` / `project_root` args — pass the resolved values; do not read globals inside them.
4. Cache rebuild/invalidation hook for the watcher: expose a function that, given a worktree id, rebuilds or evicts that worktree's `WorktreeState` **and renders the broadcast fragments (`summary-updated`, `task:<path>`) from that `WorktreeState`** — i.e. the rebuild-and-render-fragment path operates on a resolved `WorktreeState`, not module globals. This is the part task 02 needs: task 02 owns the per-worktree watcher *lifecycle* and *delivery*, but it can only "keep the watcher body unchanged and just parameterize the root" if this task already moves `rebuild_tree` / `rebuild_task` / the summary+nav fragment rendering ([plan_dashboard.py:204-286](../../../../../skills/task-system/scripts/plan_dashboard.py#L204) call sites) onto `WorktreeState`. In this task, wire the hook to the existing single watcher so behavior is preserved; task 02 generalizes the watcher to per-worktree.
5. Preserve the launch path: the CLI `serve --root <path>` ([cli.py](../../../../../skills/task-system/scripts/cli.py)) and `lifespan()` startup ([plan_dashboard.py:406](../../../../../skills/task-system/scripts/plan_dashboard.py#L406)) seed the cache with the launch worktree as the default. `/export` standalone generation keeps rendering exactly one worktree.

**Scope boundary.** This task owns the state model and request resolution for **read** routes. It does NOT change SSE scoping or the watcher lifecycle (task 02) and does NOT add `?wt=` to the client URL or selector (task 03) — but it MUST make the server *accept and honor* a `?wt=` query param so 02 and 03 have a server to build against. The existing `POST /api/worktree/switch` may keep working against the launch/default worktree for now; its retirement is finalized in task 03.

### Conventions

Work in this project worktree only: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/better-handoff`. Keep edits and commits on this worktree's branch.

## Validation

- Unit tests (extend [test_dashboard.py](../../../../../skills/task-system/scripts/test_dashboard.py)): with two task trees built in `tmp_path`, requests carrying `?wt=A` vs `?wt=B` to `/node/{path}`, `/nav`, and `/api/comments/summary` return content from the matching tree; a request with no `?wt=` returns the launch tree; an unknown `?wt=` returns 404.
- A `WorktreeState` is built at most once per worktree per file-version (cache hit on the second request; rebuilt after an invalidation call).
- The full suite still passes — no regression in single-worktree behavior or `/export`.

## Planner Guidance

- `_set_module_state()` + `/export` ([plan_dashboard.py:894](../../../../../skills/task-system/scripts/plan_dashboard.py#L894), `:1021`) already snapshot/restore module state per render — read it first; the cache generalizes that pattern. Prefer making the cache authoritative and having `/export` resolve through it.
- Keep a thin compatibility shim if it reduces diff: the globals can become properties/views over `_worktree_cache[default]` during the transition, but the end state reads from the resolved `WorktreeState`, not globals.
- Worktree-id mapping: `discover_worktrees()` returns `WorktreeInfo.path`; derive the basename id there and resolve `?wt=` against it. Centralize the basename→worktree map so 02/03 reuse it.
