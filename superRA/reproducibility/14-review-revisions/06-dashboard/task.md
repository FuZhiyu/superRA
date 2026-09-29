---
title: "Dashboard DAG Opens Readable and Carries No Dead Modes"
status: not-started
depends_on:
  - 03-readiness-model
---

## Objective

Fix six problems in the dashboard's Graph view, where task nodes expand into their steps: three a researcher sees on screen and three in the code behind them. The [navigation contract](../../04-dashboard-view/scalable-navigation/attachments/design.md) is the specification. A headless-browser review on 2026-09-28 found each problem, and the screenshots below come from it.

### Problems a researcher sees

1. **The graph opens too small to read.** On open, the view shrinks the whole graph to fit the canvas, with no minimum zoom. With 7 tasks it opens at 58%. With 50 tasks in 10 top-level groups it opens at 27%: task titles are about 3 px tall, and every edge runs through one bundle above the cards, so nobody can tell which task feeds which. The contract asks for a readable initial scale, with Fit as an explicit button.
   - **Fix:** open near 80%, centered on the selected task; keep Fit as a button.

   ![A 50-task graph opening at 27% zoom: unreadable card titles and one tangled bundle of edges above them](attachments/opens-at-27-percent.png)

2. **A written prerequisite looks the same as a file dependency.** An edge from `depends_on` and an edge inferred from one step reading another's output are drawn identically (both use the `rp-wire` style). The words "Logical prerequisite" appear only in a popup after clicking the edge. In the screenshot below, the edge into "Notes (logical only)" looks like every file edge.
   - **Fix:** draw logical edges distinctly, for example dashed.

3. **A broken task looks like an empty one.** A task whose `## Reproduction` block fails to parse shows "0 steps" with no error marker, filed under "No connections in this view". It is indistinguishable from a task that simply has no steps, although the header reports "3 errors · graph blocked".
   - **Fix:** mark the card as an error and link it to its finding.

   ![Invalid-graph fixture: the Malformed card reads "0 steps" with no error marker, and the logical-only edge into Notes matches the file edges](attachments/malformed-and-logical-edges.png)

### Problems in the code behind it

4. **Dead code from removed views.** About 100 lines of [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js) serve the trace, scope, and tier modes, which no longer exist. Tests still exercise that code, so every dashboard change has to keep dead code working. One piece still shows users a notice naming a control that is gone: "Use Whole project to recover".
   - The code: `reproSearch` (never called); `reproBranchExpansion`, `reproBoundaryHTML`, and `reproLogicalBoundaryHTML` (called only from tests); the walk, anchor, mode, and roots state in `reproProject`, which navigation always resets; and the "Outside scope" labels.
   - The older dependency views: the `/dag` Mermaid page and `dag.html`, reached only by tests, and the `buildChildFlow` mini-graph, which duplicates the Graph view.
   - **Fix:** remove all of it with the tests that pin it.

5. **The graph data repeats itself.** `/api/repro/graph`, the endpoint the Graph view loads, returns 352 KB at 200 steps, and about 40% of it is repeated:
   - `task_edges` repeats `dependencies.edges`, and `boundaries` repeats the edge evidence.
   - Every finding is sent twice, and the browser removes the copies by comparing JSON strings pairwise, which grows with the square of the number of findings.
   - One cycle is reported both as a step cycle and as a dependency cycle.
   - **Fix:** send each fact once.

6. **The layout code cannot be reviewed.** `reproHierarchyLayout` is about 80 lines of 300–900 characters each, so a change to the layout cannot be read in a diff. Speed is fine: layout takes 16 ms and drawing 38 ms at 200 expanded steps.
   - **Fix:** reformat the layout and edge router so a diff can be read; keep the algorithm.

### Validation

A headless browser runs a 50-task, 200-step fixture collapsed and fully expanded, plus an invalid-graph fixture, with no page errors. Problems 1–3 are checked on screenshots, and 4–6 in the code and payload. The contract items the review found already met stay met:

- one hierarchy, with task nodes expanding into steps;
- logical edges ending at the task boundary, even for expanded tasks or tasks with no steps;
- labeled cycles under a "graph blocked" header, with nothing offered for execution;
- diagnostics that separate malformed steps from steps caught in a cycle.

Owning task: [scalable-navigation](../../04-dashboard-view/scalable-navigation/task.md).
