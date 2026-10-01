---
title: "Dashboard Tree and Graph Workspace for Reviewing the Reproduction Graph"
status: approved
depends_on:
  - 01-section-contract
  - 02-runner
---

## Objective

Let the researcher read tasks, review an agent-built reproduction graph, and act on it in one dashboard workspace: comments flow through the task-comment loop agents already read, and builds, their cost, and staleness causes are reachable without an agent or the CLI. The workspace stays usable on projects with 500 steps across 50 owner tasks.

- **One workspace, two layouts.** Tree prioritizes task reading with a hideable sidebar; Graph prioritizes the map with hideable details. Both share search, task/status filters, task and step selection, the reader, comments, and attachments.
- **One project map.** Task containers fold and expand independently into their steps and child tasks; Project overview collapses and fits the map; search reveals a task, step, or output file without changing filters. Selection never changes the map's contents.
- **Dependencies read honestly.** One arrow per visible endpoint pair carries every connecting file and `depends_on` prerequisite; `depends_on`-only arrows are distinguishable; only step cycles and `depends_on` cycles are marked; a task whose declaration has an error is marked with a link to its finding.
- **Step inspection.** The reader shows a step's state and reason, command, inputs, outputs, acceptance, run evidence, and log tail. Markdown step links (`task.md#step-<name>`) and `?step=<name>` URLs select the step.
- **Graph actions.** Every task and step card opens a Build menu — `superra repro build <target>`, with `--upstream`, or with `--force` — each item showing its command and an estimate from last run durations. Cards show last durations and a live build; a non-fresh card opens a hover card with `superra repro explain`'s causes. `accept`, `revoke`, and `-j` stay CLI actions.
- **Data path.** Read-only `GET /api/repro/graph` and `GET /api/repro/status` routes, a live refresh after a build or a `## Reproduction` edit, and a standalone export that works offline. The build, stop, and explain routes are live-server only.

### Constraints

- **The build route runs declared commands,** so it accepts only same-origin JSON from a `Host` naming this machine, and only a target the current graph resolves, passed as one argv element after `--`. An off-loopback `--host` bind keeps the controls; doc mode and the standalone export render none.

## Results

The workspace ships in [dashboard.js](../../../skills/task-tree/scripts/templates/dashboard.js), [dashboard.css](../../../skills/task-tree/scripts/templates/dashboard.css), and [base.html](../../../skills/task-tree/scripts/templates/base.html), served by [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py). [internals.md §Dashboard](../../../skills/task-tree/references/internals.md#dashboard-plan_dashboardpy) documents its behavior, routes, payloads, and refresh rules. It replaced a separate Reproduction view that laid steps out in swimlanes with tier filters and trace modes; Board, the `/dag` route, and the scope, trace, and tier controls are gone, and legacy URLs open the full map.

### Design decisions

- **The graph opens readable at 80%** on the selected task or step, or fitted when the whole map fits at 80% or more. A 50-task, 200-step fixture had opened at 30% collapsed and 1.4% fully expanded.
- **Each fact travels once.** The graph payload carries `depends_on` edges as `logical` and the client groups file edges from `step_edges`; findings travel only in the graph payload. This cut the 200-step fixture's payload by 38%.
- **`check` is a kind, not a state.** A check step keeps its freshness colour and adds a dashed border, a `✓`, and its own legend row.
- **Every state is spelled out.** Each node, legend row, and table cell carries a glyph and the state word, so the `--rp-*` palette meets the `dataviz` status-scale bar in both themes, with on-wash text at 4.5:1 or better.
- **A comment on a step anchors to the whole `## Reproduction` fenced block**, because the comment layer anchors blocks and the section body is one fence. Comments round-trip through `superra task comment list`.
- **The layout is deterministic** for the same graph: components are laid out separately, with unconnected cards in a labeled area; routes keep separate lanes so crossings never read as joins. The layout function was split into ranking, banding, port reservation, sizing, placement, and routing without changing its output on 3,000 random models.
- **Neither route writes to the project.** `.superra-repro/` stays `superra repro`'s to create, and without `tomllib` for a legacy lock every step reads `unknown`.

### Evidence and limits

- On the 500-step, 50-task fixture, search took 0.8 ms, Project overview 3.1 ms, and full expansion 97 ms (Chrome 153, macOS ARM64). Light and dark layouts at 390, 768, and 1440 px showed no page-level horizontal overflow.
- Native Safari and physical trackpad gestures remain unverified.
- Each step in the graph payload repeats its declared inputs across `deps`, `declared_deps`, and `dependency_origins`.

### Graph actions

- **The build outlives the server.** `POST /api/repro/build` spawns the runner in its own process group with the login shell's environment (`$SHELL -l -i -c 'env -0'`, 0.5s), so Julia, conda, and `PATH` match the researcher's terminal. Stop sends SIGTERM to that group only while the lock holder belongs to it, so a recycled pid is never signalled.
- **Executing steps read "building", not `failed`.** The mutation lock records its holder's pid and the runner stamps its pid on in-flight run records. Only the holder's records read `building now`, in `status`, `explain`, `task read`, and the dashboard; a crashed build's step still reads interrupted.
- **Polling never re-lays out the graph.** The page polls `GET /api/repro/build` every 1.5s during a build and repaints nodes, chips, and the status line in place; the lock watcher refreshes states as each step completes.
- **The estimate and timings cost no request.** Both derive from the loaded payloads, since `build --dry-run` takes the mutation lock and fails during a build.
- **Explain costs about what status does**, 1.3–2.1s on a 112-step project, so the hover card fetches once per target, caches until the next refresh, and fetches task diffs only when pinned.
- **Project pages get an opaque origin.** `/files` serves any `text/html` or `*xml` type under `Content-Security-Policy: sandbox` without `allow-same-origin`, so a page in the project cannot pass the same-origin gate of the build, comment, or open routes.
- **Reviewed** at the thorough tier for security and correctness: one blocking finding (any lock holder masked interrupted steps) and four advisories, all fixed before approval.
- **Limits.** Probing the lock takes a shared lock for microseconds, so a CLI build starting in that window is refused and can be rerun. A build whose server restarted mid-run shows no "Last build" line. On a narrow screen the Build menu can extend below the short graph stage.

Tests: the dashboard routes, payloads, and refresh in [test_dashboard.py](../../../skills/task-tree/scripts/test_dashboard.py), map projection in [test_navigation_projection.py](../../../skills/task-tree/scripts/tests/test_navigation_projection.py), and browser tests of the map and the Build menu and hover cards in [test_dag_workspace_browser.py](../../../skills/task-tree/scripts/tests/test_dag_workspace_browser.py). The graph actions add `TestReproBuildRoutes` in test_dashboard.py and the lock-holder test in [test_repro_runner.py](../../../skills/task-tree/scripts/test_repro_runner.py).
