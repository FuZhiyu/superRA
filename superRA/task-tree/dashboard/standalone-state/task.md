---
title: "Parameterize the Standalone Renderer; Retire the Legacy Module Globals"
status: not-started
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
