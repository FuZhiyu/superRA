---
title: "Worktree-aware VS Code task links in the dashboard"
status: implemented
depends_on:
  - worktree-selector
  - vscode-line-anchors
tags: []
created: 2026-06-02
---

## Objective

Make every `vscode://file/` link the dashboard emits resolve against the **currently active worktree**, and add a per-task "Open in VS Code" button that jumps to that task's `task.md`. All edits are in the one dashboard source template `skills/task-tree/scripts/templates/base.html`.

**The bug (as originally diagnosed).** The client root constant was baked once at page render and never refreshed when the dashboard — a long-lived single page — rebinds to a different worktree, so after a switch every `vscode://file/` href pointed at the *original* worktree's absolute path. This produced a real failure: an editor link to `…/ElasticityBound-Local/superRA/03-bound-in-models/task.md`, a path under a worktree that is not where the file actually lives. Two emit sites shared the stale root: the per-task "Open in VS Code" button (`taskFileVscodeHref`) and the in-body file-link rewrite. The fix had to repair both. (The original diagnosis named `switchWorktree()` → `POST /api/worktree/switch` → SSE `full-reload`; that switching path was later replaced by per-request `?wt=` resolution — see the Results supersession note.)

**The fix — keep the client root bases in sync with the active worktree.** (Mechanism superseded downstream; recorded here for the current tree.) The page rebinds worktrees by client navigation to a `?wt=<wt_id>` URL. `fetchWorktrees()` reads `/api/worktrees` — `launch_wt_id` plus per-entry `wt_id`/`path`/`plan_root` — indexes each worktree's project root and resolved task-root by `wt_id`, and re-points `PROJECT_ROOT`/`RESOLVED_ROOT`/`ROOT_PREFIX` to the active `?wt=` so every editor link follows the active worktree. (The original cut used the now-retired `POST /api/worktree/switch` + server `current`/`_current_worktree_path` field; see the Results supersession note.)

**Standalone export must stay correct.** In standalone (`file://`) mode `window.fetch` is replaced by a shim whose `/api/worktrees` branch returns `{ launch_wt_id: '', worktrees: [] }`. With no worktree entries the re-point guard leaves the server-injected `PROJECT_ROOT`/`RESOLVED_ROOT`/`ROOT_PREFIX` untouched — the exported snapshot keeps the roots it was generated with. Do not regress this.

**The button.** `.vscode-btn` CSS, a `VSCODE_ICON` constant, the `taskFileVscodeHref(path)` helper, the header button markup, and its href wiring in `loadActiveNode`. The helper builds the local link off `RESOLVED_ROOT` and the GitHub link off `ROOT_PREFIX` (no hardcoded `superRA/` segment — delinked by [02-file-link-consistency](../live-server/path-basis-consistency/02-file-link-consistency/task.md)), the single convention both emit sites share.

**Scope discipline.** Touch only `base.html`. Do not hand-edit `skills/task-tree/build/lib/...` (untracked build output). No Codex-generated agent files are involved.

### Conventions

Work in this project worktree only: `/Users/zhiyufu/Dropbox/package_dev/superRA.worktrees/better-handoff`. Concurrent worktrees of this repo exist; keep all edits and the commit on this worktree's branch.

## Validation

- **Real user path (required).** Serve the dashboard (`uv run --project skills/task-tree superra dashboard`), open it, and with the worktree selector switch to a *different* worktree. Confirm both (a) the active task's "Open in VS Code" button href and (b) an in-body relative file link now carry the **switched-to** worktree's absolute path, not the page-load worktree's. Inspect the actual rendered `href`, not just the function in isolation.
- The inline `<script>` in the generated page parses (no JS syntax error) and the dashboard test suite passes: `uv run --project skills/task-tree --with pytest --with httpx python -m pytest skills/task-tree/scripts/test_dashboard.py -q`.

## Results

Every `vscode://file/` link the dashboard emits now resolves against the **currently active worktree**, and a per-task "Open in VS Code" button jumps to that task's `task.md`. All edits are in the single dashboard source template [base.html](../../../../skills/task-tree/scripts/templates/base.html).

> **Supersession note.** The worktree-following behavior this task delivered still ships, but the mechanism it originally used was replaced downstream: the global `POST /api/worktree/switch` / server `_current_worktree_path` / `data.current` model was retired by [multi-worktree-serving](../multi-worktree-serving/task.md) task 03 (switching is now per-request `?wt=` resolution), and the hardcoded `superRA/` href base was delinked to `RESOLVED_ROOT`/`ROOT_PREFIX` by [02-file-link-consistency](../live-server/path-basis-consistency/02-file-link-consistency/task.md). The Results below describe the **current** mechanism.

### What changed (current mechanism)

