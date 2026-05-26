---
title: "Render root task in dashboard tree view"
status: implemented
review_status: approved
integration_status: ~
depends_on:
  - ../templates
tags: []
created: 2026-05-25
updated: 2026-05-25
---

## Objective

When `.plan/task.md` exists and has body content (objective, model inventory, conventions, etc.), it should appear as a renderable tree node in the dashboard — not just as a header title. When there is no root `task.md` or its body is empty, the dashboard should fall back to rendering children directly as before.

## Results

### Changes

Four files changed:

1. **`templates/base.html`** (live dashboard tree view): Conditional — if `root_task.body` is non-empty, render root as a `task_node` at depth 0; otherwise loop over `root_task.children` at depth 0 as before.

2. **`templates/task_node.html`** (task node macro): Use `'root'` as fallback `path_id` when `task.path` is empty, giving `id="task-root"` instead of `id="task-"`. Bumped inline-render depth threshold from `< 2` to `< 3` (and lazy-load threshold from `>= 2` to `>= 3`) to compensate for root occupying depth 0.

3. **`plan_dashboard.py`** (static dashboard JS `renderTree`): Same conditional — check `TASK_DATA.body` before deciding whether to render root as a node or loop children.

4. **`plan_dashboard.py`** (SSE swap `_render_task_node`): Bumped hardcoded depth from 2 to 3 to match the new lazy-load threshold.

### Verification

- Live dashboard against `/Users/zhiyufu/Dropbox/Discussions/.plan` (has root `task.md` with body): root node "Hidden-Source Price-Jump Demand Elasticity Model" renders in tree view with expandable sections.
- Synthetic `.plan/` without root `task.md`: falls back to children-only rendering; no empty or "(no root task.md)" node.
- Static `generate` subcommand: same conditional logic in JS.
