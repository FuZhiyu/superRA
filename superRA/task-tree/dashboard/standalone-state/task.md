---
title: "Parameterize the Standalone Renderer; Retire the Legacy Module Globals"
status: approved
depends_on: []
---

## Objective

The standalone render path takes explicit state, and the legacy module-global compatibility layer is gone, so render correctness no longer depends on the accident that the render coroutine never awaits.

- `render_standalone_html`, `_build_standalone_fragments`, and the render helpers receive the tree/index/project-root state as parameters (extend the existing `WorktreeState` pattern); `_root_task`, `_task_index`, `_project_root`, `_sync_default_globals`, `_set_module_state`, and `/export`'s snapshot/restore dance are deleted.
- No observable behavior change: routes, CLI `generate`, and export output are unchanged. Tests that currently drive or read the legacy globals are rewritten against the new seams, preserving what they verify.
- Validation: both suites green; a standalone export of a fixture tree is byte-identical before/after this change (or every difference is explained in `## Results`); no module-level mutable render state remains except the worktree cache and launch configuration.

## Planner Guidance

The per-worktree model already exists — `WorktreeState` at [plan_dashboard.py:149-165](../../../../skills/task-tree/scripts/plan_dashboard.py#L149-L165) — but the standalone renderer still drives module globals, and `/export` mutates and restores them around a render (1451-1455). That is safe today only because `render_standalone_html` contains no `await`; this task removes the trap and unblocks `event-loop-offload` (which must run these renders off the event loop).

The parent task's `## Results` records extraction debt: the standalone build (~340 lines, no FastAPI coupling) is a clean extraction candidate following the `dashboard_artifact_workflow.py` precedent. Extracting it into its own module is optional here — do it if the parameterization makes it fall out naturally, skip it if it inflates the diff.

## Results

The standalone render path now threads its render state as parameters instead of module globals.

- **`_render_node_body`** ([plan_dashboard.py:770](../../../../skills/task-tree/scripts/plan_dashboard.py#L770)) and **`_render_summary`** ([plan_dashboard.py:777](../../../../skills/task-tree/scripts/plan_dashboard.py#L777)) now require their `project_root` / `root_task` argument outright — the `None` fallback to a module global is gone. All call sites already passed these explicitly except the standalone path (below) and test fixtures (rewritten).
- **`_build_standalone_fragments`** ([plan_dashboard.py:1380](../../../../skills/task-tree/scripts/plan_dashboard.py#L1380)) now takes a `WorktreeState` (the existing per-worktree pattern at [plan_dashboard.py:142](../../../../skills/task-tree/scripts/plan_dashboard.py#L142)) instead of reading `_root_task`/`_project_root`.
- **`render_standalone_html`** ([plan_dashboard.py:1662](../../../../skills/task-tree/scripts/plan_dashboard.py#L1662)) builds an explicit, throwaway `WorktreeState(wt_id="", plan_root=plan_root, project_root=project_root, root_task=scoped_root)` ([plan_dashboard.py:1715](../../../../skills/task-tree/scripts/plan_dashboard.py#L1715)) and threads it into `_build_standalone_fragments`. The dead `index`/`_build_index(scoped_root, index)` pair that only fed the old `_set_module_state` call is removed along with it (the `full_index` lookup used to *locate* a `--root` subtree is untouched — that one is load-bearing).
- **`/export`** ([plan_dashboard.py:1337](../../../../skills/task-tree/scripts/plan_dashboard.py#L1337)) no longer snapshots/restores `_root_task`/`_task_index`/`_project_root` around the render — `render_standalone_html` cannot perturb live state now that it owns its own render state.
- **Deleted outright:** the `_root_task`/`_task_index`/`_project_root` module globals, `_sync_default_globals`, and `_set_module_state`. Their three call sites in `rebuild_tree`, `rebuild_task`, and `rebuild_worktree_state` are simplified accordingly — those functions already operated on `WorktreeState` objects in `_worktree_cache`; only the legacy-global mirroring step is gone.
- **Extraction into its own module was skipped**, per the guidance's explicit "skip if it inflates the diff" — the parameterization here is a signature change (add a `state`/`project_root` argument, drop a global read), not a structural change that would make a module boundary fall out naturally. The extraction debt the parent task recorded is unchanged and still available for a future task.

**No remaining module-level mutable render state beyond the worktree cache and launch configuration:** confirmed by inspecting every module-level `_`-prefixed binding in [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py) after this change — the survivors are `_worktree_cache`/`_launch_wt_id` (the worktree cache), `_worktree_clients`/`_worktree_watchers`/`_worktree_stop_events`/`_worktree_locks` (the pre-existing per-worktree SSE/watcher lifecycle, out of this task's scope), `_server`/`_standalone_process_owner` (launch/process config), `_jinja_env` (a template-engine cache, not task-tree render state), and static regex/constant tables.

**Tests rewritten against the new seams** (no test intent changed, only how state is reached):
- [conftest.py:95](../../../../skills/task-tree/scripts/conftest.py#L95) adds a shared `_launch_state(pd)` helper returning `pd._worktree_cache[pd._launch_wt_id]` — the replacement for reading the retired globals directly.
- [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py), [tests/test_state_preservation.py](../../../../skills/task-tree/scripts/tests/test_state_preservation.py), and [test_worktree_selector.py](../../../../skills/task-tree/scripts/test_worktree_selector.py): every `plan_dashboard._root_task` / `_task_index` / `_project_root` read is replaced with `_launch_state(plan_dashboard).root_task` / `.task_index` / `.project_root`; bare `_render_summary()` / `_render_node_body(task)` / `_build_standalone_fragments()` calls now pass their state explicitly (the latter by constructing the same whole-tree `WorktreeState` `render_standalone_html` would have built); dead `plan_dashboard._project_root = ...` pre-assignments (immediately overwritten by the old `_sync_default_globals()`, now simply unread) are deleted.

**Validation:**
- Both suites green: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts` → `696 passed, 2 skipped` (the 2 skips are the pre-existing Playwright/chromium gate, unrelated to this change).
- Byte-identical standalone export verified both ways: rendered `render_standalone_html(Path("superRA"), root="task-tree/dashboard")` (subtree) and `render_standalone_html(Path("superRA"))` (whole tree) with this branch's `plan_dashboard.py`, and again with `git show HEAD:skills/task-tree/scripts/plan_dashboard.py` swapped into an otherwise-identical scratch copy of the scripts directory. `diff`/MD5 confirm byte-for-byte identical output in both scopes (subtree: 1,238,782 bytes; whole tree: 2,357,116 bytes) — no observable behavior change.
