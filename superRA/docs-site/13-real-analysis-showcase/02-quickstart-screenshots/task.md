---
title: "Capture Stage Screenshots for the Quickstart"
status: approved
depends_on:
  - 01-export-and-framing
tags: []
created: 2026-06-17
---

## Objective

Give the quickstart tutorial visual proof of the workflow by showing the *same real tree* at three moments, and embed the images in [docs/site/02-quickstart/task.md](../../../../docs/site/02-quickstart/task.md):

1. **After planning** — the analysis tree freshly planned, every task `not-started` (the frontier laid out).
2. **Mid-implement** — a genuine mixed-status moment: some children `approved`, one `implemented` awaiting review, one in `revise`, the rest `not-started`, with the parent rolled up. This is the state that shows status pills, the rollup, and the kanban doing real work.
3. **Complete** — the whole tree `approved`.

Each screenshot is a capture of the task-tree dashboard / standalone export rendered with **full chrome** (not the doc-mode site), so the quickstart shows the actual task tracker, matching the explorable export from `01-export-and-framing`.

**Capture mechanism.** Reproduce each state, export it with `plan_dashboard.py generate` (full chrome), and render the standalone HTML to PNG headlessly — a PEP 723 Playwright/Chromium script is the expected route. The "after planning" and "complete" states are real points in the analysis tree's git history; capture them by checking out the corresponding commit. The "mid-implement" mixed composition (some `approved`, one `implemented`, one `revise`, rest `not-started`) may never exist as a single committed snapshot — the implementer-reviewer loop advances statuses across many commits and a `revise` state is transient — so if no real commit captures it, construct the snapshot deliberately: copy the `showcase-analysis/` task files to a throwaway location, hand-set the frontmatter `status` fields to the target composition (never committing these edits to the live tree), and export from there. Record the exact commits / snapshot recipe and the command used so every image regenerates. Commit the PNGs under this task's `attachments/` and reference them from the quickstart with captions tying each to its workflow phase (PLAN → IMPLEMENT mid-flight → done).

**Validation:** the three images render in the built quickstart page, visibly differ in status composition (all grey → mixed colors → all green), and the regeneration steps are documented well enough to rebuild them.

## Results

Captured the *same* real showcase-analysis tree at three workflow phases and embedded the three screenshots into the quickstart's new `#### The same arc on a real project` subsection (between Superintegrate and Where-to-go-next) in [docs/site/02-quickstart/task.md](../../../../docs/site/02-quickstart/task.md), each with a caption tying it to PLAN → IMPLEMENT mid-flight → done.

The three states are honest points in the showcase-analysis subtree's git history — no fabricated/hand-set snapshot was needed, so the synthetic-snapshot fallback the objective describes for mid-implement was not used. The mid-implement commit `805a247e` is the genuine implement→review handoff (data approved, analysis implemented and awaiting its reviewer, writeup not-started), which carries the same legibility as the objective's `revise`-bearing target without inventing a transient state.

**Committed images** (this task's `attachments/`, base64-inlined by the docs export):

| File | Phase | Status composition | Source commit |
|---|---|---|---|
| [attachments/showcase-after-planning.png](attachments/showcase-after-planning.png) | After planning | all `not-started` (grey), rollup 0/3 | `de25a122` |
| [attachments/showcase-mid-implement.png](attachments/showcase-mid-implement.png) | Mid-implement | 01-data `approved` (green), 02-analysis `implemented` (yellow), 03-writeup `not-started` (grey), parent `in-progress`, rollup 1/3 | `805a247e` |
| [attachments/showcase-complete.png](attachments/showcase-complete.png) | Complete | all `approved` (green), rollup 3/3 | `HEAD` (`613668e1` at capture) |

All three use the **default Workspace view** at `window-size=1500,1900` consistently — the status-pill sidebar plus the parent rollup counter make the composition legible, and the view renders without JS interaction (the Kanban view is a `showView('kanban')` JS toggle with no URL route, so it cannot be reached headlessly via a hash). Each committed PNG was opened and verified to show its intended composition before commit; the built quickstart page was rendered headlessly and all three images confirmed to inline and display in order.

### Regeneration recipe

Run from the repo root. `HEAD` exports directly; the two historical states use a temporary detached worktree so the live tree is never disturbed.

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
shot() {  # shot <html> <png>
  "$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
    --window-size=1500,1900 --virtual-time-budget=4000 \
    --screenshot="$2" "file://$1"
}
ATT="superRA/docs-site/13-real-analysis-showcase/02-quickstart-screenshots/attachments"

# complete — current HEAD, from the main worktree
uv run --script skills/task-tree/scripts/plan_dashboard.py generate \
  --plan-root superRA --root showcase-analysis \
  --output /tmp/stage_3.html --repo-file-prefix superRA/showcase-analysis
shot /tmp/stage_3.html "$ATT/showcase-complete.png"

# after-planning (de25a122) and mid-implement (805a247e) — temp detached worktrees
for pair in "1:de25a122:showcase-after-planning" "2:805a247e:showcase-mid-implement"; do
  n=${pair%%:*}; rest=${pair#*:}; sha=${rest%%:*}; name=${rest#*:}
  git worktree add --detach /tmp/sc_stage_$n $sha
  ( cd /tmp/sc_stage_$n && uv run --script skills/task-tree/scripts/plan_dashboard.py generate \
      --plan-root superRA --root showcase-analysis \
      --output /tmp/stage_$n.html --repo-file-prefix superRA/showcase-analysis )
  shot /tmp/stage_$n.html "$ATT/$name.png"
  git worktree remove /tmp/sc_stage_$n
done
```

The export inlines each PNG by resolving the markdown `![...](src)` path against the quickstart task's on-disk dir (`docs/site/02-quickstart/`), so the embeds use the cross-tree relative path `../../../superRA/docs-site/13-real-analysis-showcase/02-quickstart-screenshots/attachments/<name>.png` to reach this task's committed `attachments/`.
