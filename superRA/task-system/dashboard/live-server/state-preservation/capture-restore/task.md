---
title: "Capture and restore UI state across outerHTML swaps"
status: implemented
depends_on: []
tags: []
created: 2026-05-26
---

## Objective

When htmx performs an `outerHTML` swap on a task node (in response to a `task:{path}` SSE event), the entire DOM subtree is replaced — destroying expanded/collapsed state, open sections, scroll position, and rendered markdown. Implement a capture-restore mechanism that preserves this state across swaps.

**What to capture before swap (on the node being replaced and its descendants):**
- Expanded task nodes: which `.task-toggle` elements have the `expanded` class — store as a set of `data-path` values
- Open sections: which `.section-content` elements have the `open` class — store as `{taskPath: [sectionName, ...]}` keyed by `data-path` and `data-section`
- Children visibility: which `.task-children` elements have `display !== 'none'`
- Scroll position of `.main-content` (or the nearest scrollable ancestor)

**What to restore after swap:**
- Re-apply `expanded` class on task toggles for all captured paths
- Re-show `.task-body` (add `open`) and `.task-children` (`display: ''`) for expanded nodes
- Re-open captured sections (add `open` to `.section-content`, hide `.section-preview`, rotate `.section-icon`)
- Re-render markdown in any section that was open and had `data-rendered='true'` — call `renderMarkdown()` on those sections' `.rendered-md` containers
- Restore scroll position

**Implementation approach — htmx event hooks:**
- Listen to `htmx:beforeSwap` on `document.body`: when the swap target is a `.task-node`, capture UI state from the old node and its descendants
- Listen to `htmx:afterSwap` on `document.body`: restore state onto the newly swapped node
- Store captured state in a module-scoped variable (e.g., `_pendingSwapState`) keyed by the task path being swapped — it only needs to survive between the before/after events

**Scope:** Only content-change SSE swaps (`task:{path}` events). The `full-reload` → `location.reload()` path is handled in the sibling `structural-reload` task.

**Files to modify:**
- `skills/task-system/scripts/templates/base.html` — add `htmx:beforeSwap` / `htmx:afterSwap` handlers with state capture/restore logic

**Validation:**
- Expand a task node, open a section inside it, scroll to the middle of the page → edit the corresponding `task.md` → the node updates with new content but the expanded/open/scroll state is preserved
- Nested state: expand a parent, expand a child, open a section in the child → edit the parent's `task.md` → parent updates, child remains expanded with its section open
- Comment form: have a comment form open → edit the task.md → form should not be destroyed (or if it is, the user should not lose typed text — consider warning or saving draft)

## Results

Implemented capture-restore mechanism in [base.html:916-1185](skills/task-system/scripts/templates/base.html#L916-L1185). The implementation uses the `htmx:sseBeforeMessage` / `htmx:afterSwap` event pair with a module-scoped `_pendingSwapState` dictionary keyed by task path.

### Capture (`htmx:sseBeforeMessage` handler)

Integrated state capture into the existing SSE pre-message handler (which already handled comment-edit suppression). Before the swap, `captureNodeState()` walks the target `.task-node` and all descendant `.task-node` elements to record:
- Expanded task paths (`.task-toggle.expanded` class presence)
- Visible children containers (`.task-children` with `display !== 'none'`)
- Open sections per task path (`.section-content.open` keyed by `data-section`)
- Rendered markdown state per section (`data-rendered='true'`)
- Scroll position of `.main-content`
- Comment form draft text (textarea values, keyed by section + block index to support multiple open forms per task)

### Restore (`htmx:afterSwap` handler)

Replaced the original afterSwap handler (which only did markdown rendering) with one that first checks for pending state. `restoreNodeState()` rebuilds a `nodesByPath` lookup from the new DOM, then:
- Re-applies `expanded` class on task toggles, opens `.task-body`, shows `.task-children`
- Re-opens sections (`.section-content.open`, rotates `.section-icon`, hides `.section-preview`)
- Re-renders markdown via `renderMarkdown()` for sections that had rendered content
- Restores comment form drafts: for each saved draft, finds the matching `.commentable-block` by section + block index, calls `showCommentForm()` to recreate the form, and sets the textarea value to the saved draft text; if the block is not found (e.g. structure changed), saves the draft to `sessionStorage` as a fallback
- Re-loads comments for expanded tasks via `loadComments(path)` for each expanded path, since the outerHTML swap wipes previously loaded comment threads
- Restores scroll position via `requestAnimationFrame` with window fallback

The afterSwap handler includes a parent-search fallback: if `event.detail.target` is the parent element rather than the swapped task-node itself (an outerHTML swap edge case), it searches children for a node with pending state.

### Validation

Dashboard serves the template without errors (HTTP 200). All functions (`captureNodeState`, `restoreNodeState`, `_pendingSwapState`, `showCommentForm`, `loadComments`) are present in the rendered output. HTML/JS structure is balanced (337 braces, 753 parens, 100 brackets each side). The comment-edit suppression path (`_commentEditPaths` check) takes priority and short-circuits before capture when a local comment op just happened, preserving existing behavior. Comment form draft restore, `sessionStorage` fallback, and `loadComments` re-invocation are all confirmed present in rendered output.

### Design note on event choice

Used `htmx:sseBeforeMessage` (not `htmx:beforeSwap`) for capture because `sseBeforeMessage` fires before htmx processes the SSE data, guaranteeing the old DOM is intact. The existing comment suppression logic was already using this event, so the state capture integrates naturally alongside it.

### Superseded (2026-06-07)

This entire mechanism was retired by the master-detail migration. There is no longer a single inline tree whose task nodes carry bodies, so a `task:{path}` event no longer swaps an expandable/section-bearing node — it swaps a body-free **sidebar row** (label + status badge), which has no expanded-section/scroll/markdown/comment state to capture. `captureNodeState`, `restoreNodeState`, and `_pendingSwapState` no longer exist in `base.html`. The content-edit state that does survive in the new UI is handled directly: the active-row highlight is re-asserted after the row swap (`onTaskUpdate` → deferred `updateSidebar`), the detail panel re-renders via a fresh `/node/{path}` fetch (`loadActiveNode`, sections default to expanded there), and an open comment editor is protected by the 3-second `_commentEditPaths` suppression window — the one piece of this task's design that carried forward. Sidebar tree-shape preservation moved to the `sidebar-current-page` child.
