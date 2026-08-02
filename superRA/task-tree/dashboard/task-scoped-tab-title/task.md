---
title: "Tab Title Names the Active Task and Worktree"
status: implemented
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

The tab now reads `<active page> · <where it lives>` — `Tab Title Names the Active Task and Worktree · dashboard-local-file-open` in a live dashboard, `Domain Skills · superRA Documentation` on the published docs site — so tabs of different worktrees of one repo, and different tasks within one worktree, are tellable apart at a glance.

### How it composes

[`refreshTabTitle`](../../../../skills/task-tree/scripts/templates/dashboard.js#L859) is the single writer of `document.title`. It joins two halves:

- **Page half** — [`setTabTitle`](../../../../skills/task-tree/scripts/templates/dashboard.js#L852) records the display title [`loadActiveNode` already resolved for the card head](../../../../skills/task-tree/scripts/templates/dashboard.js#L1107), so the tab and the card never disagree. At the root there is no task title; the half falls back to `SITE_TITLE`, the server-rendered `<title>` [captured once at load](../../../../skills/task-tree/scripts/templates/dashboard.js#L848). This half tracks navigation in every mode — live, doc-mode, and inside a downloaded export.
- **Second half** — the worktree in a live dashboard: its branch, or its directory name on a detached HEAD, via [`worktreeLabel`](../../../../skills/task-tree/scripts/templates/dashboard.js#L2559), which the worktree dropdown now shares (it decorates the same base label with the plan title and the agent marker). [`fetchWorktrees` indexes it per `?wt=` token](../../../../skills/task-tree/scripts/templates/dashboard.js#L2661) alongside the project/resolved roots it already indexes, and repaints when that fetch resolves — it lands after the first card render and again on every worktree switch. Until then the tab shows the page half alone, never a dangling separator. A doc site and a downloaded export have no worktree, and must not name one that will not exist wherever the file ends up, so they carry `SITE_TITLE` here instead.

Mode-dependence is confined to that second half; whether the title moves at all is not mode-dependent.

The halves are joined only when they differ, so a task titled the same as its branch does not read `main · main`, and an export's root reads as the export name alone rather than doubled.

Navigation coverage falls out of the call site: `setActive` (task clicks, breadcrumbs, popstate, SSE structural reloads) and `applyWorktree` (selector, back/forward across a `?wt=` boundary) both route through `loadActiveNode`.

**Deep descent.** `pathTitles` is harvested from sidebar rows, so a fresh deep link can render the card before the row carrying the real title lands, leaving the tab on the path slug. [`patchTabTitleWhenReady`](../../../../skills/task-tree/scripts/templates/dashboard.js#L1257) re-reads the title once that tick's sidebar update settles, using the same `_lastSidebarUpdate` completion hook and navigation-token guard as the existing status-badge patch.

**Failed card load.** When `/node/<path>` fails after a successful navigation, the card is replaced with "Could not load this task." Both error branches — [the not-ok response](../../../../skills/task-tree/scripts/templates/dashboard.js#L1088) and [the thrown-error catch](../../../../skills/task-tree/scripts/templates/dashboard.js#L1181) — clear the page half, so the tab falls back to the tree's own name rather than keeping the name of a task the card is no longer showing. That matches what a cold load of a bad deep link already did.

### Verification

Full task-tree script suite: **750 passed** (`uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`), including 17 new tests — [`TestTabTitle`](../../../../skills/task-tree/scripts/test_dashboard.py#L3169) runs the extracted functions under node through the existing `_extract_js_defs` harness (composition, branch vs directory-name fallback, worktree switch, root fallback, pre-fetch state, doc-mode page and root, export page and root, cleared page half), and [`TestTabTitleWiring`](../../../../skills/task-tree/scripts/test_dashboard.py#L3260) pins the call sites including both error branches.

Live checks in a real Chromium against this repo's dashboard on `http://localhost:8995` (restarted first so the one-hour-cached JS was re-fetched), driven by real row clicks and browser back/forward:

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

**Offline modes**, checked by clicking rows inside the built files themselves. A standalone export of the `task-tree/dashboard` subtree (`superra dashboard export --subtree task-tree/dashboard`) opened from `file://`:

| Step | `document.title` |
|---|---|
| Export root | `HTML Dashboard` |
| Click `local-file-open` | `Open Task Files on the Researcher's Machine · HTML Dashboard` |
| Click `task-scoped-tab-title` | `Tab Title Names the Active Task and Worktree · HTML Dashboard` |
| Browser Back | `Open Task Files on the Researcher's Machine · HTML Dashboard` |

The published docs site, from a real [docs/build_site.sh](../../../../docs/build_site.sh) build opened at `file://…/index.html` — the case the revision was about:

| Step | `document.title` |
|---|---|
| Site root | `superRA Documentation` |
| Click `03-domain-skills` | `Domain Skills · superRA Documentation` |
| Click `02-quickstart` | `Quickstart: Your First Workflow · superRA Documentation` |

Live `superra dashboard --doc-mode --root docs/site` gives the same shape (`Domain Skills · superRA Documentation` on a page, `superRA Documentation` at the root), so previewing the site and publishing it now agree.

**Failed card load**, forced in the live page by failing every `/node` request with a 500 after a successful navigation: the card read "Could not load this task." and the tab moved from `Tab Title Names the Active Task and Worktree · dashboard-local-file-open` to `superRA · dashboard-local-file-open`, so it no longer names a task the card is not showing.
