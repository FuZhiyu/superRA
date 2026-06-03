---
title: "Worktree-aware VS Code task links in the dashboard"
status: approved
depends_on: [worktree-selector, vscode-line-anchors]
tags: []
created: 2026-06-02
---

## Objective

Make every `vscode://file/` link the dashboard emits resolve against the **currently active worktree**, and add a per-task "Open in VS Code" button that jumps to that task's `task.md`. All edits are in the one dashboard source template `skills/task-system/scripts/templates/base.html`.

**The bug.** The client constant `PROJECT_ROOT` is baked once at page render (`base.html:1318`, `var PROJECT_ROOT = {{ project_root | tojson }};`). The dashboard is a long-lived single page that can rebind to a different worktree through the worktree selector: `switchWorktree()` → `POST /api/worktree/switch` → the server updates `_project_root` and broadcasts an SSE `full-reload` → `onFullReload()` (`base.html:3032`) rebuilds the sidebar and re-runs `setActive`. `PROJECT_ROOT` is never refreshed during this, so after a switch every `vscode://file/` href points at the *original* worktree's absolute path. This produced a real failure: an editor link to `…/ElasticityBound-Local/superRA/03-bound-in-models/task.md`, a path under a worktree that is not where the file actually lives. Two emit sites share this stale constant: the per-task "Open in VS Code" button (`taskFileVscodeHref`, `base.html:1907`) and the pre-existing in-body file-link rewrite (`base.html:1413`). The fix must repair both.

**The fix — keep `PROJECT_ROOT` in sync with the active worktree.** The `GET /api/worktrees` response already carries `current` = the active worktree's project root (server field `_current_worktree_path`, which equals `PLAN_ROOT.resolve().parent` and is updated on every switch). Use it:

- In `fetchWorktrees()` (`base.html:3128`), when the response has a non-empty `current`, assign `PROJECT_ROOT = data.current` (alongside the existing `populateWorktreeSelector(data)` call).
- Make `fetchWorktrees()` return its fetch promise, and `await fetchWorktrees()` inside `onFullReload()` **before** `setActive(target)`, so the refreshed root is in place before the active card (and its VS Code button) re-render. This closes the race where the card could render with the pre-switch root.

**Standalone export must stay correct.** In standalone (`file://`) mode `window.fetch` is replaced by a shim whose `/api/worktrees` branch returns `{ current: '', worktrees: [] }` (`base.html:1299`). The non-empty `current` guard therefore leaves the baked `PROJECT_ROOT` untouched in standalone mode — the exported snapshot keeps the project root it was generated with. Do not regress this.

**The button (already in the working tree, uncommitted).** This session added `.vscode-btn` CSS, a `VSCODE_ICON` constant, the `taskFileVscodeHref(path)` helper, the header button markup, and its href wiring in `loadActiveNode`. That groundwork is part of this task's concern; commit it together with the worktree-sync fix as one coherent change. The helper builds `vscode://file/' + PROJECT_ROOT + '/superRA/' + (path ? path + '/' : '') + 'task.md'`, mirroring the `superRA/<path>/` prefix the in-body rewrite already uses — keep that single convention.

**Scope discipline.** Touch only `base.html`. Do not hand-edit `skills/task-system/build/lib/...` (untracked build output). No Codex-generated agent files are involved.

### Conventions

Work in this project worktree only: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/better-handoff`. Concurrent worktrees of this repo exist; keep all edits and the commit on this worktree's branch.

## Validation

- **Real user path (required).** Serve the dashboard (`uv run --project skills/task-system superra dashboard`), open it, and with the worktree selector switch to a *different* worktree. Confirm both (a) the active task's "Open in VS Code" button href and (b) an in-body relative file link now carry the **switched-to** worktree's absolute path, not the page-load worktree's. Inspect the actual rendered `href`, not just the function in isolation.
- The inline `<script>` in the generated page parses (no JS syntax error) and the dashboard test suite passes: `uv run --project skills/task-system --with pytest --with httpx python -m pytest skills/task-system/scripts/test_dashboard.py -q`.

## Results

Every `vscode://file/` link the dashboard emits now resolves against the **currently active worktree**, and a per-task "Open in VS Code" button jumps to that task's `task.md`. All edits are in the single dashboard source template [base.html](../../../../skills/task-system/scripts/templates/base.html).

### What changed

**Worktree-sync fix (the bug).** `PROJECT_ROOT` was baked once at render ([base.html:1318](../../../../skills/task-system/scripts/templates/base.html#L1318)) and never refreshed when the worktree selector rebinds the page, so after a switch both emit sites pointed at the *original* worktree's absolute path. Two edits close this:

- `fetchWorktrees()` ([base.html:3128](../../../../skills/task-system/scripts/templates/base.html#L3128)) now assigns `PROJECT_ROOT = data.current` when the `/api/worktrees` response carries a non-empty `current` (the active worktree's project root, refreshed server-side on every switch), and returns its fetch promise.
- `onFullReload()` ([base.html:3032](../../../../skills/task-system/scripts/templates/base.html#L3032)) now `await fetchWorktrees()` **before** `setActive(target)`, landing the switched-to root before the active card (and its VS Code button) re-render. This closes the race where the card could render with the pre-switch root.

Both emit sites read this one constant, so the fix repairs both: the per-task button via `taskFileVscodeHref` ([base.html:1907](../../../../skills/task-system/scripts/templates/base.html#L1907)) and the in-body file-link rewrite ([base.html:1413](../../../../skills/task-system/scripts/templates/base.html#L1413)).

**Standalone export preserved.** In `file://` mode the fetch shim's `/api/worktrees` branch returns `{ current: '', worktrees: [] }` ([base.html:1299](../../../../skills/task-system/scripts/templates/base.html#L1299)). The `if (data.current)` guard therefore leaves the baked `PROJECT_ROOT` untouched, so an exported snapshot keeps the project root it was generated with.

**The button (groundwork committed together).** `.vscode-btn` CSS, the `VSCODE_ICON` constant, the `taskFileVscodeHref(path)` helper, the active-card header button markup, and its href wiring in `loadActiveNode` are committed as one coherent change with the sync fix. The helper builds `vscode://file/' + PROJECT_ROOT + '/superRA/' + (path ? path + '/' : '') + 'task.md'`, mirroring the `superRA/<path>/` prefix the in-body rewrite uses.

### Verification

- **Real user path (server).** Served the dashboard, then drove a worktree switch via the live API. Before the switch `/api/worktrees` reported `current = …/better-handoff`; `POST /api/worktree/switch` to `…/codex-task-hooks-impl/superRA` returned HTTP 200 and `current` flipped to `…/codex-task-hooks-impl`. `fetchWorktrees()` assigns that exact value to `PROJECT_ROOT`, and `/node/` then served from the switched tree. Switched back cleanly to restore state.
- **Rendered href inspection.** Ran both emit-site expressions through a worktree switch driven by the guarded `if (data.current) PROJECT_ROOT = data.current` assignment. The button href and in-body href both flip from `vscode://file//…/better-handoff/superRA/…/task.md` to `vscode://file//…/codex-task-hooks-impl/superRA/…/task.md`. With `current=''` (standalone), `PROJECT_ROOT` is preserved unchanged.
- **JS parse.** Generated a static dashboard and `node --check`'d all four inline `<script>` blocks (incl. the 1.75 MB app script carrying these changes) — all parse with no syntax error.
- **Test suite.** `python -m pytest skills/task-system/scripts/test_dashboard.py -q` → 81 passed.

