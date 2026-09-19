# Reproduction UI: expand one graph from tasks to steps

The Reproduction view helps a researcher find a result, understand what produces or consumes it, and inspect why a step needs attention. The initial view collapses tasks; expanding them reveals their steps within the same dependency model. Logical and inferred edge semantics follow the [0.5 design](../../../attachments/v05-design.md). This design targets 500 steps across 50 owner tasks.

Subtree/tier filtering, task grouping, and task/step views are researcher requirements. The scale target is a planning acceptance budget. This document is the implementation contract referenced by the [owning task](../task.md).

## Interaction contract

### One scope applies to the overview, graph, and search

- **Subtrees:** a searchable tree picker supports one or more roots. A root includes its own task and every descendant, including steps owned by a non-leaf task. Selected roots form a union; selecting an ancestor subsumes selected descendants. The default is the whole project. Display task titles with paths to distinguish repeated names.
- **Tiers:** `All tiers`, `required`, and `on-demand`; default `All tiers`. The tier condition intersects the subtree union. Filtering never changes a task's registered tier.
- **Feedback:** visible scope chips, a clear-filters action, and a matching-step count. An empty match offers filter recovery and differs from an empty task tree or a graph that failed to load. No reproduction declarations still leaves the logical task graph available. Report graph-loading errors even when the affected task falls outside the visible scope; keep long findings expandable.
- **Search:** match step names, owner titles/paths, and logical output paths within scope. Show the matching output when it found the step. A separate `Search whole project` action can locate an out-of-scope result; opening it visibly widens the necessary filters and creates a reversible navigation entry.
- **Selection after filtering:** an explicit filter change clears a selection or tracing anchor that no longer matches and returns the graph to Scope mode. A surviving selection remains. Clear manually revealed boundary context when the scope changes.

### Task and step views expand the same graph

Show compact task containers with effective dependency arrows, task titles, paths for disambiguation, step counts, and state distributions. Inferred and logical connections share one graph; edge inspection reveals their evidence. Logical-only tasks remain visible. A parent may contain its own steps and child tasks; adding a child does not change the owner's steps or their freshness.

Expand/collapse controls support task-level, step-level, and mixed views. A collapsed group's count includes each descendant once. Logical-only edges stay at task boundaries; expanded file edges name actual producers, consumers, and connecting files. Expansion must not fabricate step edges or imply a task has a single freshness state.

`Explore` scopes to the chosen subtree while retaining the tier filter. Task-page and search links reveal the selected step and its owner container. Browser Back restores scope and expansion. Preserve group order and geometry on status-only refreshes.

Invalid task cycles remain inspectable with their original evidence and declaration links. Step acyclicity cannot excuse a cycle between disjoint task groups. Internal parent-owned-step/child-step connections are not parent self-dependencies.

### A bounded graph viewport supports both browsing and tracing

The desktop layout keeps controls and inspection outside the pannable graph:

```text
Reproduction                 [Subtrees: Analysis] [Tier: required]
[Search steps or outputs...]  [Tasks | Steps]     [Clear filters]
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

Provide drag/touch panning, zoom controls, Fit, and Center selected. Scope changes fit the new view once. Selection, inspection, and status refresh never auto-fit. Zooming out simplifies secondary labels; it does not shrink the inspector or its readable text. Full names remain available through selection and the searchable step list. Selection stays visible when inspection changes the available canvas width.

### Filtering preserves dependency meaning

**Matching steps and dependency context are distinct.** With All tiers, task view includes scoped tasks without reproduction sections; narrower tiers keep logical-only prerequisite tasks as labeled context. Filters never suppress global graph errors.  Scope mode shows matching steps plus compact boundary markers for direct edges to hidden steps. Each marker exposes direction, hidden neighbor count, and the reasons neighbors are hidden (subtree, tier, or focus). Opening it lists the actual adjacent steps and connecting files; revealing a neighbor adds labeled context without silently changing the filters.

Tracing follows real step edges across subtree and tier boundaries. Steps outside the filters remain labeled `Outside scope` and are counted separately from matches. A tier filter must not remove an intermediate producer from a traced chain.

Every drawn step-to-step edge corresponds to a declared/inferred edge from the payload. Never replace a path through hidden steps with an unlabeled direct edge. External boundary files are labeled as inputs, not fabricated executable steps. The inspector lists external inputs with their available state evidence.

Use compact task containers with readable initial zoom; Fit remains an explicit whole-graph overview. Expanded containers show real step-level dependencies, while collapsed connections show the effective task DAG. Use directional arrows and expose edge provenance. Route long edges around node boxes, including a first-to-last shortcut across a chain. Disconnected components remain distinct. Stable identifiers and deterministic tie-breaking preserve layout for unchanged topology.

### Inspection stays beside the selected step

The inspector contains state and reason, command, owner-task link, tier and kind, deps, outs and sidecars, last duration/time, and log tail. Reviewed acceptance reads as fresh; its reason/evidence is available here without an extra status or mandatory badge, and the last-run time continues to name an actual execution. Immediate producer/consumer lists navigate to actual steps; connecting files explain each relationship. Commands and logs wrap or scroll inside the pane without stretching the canvas.

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
| A-to-B-to-A between disjoint task groups, mixed-source cycle, and valid parent setup → child → parent report | Invalid group cycles show actionable errors; valid internal edges remain navigable without self-dependencies |
| Chain with a shortcut edge and mixed expansion | Arrow direction is unambiguous; edges avoid intervening cards; expansion preserves actual step/file evidence |
| Existing small fixture, disconnected graph, wide fan-out/fan-in, deep chain | No overlapping node boxes, lost components, or inaccessible steps; every edge retains its source relationship |
| 500 steps, 50 tasks, and approximately 1,500 edges | Overview, search, scope changes, trace, and full-graph opt-in remain usable; once payloads are loaded, search/filter feedback targets 200 ms and graph layout settles within 2 s on the recorded desktop browser/machine |
| Select a distant step, inspect its log, receive a status update, leave and return | Selection, focus, viewport, filters, and inspector remain coherent; status-only updates do not change node positions |
| Copy a scoped step link, reload, use Back/Forward, switch worktrees, delete a selected step/subtree | State restores in the correct worktree; removed targets are explained; task/attachment routing remains valid |
| Light/dark themes at desktop, tablet, and 390 px phone width | Graph and inspection remain usable without page-level horizontal overflow; keyboard and touch complete search-to-step-to-declaration navigation |
| Offline export with networking disabled; empty and malformed declarations | Local interactions work from the embedded snapshot; empty/filter/error states remain distinct and errors cannot be hidden by scope |

Measure the performance targets after data loading, using reproducible fixtures and recording the environment and repeated-run timing. They are acceptance budgets, not claims about current performance. Graph sizes above the target keep overview/search available and report any rendering limit explicitly; never truncate silently.

## Implementation guidance

The [client](../../../../../skills/task-tree/scripts/templates/dashboard.js#L895) already loads the whole graph and status pair. Derive scope, adjacency, search, and counts from that shared snapshot. Keep the pure graph projection separate from UI state and rendering so fixtures can verify relationships without a browser.

The layout mechanism remains an implementation choice, judged against the geometry and scale checks above. If a library is needed, its local vendoring and offline embedding follow the [existing asset contract](../../../../../skills/task-tree/scripts/vendor/README.md); no framework migration is required by this design. A minimap and persistent manual node positions are deferred until navigation evidence justifies them.
