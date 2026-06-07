---
title: "Preserve UI state across SSE updates"
status: in-progress
depends_on: []
tags: []
created: 2026-05-26
---

## Objective

Editing a `task.md` while the dashboard is open must not throw away the UI state the user is sitting in.

**Architecture note (updated 2026-06-07).** This tree was originally written against the old single-tree dashboard, where the whole task body lived inline in `#view-tree` and a `task:{path}` SSE event swapped the entire task node via htmx `outerHTML` — so state preservation meant capturing expanded/section/scroll/markdown/comment state across that swap (the `capture-restore` child) and replacing `location.reload()` on structural changes (the `structural-reload` child). The dashboard has since moved to a **master-detail layout**: a body-free navigation tree in the sidebar (`#nav-tree`, served by `/nav` + `/nav/{path}`) plus a detail panel (`#active-node`, served by `/node/{path}`) driven by the `activePath` hash router. Those two original children describe a mechanism that no longer exists; see their own Results for what superseded each, and the new `sidebar-current-page` child for the work that brought state preservation up to the current architecture.

**What state preservation means in the master-detail UI:**

1. **Content edit** (`task.md` modified, no child-set change): the watcher broadcasts `task:{path}`; htmx swaps only the body-free **sidebar row** (`outerHTML` on a label+badge, nothing to preserve), and `onTaskUpdate` re-renders the detail panel for the active task. The only state at risk is the active-row highlight (re-asserted after the swap) and an in-flight comment editor (suppressed for 3s via `_commentEditPaths`). Both already handled.

2. **Structural change** (`task.md` added/deleted, or a `task.md` edit that changes the task's own child set): the watcher broadcasts `full-reload`; the client rebuilds the whole sidebar from `/nav` (`onFullReload` → `loadNavTree`), then re-derives highlight + breadcrumb + panels from `activePath`. A bare rebuild folds **every** manually-opened branch back to the root — this is the data loss the `sidebar-current-page` child fixes.

**Goal:** across both event kinds, preserve the sidebar's open/closed shape (the branches the user expanded), keep the current page visible and expanded to its own children, hold the active-row highlight, and never re-render an open comment editor out from under the user.

**Files:** `skills/task-system/scripts/plan_dashboard.py` (watcher + SSE broadcasting), `skills/task-system/scripts/templates/base.html` (the `activePath` router, sidebar nav, and SSE handlers), `skills/task-system/scripts/templates/nav_node.html` / `nav_children.html` (body-free sidebar fragments).

## Results

The original capture-restore-across-outerHTML approach was overtaken by the master-detail migration and is documented as superseded in the two original children. The live state-preservation work for the current architecture — keeping the current page expanded to its children and preserving manually-opened branches across a `full-reload` rebuild — is implemented in the `sidebar-current-page` child.

## Review Notes

1. MAJOR — stored child statuses do not match the documented reality, leaving this subtree permanently pinned at `in-progress`. The three original children — [capture-restore](capture-restore/task.md), [structural-reload](structural-reload/task.md), and [tests](tests/task.md) — each carry an accurate "Superseded (2026-06-07)" note stating their mechanism was retired by the master-detail migration, yet all three still store `status: implemented` (live work awaiting review). Because `compute_status` ([_task_io.py:489-494](skills/task-system/scripts/_task_io.py#L489)) treats `implemented` as in-progress and only excludes `archived`/`postponed` children from the rollup, `state-preservation` will roll up to `in-progress` indefinitely even though its sole remaining active child, [sidebar-current-page](sidebar-current-page/task.md), is `approved`. `superra task check` is clean only because it does not flag superseded-but-implemented children. Retired tasks should reach a parked terminal status (`archived`) so the rollup drops them and this subtree resolves to `approved`.

   No status field is changed in-review to signal this: the parent's `status` is rollup-computed (manually setting it produces a stored-vs-computed `check` warning), and forcing `revise` onto the three leaf children would misrepresent them as code-rework tasks when the remedy is archival. The remedy — archive the three retired children vs. keep them as historical `implemented` records — is a planning-lifecycle decision (status archival is planner-owned), escalated here and in the review return for orchestrator/planner adjudication rather than resolved in-review.

