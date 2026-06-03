---
title: "Worktree-in-URL routing (?wt=) + selector navigation"
status: not-started
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
