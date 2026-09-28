---
title: "Dashboard DAG Opens Readable and Carries No Dead Modes"
status: not-started
depends_on:
  - 03-readiness-model
---

## Objective

The dashboard's dependency graph, where task nodes expand into their steps, opens at a readable size, draws each kind of edge distinctly, flags broken tasks, and carries no code from retired modes. The [navigation contract](../../04-dashboard-view/scalable-navigation/attachments/design.md) is the specification.

### What the reader sees

- **Readable on open.** The first render fits the whole graph to the canvas with no minimum zoom: 58% with 7 top-level tasks, 27% with 10 collapsed groups, where task titles are about 3 px tall. The contract asks for a readable initial scale plus an explicit Fit. Open near 80% on the selection; Fit stays a button.
- **Logical edges look different from file edges.** Both use the `rp-wire` style, and "Logical prerequisite" appears only in the popup after a click. Draw logical edges distinctly, for example dashed.
- **A task with malformed steps shows an error marker.** Its card reads "0 steps".

### What the code carries

- **No code from retired modes.** About 100 lines of [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js) serve the removed trace, scope, and tier modes: `reproSearch` (never called), `reproBranchExpansion`, `reproBoundaryHTML`, and `reproLogicalBoundaryHTML` (called only from tests), the walk, anchor, mode, and roots state in `reproProject`, the "Outside scope" labels, and a notice naming a control that no longer exists ("Use Whole project to recover"). Remove them with the tests that pin them.
- **Each fact appears once in `/api/repro/graph`.** At 200 steps the payload is 352 KB, about 40% of it duplicated:
  - `task_edges` repeats `dependencies.edges`, and `boundaries` repeats the edge evidence.
  - Findings appear twice, and the client deduplicates them with an O(n²) `JSON.stringify` comparison.
  - One cycle is reported both as a step cycle and as a dependency cycle.
- **Readable layout code.** `reproHierarchyLayout` is about 80 lines of 300–900 characters each.

### Validation

A headless browser runs a 50-task, 200-step fixture collapsed and fully expanded, plus an invalid-graph fixture, with no page errors. The contract items the review found met stay met: one hierarchy with task nodes expanding to steps; logical edges ending at the task boundary, even for expanded or step-less tasks; labeled cycles under a "graph blocked" header, with nothing offered for execution; diagnostics that separate omitted malformed steps from steps in a cycle.

### Researcher decisions

- **Layout code: reformat it, or replace the hand-written layout and edge router with a layered-layout library.** Recommendation: reformat. Layout takes 16 ms and drawing 38 ms at 200 expanded steps, so the cost is maintenance only.
- **Older dependency views.** The `/dag` Mermaid route and `dag.html` are reached only by tests, and the `buildChildFlow` mini-graph duplicates the new graph. Recommendation: remove them here.

Owning task: [scalable-navigation](../../04-dashboard-view/scalable-navigation/task.md).
