---
title: "Navigate Reproduction Graphs by Subtree, Tier, and Dependency"
status: in-progress
depends_on: []
---

## Objective

Make the Reproduction view usable for locating a result, tracing its dependencies, and inspecting execution state in projects with 500 steps across 50 owner tasks.

- Implement the [interaction contract and acceptance checks](attachments/design.md): task overview, combined subtree/tier filtering, focused step graphs, persistent inspection, and navigation recovery.
- Preserve the parent's data, task-comment, and standalone-export contracts. Keep this change within dashboard presentation and navigation; reproduction declarations, execution, and freshness semantics remain unchanged.
- Validate graph semantics with deterministic fixtures and navigation with browser interactions, including live updates and an offline export. Record the exercised environment and visual evidence alongside the results.

## Details

- **Placement:** this is a substantial extension of [the reproduction dashboard](../task.md), whose shipped view covers a small all-step graph. The general [dashboard task](../../../task-tree/dashboard/task.md) owns the application shell, not reproduction graph semantics. One implementation task owns this shared UI edit surface; splitting search, filters, layout, and inspection into sibling tasks would duplicate ownership.
- **Implementation surface:** [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js#L895) owns reproduction rendering and the shared hash router; [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css#L1603) owns its presentation. [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py) embeds client assets and graph snapshots for export. [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py#L6637) and [state-preservation tests](../../../../skills/task-tree/scripts/tests/test_state_preservation.py) are the existing verification homes.
- **Data already available:** [graph_to_dict](../../../../skills/task-tree/scripts/_repro.py#L566) provides task ownership, tiers, file paths, step edges with their connecting files, and external inputs. The current client fetches all tiers. Filtering and tracing can operate locally without a new graph API.
- **Navigation coupling:** the shared router uses the hash for the active task and attachment; the worktree selector lives in the ordinary query string. Extend this router coherently so reproduction history cannot hijack task or attachment navigation.
- **Artifacts:** maintained UI code and regression fixtures belong beside their existing runtime and test owners. Screenshots and a concise manual-verification record belong in this task's attachments. The hand-authored design below has no producer step; register any retained scripted measurement when its results are cited, per [reproducibility](../../../../skills/reproducibility/SKILL.md#what-gets-a-step).
- **Status impact:** this child reopens its ancestors through normal rollup. No sibling input or reproduction schema changes, so existing sibling approvals stand.

## Results

The partial Reproduction redesign has matching [layout styles](../../../../skills/task-tree/scripts/templates/dashboard.css) and [control handlers](../../../../skills/task-tree/scripts/templates/dashboard.js). The repair covers the task overview, subtree picker, search results, bounded pan/zoom canvas, responsive inspector, graph controls, task-page step links, and scoped navigation on reload and Back/Forward.

The [dashboard tests](../../../../skills/task-tree/scripts/test_dashboard.py) and [state-preservation tests](../../../../skills/task-tree/scripts/tests/test_state_preservation.py) passed: 419 passed, 4 skipped. Added Node-based cases exercise Explore/select/trace/clear, out-of-scope step links, scoped reload, zoom, and inspector dismissal. JavaScript syntax, CSS parsing, and diff checks passed.

The installed Claude plugin serving the [heterogeneity dashboard](https://home-studio.tail7992bc.ts.net:8444/?wt=heterogeneity-reproduction) received both repaired assets. HTTP retrieval confirmed byte-for-byte agreement with the checkout and cache version `0137f92dcd03`. Original installed assets are backed up under `/Users/zhiyufu/.cache/superra-dashboard-mismatch-backup-20260917/`.

The full scalable-navigation contract remains in progress. Browser visual verification could not run: computer-use access reported no available browser and no Chrome/Safari window. The 500-step performance pass, full live/offline interaction journeys, and visual evidence required by the objective remain outstanding; passing unit and route tests does not establish those checks.
