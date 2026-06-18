---
title: "Build Historical-State Live Exports From Committed Fixtures"
status: not-started
depends_on:
  - 01-retire-and-rewire
tags: []
created: 2026-06-17
---

## Objective

Give the Quickstart three *live, explorable* views of the real [showcase-analysis](../../../showcase-analysis/task.md) tree at three workflow moments — after-planning, mid-implement, complete — as standalone HTML pages it can link, replacing the static screenshots. The reader clicks through to the actual task tracker (crisp text, deep links, the Kanban toggle) instead of squinting at a PNG.

**Why fixtures, not a git-history rebuild.** The after-planning (`de25a122`) and mid-implement (`805a247e`) states are honest points in this branch's history, but they are not durably reachable at build time: CI checks out shallow (`actions/checkout@v4`, depth 1) and builds on push to `main`, and this branch squash-merges to `main`, which collapses those commits away. So the two historical states must be **committed as frozen fixtures** — the `showcase-analysis` subtree as it stood at each SHA, carrying that era's empty / partial `## Results` — and exported from the fixture at build time. The `complete` state is the current all-`approved` tree, already exported as `showcase-analysis-tree.html`, so it is reused, not re-frozen.

- **Capture two fixtures** under `docs/showcase-fixtures/`, each a copy of the `showcase-analysis` subtree extracted from its source commit (`git archive <sha> -- superRA/showcase-analysis | tar -x …`, or check out the commit in a temp worktree then copy out — never disturb the live tree):
  - `docs/showcase-fixtures/after-planning/showcase-analysis/` from `de25a122` — the four `task.md` files, all `status: not-started`, no `## Results`, no figures (freshly-planned frontier).
  - `docs/showcase-fixtures/mid-implement/showcase-analysis/` from `805a247e` — `01-data` `approved`, `02-analysis` `implemented` (with its four `attachments/*.png` figures, which the export inlines from its Results), `03-writeup` `not-started`, parent rolled up to `in-progress`. Include exactly the files the export renders or inlines (the `task.md` files plus `02-analysis/attachments/`); the analysis code/data files are not needed for a dashboard export.
- **Wire [docs/build_site.sh](../../../../docs/build_site.sh)** (the two-export script established by [01-retire-and-rewire](../01-retire-and-rewire/task.md)) to emit two more full-chrome pages from the fixtures, alongside the existing `index.html` and `showcase-analysis-tree.html`:
  - `showcase-after-planning.html` ← `generate --plan-root docs/showcase-fixtures/after-planning --root showcase-analysis`
  - `showcase-mid-implement.html` ← `generate --plan-root docs/showcase-fixtures/mid-implement --root showcase-analysis`
  - Pass `--repo-file-prefix superRA/showcase-analysis` on both so in-task repo-file links resolve to the real tree, matching the existing exports. Full chrome (the standard `generate`, never `--doc-mode`). Update the header comment, the required-input existence check, the output-verification loop, and the final echo to cover all four output files.
  - Add `--doc-local-link showcase-after-planning.html` and `--doc-local-link showcase-mid-implement.html` to the `index.html` doc-mode build so the Quickstart's links to them stay relative (alongside the existing `--doc-local-link showcase-analysis-tree.html`).
- **CI** ([.github/workflows/docs-site.yml](../../../../.github/workflows/docs-site.yml)): add `docs/showcase-fixtures/**` to the push path filter so fixture edits trigger a rebuild.

The fixtures are intentionally frozen historical snapshots — they are **not** kept in sync with later edits to the live `showcase-analysis` prose; that staleness is the point (they show the tree at a past moment). Note this in `build_site.sh` near the fixture exports so a future reader does not "fix" the drift.

**Validation:** `docs/build_site.sh <scratch>` emits exactly `index.html`, `showcase-analysis-tree.html`, `showcase-after-planning.html`, `showcase-mid-implement.html`, all non-empty. The after-planning page shows all three tasks `not-started` (rollup 0/3) with no Results; the mid-implement page shows the mixed composition (01-data green, 02-analysis yellow with its figures inlined, 03-writeup grey, rollup 1/3); both render with full chrome (status pills, DAG, Kanban toggle). No fixture file is committed into the live `superRA/showcase-analysis` tree. Record the capture commands so the fixtures regenerate.

## Results

_Not started._
