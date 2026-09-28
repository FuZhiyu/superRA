---
title: "Dashboard DAG Opens Readable and Carries No Dead Modes"
status: not-started
depends_on:
  - 03-readiness-model
---

## Objective

The dashboard's task/step DAG meets the [navigation contract](../../04-dashboard-view/scalable-navigation/attachments/design.md) at scale and carries no code from retired modes.

- **Readable initial scale.** The first render fits to the canvas with no zoom floor (`reproFit`), opening at 27–58%. Open near 80% anchored on the selection; keep Fit as an explicit button.
- **Logical-only edges look different** from file edges (for example dashed); both now share the `rp-wire` class, and the "Logical prerequisite" label appears only in the click popup.
- **A malformed task's card shows an error marker**, not "0 steps".
- **Dead code from retired trace, scope, and tier modes is gone**, with the tests that pin it: `reproSearch` (never called), `reproBranchExpansion`, `reproBoundaryHTML`, `reproLogicalBoundaryHTML`, the walk/anchor/mode/roots state in `reproProject`, the "Outside scope" labels, and the "Use Whole project to recover" notice naming a removed control.
- **The `/api/repro/graph` payload carries each fact once:** `task_edges` duplicates `dependencies.edges`, `boundaries` repeats the evidence, findings appear twice (deduplicated client-side by an O(n²) `JSON.stringify` comparison), and one cycle is reported both as a step cycle and a dependency cycle.
- **The layout code is maintainable.** `reproHierarchyLayout` runs about 80 lines of 300–900 characters each.

Validation: a headless-browser pass on a 50-task / 200-step fixture, collapsed and fully expanded, plus an invalid-graph fixture.

### Researcher decisions

- **Layout code: reformat or vendor a layered-layout library** and drop the hand-written port and channel router. Recommendation: reformat; layout already runs in 16 ms and draws in 38 ms at 200 expanded steps.
- **Pre-existing dependency views** (the `/dag` Mermaid route and `dag.html`, reached only by tests; the `buildChildFlow` mini-graph) duplicate the new workspace. Recommendation: remove them here.

Owning task: [scalable-navigation](../../04-dashboard-view/scalable-navigation/task.md).

## Details

Contract items the review found met in a headless browser: one hierarchy with task nodes expanding to steps; logical edges ending at the task boundary even for expanded or step-less tasks; labeled cycles with a "graph blocked" header and nothing offered for execution; diagnostics separating omitted malformed steps from steps in a cycle; no page errors. At 200 steps the payload is 352 KB, about 40% duplicated.
