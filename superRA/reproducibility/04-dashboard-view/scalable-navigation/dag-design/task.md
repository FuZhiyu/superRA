---
title: Unified Tree and Graph Workspace
status: approved
depends_on: []
---

## Objective

Unify Tree and Graph navigation around one search, task/status filter, selection, and task reader. Remove Board. Tree prioritizes task reading with a hideable sidebar; Graph prioritizes the map with hideable details.

- Give the graph most of the viewport. Use the dashboard's existing typography, warm neutral surfaces, borders, spacing, and accent palette; keep controls compact and clearly grouped, with secondary options and diagnostic details progressively disclosed.
- Show the task preview by default when the viewport has useful space: beside the graph in wide windows, below it in narrow, tall windows. Use a real layout split rather than an overlay. Provide an obvious hide/show control consistent with the tree sidebar and a draggable, keyboard-accessible divider for width or height. Remember explicit visibility and preferred dimensions; window resizing must not override a manual hide. Keep graph navigation and selection stable through resizing, closing, reopening, orientation changes, and full-width reading.
- Support two-finger touchpad scrolling in both axes to pan and pinch to zoom around the pointer, including Safari gestures and Chromium control-wheel events. Keep drag panning, accessible zoom buttons, fit, and keyboard recovery; prevent unintended page zoom or scroll while handling canvas gestures.
- Use one project map with an always-visible Project overview action, global search, and local task chevrons. Overview collapses all groups and fits the map; selection preserves graph contents and viewport. Folding a selected step's ancestor preserves selection and details, with a Contains selected step indicator and Show in graph recovery.
- Provide one shared Filter panel with a visibly nested, collapsible task checklist, Select all, Deselect all, partial-selection indicators, and status choices, visible active-filter summaries, and Clear filters recovery. Hidden tasks hide descendants; status matches retain ancestor context. Search opens tasks, steps, and files without changing filters. Switching layouts preserves selection, reader content/scroll, and filter state; each layout retains its own expansion and pane preference. Remove Board UI and runtime/export support.
- Remove trace modes, reproduction-tier filters, scope controls, and expansion-depth controls. Normalize legacy links to the full map while preserving meaningful task/step selection and expansion. Keep URL history, worktree isolation, and offline navigation.
- Support relative Markdown step links using `task.md#step-<name>` and same-task `#step-<name>`, with the declaration's existing name as identity. Reveal/select the exact step and validate its owner; report broken references. Dashboard sharing uses `?step=<name>`, and rendered step rows expose the anchor.
- Integrate step inspection into the shared reader with task context, clear status and output hierarchy, a copyable command, and progressive disclosure for inputs, dependencies, and run evidence. Fix task loading from Tree step selections and direct links; verify the research example, both themes, narrow panes, history, and offline navigation.
- Bundle file connections by endpoint pair; retain every file in arrow evidence and grouped Uses/Used by lists.
- Make each dependency arrow independently traceable. Avoid shared line segments that imply a common bus, false connection, or enclosing box; provide distinct routes and readable arrowheads, with source/destination highlighting on hover and keyboard focus. Verify collapsed top-level tasks and the expanded heterogeneity branch without changing dependency semantics.
- Identify cyclic dependencies with the dashboard's existing muted rust accent and a compact accessible cycle label, keeping card surfaces neutral. Distinguish a cycle in collapsed task groups from an executable-step cycle; do not imply that aggregation alone makes execution impossible. Keep acyclic edges neutral and preserve cycle visibility during edge inspection. Use existing theme tokens rather than a competing error-red palette.
- Clearly separate disconnected dependency groups in the visible graph, and place cards without visible connections in a labeled area away from routed arrows. Derive groups from connectivity in either direction, respecting task containers and the current projection; cycles remain within their connected group. Preserve all nodes, edges, expansion, selection, and inspection. Verify multiple components, isolated tasks, nested expansion, and the research overview shown by the user.
- Let the tree sidebar grow sufficiently to read long task titles, replacing its restrictive fixed width cap with bounds based on available window space. Preserve pinned, unpinned, drawer, touch, keyboard resizing, persistence, and a usable minimum task-content area.
- Preserve graph semantics, task/step inspection, URL navigation, diagnostics visibility, comments, dark mode, and standalone export. Do not alter research data or resolve the fixture's dependency declarations.
- Verify visual hierarchy and ordinary journeys in Safari through computer control at desktop and narrow widths. Add behavioral regression checks for viewport gestures and preview state; record limitations honestly where physical gestures cannot be synthesized.

