---
title: "Integrate Task Navigation and Expandable Dependencies"
status: approved
depends_on: []
---

## Objective

Integrate task reading and dependency inspection into one workspace, with Tree and DAG as alternative navigators sharing selection and task content, and flexible task/step expansion in projects with 500 steps across 50 owner tasks.

- Implement the [interaction contract and acceptance checks](attachments/design.md): Tree/DAG navigation, shared task reader and comments, independent selection and expansion, a visible project overview, persistent inspection, and navigation recovery. Remove the duplicate reproduction overview and subtree picker; make existing task-page dependency entry points use the same graph.
- Group step cards by owner task with collapsible summaries, readable initial zoom, routed directional edges, and selection that remains visible beside the inspector. Validate against the heterogeneity graph as well as synthetic fixtures.
- Consume the [0.5 dependency and freshness contract](../../attachments/v05-design.md) from the graph/runner owners; preserve task comments and standalone export. This task owns dashboard presentation and payload integration, not a second dependency or freshness implementation.
- Expose logical-only tasks/edges, parent-owned steps, invalid combined cycles, and fresh-by-acceptance evidence without additional status vocabulary.
- Validate graph semantics with deterministic fixtures and navigation with browser interactions, including live updates and an offline export. Record the exercised environment and visual evidence alongside the results.

## Details

- **Placement:** this is a substantial extension of [the reproduction dashboard](../task.md), whose shipped view covers a small all-step graph. The general [dashboard task](../../../task-tree/dashboard/task.md) owns the application shell, not reproduction graph semantics. One implementation task owns this shared UI edit surface; splitting search, filters, layout, and inspection into sibling tasks would duplicate ownership.
- **Implementation surface:** [base.html](../../../../skills/task-tree/scripts/templates/base.html) owns the shared workspace shell; [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js#L895) owns reproduction rendering and the shared hash router; [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css#L1603) owns its presentation. [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py) embeds client assets and graph snapshots for export. [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py#L6637) and [state-preservation tests](../../../../skills/task-tree/scripts/tests/test_state_preservation.py) are the existing verification homes.
- **Data already available:** [graph_to_dict](../../../../skills/task-tree/scripts/_repro.py#L566) provides task ownership, tiers, file paths, step edges with their connecting files, and external inputs. The client fetches all tiers. The graph owner supplies effective task nodes/edges and provenance; the runner owner supplies acceptance explanations. Reuse these payloads for local expansion, filtering, and tracing.
- **Navigation coupling:** the shared router uses the hash for the active task and attachment; the worktree selector lives in the ordinary query string. Extend this router coherently so reproduction history cannot hijack task or attachment navigation.
- **Artifacts:** maintained UI code and regression fixtures belong beside their existing runtime and test owners. Screenshots and a concise manual-verification record belong in this task's attachments. The hand-authored design below has no producer step; register any retained scripted measurement when its results are cited, per [reproducibility](../../../../skills/reproducibility/references/designing-the-graph.md#what-earns-a-step).
- **Interaction preview:** [Tree/DAG example](attachments/task-dag-preview.html) is a hand-authored design companion for selection, branch expansion, scope, and reader placement. Its small example graph illustrates interactions; the design contract and runtime verification requirements remain authoritative.
- **Status impact:** this child reopens its ancestors through normal rollup. No sibling input or reproduction schema changes, so existing sibling approvals stand.

## Results

- [The workspace DAG](../../../../skills/task-tree/scripts/templates/dashboard.js) uses the shared task reader and comments, independently folded task containers, global search, and logical/file edge evidence; the [unified workspace](dag-design/task.md) later replaced scope and trace controls with one project map. [Projection regressions](../../../../skills/task-tree/scripts/tests/test_navigation_projection.py) cover parent setup → child → parent report, inherited logical prerequisites, nested folding, chain shortcuts, disconnected components, fan-out, and cyclic graph inspection.

- Verification: dashboard, state-preservation, projection, and browser suites passed **503 tests, 4 skipped**. On Chrome 153.0.8010.48 / macOS ARM64, repeated loaded-payload maxima on the 500-step fixture were **0.8 ms search**, **3.1 ms Project overview**, and **97.2 ms full expansion**; the collapsed map opens at 59% scale. An earlier duplicate producer that timed the removed scope filter is retired. Light/dark desktop, tablet, and 390 px phone checks found no page-level horizontal overflow. The retained real-project image omits research prose and execution content.

