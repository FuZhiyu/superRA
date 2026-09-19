---
title: Clean, Intuitive DAG Workspace
status: approved
depends_on: []
---

## Objective

Remake the DAG workspace into a clean, intuitive interface consistent with the rest of the dashboard, verified on the [Treasury dashboard](http://localhost:8996/?wt=v05-compatibility#/04-treasury-market-bound?repro=%7B%22roots%22%3A%5B%5D%2C%22view%22%3A%22graph%22%7D).

- Give the graph most of the viewport. Use the dashboard's existing typography, warm neutral surfaces, borders, spacing, and accent palette; keep controls compact and clearly grouped, with secondary options and diagnostic details progressively disclosed.
- Show the task preview by default when the viewport has useful space: beside the graph in wide windows, below it in narrow, tall windows. Use a real layout split rather than an overlay. Provide an obvious hide/show control consistent with the tree sidebar and a draggable, keyboard-accessible divider for width or height. Remember explicit visibility and preferred dimensions; window resizing must not override a manual hide. Keep graph navigation and selection stable through resizing, closing, reopening, orientation changes, and full-width reading.
- Support two-finger touchpad scrolling in both axes to pan and pinch to zoom around the pointer, including Safari gestures and Chromium control-wheel events. Keep drag panning, accessible zoom buttons, fit, and keyboard recovery; prevent unintended page zoom or scroll while handling canvas gestures.
- Offer task-specific expansion to 1, 2, 3, or all levels, starting at two levels and showing the projected card count before applying. Keep the chevron's one-level behavior; bound previously expanded descendants to the chosen depth, leave other branches and scope unchanged, and make large expansions explicit. Verify the counts and behavior on the Treasury and heterogeneity branches and nested synthetic fixtures.
- Make each dependency arrow independently traceable. Avoid shared line segments that imply a common bus, false connection, or enclosing box; provide distinct routes and readable arrowheads, with source/destination highlighting on hover and keyboard focus. Verify collapsed top-level tasks and the expanded heterogeneity branch without changing dependency semantics.
- Identify cyclic dependencies with the dashboard's existing muted rust accent and a compact accessible cycle label, keeping card surfaces neutral. Distinguish a cycle in collapsed task groups from an executable-step cycle; do not imply that aggregation alone makes execution impossible. Keep acyclic edges neutral and preserve cycle visibility during edge inspection. Use existing theme tokens rather than a competing error-red palette.
- Clearly separate disconnected dependency groups in the visible graph, and place cards without visible connections in a labeled area away from routed arrows. Derive groups from connectivity in either direction, respecting task containers and the current projection; cycles remain within their connected group. Preserve all nodes, edges, filtering, expansion, selection, and inspection. Verify multiple components, isolated tasks, filtering, nested expansion, and the research overview shown by the user.
- Let the tree sidebar grow sufficiently to read long task titles, replacing its restrictive fixed width cap with bounds based on available window space. Preserve pinned, unpinned, drawer, touch, keyboard resizing, persistence, and a usable minimum task-content area.
- Preserve graph semantics, task/step inspection, filtering, URL navigation, diagnostics visibility, comments, dark mode, and standalone export. Do not alter research data or resolve the fixture's dependency declarations.
- Verify visual hierarchy and ordinary journeys in Safari through computer control at desktop and narrow widths. Add behavioral regression checks for viewport gestures and preview state; record limitations honestly where physical gestures cannot be synthesized.

## Details

- Responsive panes: choose the side/bottom breakpoint from usable graph and reading widths; for very short windows, avoid opening a pane that leaves neither area useful. Persist manual visibility separately from automatic placement, and remember side width and bottom height separately so rotating/resizing does not destroy the preferred sizes. Match tree-sidebar divider and hide-control affordances, including accessible labels and keyboard actions. Test fresh defaults, manual hide/reopen, reload, wide/portrait/short viewports, both drag axes, bounds, and tree/DAG switching.

- The existing navigation task owns the functional model. This temporary child owns the substantial visual and interaction redesign on that same runtime surface; the general dashboard task does not own DAG-specific presentation.
- Initial Safari review at roughly 1030 × 768 showed controls wrapping to several rows, expanded diagnostic prose above the graph, and a reader consuming about one third of the workspace. The graph starts near the bottom edge. Chrome at 1372 × 768 has the same hierarchy problem.
- Suggested design: a compact heading/scope row and search/filter toolbar; graph canvas filling remaining height; grouped viewport controls on the canvas; a concise error/warning summary with collapsed details; task cards with readable titles and subdued metadata. Preserve persistent selection while making reading an explicit choice.
- Runtime owners: [dashboard.js](../../../../../skills/task-tree/scripts/templates/dashboard.js), [dashboard.css](../../../../../skills/task-tree/scripts/templates/dashboard.css), and [base.html](../../../../../skills/task-tree/scripts/templates/base.html). The reviewed navigation branch was merged into the local superra-dev checkout at 14fcd6f6; make this revision there. Port 8996 still serves the temporary navigation checkout, while the research dashboard on port 8653 loads installed plugin assets.
- Execution: Astra implementer; main agent performs thorough correctness, scope-fidelity, and visual usability review. No generated runtime assets are planned.
- Branch-expansion exploration: Treasury contains 15 active task cards and 7 steps; one/two/three/all levels show 8/16/22/22 cards. Heterogeneity contains 31 task cards and 54 steps; the same depths show 8/32/74/85 cards. Suggested control: Graph options → Expand selected branch, with depth and projected counts computed from the existing graph projection before Apply. An out-of-scope selection needs an explicit focus action; expansion must not silently widen scope. Replace the unqualified global Expand all steps action with this task-scoped control.
- Routing review: coincident horizontal and vertical tracks falsely suggest Methods → Verification and a box enclosing the four top-level research tasks. The declared top-level Treasury flow is Heterogeneity → Treasury → Reproduce manuscript exhibits. Use separate lanes and endpoint ports, minimize crossings and detours, and keep routes outside unrelated cards. Inspect cycles or aggregation-induced cycles before changing rank placement; preserve all real edges and their evidence. Dense graphs may cross, but crossings must not look like joins.
- Disconnected-group design: the research overview currently places unconnected tasks in the first rank beside the Stock-Market Construction Inputs routes, visually implying they feed downstream. Lay out connected components independently, with connected groups first and a compact isolated-card area afterward. Prefer understated headings, whitespace, and separators using existing theme tokens; avoid enclosing outlines that resemble dependency routes. Qualify isolated cards as “No connections in this view,” since filters and collapsed containers affect visible connectivity. Use component-local routing so arrows cannot pass beside an unrelated group. Keep ordering deterministic and retain viewport anchoring during expansion.

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
    cmd: uv run --with pytest --with playwright --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts/tests/test_dag_workspace_browser.py skills/task-tree/scripts/tests/test_navigation_projection.py -q
    deps:
      - skills/task-tree/scripts/tests/test_dag_workspace_browser.py
      - skills/task-tree/scripts/tests/test_navigation_projection.py
      - skills/task-tree/scripts/test_dashboard.py
      - skills/task-tree/scripts/tests/navigation_browser.py
      - skills/task-tree/scripts/plan_dashboard.py
      - skills/task-tree/scripts/templates
      - skills/task-tree/scripts/vendor
      - skills/task-tree/scripts/_artifacts.py
      - skills/task-tree/scripts/_comments.py
      - skills/task-tree/scripts/_repro.py
      - skills/task-tree/scripts/_repro_state.py
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

The DAG separates independent dependency groups into labeled bands, with cards lacking visible connections in a compact area below the routes. The task preview opens beside the graph in wide windows and below it in narrow, tall windows. Both panes occupy their own layout space, with a draggable divider and compact search, tier, tracing, and graph controls. Diagnostics, state legend, step list, scope management, and dependency evidence remain accessible through menus. Task cards show two-line titles and bounded metadata; the shared preview gives its title a full row and keeps its exit controls visible while reading long declarations. See [dashboard.js](../../../../../skills/task-tree/scripts/templates/dashboard.js), [dashboard.css](../../../../../skills/task-tree/scripts/templates/dashboard.css), and [base.html](../../../../../skills/task-tree/scripts/templates/base.html).

- **Preview placement adapts without losing preferences.** Side placement starts at 1100 px workspace width; automatic opening needs 420 px usable height beside the graph or 650 px below it. Short windows start graph-only; explicitly showing the preview uses a full reader when a useful split cannot fit, with Back to graph and Hide preview available. Manual visibility persists across reloads, Tree/DAG navigation, and worktrees. Full-reader state cannot override a later manual hide.
- **Both preview dimensions are adjustable.** The separator supports pointer/touch dragging, arrow-key nudges, Shift for larger nudges, and Home/End bounds. Side width and bottom height are remembered separately and survive viewport clamping. Selection and resizing preserve graph position; Hide preview restores the graph from full-width reading. The [command reference](../../../../../skills/task-tree/references/commands.md) describes the controls.
- **The Tree sidebar accommodates long titles.** Its default remains 280 px; the maximum leaves 360 px for task content, while drawer mode retains its 86vw bound. Pointer and keyboard resizing preserve the preferred width through narrow reloads and later expansion. Pinned, unpinned, and touch drawer behavior remain intact.
- **Branch expansion is bounded and previewed.** Graph options → Expand selected branch offers 1, 2 (default), 3, or All levels, with projected task/step card counts before Apply. A shallower choice folds deeper descendants while preserving peers, scope, preview state, and the branch header’s canvas position. Hidden or out-of-scope selections require an explicit focus action. Browser history restores expansion; Escape, Cancel, and Apply restore keyboard focus.
- **Independent graphs stay separate.** Weak connectivity is computed between projected siblings, including descendant connections. Each connected group has its own layout and routing tracks; containment adds no dependency. An expanded container with internal edges remains a dependency group. Cards whose visible subtrees have no edges appear under “No connections in this view,” in rows of up to three. Nested headings are omitted when a container has only one connected group. Expansion preserves the selected header’s position, including native canvas scroll offsets.
- **Connections remain individually traceable.** Strongly connected components retain distinct rank columns; downstream tasks keep their own ranks. Adjacent connections use short routes; longer connections use separate hierarchy tracks, column gutters, and endpoint ports. Crossing lines have a background casing. Arrowheads stay 6 px high during inspection, with at least 7 px between ports; high-degree cards reserve the needed height. All declared edges and evidence remain intact.
- **Connection inspection names both endpoints.** Hover or keyboard focus highlights the route and its source/destination cards, with a human-readable source → destination label. Enter/Space opens the evidence. Focus and cycle metadata survive unchanged-topology redraws. Cycles use the existing muted rust accent and a compact accessible label on neutral cards; labels distinguish task-group cycles from step cycles without changing validation or execution status.
- **Canvas input covers both platforms.** Two-axis wheel events pan; Chromium control-wheel and Safari gesture events zoom around the pointer. Handled events cancel native scrolling/zooming. Drag, zoom buttons, Fit, Center selected, arrow keys, `+`/`−`, `0` (fit), and `C` (center) remain available. Physical trackpad pinch cannot be synthesized by the available computer-control surface; the [browser regression](../../../../../skills/task-tree/scripts/tests/test_dag_workspace_browser.py) dispatches platform events into the production listeners and checks anchoring, cancellation, and duplicate-event suppression.
- **Verification:** the dashboard suite passed **385 tests, with 4 skipped**; the scoped interaction check passed **35 tests** (17 browser journeys and 18 projection checks). These cover wide/portrait/short defaults, manual hide/show and reload, side/bottom pointer dragging, touch dragging, keyboard bounds, retained dimensions, full-reader recovery, wider sidebar persistence, independent graph bands, isolated cards, internal DAG containers, nested escaping edges, component changes under tier/scope filters, node/edge conservation, branch anchoring, cycle ranking and downstream placement, noncoincident nested routes, dense fan-in port spacing, ancestor/descendant logical edges, endpoint focus/hover, cached cycle badges, diagnostic popup bounds, desktop-resized previews at phone width, nested branch depths/counts, unrelated expansion, trace/filter semantics, live redraws, and keyboard recovery. The four pre-existing browser checks require a bundled Playwright Chromium unavailable in this environment; the browser checks used installed Chrome, including 1440 × 900, 1372 × 768, 1030 × 768, 390 × 844, and 820 × 1180, plus short-window recovery cases. JavaScript syntax and git whitespace checks passed.
- **Scale and compatibility:** the [500-step browser journey](../../../../../skills/task-tree/scripts/tests/navigation_browser.py) passed with 51 task records and 1,494 edges, including comments through CLI round-trip, history, live status refresh, worktree isolation, legacy/removal recovery, offline export, keyboard reading, resizing, and touch panning. [Recorded results](attachments/browser/browser-results.json) identify Chrome 153.0.8010.48 on macOS arm64: repeated search, filter, and full-expansion timings remain below the navigation budgets. Research fixtures were read-only; data and declarations were unchanged.

Native Safari review confirmed the wide side preview, visible divider, Hide preview control, and unchanged graph on the research dashboard. The researcher was interacting with Safari, so the current portrait, short-window, and drag sequences are verified in Chromium rather than claimed as native Safari checks. Earlier Safari graph checks covered selection, vertical panning, selected-task focus, step evidence, full-width reading, themes, independent graph separation, and expansion/folding with header anchoring. Treasury expansion applied two levels (16 cards), All (22), then one level (8); Heterogeneity previews showed 32/74/85 cards at two/three/All levels. Native horizontal scroll calls did not produce a visible pan, and physical pinch was unavailable; those Safari gestures remain physically unverified.

![Chromium: side preview and accessible divider at desktop width](attachments/browser/dag-preview-side.png)

The [portrait preview](attachments/browser/dag-preview-bottom.png) occupies a separate bottom pane. The [wide Tree sidebar](attachments/browser/tree-wide-sidebar.png) shows a 712 px sidebar with long task titles alongside task content.

Routing verification also used the real research fixture read-only: collapsed roots, one-level Heterogeneity, fully expanded Heterogeneity, fully expanded Treasury, and the fully expanded project (342 cards, 215 displayed edges). The reviewed research snapshot contained one eight-task connected group and four isolated tasks. Geometry probes found no coincident positive-length segments and no crossings through unrelated cards in any of these views. Native Safari confirmed the initial routing and edge-evidence interaction. The corrected palette, card metadata, arrowheads, and light/dark controls were reviewed in the retained Chromium artifacts while the researcher was using Safari; these final visual details are not claimed as a separate native Safari pass.

![Chromium: two independent dependency groups above a separate area for four unconnected cards](attachments/browser/dag-routing-components.png)

The [dark component view](attachments/browser/dag-routing-components-dark.png) uses the same nine-card, three-edge fixture. Projection checks also cover internal graphs within containers, filtering, and edges that leave a lower nested band without crossing an earlier independent graph.

![Chromium: task-group cycle with distinct routes and a separate downstream task](attachments/browser/dag-routing-cycle.png)

![Chromium: acyclic fan and long connections in dark mode](attachments/browser/dag-routing-fan-dark.png)

The producer also retains [dark cycle](attachments/browser/dag-routing-cycle-dark.png) and [light fan](attachments/browser/dag-routing-fan.png) views. The small cycle fixture preserves the six root-cycle connections plus one acyclic downstream edge; the fan fixture has seven acyclic connections.

![Chromium: collapsed 500-step graph with its default side preview](attachments/browser/dag-desktop.png)

The on-demand reproduction steps above generate the retained [Chromium evidence folder](attachments/browser/) directly from the synthetic scale and routing fixtures and verify interaction behavior. No research input is consumed. Scoped build succeeded for `dashboard-dag-design-browser` and `dashboard-dag-design-interaction-check`; matching status reports both **fresh**. The updated [pytask.lock](../../../../../pytask.lock) records these runs.

Regression command:

```bash
uv run --with pytest --with playwright --with pyyaml --with fastapi --with jinja2 \
  --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest \
  skills/task-tree/scripts/test_dashboard.py \
  skills/task-tree/scripts/tests/test_navigation_projection.py \
  skills/task-tree/scripts/tests/test_dag_workspace_browser.py -q
```