## Details

- Responsive panes: choose the side/bottom breakpoint from usable graph and reading widths; for very short windows, avoid opening a pane that leaves neither area useful. Persist manual visibility separately from automatic placement, and remember side width and bottom height separately so rotating/resizing does not destroy the preferred sizes. Match tree-sidebar divider and hide-control affordances, including accessible labels and keyboard actions. Test fresh defaults, manual hide/reopen, reload, wide/portrait/short viewports, both drag axes, bounds, and tree/DAG switching.

- This child owns the shared navigation controls and the different Tree/Graph pane priorities on the existing workspace runtime.
- Initial Safari review at roughly 1030 × 768 showed controls wrapping to several rows, expanded diagnostic prose above the graph, and a reader consuming about one third of the workspace. The graph starts near the bottom edge. Chrome at 1372 × 768 has the same hierarchy problem.
- Runtime owners: [dashboard.js](../../../../../skills/task-tree/scripts/templates/dashboard.js), [dashboard.css](../../../../../skills/task-tree/scripts/templates/dashboard.css), and [base.html](../../../../../skills/task-tree/scripts/templates/base.html). Port 8996 serves the temporary navigation checkout; the research dashboard on port 8653 serves this development checkout.
- Execution: main-agent implementation and self-review in interactive mode. No generated runtime assets.
- Routing review: coincident horizontal and vertical tracks falsely suggest Methods → Verification and a box enclosing the four top-level research tasks. The declared top-level Treasury flow is Heterogeneity → Treasury → Reproduce manuscript exhibits. Use separate lanes and endpoint ports, minimize crossings and detours, and keep routes outside unrelated cards. Inspect cycles or aggregation-induced cycles before changing rank placement; preserve all real edges and their evidence. Dense graphs may cross, but crossings must not look like joins.
- Disconnected-group design: the research overview currently places unconnected tasks in the first rank beside the Stock-Market Construction Inputs routes, visually implying they feed downstream. Lay out connected components independently, with connected groups first and a compact isolated-card area afterward. Prefer understated headings, whitespace, and separators using existing theme tokens; avoid enclosing outlines that resemble dependency routes. Qualify isolated cards as “No connections in this view,” since collapsed containers affect visible connectivity. Use component-local routing so arrows cannot pass beside an unrelated group. Keep ordering deterministic and retain viewport anchoring during expansion.

## Reproduction

```yaml
steps:
  - name: dashboard-dag-design-browser
    cmd: uv run --with playwright --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python skills/task-tree/scripts/tests/navigation_browser.py --evidence superRA/reproducibility/04-dashboard-view/scalable-navigation/dag-design/attachments/browser
    deps:
      - skills/task-tree/scripts/tests/navigation_browser.py
      - skills/task-tree/scripts/plan_dashboard.py
      - skills/task-tree/scripts/templates
      - skills/task-tree/scripts/vendor
      - skills/task-tree/scripts/_artifacts.py
      - skills/task-tree/scripts/_comments.py
      - skills/task-tree/scripts/_repro.py
      - skills/task-tree/scripts/_repro_state.py
      - skills/task-tree/scripts/_repro_scope.py
      - skills/task-tree/scripts/_repro_acceptance.py
      - skills/task-tree/scripts/_task_io.py
      - skills/task-tree/scripts/_task_dependencies.py
      - skills/task-tree/scripts/_task_snapshot.py
      - skills/task-tree/scripts/_task_validate.py
      - skills/task-tree/scripts/_worktree_discovery.py
      - skills/task-tree/scripts/cli.py
      - skills/task-tree/scripts/task_comment.py
    outs:
      - superRA/reproducibility/04-dashboard-view/scalable-navigation/dag-design/attachments/browser
  - name: dashboard-dag-design-interaction-check
    kind: check
    cmd: uv run --with pytest --with playwright --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/tests/test_dag_workspace_browser.py skills/task-tree/scripts/tests/test_navigation_projection.py skills/task-tree/scripts/test_step_links.py -q
    deps:
      - skills/task-tree/scripts/tests/test_dag_workspace_browser.py
      - skills/task-tree/scripts/tests/test_navigation_projection.py
      - skills/task-tree/scripts/test_step_links.py
      - skills/task-tree/scripts/_step_links.py
      - skills/task-tree/scripts/task_check.py
      - skills/task-tree/scripts/test_dashboard.py
      - skills/task-tree/scripts/tests/navigation_browser.py
      - skills/task-tree/scripts/plan_dashboard.py
      - skills/task-tree/scripts/templates
      - skills/task-tree/scripts/vendor
      - skills/task-tree/scripts/_artifacts.py
      - skills/task-tree/scripts/_comments.py
      - skills/task-tree/scripts/_repro.py
      - skills/task-tree/scripts/_repro_state.py
      - skills/task-tree/scripts/_repro_scope.py
      - skills/task-tree/scripts/_repro_acceptance.py
      - skills/task-tree/scripts/_task_io.py
      - skills/task-tree/scripts/_task_dependencies.py
      - skills/task-tree/scripts/_task_snapshot.py
      - skills/task-tree/scripts/_task_validate.py
      - skills/task-tree/scripts/_worktree_discovery.py
      - skills/task-tree/scripts/cli.py
      - skills/task-tree/scripts/task_comment.py
```

