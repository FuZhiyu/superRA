---
title: "Integrate Task Navigation and Expandable Dependencies"
status: in-progress
depends_on: []
---

## Objective

Integrate task reading and dependency inspection into one workspace, with Tree and DAG as alternative navigators sharing selection and task content, and flexible task/step expansion in projects with 500 steps across 50 owner tasks.

- Implement the [interaction contract and acceptance checks](attachments/design.md): Tree/DAG navigation, shared task reader and comments, independent selection/expansion/focus actions, combined subtree/tier filtering, persistent inspection, and navigation recovery. Remove the duplicate reproduction overview and subtree picker; make existing task-page dependency entry points use the same graph.
- Group step cards by owner task with collapsible summaries, readable initial zoom, routed directional edges, and selection that remains visible beside the inspector. Validate against the heterogeneity graph as well as synthetic fixtures.
- Consume the [0.5 dependency and freshness contract](../../attachments/v05-design.md) from the graph/runner owners; preserve task comments and standalone export. This task owns dashboard presentation and payload integration, not a second dependency or freshness implementation.
- Expose logical-only tasks/edges, parent-owned steps, invalid combined cycles, and fresh-by-acceptance evidence without additional status vocabulary.
- Validate graph semantics with deterministic fixtures and navigation with browser interactions, including live updates and an offline export. Record the exercised environment and visual evidence alongside the results.

## Details

- **Placement:** this is a substantial extension of [the reproduction dashboard](../task.md), whose shipped view covers a small all-step graph. The general [dashboard task](../../../task-tree/dashboard/task.md) owns the application shell, not reproduction graph semantics. One implementation task owns this shared UI edit surface; splitting search, filters, layout, and inspection into sibling tasks would duplicate ownership.
- **Implementation surface:** [base.html](../../../../skills/task-tree/scripts/templates/base.html) owns the shared workspace shell; [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js#L895) owns reproduction rendering and the shared hash router; [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css#L1603) owns its presentation. [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py) embeds client assets and graph snapshots for export. [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py#L6637) and [state-preservation tests](../../../../skills/task-tree/scripts/tests/test_state_preservation.py) are the existing verification homes.
- **Data already available:** [graph_to_dict](../../../../skills/task-tree/scripts/_repro.py#L566) provides task ownership, tiers, file paths, step edges with their connecting files, and external inputs. The client fetches all tiers. The graph owner supplies effective task nodes/edges and provenance; the runner owner supplies acceptance explanations. Reuse these payloads for local expansion, filtering, and tracing.
- **Navigation coupling:** the shared router uses the hash for the active task and attachment; the worktree selector lives in the ordinary query string. Extend this router coherently so reproduction history cannot hijack task or attachment navigation.
- **Artifacts:** maintained UI code and regression fixtures belong beside their existing runtime and test owners. Screenshots and a concise manual-verification record belong in this task's attachments. The hand-authored design below has no producer step; register any retained scripted measurement when its results are cited, per [reproducibility](../../../../skills/reproducibility/SKILL.md#what-gets-a-step).
- **Status impact:** this child reopens its ancestors through normal rollup. No sibling input or reproduction schema changes, so existing sibling approvals stand.

## Revision Notes

The 0.5 contract replaces separate task summaries and step dependencies with one expandable hierarchy. The researcher further selected Tree and DAG as alternative task navigators, replacing the separate Reproduction destination and duplicate tree. Earlier task-return allowances are invalid between disjoint groups; parent/child internal edges remain valid. The graph and runner parent prerequisites must land before the UI can verify the new payloads.

## Results

The partial Reproduction redesign has matching [layout styles](../../../../skills/task-tree/scripts/templates/dashboard.css) and [control handlers](../../../../skills/task-tree/scripts/templates/dashboard.js). The repair covers the task overview, subtree picker, search results, bounded pan/zoom canvas, responsive inspector, graph controls, task-page step links, and scoped navigation on reload and Back/Forward.

Explore's cross-subtree dependency display crashed because it called `.join()` on the API's scalar `via` file path. The renderer now displays that path directly. A [regression test](../../../../skills/task-tree/scripts/test_dashboard.py) feeds the graph API response through the actual Explore handler and HTML renderer; it reproduced the TypeError before the fix and passes afterward. The dashboard and [state-preservation tests](../../../../skills/task-tree/scripts/tests/test_state_preservation.py) passed: 424 passed. JavaScript syntax and diff checks passed.

The installed Claude plugin serving the [heterogeneity dashboard](https://home-studio.tail7992bc.ts.net:8444/?wt=heterogeneity-reproduction) received the Explore fix. HTTP retrieval confirmed byte-for-byte JavaScript agreement with the checkout and cache version `98c6417744dd`. A Node render check using the live graph (96 steps, 296 file edges) exercised Explore for all 54 subtree scopes. The preceding installed JavaScript is backed up at `/Users/zhiyufu/.cache/superra-dashboard-explore-backup-20260918.js`.

The full scalable-navigation contract remains in progress. Browser visual verification could not run: computer-use access reported no available browser and no Chrome/Safari window. The 500-step performance pass, full live/offline interaction journeys, and visual evidence required by the objective remain outstanding; passing unit and route tests does not establish those checks.

## Review Notes

Planning design review: shared navigation state and expansion/folding journeys.

1. **[BLOCKING] Define tracing by its anchor after selection changes.** [Folding](attachments/design.md#L35) selects the folded task when its selected step becomes hidden and preserves the trace anchor, but the [mode table and prerequisite](attachments/design.md#L62-L70) define tracing around the selected step and require one to remain selected. The required fold journey therefore has no consistent tracing state; selecting a different task while tracing has the same conflict. Define a selected step as the prerequisite for starting a trace, derive an existing trace's node set from its stored anchor, and specify that folding projects that set through current containers without clearing the trace or reopening the group. Add an acceptance journey that starts a trace, selects a task, folds the anchor's ancestor, and reopens it while preserving the anchor and mode. → implemented: [trace modes](attachments/design.md#a-bounded-graph-viewport-supports-both-browsing-and-tracing) now use the stored anchor and project through folds; the [acceptance checks](attachments/design.md#acceptance-checks) include the requested journey.
