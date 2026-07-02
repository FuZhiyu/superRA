---
title: "Fix Sidebar Focus on Initial Deep-Link Load"
status: approved
depends_on: []
---

## Objective

When the dashboard is opened at a task URL on a fresh load (e.g. pasting/clicking `http://localhost:<port>/#/<deep/task/path>` in a new tab), the left sidebar must **reveal and highlight** that task's row — expand its ancestors, mark it active, and scroll it into a visible position. Today the target row is not brought into focus on initial deep-link load.

**Reproduce first, then fix the confirmed failure.** Serve the dashboard against this worktree's `superRA/` tree, open a deep-link URL to a **depth ≥3** task in a fresh tab, and observe what actually fails — is the row un-highlighted, or highlighted-but-not-scrolled-into-view? Fix that specific failure; do not fix by hypothesis.

**Success criteria:**

- Opening a deep-link URL to a deep (≥3 levels) task in a fresh tab: the target row is expanded, carries `.nav-active` + `aria-selected`, and is scrolled to a clearly visible position (not hidden under the sticky sidebar chrome, not off-screen).
- The same holds for a shallow (top-level) task and for the root.
- In-app clicks and back/forward (`popstate`) navigation continue to reveal/highlight correctly (no regression).
- Verified on the real rendered page (inspect the DOM for `.nav-active`/`aria-selected` and confirm the row is visibly scrolled to), per the "verify the real user path for UI" discipline — not only a unit assertion.

## Planner Guidance

Investigation of the current mechanism (in `skills/task-tree/scripts/templates/base.html`) — use as priors, confirm against the live repro:

- **Boot order is already race-safe.** `DOMContentLoaded` (~4981) does `await loadNavTree()` (~4986) *before* `initRouter()` (~4987), and `updateSidebar` (~3564) awaits the ancestor walk (`expandNavNode` per segment, ~3579-3594) before highlighting. So the "rows don't exist yet" race is guarded; the highlight/expand logic itself looks correct. Do not assume a timing race without reproducing one.
- **Most probable real culprit — reveal/scroll:** `row.scrollIntoView({ block: 'nearest' })` in a `requestAnimationFrame` (~3604-3606). `'nearest'` is a no-op when the browser judges the row already minimally visible, and it doesn't account for the sticky sidebar header/toolbar or the `#nav-tree` scroll container — so on a fresh tall tree the highlighted row can stay off-screen or occluded. If the repro shows "highlighted but not scrolled," fix the scroll (e.g. a reveal that accounts for the scroll container / sticky chrome, or forcing a non-`nearest` reveal on initial load) rather than touching the highlight path.
- **Secondary suspects** (only if the repro points there): a silent `/nav/<path>` lazy-load fetch failure makes the ancestor walk `break` and then `if (!target) return` bails with no highlight (~3582/3588); and `navNodeId` slug collisions (`/`→`-`, ~3439) could resolve the wrong row.

Keep the fix surgical and confined to the initial-load reveal; preserve the existing click / `popstate` / search-open paths, which already work because their ancestors are present in the DOM.

## Results

**Reproduced first.** Served this worktree's `superRA/` tree on a live dashboard (port 8971) and opened deep-link URLs in fresh Chromium contexts (Playwright), probing the target row's `.nav-active`/`aria-selected` state and its bounding rect vs. the `#nav-tree` scroll container:

- Deep (`task-tree/codex-task-hooks/04-docs-tests-and-compat`) and shallow (`task-tree`) targets were correctly highlighted (`.nav-active` + `aria-selected="true"`) but had a **zero-size bounding rect** (`offsetParent === null`) — not "highlighted-but-not-scrolled", but **highlighted-yet-not-laid-out**.
- Walking the ancestor chain showed why: the top node (`path=""`, the root/umbrella container, `navNodeId('')` → `task-root`) was **collapsed** (`toggle` not `expanded`, its `.task-children` `display:none`), so every top-level task and everything below it was hidden. The intermediate ancestors (`task-tree`, `codex-task-hooks`) were expanded but had `offsetHeight:0` because their common root ancestor was `display:none`. Root (`path=""` target) worked because the root's own row sits outside that collapsed children container.

**Root cause.** `updateSidebar`'s ancestor walk ([base.html:3595-3600](../../../skills/task-tree/scripts/templates/base.html#L3595)) accumulates ancestors from `segs[0]` upward, so it expands the *named* path-segment ancestors but never the root container (`path=""`), which is named by no segment. For a top-level target (`segs.length === 1`) the loop body never runs at all, leaving the root collapsed and even that row hidden. The scroll (`scrollIntoView({block:'nearest'})`) — the planner's flagged prime suspect — was never the culprit: it can't reveal a row inside a `display:none` subtree.

**Fix.** Expand the root/umbrella container before the segment walk ([base.html:3591-3597](../../../skills/task-tree/scripts/templates/base.html#L3591)): `var rootNode = document.getElementById(navNodeId('')); if (rootNode) await expandNavNode(rootNode);`. `expandNavNode` is idempotent, so this is a no-op when the root is already open (in-app clicks / popstate), and harmless in the forest case where no `task-root` node exists. `scrollIntoView({block:'nearest'})` is left untouched — per "fix the confirmed failure, not by hypothesis."

**Verification (real rendered page).** After the fix, in fresh contexts (viewport 1200×800 and a short 1200×420 that forces the `#nav-tree` container to overflow and scroll):

- Deep target: `.nav-active` + `aria-selected="true"`, `fullyVisible: true` (row rect within the container; e.g. row 367–396 inside container 147–420 on the short viewport — scrolled in, clear of the sidebar-head chrome above `#nav-tree`).
- Shallow (top-level) target and root: same — highlighted and fully visible.
- No regression: in-app hash navigation between two deep sibling branches, plus back/forward (`popstate`), all keep `.nav-active` + `aria-selected` and `fullyVisible: true`.

**Test** (`test_dashboard.py`): added `TestSidebarStatePreservation.test_expands_root_container_before_segment_walk`, asserting `updateSidebar` expands `navNodeId('')` before the segment loop. Full `test_dashboard.py` suite: 265 passed.
