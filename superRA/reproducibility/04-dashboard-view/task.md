---
title: "Dashboard Reproduction View for Reviewing the Graph"
status: implemented
depends_on: [01-section-contract, 02-runner]
---

## Objective

Let the researcher review an agent-built graph in the dashboard and comment on it, so graph feedback flows through the task-comment loop agents already read.

- **Reproduction view** (new top-level view beside Workspace and Kanban): a layered DAG with drawn edges, nodes colored by state (`fresh`, `stale`, `missing`, `failed`, `external`, `check`), grouped by owner task with the task title as the group label, tier filter, and a legend. Clicking a node opens a detail panel: command, deps, outs, owner task link, state reason, last duration, and the log tail. Layout is deterministic for the same graph.
- **Task page:** when a task has a `## Reproduction` section, render a step table (name, state, reason, outs) above the raw YAML block and link each row to the node in the Reproduction view. The section keeps its existing comment gutter; verify that a comment on a step line round-trips through `task comment list`.
- **Data path:** `GET /api/repro/graph` and `GET /api/repro/status` serve the JSON from [01-section-contract](../01-section-contract/task.md) and [02-runner](../02-runner/task.md); state refreshes on the existing SSE reload after a build touches the lock. The standalone export embeds a snapshot of both.
- **Validation criteria:** dashboard tests cover the two routes, the export snapshot, and rendering with no registered tasks (view shows an empty state, no errors); a manual pass on a fixture graph of at least 15 steps across 4 owner tasks is recorded with a screenshot in `attachments/`. The real-graph pass belongs to [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md).

## Details

