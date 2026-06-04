---
title: "Worktree-in-URL routing (?wt=) + selector navigation"
status: revise
depends_on: 
  - 01-per-worktree-state

tags: []
created: 2026-06-03
---

## Objective

Put the active worktree in the **browser URL** as `?wt=<name>` and make the dashboard client honor it, so a URL is shareable/bookmarkable to a specific worktree and switching worktrees is a navigation — not a global server mutation that flips every tab. This is the change the user actually asked for; tasks 01/02 make the server able to serve it correctly.

**Deliverables:**

1. **On load:** read `?wt=<name>` from the URL alongside the existing `#/<task-path>` hash. Initialize the active worktree from `?wt=` (default = launch worktree when absent), and include `?wt=` on every server fetch the client makes (`/nav`, `/node/{path}`, `/dag`, `/export`, `/events`, comment APIs) so all panels render that worktree. The hash router (`parseHash`/`setActive`, [base.html:1788-1837](../../../../../skills/task-system/scripts/templates/base.html#L1788)) stays the single source of truth for the **task path** and is otherwise untouched.
2. **Selector becomes navigation.** `switchWorktree()` ([base.html:3153](../../../../../skills/task-system/scripts/templates/base.html#L3153)) sets `?wt=<name>` in the URL via `history.pushState` and re-renders panels against the new worktree — it no longer issues the global `POST /api/worktree/switch` + global SSE full-reload. Back/forward restores both the worktree and the task path. `populateWorktreeSelector` / `fetchWorktrees` ([base.html:3105-3151](../../../../../skills/task-system/scripts/templates/base.html#L3105)) set the selector to the URL's worktree. The selector option **value must be the basename id** (`?wt=` token), not the absolute `plan_root` path it currently uses ([base.html:3120](../../../../../skills/task-system/scripts/templates/base.html#L3120)), reusing task 01's basename→worktree map.
3. **`/api/worktrees` `current`/`is_current` become URL-derived, not server-global.** That route ([plan_dashboard.py:701](../../../../../skills/task-system/scripts/plan_dashboard.py#L701)) reports a server-global `current` and computes `is_current` against global `PLAN_ROOT`. Under per-request resolution "current" is the URL's worktree — update the route (or the client's use of it) so the selector's current-selection follows the URL, and remove or repurpose the now-meaningless server-global `current` so it cannot drift. This task owns closing that field.
4. **`PROJECT_ROOT` is per-worktree.** The vscode-link base ([base.html:3147](../../../../../skills/task-system/scripts/templates/base.html#L3147)) must reflect the URL's worktree, not a server-global, so the worktree-aware VS Code links stay correct under the new model. `/events` must subscribe with the URL's `?wt=` so live-reload (task 02) targets the right worktree.
5. **Retire the global switch.** Remove `POST /api/worktree/switch`'s global-mutation role (and its all-clients `full-reload`) unless a non-URL consumer still needs it; if removed, delete the dead server code and its client caller. Document the new "switch = navigate" model wherever the old switch flow was described.
6. **Standalone export unaffected.** In `window.STANDALONE` / `file://` mode the selector stays hidden and `?wt=` is ignored — the exported snapshot renders the single worktree it was built with. The fetch shim ([base.html:1289-1314](../../../../../skills/task-system/scripts/templates/base.html#L1289)) must not regress; do not key standalone fragments on `?wt=`.

**Scope boundary.** This task owns client URL/selector/`PROJECT_ROOT` behavior and the retirement of the global switch. It depends on task 01 (the server must honor `?wt=` on read routes) and composes with task 02 (the `/events` subscription it issues carries `?wt=`), but it does not itself implement SSE scoping.

### Conventions

Work in this project worktree only: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/better-handoff`. Keep edits and commits on this worktree's branch. All client edits are in the single template [base.html](../../../../../skills/task-system/scripts/templates/base.html).

## Validation

- **Real user path (required).** Serve the dashboard over a repo with ≥2 worktrees; in two tabs open `/?wt=<A>` and `/?wt=<B>` and confirm each renders its own tree and neither changes when the other loads or when the other's files change. Inspect the actual rendered panels and the `?wt=` in the address bar, not functions in isolation.
- Switching via the selector updates the address bar to the new `?wt=` and re-renders without a global reload; back/forward restores both worktree and task path.
- A bookmarked `/?wt=<name>#/<task>` reopens to the same worktree + task.
- The per-task "Open in VS Code" href resolves against the URL's worktree.
- Standalone export: selector hidden, `?wt=` ignored, snapshot still correct; dashboard test suite passes (incl. the inline-script parse check).

## Planner Guidance

- The existing worktree-aware VS Code work (`worktree-vscode-link`, approved) already syncs `PROJECT_ROOT` from `/api/worktrees`' `current`; here `PROJECT_ROOT` instead follows the URL's `?wt=`. Reconcile the two so the link base has one source of truth (the resolved worktree), and keep the standalone guard that leaves the baked root untouched when `current`/`?wt=` is empty.
- `?wt=` lives in `location.search`; the task path stays in `location.hash`. Read both in `initRouter` ([base.html:2329](../../../../../skills/task-system/scripts/templates/base.html#L2329)); write both together in `pushState`/`replaceState` so history entries carry the pair.
- Confirm whether anything besides the selector calls `POST /api/worktree/switch` before deleting it.

## Results

The active worktree is now a dimension of the browser URL (`?wt=<id>` in `location.search`), orthogonal to the task path (`#/<task>` in `location.hash`). Switching worktrees is a client navigation, not a server mutation: it touches only the navigating tab, leaving other tabs on other worktrees untouched. The `POST /api/worktree/switch` global-mutation route is gone.

### How it works

The server renders the same page for any worktree, bound at render time to the worktree the request resolved via task 01's `resolve_worktree`. The index route ([plan_dashboard.py](../../../../../skills/task-system/scripts/plan_dashboard.py)) now passes `wt_id` to the template (empty for the launch worktree, so its URL stays a clean `/`). That id is baked into the `sse-connect` attribute (`/events?wt=<id>`) and read client-side from `location.search` into `ACTIVE_WT`. A single `wtUrl(url)` helper appends `?wt=<ACTIVE_WT>` (merging with any existing query string) and is applied at every server fetch — `/nav`, `/nav/{path}`, `/node/{path}`, `/task/{path}`, `/dag`, `/kanban`, `/export`, `/api/worktrees`, and all comment APIs — so every panel renders the URL's worktree. In standalone (`file://`) mode `ACTIVE_WT` stays `''` and `wtUrl` returns the URL untouched, so the exact-string fetch shim still matches and the snapshot renders its single baked worktree.

`PROJECT_ROOT` (the VS Code link base) follows the URL's worktree: the server bakes the resolved worktree's project root on initial load, and `fetchWorktrees` re-points it to the active worktree's `path` after a client-side switch. The old "sync from `current`" coupling is replaced — there is no server-global current worktree anymore.

**Selector = navigation.** The option value is the worktree's `?wt=` token (`wt_id`; `''` for the launch worktree). `switchWorktree(token)` `pushState`s the new `?wt=` (keeping the current task hash) and calls `applyWorktree`, which updates `ACTIVE_WT`, reconnects the SSE stream to the new worktree (`reconnectSse`), refreshes `PROJECT_ROOT` + the selector, rebuilds the sidebar from the new `/nav`, and re-renders the panels for the same task path (falling back to the nearest surviving ancestor when that task does not exist in the new worktree). Back/forward across a `?wt=` boundary is handled in `popstate`: when the URL's worktree differs from `ACTIVE_WT` it routes through `applyWorktree`, otherwise it is a plain task-path step. History `pushState`/`replaceState` use relative `#/...` URLs that preserve `location.search`, so task navigation never drops the worktree, and the state object carries `{path, wt}`.

**SSE reconnection** (`reconnectSse`) closes the htmx-cached `EventSource` on `.main-content`, rewrites `sse-connect` to the new `?wt=`, and re-processes the element so the htmx sse extension opens a fresh source and re-binds every `sse-swap` listener (summary bar, full-reload sentinel, and — after the sidebar rebuild re-runs `htmx.process` — the nav rows). This makes an in-place worktree switch live-reloadable against the switched-to worktree.

**`/api/worktrees`** now returns per-entry `wt_id` (task 01's basename map with longest-unique-suffix disambiguation) and a top-level `launch_wt_id`; the stale server-global `current`/`is_current` fields are removed (under per-request resolution they would only drift). The client marks the current selection from the URL, defaulting to `launch_wt_id`.

**Launch-id canonicalization** (advisory 2 from task 01's review). `_worktree_id_for_plan_root` now returns the same key `_discovered_worktree_map()` uses for the launch worktree's plan root — so on a basename collision the launch worktree caches under its disambiguated suffix key (e.g. `a/feature`), not redundantly under both the bare basename and the suffix. Its cache key, `?wt=` selector token, and the resolver's default short-circuit all agree, so the selector's current-selection round-trips through the resolver. Non-colliding and no-git cases fall back to the bare basename unchanged.

### Verification

- **Dashboard test suite (full):** 434 passed (`uv run --project skills/task-system --with pytest --with httpx python -m pytest skills/task-system/scripts -q`), including the standalone-generation and fragment-parity tests and `test_worktree_selector.py`'s `/api/worktrees` contract tests updated to the new `launch_wt_id` / per-entry `wt_id` shape.
- **Real user path (browser-driven, headless Chromium, 27 checks across two scripts, zero JS errors):** served the dashboard over this repo (≥6 worktrees with task trees) on one port. Two tabs at `/` (launch worktree `better-handoff`) and `/?wt=task-hook-agent-feedback` each rendered their own tree and stayed isolated; a node present only in `better-handoff` (`task-system/dashboard/multi-worktree-serving`) was present in the launch tab and absent in the other (server-side: same path returns 200 under default and 404 under `?wt=task-hook-agent-feedback`). Address bar carried the right `?wt=`; `PROJECT_ROOT` and the per-task "Open in VS Code" href resolved against the URL's worktree. Selector navigation switched the tab in place (address bar + tree + `PROJECT_ROOT` updated, no global reload), back restored the launch worktree and tree, forward returned to the other worktree, and a deep-link `/?wt=X#/<task>` bookmark reopened to the same worktree + task.
- **Live-reload after in-place switch + cross-worktree SSE isolation:** after switching a tab to worktree B via the selector, editing B's `task.md` live-updated that tab (confirming `reconnectSse` re-binds the stream); the same edit did not touch a tab on the launch worktree, and a launch-worktree edit updated only the launch tab — isolation holds in both directions.
- **Canonicalization:** unit-checked `_worktree_id_for_plan_root` against a simulated basename collision (launch resolves to the disambiguated map key, not the bare basename), a non-colliding worktree (bare basename), and an unknown plan root (bare-basename fallback).

### Deviation from Planner Guidance

The guidance suggested reading both `?wt=` and the hash in `initRouter`. `?wt=` is instead read once at load into `ACTIVE_WT` (the server already binds the page to that worktree and bakes `sse-connect`/`project_root`), and `initRouter` keeps owning only the task path. This keeps the hash router as the single source of truth for the task path while the worktree dimension is established server-side at render and re-applied client-side only on an actual switch (`applyWorktree`) — satisfying the objective's "read `?wt=` on load, default to launch, include it on every fetch" without overloading the hash router.

## Review Notes

1. **MAJOR — the required test suite is red: 9 errors in `test_worktree_selector.py` from this task's own deletions.** The dispatch and `## Validation` require the dashboard suite to pass; running it from live source (`python -m pytest skills/task-system/scripts -q`) gives `431 passed, 9 errors`. Both erroring classes test behavior this task deliberately retired but whose tests were not updated:
   - `TestWorktreeRoutes` and `TestSSEBroadcastOnSwitch` setup fixtures reference the removed global at [test_worktree_selector.py:608](../../../../../skills/task-system/scripts/test_worktree_selector.py#L608), [:615](../../../../../skills/task-system/scripts/test_worktree_selector.py#L615), [:625](../../../../../skills/task-system/scripts/test_worktree_selector.py#L625), [:824](../../../../../skills/task-system/scripts/test_worktree_selector.py#L824), [:831](../../../../../skills/task-system/scripts/test_worktree_selector.py#L831), [:838](../../../../../skills/task-system/scripts/test_worktree_selector.py#L838) — `plan_dashboard._current_worktree_path`, deleted at [plan_dashboard.py:71-75](../../../../../skills/task-system/scripts/plan_dashboard.py#L71). The fixture raises `AttributeError` at collection, erroring every test in the class.
   - `test_get_worktrees_returns_json` / `test_get_worktrees_fields` / `test_get_worktrees_fallback_no_git` ([:636](../../../../../skills/task-system/scripts/test_worktree_selector.py#L636), [:662](../../../../../skills/task-system/scripts/test_worktree_selector.py#L662), [:686](../../../../../skills/task-system/scripts/test_worktree_selector.py#L686)) assert the `current` / `is_current` response fields this task removed (Deliverable 3, [plan_dashboard.py:1019](../../../../../skills/task-system/scripts/plan_dashboard.py#L1019)). They must be rewritten to assert the new `launch_wt_id` / per-entry `wt_id` contract.
   - `test_switch_*` and `test_switch_broadcasts_full_reload` ([:695](../../../../../skills/task-system/scripts/test_worktree_selector.py#L695)–[:881](../../../../../skills/task-system/scripts/test_worktree_selector.py#L881)) exercise `POST /api/worktree/switch`, deleted at [plan_dashboard.py:1067](../../../../../skills/task-system/scripts/plan_dashboard.py#L1067) (Deliverable 5). They test retired behavior and should be removed (or replaced with the navigation model, though new `?wt=` integration coverage is task 04's scope).

   Fix: update/remove these tests so the full `skills/task-system/scripts` suite is green. Adding brand-new cross-worktree integration tests stays task 04's job, but the suite cannot be left red by this task's own removals. (The `_get_current_worktree_path` function in `_worktree_discovery.py` is unrelated and untouched — do not confuse it with the removed global.)
   → implemented: removed the `_current_worktree_path` save/set/restore lines from `TestWorktreeRoutes.setup_app` ([test_worktree_selector.py:605](../../../../../skills/task-system/scripts/test_worktree_selector.py#L605)); rewrote the three `/api/worktrees` tests to assert the new contract — top-level `launch_wt_id` (no `current`), per-entry `wt_id` (no `is_current`), and a fallback entry whose `wt_id` equals `launch_wt_id` ([test_worktree_selector.py:642](../../../../../skills/task-system/scripts/test_worktree_selector.py#L642)); deleted the 5 `test_switch_*` tests and the whole `TestSSEBroadcastOnSwitch` class (retired `POST /api/worktree/switch` + its full-reload broadcast). Full suite now green: 434 passed, 0 errors. No new `?wt=` integration coverage added (task 04's scope). `_worktree_discovery._get_current_worktree_path` left untouched.

2. **MINOR — `## Results` "237 passed" reflects only `test_task_system.py`, not the suite the task requires.** `## Validation` and the dispatch call for the dashboard suite; the verification ran a single file and so missed finding 1. Update the verification claim to the full `skills/task-system/scripts` run once green.
   → implemented: corrected the `## Results` verification line to the full-suite run — 434 passed via `python -m pytest skills/task-system/scripts -q` from live source.
