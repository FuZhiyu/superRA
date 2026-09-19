# Reproduction UI: scope first, then trace a result

The Reproduction view helps a researcher find a result, understand what produces or consumes it, and inspect why a step needs attention. The initial view summarizes tasks; a step graph opens within the chosen scope. This design targets 500 steps across 50 owner tasks.

Subtree and tier filtering are researcher requirements. Task-overview entry and the scale target are recommended planning defaults, not recorded researcher selections. This document is the implementation contract referenced by the [owning task](../task.md).

## Interaction contract

### One scope applies to the overview, graph, and search

- **Subtrees:** a searchable tree picker supports one or more roots. A root includes its own task and every descendant, including steps owned by a non-leaf task. Selected roots form a union; selecting an ancestor subsumes selected descendants. The default is the whole project. Display task titles with paths to distinguish repeated names.
- **Tiers:** `All tiers`, `required`, and `on-demand`; default `All tiers`. The tier condition intersects the subtree union. Filtering never changes a task's registered tier.
- **Feedback:** visible scope chips, a clear-filters action, and a matching-step count. An empty match offers filter recovery and differs from an undeclared graph or a graph that failed to load. Report graph-loading errors even when the affected task falls outside the visible scope; keep long findings expandable.
- **Search:** match step names, owner titles/paths, and logical output paths within scope. Show the matching output when it found the step. A separate `Search whole project` action can locate an out-of-scope result; opening it visibly widens the necessary filters and creates a reversible navigation entry.
- **Selection after filtering:** an explicit filter change clears a selection or tracing anchor that no longer matches and returns the graph to Scope mode. A surviving selection remains. Clear manually revealed boundary context when the scope changes.

### The overview summarizes tasks without inventing a task DAG

Show a compact hierarchy of tasks with matching steps, retaining ancestors as navigation containers. Rows expose matching-step counts and state counts; collapsed parents count each descendant step once. Preserve tree order while live state counts change. No single task-level freshness label replaces the distribution of step states.

`Explore` opens the row's subtree in the graph, retaining the tier filter. The breadcrumb and Back restore the previous scope. `View graph` opens all steps matching the current scope. A task-page step link opens that step directly in the graph and its inspector; an out-of-scope target uses the same visible, reversible filter widening as whole-project search.

Task summaries carry no dependency arrows: an acyclic step sequence can alternate owners A, B, A, creating A-to-B and B-to-A task connections. The step graph is the authoritative dependency view.

### A bounded graph viewport supports both browsing and tracing

The desktop layout keeps controls and inspection outside the pannable graph:

```text
Reproduction                 [Subtrees: Analysis] [Tier: required]
[Search steps or outputs...]  [Overview | Graph]  [Clear filters]
Project / Analysis           24 matching steps
----------------------------------------------------------------
[Scope | Nearby | Upstream | Downstream | Both]    | Step details
                                                  | selected name
   outside-scope input --> [selected step] --> ...  | state + reason
                                                  | command / files
   [Zoom -] [100%] [Zoom +] [Fit] [Center selected] | upstream / downstream
----------------------------------------------------------------
```

These are layout regions, not fixed pixel dimensions. On narrow screens, the inspector becomes a dismissible sheet with its own scroll; closing it returns focus to the selected step.

| Graph mode | Visible step set |
| --- | --- |
| Scope | All matching steps; used when opening a task/subtree or `View graph` |
| Nearby | Selected step and its immediate producers and consumers; used when opening a search result or task-page step link |
| Upstream | Selected step and all producer ancestors |
| Downstream | Selected step and all consumer descendants |
| Both | Union of upstream and downstream; excludes unrelated siblings |

Tracing modes require a selected step. Selecting a node opens its inspector and highlights its incident edges without moving nodes or recomputing the layout. `Trace from here` explicitly changes the tracing anchor; `Center selected` changes only the viewport. The tracing anchor remains named in the mode controls when selection moves elsewhere.

Provide drag/touch panning, zoom controls, Fit, and Center selected. Scope changes fit the new view once. Selection, inspection, and status refresh never auto-fit. Zooming out simplifies secondary labels; it does not shrink the inspector or its readable text. Full names remain available through selection and the searchable step list.

### Filtering preserves dependency meaning

**Matching steps and dependency context are distinct.** Scope mode shows matching steps plus compact boundary markers for direct edges to hidden steps. Each marker exposes direction, hidden neighbor count, and the reasons neighbors are hidden (subtree, tier, or focus). Opening it lists the actual adjacent steps and connecting files; revealing a neighbor adds labeled context without silently changing the filters.

Tracing follows real step edges across subtree and tier boundaries. Steps outside the filters remain labeled `Outside scope` and are counted separately from matches. A tier filter must not remove an intermediate producer from a traced chain.

