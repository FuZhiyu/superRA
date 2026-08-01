---
title: "Tab Title Names the Active Task and Worktree"
status: not-started
depends_on: 
  - local-file-open

---

## Objective

Make the browser tab title identify what the tab is showing. It is currently the server-rendered tree title and nothing else, so every tab of every worktree of a repo reads identically and a researcher with several open cannot tell them apart.

- The title carries the active task's title first, then the worktree it lives in — tabs truncate from the right, so the more specific part leads.
- It follows navigation: every task change and every worktree switch updates it, and it resolves the real task title on a deep descent where the sidebar row has not landed yet.
- The worktree part is the branch, falling back to the worktree directory name when there is no branch.
- Doc-mode has no worktree identity to show and names the site instead; the standalone export keeps a title that is stable in a downloaded file.
- Verification: the dashboard and full task-tree script suites pass, plus a live check that the title tracks a deep-linked task, a worktree switch, and a back/forward navigation.

## Planner Guidance

`setActive` in `skills/task-tree/scripts/templates/dashboard.js` is the single navigation entry point and already refreshes every derived region, so it is the natural call site. The complication is timing: `pathTitles` is populated by the sidebar fetch, which can still be in flight on a deep descent, while `loadActiveNode` resolves the same title for the card head a moment earlier. Setting the title from `loadActiveNode` once it has resolved the title avoids a tab that briefly reads as a path slug.

The worktree's branch arrives in the `/api/worktrees` payload that `fetchWorktrees` already consumes — it indexes `wt.path` and `wt.plan_root` per `wt_id` for `PROJECT_ROOT` / `RESOLVED_ROOT` and builds a selector label from `wt.branch` with a directory-name fallback. Index the label the same way and refresh the title when that fetch resolves, since it lands after the first render.

Capture the server-rendered `<title>` once at load: it is the tree's own name and the correct fallback for the root node, for doc-mode, and for standalone, where no worktree list is ever fetched.

## Results
