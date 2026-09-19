---
title: Clean, Intuitive DAG Workspace
status: not-started
depends_on: []
---

## Objective

Remake the DAG workspace into a clean, intuitive interface consistent with the rest of the dashboard, verified on the [Treasury dashboard](http://localhost:8996/?wt=v05-compatibility#/04-treasury-market-bound?repro=%7B%22roots%22%3A%5B%5D%2C%22view%22%3A%22graph%22%7D).

- Give the graph most of the viewport. Use the dashboard's existing typography, warm neutral surfaces, borders, spacing, and accent palette; keep controls compact and clearly grouped, with secondary options and diagnostic details progressively disclosed.
- Hide the task preview on initial DAG entry, including existing deep links. Provide an obvious toggle and close action; selection, expansion, and graph navigation must work while it is hidden, and opening it must show the selected task without losing graph position.
- Support two-finger touchpad scrolling in both axes to pan and pinch to zoom around the pointer, including Safari gestures and Chromium control-wheel events. Keep drag panning, accessible zoom buttons, fit, and keyboard recovery; prevent unintended page zoom or scroll while handling canvas gestures.
- Offer task-specific expansion to 1, 2, 3, or all levels, starting at two levels and showing the projected card count before applying. Keep the chevron's one-level behavior; bound previously expanded descendants to the chosen depth, leave other branches and scope unchanged, and make large expansions explicit. Verify the counts and behavior on the Treasury and heterogeneity branches and nested synthetic fixtures.
- Preserve graph semantics, task/step inspection, filtering, URL navigation, diagnostics visibility, comments, dark mode, and standalone export. Do not alter research data or resolve the fixture's dependency declarations.
- Verify visual hierarchy and ordinary journeys in Safari through computer control at desktop and narrow widths. Add behavioral regression checks for viewport gestures and preview state; record limitations honestly where physical gestures cannot be synthesized.

## Details

- The existing navigation task owns the functional model. This temporary child owns the substantial visual and interaction redesign on that same runtime surface; the general dashboard task does not own DAG-specific presentation.
- Initial Safari review at roughly 1030 × 768 showed controls wrapping to several rows, expanded diagnostic prose above the graph, and a reader consuming about one third of the workspace. The graph starts near the bottom edge. Chrome at 1372 × 768 has the same hierarchy problem.
- Suggested design: a compact heading/scope row and search/filter toolbar; graph canvas filling remaining height; grouped viewport controls on the canvas; a concise error/warning summary with collapsed details; task cards with readable titles and subdued metadata. Preserve persistent selection while making reading an explicit choice.
- Runtime owners: [dashboard.js](../../../../../skills/task-tree/scripts/templates/dashboard.js), [dashboard.css](../../../../../skills/task-tree/scripts/templates/dashboard.css), and [base.html](../../../../../skills/task-tree/scripts/templates/base.html). The existing v05-navigation checkout contains the implementation served by port 8996; the parent checkout has older UI code.
- Execution: Astra implementer; main agent performs thorough correctness, scope-fidelity, and visual usability review. No generated runtime assets are planned.
- Branch-expansion exploration: Treasury contains 15 active task cards and 7 steps; one/two/three/all levels show 8/16/22/22 cards. Heterogeneity contains 31 task cards and 54 steps; the same depths show 8/32/74/85 cards. Suggested control: Graph options → Expand selected branch, with depth and projected counts computed from the existing graph projection before Apply. An out-of-scope selection needs an explicit focus action; expansion must not silently widen scope. Replace the unqualified global Expand all steps action with this task-scoped control.

## Results
