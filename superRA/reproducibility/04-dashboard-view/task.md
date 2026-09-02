---
title: "Dashboard Reproduction View for Reviewing the Graph"
status: not-started
depends_on: [01-section-contract, 02-runner]
---

## Objective

Let the researcher review an agent-built graph in the dashboard and comment on it, so graph feedback flows through the task-comment loop agents already read.

- **Reproduction view** (new top-level view beside Workspace and Kanban): a layered DAG with drawn edges, nodes colored by state (`fresh`, `stale`, `missing`, `failed`, `external`, `check`), grouped by owner task with the task title as the group label, tier filter, and a legend. Clicking a node opens a detail panel: command, deps, outs, owner task link, state reason, last duration, and the log tail. Layout is deterministic for the same graph.
- **Task page:** when a task has a `## Reproduction` section, render a step table (name, state, reason, outs) above the raw YAML block and link each row to the node in the Reproduction view. The section keeps its existing comment gutter; verify that a comment on a step line round-trips through `task comment list`.
- **Data path:** `GET /api/repro/graph` and `GET /api/repro/status` serve the JSON from [01-section-contract](../01-section-contract/task.md) and [02-runner](../02-runner/task.md); state refreshes on the existing SSE reload after a build touches the lock. The standalone export embeds a snapshot of both.
- **Validation criteria:** dashboard tests cover the two routes, the export snapshot, and rendering with no registered tasks (view shows an empty state, no errors); a manual pass on a fixture graph of at least 15 steps across 4 owner tasks is recorded with a screenshot in `attachments/`. The real-graph pass belongs to [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md).

## Details

- No DAG library is vendored today; the children panel draws tiers of cards without edges ([dashboard.js §buildChildFlow](../../../skills/task-tree/scripts/templates/dashboard.js#L2252)). A hand-rolled layered layout in SVG (longest-path layering, barycenter ordering, orthogonal or bezier edges) fits ~50 nodes and avoids a vendored library; if a library is chosen instead, follow [vendor/README.md](../../../skills/task-tree/scripts/vendor/README.md).
- Route and export mechanics: [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py) `/api/children-graph` and `/export`; theme tokens in `templates/base.html`.
- Load `dataviz` guidance for the state palette and legend: states must stay distinguishable in both themes.

## Results
