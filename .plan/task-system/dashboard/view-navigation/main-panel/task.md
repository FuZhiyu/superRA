---
title: "Main panel — active-node card + children DAG"
status: implemented
depends_on:
  - server-partials
  - routing-shell
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Fill the main panel: the active node's own content, then its direct children as a clickable DAG. Load `frontend-design:frontend-design` before touching markup or CSS. Live server only; edit `skills/task-system/scripts/templates/base.html`. Build on `routing-shell` (the `#active-node` / `#children-dag` regions and `setActive`) and `server-partials` (the `/node/{path}` route). This task and `sidebar-nav` both edit `base.html`, so they run serially — coordinate edits to shared functions.

**Active-node card — implement `loadActiveNode(path)`** (the stub from `routing-shell`): fetch `GET /node/{path}` into `#active-node`, then render its markdown sections and load comments by reusing the existing pipeline unchanged — `renderMarkdown` ([`base.html:679`](../../../../../skills/task-system/scripts/templates/base.html#L679)), the section render-on-reveal logic from `expandTaskDetails` ([`base.html:1105`](../../../../../skills/task-system/scripts/templates/base.html#L1105)), and `loadComments(path)`. Sections default to **expanded** in the card (this is the focused detail view). Show the task's title + status badge at the top of the panel (the breadcrumb already shows the path).

**Children DAG — implement `loadChildrenDag(path)`** (the stub from `routing-shell`):

- **Leaf** active node → render nothing in `#children-dag` (card only).
- **Children with at least one inter-child dependency** (`Task.has_child_dependency_graph()` is true) → fetch the existing `GET /dag?root={path}` ([`plan_dashboard.py:481`](../../../../../skills/task-system/scripts/plan_dashboard.py#L481)) — which already returns exactly the direct-children sibling graph — run `mermaid.run`, then call the existing `wireDagNodeClicks(container)` ([`base.html:943`](../../../../../skills/task-system/scripts/templates/base.html#L943)). **Change its terminal action from `revealTask(path)` to `setActive(path)`** so clicking a child descends.
- **Children with no inter-dependencies** → render a plain clickable child-card grid (slug + title + status badge per child), each calling `setActive(childPath)` — cheaper and clearer than an edgeless mermaid graph.
- Render the DAG **after** the card paints so the detail is interactive immediately; cache rendered output keyed by `(path, child-status-signature)` and skip re-render when navigating back to an unchanged node.

**Remove the superseded code.** Delete the global DAG tab path `renderDagView()` ([`base.html:917`](../../../../../skills/task-system/scripts/templates/base.html#L917)) and the inline per-node `toggleDagPanel()` accordion ([`base.html` ~975]) — both are replaced by the children-DAG region. Leave `dag.html`, the `node_id↔path` map, and `wireDagNodeClicks` (reused). The `revealTask`→`setActive` alias from `routing-shell` means Kanban cards now open the workspace at the clicked task; confirm that end-to-end here.

## Validation

- Selecting a node (sidebar row, breadcrumb, child node, Kanban card, or deep-link) renders its sections (markdown rendered, comments loaded) in `#active-node` and, below, its direct-children DAG; clicking a child node descends (active = child, hash + breadcrumb + sidebar update).
- A leaf node shows only the card, no DAG region. A parent whose children have no dependencies shows a clickable child-card grid; a parent with inter-child edges shows the mermaid graph, status-colored, in both themes.
- Comment gutters and markdown (links rewritten to `vscode://`, images via `/files/`) work in the card exactly as in the old tree body.
- Navigating back to a previously viewed node does not re-run mermaid (cache hit); a child whose status changed does re-render.
- No references remain to `renderDagView` or `toggleDagPanel`; `node --check` on the main script passes; live-server drive (HTTP + headless browser where available) shows the full drill loop with no console errors. `pytest skills/task-system/scripts/test_task_system.py` still passes.

## Results

The main panel now renders: `loadActiveNode` and `loadChildrenDag` are implemented in [`base.html`](../../../../../skills/task-system/scripts/templates/base.html), the empty `#active-node` / `#children-dag` containers fill on every navigation, and the superseded global-DAG / inline-accordion code is gone. All work is on the live server template; the static `generate` path is untouched. Note: source line numbers in the Objective drifted after `sidebar-nav`/`routing-shell` landed (`renderDagView` and `expandTaskDetails` were already deleted in `routing-shell`); the work targeted the functions by name, not by the stale line cites.

**Active-node card — `loadActiveNode(path)`.** Fetches the body-only `GET /node/<path>` partial and wraps it in a real `<div class="task-node active-node-body" data-path="<path>">` inside `#active-node`. That wrapper is the key to reuse: `toggleSection`, `loadComments`, `updateSectionBadges`, and the comment forms all resolve their task context via `.task-node[data-path]`, so the entire existing section + comment pipeline consumes the partial byte-for-byte as the old tree body did — no fork of that code. A header (`.active-node-head`) shows the task's `slug · title` (title via `textContent`, no injection) plus its status badge; the breadcrumb carries the path. Sections default to **expanded**: [`revealCardSection`](../../../../../skills/task-system/scripts/templates/base.html#L1364) mirrors `toggleSection`'s expand branch (add `.open`, `uncapAfterTransition`, lazy-render the `text/x-markdown` payload via the unchanged `renderMarkdown`) without the click event, scoped to `:scope > [data-section]` so the nested `.commentable-block`s that `renderMarkdown` injects are not re-revealed. A monotonic `_token` guard drops a stale fetch that lands after the user has navigated on.

**Status-badge timing.** The badge status is read off the sidebar row's `data-status` ([`navRowStatus`](../../../../../skills/task-system/scripts/templates/base.html#L1390)). On a fresh deep descent the sidebar's ancestor-walk (`updateSidebar`, started in the same `setActive` tick) can outlast the `/node` fetch, so the row may not exist yet. The status read is moved after the `await`, and [`patchCardBadgeWhenReady`](../../../../../skills/task-system/scripts/templates/base.html#L1398) polls briefly (≤10×60ms, token-guarded) to inject the badge once the row materializes. Verified the badge lands on deep-link, DAG-node-click, child-card-click, and breadcrumb descents.

**Children DAG — `loadChildrenDag(path)`.** A single `GET /dag?root=<path>` fetch drives all three cases by parsing the fragment's authoritative `data-node-paths` map (child set), its `style <id> fill:#<color>` lines (per-child status, via the fixed color→status map mirroring `dag.html`), and the presence of `-->` edges:
- **Leaf** (no child nodes) → `#children-dag` cleared, card-only.
- **Inter-child deps** (`edges > 0`) → inject the mermaid fragment, `await mermaid.run`, then `wireDagNodeClicks`.
- **No deps** (`edges === 0`) → a clickable `.child-card` grid (slug + title + status badge per child) built by [`buildChildGrid`](../../../../../skills/task-system/scripts/templates/base.html), titles/slugs escaped, descent via a single delegated `onChildGridClick` → `setActive`.

The **root** is special-cased: `GET /dag?root=` with an empty root returns the *global* graph, not root's direct children, and the root never has inter-child deps — so root's children are read straight off the always-present top-level nav rows ([`rootChildrenFromNav`](../../../../../skills/task-system/scripts/templates/base.html)) and rendered as a grid. Output is cached in `_childrenDagCache` keyed by `path` with a `(child-path:status|…)` signature: revisiting an unchanged node restores the cached HTML (and re-wires clicks) instead of re-running mermaid; a child whose status changed busts the signature and forces a re-render. Confirmed a back-navigation to a mermaid node yields exactly one SVG (cache hit, no duplicate render).

**`wireDagNodeClicks` terminal action** changed from `revealTask(path)` to `setActive(path)` ([`base.html:1160`](../../../../../skills/task-system/scripts/templates/base.html#L1160)) so a DAG child click descends directly. The `revealTask`/`showTreeAndExpand` aliases (`showView('workspace'); setActive(path)`) stay for the Kanban cards; verified a Kanban card opens the workspace at the clicked task end-to-end.

**Comment resolver disambiguation.** Both the sidebar nav row and the active-node card carry `.task-node[data-path]` for the active task, with the sidebar row first in the DOM, so the old global `document.querySelector('.task-node[data-path=…]')` in `loadComments`/`updateSectionBadges`/the `task:` SSE handler would resolve to the body-free nav row. Added [`commentTaskNode(taskPath)`](../../../../../skills/task-system/scripts/templates/base.html#L2261) — prefers `#active-node .task-node[data-path]`, falls back to the global match — and pointed those three call sites at it, so comments land where the commentable blocks live (the card). The comment-form/edit helpers use `block.closest('.task-node')` and were already card-local.

**Removed superseded code.** Deleted `toggleDagPanel` (the inline per-subtree DAG accordion) and its `.dag-panel*` CSS; `renderDagView` was already removed by `routing-shell`. `dag.html`, the `node_id↔path` map, and `wireDagNodeClicks` are retained (reused by the children DAG). Updated `dag.html`'s stale header comment (it described the old `revealTask`/global-tab model; now documents `setActive` descent + the per-node `GET /dag?root=<path>` role). No references to `renderDagView`, `toggleDagPanel`, `dag-panel`, or `dagRoot` remain in the templates.

**New CSS** (editorial palette, theme-aware): `.active-node-head`/`.active-node-title`, `.children-dag` spacing (`:empty` collapses for leaves), and the `.child-grid`/`.child-card` cards (paper-card bg, terracotta accent slug, hover lift + accent border). Verified the grid background resolves to the dark `--bg-card` token under the dark theme.

**Verification.** Headless-Chromium drive of the live server (real `.plan`) across the full drill loop — root grid (3 cards), deep-link to an inter-dep parent (6-node mermaid), DAG-node descent, no-dep parent grid (7 cards), child-card descent, leaf (card-only, empty DAG region), breadcrumb ascent (13-node mermaid), cache revisit (single SVG), Kanban-card→workspace — **0 console errors/warnings** in every scenario, exactly one `.nav-active` row, `vscode://` link rewrite confirmed (5/5), and the dark theme verified for both mermaid and grid. A scripted comment post + `loadComments` rendered the thread under the correct block in the card with the section badge at "1" (test `comments.yaml` removed afterward). `node --check` on the rendered main script passes; `/`, `/nav`, `/kanban`, `/dag`, `/tree`, `/node/<path>` all 200 and `/node/<missing>` 404. `pytest test_task_system.py test_dashboard.py` — **209 passed** (152 + 57); no test changes needed.
