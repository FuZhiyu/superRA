---
title: "Frontend Responsiveness and Cache-Coherence Fixes"
status: not-started
depends_on:
  - template-split
---

## Objective

The known frontend performance and staleness defects from the 2026-07-19 review are fixed:

- The sidebar filter input is debounced and no longer re-scans each subtree once per ancestor on every keystroke.
- SSE task events trigger at most one debounced comment-summary refresh per burst, and badges are not torn down before the fetch resolves (no flicker window).
- The children-panel cache signature includes the title, and the cache is cleared on worktree switch and full-reload; `pathTitles` (breadcrumb titles) refreshes when an SSE row swap changes a title — net effect: a title edit propagates to the children panel and breadcrumb without a structural reload.
- The worktree dropdown issues one `/api/worktrees` fetch per open, not two.
- Dead parameters and never-invoked closures in the comment UI are removed; `style.cssText` strings duplicating existing CSS rules become classes.
- Validation: a targeted test (or scripted browser check) shows a title edit propagating to panel + breadcrumb live; one summary fetch observed per SSE burst; both suites green.

## Planner Guidance

Locations (pre-split `base.html` line numbers; after `template-split` these live in the extracted JS/CSS): filter `oninput` with recursive `querySelectorAll` scans at 1825 + 2645-2784; per-event summary fetch and teardown-before-fetch at 4374-4385 + 4828-4901; `childrenSig` omitting title at 3180-3183 with cache hits at 3191-3194, `applyWorktree`/`onFullReload` never clearing `_childrenDagCache` (4528, 4312); dropdown double-bind `mousedown`+`focus` at 4567-4573; `cssText` duplication at 4761-4776 + 4940-4951 vs CSS 1721-1732; unused `btn` params and stored-but-never-called `save`/`cancel` closures at 5005-5015 + 4998-5002.

Also worth taking if cheap (advisory): parallelize the serial `/nav/{path}` fetch waterfall in `restoreExpandedNavPaths` (3563-3572) by depth level; replace the `setTimeout`-polling `patchCardBadgeWhenReady` (3099-3116) with a completion hook.
