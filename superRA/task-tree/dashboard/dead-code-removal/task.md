---
title: "Remove the Dead Giant-Tree Rendering Path"
status: not-started
depends_on: []
---

## Objective

Remove the unreachable pre-master-detail rendering subsystem so the dashboard has exactly one row-rendering path (`nav_node.html`).

- Delete the `GET /tree` and `GET /task/{path}` routes, the `_render_task_fragment` / `_render_task_node` helpers, the `task_node.html` and `task_children.html` templates, and the client-side cluster `toggleTask` + its `/task/` lazy-load + the `:scope > .task-body` branch of `updateTreeCommentBadges`.
- After removal, no duplicated row markup remains: the row + approved-count loop lives only in `nav_node.html`.
- The standalone export must not regress — verify (not assume) that `_build_standalone_fragments` and the client fetch shim never reference the removed routes or templates.
- Validation: full dashboard and task-tree suites green; a grep for the removed names finds nothing outside test history; a live serve renders sidebar, active card, kanban, and DAG views, and a fresh export opens with rendering intact.

## Planner Guidance

Evidence the subsystem is dead (2026-07-19 design review): the shipped page renders the sidebar via `/nav` (`nav_node.html`) and the active card via `/node/` (`node_body.html`); `task_node` markup is emitted only by `/tree`, which returns a bare fragment with no script, so its `onclick="toggleTask(this)"` handlers are non-functional there too. Client cluster at [base.html:2553-2596](../../../../skills/task-tree/scripts/templates/base.html#L2553-L2596); dead badge branch at base.html:4856-4857 (nav rows have no `.task-body`); duplicated row markup [nav_node.html:31-45](../../../../skills/task-tree/scripts/templates/nav_node.html#L31-L45) vs [task_node.html:87-101](../../../../skills/task-tree/scripts/templates/task_node.html#L87-L101); routes at [plan_dashboard.py:1003-1023](../../../../skills/task-tree/scripts/plan_dashboard.py#L1003-L1023) and 1383-1391.

`test_dashboard.py` pins some of these surfaces — update or remove those tests as part of this task, and say in `## Results` which tests were retired and why.