Every drawn step-to-step edge corresponds to a declared/inferred edge from the payload. Never replace a path through hidden steps with an unlabeled direct edge. External boundary files are labeled as inputs, not fabricated executable steps. The inspector lists external inputs with their available state evidence.

Group steps in compact, collapsible owner-task containers with task titles and freshness counts. Large scopes start with task summaries; a selected step opens its owner. Expanded containers retain step-level dependency arrows; collapsed connections summarize ownership relationships and never imply an executable task DAG. Keep task return paths legal when the step graph is acyclic. Use directional arrows and readable initial zoom; Fit remains an explicit whole-graph overview. Route long edges around node boxes, including a first-to-last shortcut across a chain. Disconnected components remain distinct. Stable identifiers and deterministic tie-breaking preserve layout for unchanged topology.

### Inspection stays beside the selected step

The inspector contains state and reason, command, owner-task link, tier and kind, deps, outs and sidecars, last duration/time, and log tail. Immediate producer/consumer lists navigate to actual steps; connecting files explain each relationship. Commands and logs wrap or scroll inside the pane without stretching the canvas.

An `Open declaration` action returns to the existing task-page Reproduction section and comment flow. This redesign adds no graph editor, build button, or separate commenting system.

### Navigation survives updates

- Store scope, overview/graph mode, tracing anchor/mode, and selection in shareable navigation state. Browser Back/Forward restores these; pan/zoom does not create history entries. Preserve existing task/attachment links and the worktree selector.
- Keep viewport and inspector state per worktree while switching views or receiving updates. A status-only refresh changes badges/details without recomputing positions or replacing the canvas. Topology changes preserve the selected step's screen position when it survives; a removed selection closes with an explicit notice.
- Validate restored scope against the active worktree. If a selected subtree disappeared, show that condition and offer recovery; do not silently widen to the whole project. Ignore superseded asynchronous loads.
- Live mode and offline export support the same local search, scope, trace, and navigation interactions. Exported statuses remain identified as a snapshot.

### Keyboard and touch have complete navigation paths

Native controls expose search results, filter selection, step selection, related-step navigation, and inspector dismissal without pointer-only actions. Keep visible focus and return it after closing an overlay. A step list provides access when graph labels are simplified. Preserve the current state glyphs and words alongside colors; `check` remains a kind, independent of freshness. Respect reduced motion and keep touch controls large enough to use on a phone.

## Acceptance checks

| Fixture or journey | Required observation |
| --- | --- |
| Nested tasks, overlapping selected roots, repeated titles, and mixed tiers | Subtree union and tier intersection produce exact, deduplicated counts; own steps on non-leaf tasks remain selectable; similarly prefixed sibling paths do not match |
| Required result with an on-demand producer outside the selected subtree | Scope mode names the hidden dependency; upstream mode shows the complete chain with out-of-scope labels and separate counts |
| A-to-B-to-A task ownership and a chain with a shortcut edge | No invented task-cycle error; visible edge direction is unambiguous and edges avoid intervening node boxes |
| Existing small fixture, disconnected graph, wide fan-out/fan-in, deep chain | No overlapping node boxes, lost components, or inaccessible steps; every edge retains its source relationship |
| 500 steps, 50 tasks, and approximately 1,500 edges | Overview, search, scope changes, trace, and full-graph opt-in remain usable; once payloads are loaded, search/filter feedback targets 200 ms and graph layout settles within 2 s on the recorded desktop browser/machine |
| Select a distant step, inspect its log, receive a status update, leave and return | Selection, focus, viewport, filters, and inspector remain coherent; status-only updates do not change node positions |
| Copy a scoped step link, reload, use Back/Forward, switch worktrees, delete a selected step/subtree | State restores in the correct worktree; removed targets are explained; task/attachment routing remains valid |
| Light/dark themes at desktop, tablet, and 390 px phone width | Graph and inspection remain usable without page-level horizontal overflow; keyboard and touch complete search-to-step-to-declaration navigation |
| Offline export with networking disabled; empty and malformed declarations | Local interactions work from the embedded snapshot; empty/filter/error states remain distinct and errors cannot be hidden by scope |

Measure the performance targets after data loading, using reproducible fixtures and recording the environment and repeated-run timing. They are acceptance budgets, not claims about current performance. Graph sizes above the target keep overview/search available and report any rendering limit explicitly; never truncate silently.

## Implementation guidance

The [current client](../../../../../skills/task-tree/scripts/templates/dashboard.js#L895) already loads the whole graph and status pair. Derive scope, adjacency, search, and counts from that shared snapshot. Keep the pure graph projection separate from UI state and rendering so fixtures can verify relationships without a browser.

The layout mechanism remains an implementation choice, judged against the geometry and scale checks above. If a library is needed, its local vendoring and offline embedding follow the [existing asset contract](../../../../../skills/task-tree/scripts/vendor/README.md); no framework migration is required by this design. A minimap and persistent manual node positions are deferred until navigation evidence justifies them.
