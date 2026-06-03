---
title: "Worktree-aware VS Code task links in the dashboard"
status: not-started
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