## Results

Tree and Graph use one search, task/status filter, selection, and reader in the [dashboard runtime](../../../../../skills/task-tree/scripts/templates/dashboard.js). Board and its live/export route are removed. Tree prioritizes task reading with a hideable sidebar; Graph prioritizes the map with hideable details. Each layout retains its pane preference, and switching layouts preserves the open document and selected step.

- **Filtering:** the [task checklist](attachments/browser/workspace-filter-tree.png) has visible hierarchy guides, independent folding, branch checkboxes, partial-selection indicators, Select all, and Deselect all. Task and status choices apply to both layouts, retain matching descendants' ancestors, and survive URLs, history, and worktree switching. [Phone evidence](attachments/browser/workspace-filter-phone.png) shows a scrolling task list with controls kept outside it.
- **Navigation:** global search finds tasks, steps, output files, and task text. Hidden results open without changing filters; the reader labels the hidden selection. Tree lists steps beneath their owner, and Markdown step links preserve the current layout. Uses/Used by retains hidden connections. A live-refresh regression check verifies that background refresh cannot replace a newer selection.
- **Step reader:** task and step content occupy the same pane beneath the task breadcrumb. A readable heading, state, copyable resolved command, and linked output files replace the specification dump. Inputs include external availability inline; connected steps, parameters, declared command, extra outputs, and run evidence expand on demand. Failed runs expose their evidence automatically. Back to task clears step selection; View declaration highlights its task row; Show in graph reveals the map even after full-width reading. [Runtime](../../../../../skills/task-tree/scripts/templates/dashboard.js), [styles](../../../../../skills/task-tree/scripts/templates/dashboard.css).
- **Verification:** 35 [browser cases](../../../../../skills/task-tree/scripts/tests/test_dag_workspace_browser.py) passed, including Tree selection, reload/history, offline use, clipboard, declaration navigation, failure recovery, reviewed reuse, and responsive themes. The [500-step acceptance fixture](../../../../../skills/task-tree/scripts/tests/navigation_browser.py) passed with 1,494 file connections, comments, worktree isolation, and offline navigation. Browser coverage now verifies accepted-result evidence previously tested through a DOM mock. Direct verification of the real paper-predictability task passed at 390, 768, and 1440 pixels in light/dark Tree and Graph layouts. Native Safari and physical trackpad gestures remain unverified.
- **Reproduction:** both steps were rebuilt against the current runtime and are `fresh`; the committed bundle and lock are current. The rebuild surfaced three regressions of this redesign, now fixed: the default workspace state no longer appends `repro=` to task and attachment URLs, the pinned-sidebar test expects the window-based cap (1024 − 360 = 664), and the snapshot harness opens the collapsed diagnostics before reading the cycle finding. The attachment and sidebar suite passes 6 of 6.
- **Live dashboard:** [port 8653](http://localhost:8653/?wt=heterogeneity-reproduction) serves the development source. The reported task-loading error did not recur after restarting the stopped server and testing the supplied link, sidebar clicks, and reloads; its original cause remains unconfirmed. Task-load exceptions now offer Retry, verified with an interrupted request.

Independent quick review of the step-reader change approved correctness, UI integration, and navigation, with one saved-input link advisory. The fix preserves resolved paths; its [browser regression](../../../../../skills/task-tree/scripts/tests/test_dag_workspace_browser.py) failed before the fix and passed afterward at phone/light and desktop/dark sizes.