**Worktree-following hrefs.** The page is long-lived and rebinds to a different worktree by client navigation to a `?wt=<wt_id>` URL (no server-wide swap). `fetchWorktrees()` ([base.html:3805](../../../../skills/task-tree/scripts/templates/base.html#L3805)) reads `/api/worktrees` — which now returns `launch_wt_id` plus a per-entry `wt_id`/`path`/`plan_root` ([plan_dashboard.py:1149-1217](../../../../skills/task-tree/scripts/plan_dashboard.py#L1149)) — and indexes each worktree's project root and resolved task-root by `wt_id` (`_wtProjectRoots` / `_wtResolvedRoots`). For the active `?wt=` it re-points all three client bases — `PROJECT_ROOT`, `RESOLVED_ROOT`, and `ROOT_PREFIX` ([base.html:3830-3834](../../../../skills/task-tree/scripts/templates/base.html#L3830)) — so every editor link follows the active worktree.

**Both emit sites follow the re-pointed bases.** The per-task "Open in VS Code" button (`taskFileVscodeHref`) and the in-body file-link rewrite build hrefs off `RESOLVED_ROOT`/`ROOT_PREFIX` rather than a hardcoded `superRA/` segment — [test_dashboard.py:2060-2073](../../../../skills/task-tree/scripts/test_dashboard.py#L2060) asserts the `/superRA/` literal is absent from `taskFileVscodeHref`. Because both sites read the same re-pointed bases, the worktree follow repairs both at once.

**Standalone export preserved.** In `file://` mode the fetch shim's `/api/worktrees` branch returns `{ launch_wt_id: '', worktrees: [] }` ([base.html:1631](../../../../skills/task-tree/scripts/templates/base.html#L1631)). With no worktree entries the re-point guard leaves the server-injected `PROJECT_ROOT`/`RESOLVED_ROOT`/`ROOT_PREFIX` untouched, so an exported snapshot keeps the roots it was generated with.

### Verification

- **Worktree-follow.** `fetchWorktrees()` indexes `_wtResolvedRoots`/`_wtProjectRoots` per `wt_id` from `/api/worktrees` and re-points `PROJECT_ROOT`/`RESOLVED_ROOT`/`ROOT_PREFIX` to the active `?wt=`, so both emit sites' hrefs carry the active worktree's absolute path. Covered by `TestWorktreeRootFollowing` (the `/api/worktrees` `plan_root` field + the `fetchWorktrees` re-point) added in [02-file-link-consistency](../live-server/path-basis-consistency/02-file-link-consistency/task.md).
- **Delink guard.** `taskFileVscodeHref` carries no `/superRA/` literal — pinned by [test_dashboard.py:2060-2073](../../../../skills/task-tree/scripts/test_dashboard.py#L2060).
- **Test suite.** The dashboard suite passes on the current tree (see the full-suite run recorded under [02-file-link-consistency](../live-server/path-basis-consistency/02-file-link-consistency/task.md) and serve-lifecycle).

## Review Notes

1. **MAJOR** — both the Objective and the Results describe retired mechanics as the current implementation: `POST /api/worktree/switch`, the server field `_current_worktree_path`, `fetchWorktrees()` assigning `PROJECT_ROOT = data.current`, and the `vscode://file/' + PROJECT_ROOT + '/superRA/' + …` href convention. None of this exists anymore: the switch endpoint and `current` field were removed by [multi-worktree-serving](../multi-worktree-serving/task.md) task 03 (`/api/worktrees` now returns `launch_wt_id` + per-entry `wt_id`/`plan_root`, [plan_dashboard.py:1149-1217](../../../../skills/task-tree/scripts/plan_dashboard.py#L1149)), and the hardcoded `superRA/` href base was delinked to `RESOLVED_ROOT`/`ROOT_PREFIX` by [02-file-link-consistency](../live-server/path-basis-consistency/02-file-link-consistency/task.md) — [test_dashboard.py:2060-2073](../../../../skills/task-tree/scripts/test_dashboard.py#L2060) now asserts the `/superRA/` literal is *absent* from `taskFileVscodeHref`. The worktree-following behavior this task delivered still exists (now via `_wtResolvedRoots` re-pointing `PROJECT_ROOT`/`RESOLVED_ROOT`/`ROOT_PREFIX` per `?wt=`, [base.html:3805-3830](../../../../skills/task-tree/scripts/templates/base.html#L3805)); per the stale-content checklist, rewrite the Results in place to the current mechanism with a one-line supersession note, so a reader verifying this approved task against the code does not find the claimed implementation absent.
   → implemented: rewrote `## Results` (added a supersession blockquote; "What changed (current mechanism)" now describes the `?wt=` per-request follow via `_wtResolvedRoots`/`_wtProjectRoots` re-pointing `PROJECT_ROOT`/`RESOLVED_ROOT`/`ROOT_PREFIX`, and the `RESOLVED_ROOT`/`ROOT_PREFIX` href bases with no hardcoded `superRA/`) ([task.md:35](task.md)); also de-staled the §Objective "The bug"/"The fix"/"The button" paragraphs to the current mechanism with a supersession note ([task.md:13](task.md)).
