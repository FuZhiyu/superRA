---
title: "Preserve UI state across SSE updates"
status: approved
depends_on: []
tags: []
created: 2026-05-26
---

## Objective

Editing a `task.md` while the dashboard is open must not throw away the UI state the user is sitting in.

**Architecture note (updated 2026-06-07).** This tree was originally written against the old single-tree dashboard, where the whole task body lived inline in `#view-tree` and a `task:{path}` SSE event swapped the entire task node via htmx `outerHTML` — so state preservation meant capturing expanded/section/scroll/markdown/comment state across that swap and replacing `location.reload()` on structural changes. The dashboard has since moved to a **master-detail layout**: a body-free navigation tree in the sidebar (`#nav-tree`, served by `/nav` + `/nav/{path}`) plus a detail panel (`#active-node`, served by `/node/{path}`) driven by the `activePath` hash router. That original outerHTML-swap mechanism no longer exists; the `sidebar-current-page` child carries the work that brought state preservation up to the current architecture.

**What state preservation means in the master-detail UI:**

1. **Content edit** (`task.md` modified, no child-set change): the watcher broadcasts `task:{path}`; htmx swaps only the body-free **sidebar row** (`outerHTML` on a label+badge, nothing to preserve), and `onTaskUpdate` re-renders the detail panel for the active task. The only state at risk is the active-row highlight (re-asserted after the swap) and an in-flight comment editor (suppressed for 3s via `_commentEditPaths`). Both already handled.

2. **Structural change** (`task.md` added/deleted, or a `task.md` edit that changes the task's own child set): the watcher broadcasts `full-reload`; the client rebuilds the whole sidebar from `/nav` (`onFullReload` → `loadNavTree`), then re-derives highlight + breadcrumb + panels from `activePath`. A bare rebuild folds **every** manually-opened branch back to the root — this is the data loss the `sidebar-current-page` child fixes.

**Goal:** across both event kinds, preserve the sidebar's open/closed shape (the branches the user expanded), keep the current page visible and expanded to its own children, hold the active-row highlight, and never re-render an open comment editor out from under the user.

**Files:** `skills/task-tree/scripts/plan_dashboard.py` (watcher + SSE broadcasting), `skills/task-tree/scripts/templates/base.html` (the `activePath` router, sidebar nav, and SSE handlers), `skills/task-tree/scripts/templates/nav_node.html` / `nav_children.html` (body-free sidebar fragments).

## Results

The original capture-restore-across-outerHTML approach was overtaken by the master-detail migration. The live state-preservation work for the current architecture — keeping the current page expanded to its children and preserving manually-opened branches across a `full-reload` rebuild — is implemented in the `sidebar-current-page` child.
