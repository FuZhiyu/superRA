---
title: "Tab Title Names the Active Task and Worktree"
status: revise
depends_on: 
  - local-file-open

---

## Objective

Make the browser tab title identify what the tab is showing. It is currently the server-rendered tree title and nothing else, so every tab of every worktree of a repo reads identically and a researcher with several open cannot tell them apart.

- The title carries the active task's title first, then the worktree it lives in — tabs truncate from the right, so the more specific part leads.
- It follows navigation: every task change and every worktree switch updates it, and it resolves the real task title on a deep descent where the sidebar row has not landed yet.
- The worktree part is the branch, falling back to the worktree directory name when there is no branch.
- The title tracks the active page in every mode, including the standalone export and the published docs site that is built from it. Doc-mode and standalone have no worktree to name, so the second half is the site or export's own name; only the worktree half is mode-dependent, never whether the title moves at all.
- Verification: the dashboard and full task-tree script suites pass, plus a live check that the title tracks a deep-linked task, a worktree switch, and a back/forward navigation, and that a standalone export's title follows in-file navigation.

## Revision Notes

The standalone clause originally read "keeps a title that is stable in a downloaded file," which the implementer correctly read as freezing the title. That froze the published docs site too, since `docs/build_site.sh` builds it as a standalone export — so every page on the published site carried the site name alone. The intent behind "stable" was only that an offline file must not name a worktree that does not exist there, not that the title should stop tracking the page. Researcher chose per-page titles on the published site, so the clause is rewritten to scope mode-dependence to the second half alone.

## Planner Guidance

`setActive` in `skills/task-tree/scripts/templates/dashboard.js` is the single navigation entry point and already refreshes every derived region, so it is the natural call site. The complication is timing: `pathTitles` is populated by the sidebar fetch, which can still be in flight on a deep descent, while `loadActiveNode` resolves the same title for the card head a moment earlier. Setting the title from `loadActiveNode` once it has resolved the title avoids a tab that briefly reads as a path slug.

The worktree's branch arrives in the `/api/worktrees` payload that `fetchWorktrees` already consumes — it indexes `wt.path` and `wt.plan_root` per `wt_id` for `PROJECT_ROOT` / `RESOLVED_ROOT` and builds a selector label from `wt.branch` with a directory-name fallback. Index the label the same way and refresh the title when that fetch resolves, since it lands after the first render.

Capture the server-rendered `<title>` once at load: it is the tree's own name and the correct fallback for the root node, for doc-mode, and for standalone, where no worktree list is ever fetched.

## Results

The tab now reads `<active task> · <worktree>` — e.g. `Tab Title Names the Active Task and Worktree · dashboard-local-file-open` — so tabs of different worktrees of one repo, and different tasks within one worktree, are tellable apart at a glance.

### How it composes

[`refreshTabTitle`](../../../../skills/task-tree/scripts/templates/dashboard.js#L859) is the single writer of `document.title`. It joins two halves:

- **Task half** — [`setTabTitle`](../../../../skills/task-tree/scripts/templates/dashboard.js#L852) records the display title [`loadActiveNode` already resolved for the card head](../../../../skills/task-tree/scripts/templates/dashboard.js#L1098), so the tab and the card never disagree. At the root there is no task title; the half falls back to `SITE_TITLE`, the server-rendered `<title>` [captured once at load](../../../../skills/task-tree/scripts/templates/dashboard.js#L848).
- **Worktree half** — the branch, or the worktree's directory name on a detached HEAD, via [`worktreeLabel`](../../../../skills/task-tree/scripts/templates/dashboard.js#L2549), which the worktree dropdown now shares (it decorates the same base label with the plan title and the agent marker). [`fetchWorktrees` indexes it per `?wt=` token](../../../../skills/task-tree/scripts/templates/dashboard.js#L2651) alongside the project/resolved roots it already indexes, and repaints when that fetch resolves — it lands after the first card render and again on every worktree switch. Until then the tab shows the task half alone, never a dangling separator.

The halves are joined only when they differ, so a task titled the same as its branch does not read `main · main`.

Navigation coverage falls out of the call site: `setActive` (task clicks, breadcrumbs, popstate, SSE structural reloads) and `applyWorktree` (selector, back/forward across a `?wt=` boundary) both route through `loadActiveNode`.

**Deep descent.** `pathTitles` is harvested from sidebar rows, so a fresh deep link can render the card before the row carrying the real title lands, leaving the tab on the path slug. [`patchTabTitleWhenReady`](../../../../skills/task-tree/scripts/templates/dashboard.js#L1247) re-reads the title once that tick's sidebar update settles, using the same `_lastSidebarUpdate` completion hook and navigation-token guard as the existing status-badge patch.

**Doc-mode and standalone.** Doc-mode has no worktree, so the second half is the site name (`Domain Skills · superRA Documentation`). Standalone leaves `document.title` exactly as exported, so a downloaded file keeps a stable title.

Caveat worth knowing: the published docs site is built as a standalone export ([docs/build_site.sh](../../../../docs/build_site.sh)), so the standalone rule wins there and its per-page titles stay frozen at the site name. The doc-mode branch is live in `superra dashboard --doc-mode` serving (verified below), which is how the site is previewed. Making published doc pages carry per-page titles is a behavior change to the standalone rule, not a bug in this one — left as the objective specifies.

### Verification

Full task-tree script suite: **747 passed** (`uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`), including 14 new tests — [`TestTabTitle`](../../../../skills/task-tree/scripts/test_dashboard.py#L3168) runs the extracted functions under node through the existing `_extract_js_defs` harness (composition, branch vs directory-name fallback, worktree switch, root fallback, pre-fetch state, both doc-mode cases, standalone), and [`TestTabTitleWiring`](../../../../skills/task-tree/scripts/test_dashboard.py#L3239) pins the call sites.

Live checks in a real Chromium against this repo's dashboard on `http://localhost:8995` (restarted first so the one-hour-cached JS was re-fetched):

| Step | `document.title` |
|---|---|
| Deep link `#/task-tree/dashboard/task-scoped-tab-title` | `Tab Title Names the Active Task and Worktree · dashboard-local-file-open` |
| Click a sibling task row | `Open Task Files on the Researcher's Machine · dashboard-local-file-open` |
| Browser Back | `Tab Title Names the Active Task and Worktree · dashboard-local-file-open` |
| Browser Forward | `Open Task Files on the Researcher's Machine · dashboard-local-file-open` |
| Worktree switch to `interactive-mode` | `HTML Dashboard · interactive-mode` (task absent there → nearest surviving ancestor, as `resolveSurvivingPath` intends) |
| Back across the `?wt=` boundary | `Open Task Files on the Researcher's Machine · dashboard-local-file-open` |
| Root `#/` | `superRA · dashboard-local-file-open` |

Sampling the title every 400 ms through a cold deep-link load showed the intended two-phase fill and no later regression: `Tab Title Names the Active Task and Worktree` at 0.4 s, then `… · dashboard-local-file-open` from 0.8 s on. Repeating it with every `/nav` response delayed 1.5 s left the final title correct throughout.

The deep-descent patch was exercised directly in the live page — clearing `pathTitles[path]` and holding `_lastSidebarUpdate` open gave `task-scoped-tab-title · dashboard-local-file-open` (slug) during the race and `Tab Title Names the Active Task and Worktree · dashboard-local-file-open` once the sidebar update settled.

Mode checks: live `superra dashboard --doc-mode --root docs/site` gave `Domain Skills · superRA Documentation` on a page and `superRA Documentation` at the root; a standalone export of the `task-tree/dashboard` subtree stayed `HTML Dashboard` at the root and on a deep link.