- No DAG library is vendored today; the children panel draws tiers of cards without edges ([dashboard.js §buildChildFlow](../../../skills/task-tree/scripts/templates/dashboard.js#L2252)). A hand-rolled layered layout in SVG (longest-path layering, barycenter ordering, orthogonal or bezier edges) fits ~50 nodes and avoids a vendored library; if a library is chosen instead, follow [vendor/README.md](../../../skills/task-tree/scripts/vendor/README.md).
- Route and export mechanics: [plan_dashboard.py](../../../skills/task-tree/scripts/plan_dashboard.py) `/api/children-graph` and `/export`; theme tokens in `templates/base.html`.
- Load `dataviz` guidance for the state palette and legend: states must stay distinguishable in both themes.

## Results

The dashboard has a third top-level view, **Reproduction**, over the graph [01-section-contract](../01-section-contract/task.md) defines and the freshness [02-runner](../02-runner/task.md) computes. Graph feedback goes back to agents through the `## Reproduction` section's existing comment gutter. The real-graph pass is [08-pilot-treasurygiv](../08-pilot-treasurygiv/task.md)'s.

![The Reproduction view on a 16-step fixture: swimlanes by owner task, columns by dependency depth, each step coloured by state, with the tier filter, the legend, and the graph findings above the canvas.](attachments/reproduction-view-light.png)

### What the researcher sees

- **The graph, laid out in swimlanes.** Rows are owner tasks, labelled with the task title and its path; columns are longest-path dependency depth, so every drawn edge points rightward and the pipeline reads left to right. Lanes follow the tree's own task order and both ordering passes break ties on the step name, so the same graph lays out identically every time and reordering its edges moves nothing ([dashboard.js:966](../../../skills/task-tree/scripts/templates/dashboard.js#L966)).
- **A node names its state twice** — a glyph and the state word, beside a wash and a 3px state border — and check steps carry a `✓` and a dashed edge. Clicking one opens its command, tier, deps, outs, owner-task link, state reason, last duration, and log tail ([dashboard.js:1243](../../../skills/task-tree/scripts/templates/dashboard.js#L1243)), and lights its incident edges.
- **A task page with a `## Reproduction` section gets a step table** — name, state, reason, outs — above the raw YAML, each row linking to its node in the view ([task-step-table.png](attachments/task-step-table.png)). The table is prepended after `renderMarkdown` has wrapped the section's commentable blocks, so it adds no block and the fence keeps its comment anchors ([dashboard.js:1306](../../../skills/task-tree/scripts/templates/dashboard.js#L1306)).
- **Graph findings sit above the canvas.** Not in `## Objective`, but a graph that failed to parse is missing steps, and letting a researcher review it without saying so would mislead.
- **Empty state:** a tree that declares no section shows what to add and the command that reports it, with no canvas and no console error.

### Two read-only routes

[`/api/repro/graph`](../../../skills/task-tree/scripts/plan_dashboard.py#L1428) and [`/api/repro/status`](../../../skills/task-tree/scripts/plan_dashboard.py#L1437) serve `graph_to_dict` and `compute_status(...).to_dict()` unchanged, off the event loop.

- **The client fetches `?tier=all` once and filters tiers in the browser**, so the tier control costs no request and the standalone export embeds one snapshot per route that serves every tier the exported view can select.
- **The status payload carries a per-step `log_tail`**, the one dashboard-local addition, so the detail panel needs no third route and the export snapshot is complete. It is read by step name rather than by the path the on-disk run record carries, and bounded to the last 64 KiB — a build step's stdout can run to megabytes ([plan_dashboard.py:3081](../../../skills/task-tree/scripts/plan_dashboard.py#L3081)).
- **Neither route writes to the project.** `.superra-repro/` and its `.gitignore` entry stay `superra repro`'s to create, so the dashboard leaves a never-built tree untouched.
- **Neither needs pytask**, and without `tomllib` the status payload names the reason in `unavailable` and the view reads every step as `unknown` off the graph.

### Live refresh reaches the lock

A build rewrites `pytask.lock` at the project root, outside the watched plan root, so the per-worktree watcher adds that one file when it exists and broadcasts `repro-updated` ([plan_dashboard.py:575](../../../skills/task-tree/scripts/plan_dashboard.py#L575)). Verified end to end: with the view open, `superra repro build` in another process moved `fama-macbeth` from `stale` to `fresh` with no page reload. A tree that has never built has no lock to watch and no freshness to push; the view re-fetches on open, on `Refresh`, and on any task edit.

### The state palette is a status scale, not a series palette

Five states plus the check kind, each a wash (`--rp-*`) with an ink (`--rp-*-t`) carrying the border and the glyph; the node's own label stays `--text` so it reads at full contrast whatever the state ([dashboard.css:50](../../../skills/task-tree/scripts/templates/dashboard.css#L50)).

Reusing the task-status `--st-*` pairs was the first attempt and failed measurement: `--st-rev-t` against `--st-impl-t` is ΔE 2.3 deuteranopic, and `--st-post-t` against `--st-ns-t` is ΔE 6.0 to full colour vision, both under `dataviz`'s floors. The shipped inks were re-stepped against each theme's own `--bg` and validated with `dataviz/scripts/validate_palette.js --pairs all` over the four chromatic states:

| Check | Light | Dark |
|---|---|---|
| Lightness band | PASS | FAIL, by the trade below |
| Chroma floor | PASS | PASS |
| Normal-vision floor (≥15) | PASS, worst 16.4 | PASS, worst 16.0 |
| CVD separation (≥8 target, ≥6 floor) | WARN, worst 7.3 | WARN, worst 7.5 |
| Contrast vs surface (≥3:1) | PASS | PASS |

Both non-PASS results are deliberate. The dark inks sit above the dark mark band because they double as the glyph's colour on a dark wash, so they must clear text contrast, not only mark contrast. The CVD warn band — `stale` against `fresh` at 7.3 protanopic in light, `failed` against `fresh` at 7.5 deuteranopic in dark — is what `dataviz` licenses for a status scale that ships a glyph and a label, which is why every node, legend row, and table cell spells the state out. The neutral grey `missing` stays out of the chromatic set by design: "never built" is the absence of a state.

### Three judgment calls

- **`check` is a kind, not a sixth state.** `## Objective` lists it among the states, but a check step still has one of the five freshnesses and colouring by kind would erase it. Check steps keep their state colour and take a dashed border, a `✓`, and their own legend row, so all six items stay distinguishable.
- **A comment anchors to the fenced block, not to a step line.** The comment layer anchors `(section, block index)` and the section body is exactly one fence, so a comment on a step lands on the whole block. Verified round-tripping: a comment posted through the gutter came back from `superra task comment list 03-estimation` anchored to `Reproduction`, block 0, with the step lines as its block.
- **A full reload restores the view it interrupted.** `onFullReload` ends in `setActive`, which forces Workspace; the restore is written for any non-Workspace view rather than for Reproduction alone, since the asymmetry would be a latent bug. Kanban gains the same fix.

### Validation

24 tests from [test_dashboard.py:6637](../../../skills/task-tree/scripts/test_dashboard.py#L6637); the suite is 964 passed / 28 skipped, up from the 940 / 28 baseline.

Coverage follows the objective's list — both routes, the export snapshot, and the empty state — plus the tier filter and its 400, the `unavailable` degradation, the bounded log tail, the read-only invariant, the lock watch and its existence guard, and the layout under node (columns, lanes, stacking, determinism under reordered edges, cycles, and edges to filtered-out steps). Reverting any of the log-tail enrichment, the lock-existence guard, the export fragments, or the read-only invariant reddens its tests.

The manual pass ran on a 16-step, 4-owner-task fixture built by [repro_fixture.py](attachments/repro_fixture.py), driven into all five states plus check steps at once:

```bash
python3 attachments/repro_fixture.py <dir> --cli skills/task-tree/scripts/repro_run.py
superra dashboard --root <dir>/superRA --port 8996 --no-open
```

Recorded in [reproduction-view-light.png](attachments/reproduction-view-light.png), [reproduction-view-dark.png](attachments/reproduction-view-dark.png) (a selected node with its detail panel and log tail), and [task-step-table.png](attachments/task-step-table.png). Also exercised by hand: the standalone export rendering all 16 nodes from `file://` with the network blocked, the empty state, and the layout at 1280px and 430px, each with a clean console.
