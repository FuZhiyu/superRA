---
title: Unified Tree and Graph Workspace
status: in-progress
depends_on: []
---

## Objective

Unify Tree and Graph navigation around one search, task/status filter, selection, and task reader. Remove Board. Tree prioritizes task reading with a hideable sidebar; Graph prioritizes the map with hideable details.

- Give the graph most of the viewport. Use the dashboard's existing typography, warm neutral surfaces, borders, spacing, and accent palette; keep controls compact and clearly grouped, with secondary options and diagnostic details progressively disclosed.
- Show the task preview by default when the viewport has useful space: beside the graph in wide windows, below it in narrow, tall windows. Use a real layout split rather than an overlay. Provide an obvious hide/show control consistent with the tree sidebar and a draggable, keyboard-accessible divider for width or height. Remember explicit visibility and preferred dimensions; window resizing must not override a manual hide. Keep graph navigation and selection stable through resizing, closing, reopening, orientation changes, and full-width reading.
- Support two-finger touchpad scrolling in both axes to pan and pinch to zoom around the pointer, including Safari gestures and Chromium control-wheel events. Keep drag panning, accessible zoom buttons, fit, and keyboard recovery; prevent unintended page zoom or scroll while handling canvas gestures.
- Use one project map with an always-visible Project overview action, global search, and local task chevrons. Overview collapses all groups and fits the map; selection preserves graph contents and viewport. Folding a selected step's ancestor preserves selection and details, with a Contains selected step indicator and Show in graph recovery.
- Provide one shared Filter panel with task checkboxes and status choices, visible active-filter summaries, and Clear filters recovery. Hidden tasks hide descendants; status matches retain ancestor context. Search opens tasks, steps, and files without changing filters. Switching layouts preserves selection, reader content/scroll, and filter state; each layout retains its own expansion and pane preference. Remove Board UI and runtime/export support.
- Remove trace modes, reproduction-tier filters, scope controls, and expansion-depth controls. Normalize legacy links to the full map while preserving meaningful task/step selection and expansion. Keep URL history, worktree isolation, and offline navigation.
- Support relative Markdown step links using `task.md#step-<name>` and same-task `#step-<name>`, with the declaration's existing name as identity. Reveal/select the exact step and validate its owner; report broken references. Dashboard sharing uses `?step=<name>`, and rendered step rows expose the anchor.
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
tier: on-demand
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

The prior map simplification and step-link support are implemented. The approved revision now unifies Tree/Graph controls and selection, adds explicit task/status filtering, and removes Board. Implementation and fresh verification are in progress.
