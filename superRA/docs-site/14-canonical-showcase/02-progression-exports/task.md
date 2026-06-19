---
title: "Build Historical-State Live Exports From Committed Fixtures"
status: approved
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

Two frozen historical fixtures are committed under [docs/showcase-fixtures/](../../../../docs/showcase-fixtures/), and [docs/build_site.sh](../../../../docs/build_site.sh) now emits four pages: `index.html`, `showcase-analysis-tree.html` (complete state, unchanged), `showcase-after-planning.html`, and `showcase-mid-implement.html`. CI ([.github/workflows/docs-site.yml](../../../../.github/workflows/docs-site.yml)) rebuilds when `docs/showcase-fixtures/**` changes.

### Fixtures and how to regenerate them

Both fixtures are the `showcase-analysis` subtree as it stood at a past commit, extracted with `git show` and never disturbing the live tree. The statuses at each source commit were verified against the spec before extraction.

- **after-planning** (`de25a122`, freshly-planned frontier) — four `task.md` files, all `status: not-started`, no `## Results`, no figures:

  ```sh
  ap=docs/showcase-fixtures/after-planning/showcase-analysis
  mkdir -p "$ap" "$ap"/{01-data,02-analysis,03-writeup}
  git show de25a122:superRA/showcase-analysis/task.md             > "$ap/task.md"
  git show de25a122:superRA/showcase-analysis/01-data/task.md     > "$ap/01-data/task.md"
  git show de25a122:superRA/showcase-analysis/02-analysis/task.md > "$ap/02-analysis/task.md"
  git show de25a122:superRA/showcase-analysis/03-writeup/task.md  > "$ap/03-writeup/task.md"
  ```

- **mid-implement** (`805a247e`, 01-data approved / 02-analysis implemented / 03-writeup not-started, parent rolled up to in-progress) — same four `task.md` files plus only `02-analysis/attachments/` (the four figures the export inlines from 02-analysis's Results); the analysis code/data files and 03-writeup attachments are not rendered by a dashboard export, so they are omitted:

  ```sh
  mi=docs/showcase-fixtures/mid-implement/showcase-analysis
  mkdir -p "$mi" "$mi"/{01-data,02-analysis/attachments,03-writeup}
  git show 805a247e:superRA/showcase-analysis/task.md             > "$mi/task.md"
  git show 805a247e:superRA/showcase-analysis/01-data/task.md     > "$mi/01-data/task.md"
  git show 805a247e:superRA/showcase-analysis/02-analysis/task.md > "$mi/02-analysis/task.md"
  git show 805a247e:superRA/showcase-analysis/03-writeup/task.md  > "$mi/03-writeup/task.md"
  for f in fig1_alpha_grids fig2_realized_vs_predicted fig3_cumulative_factors fig4_ff3_hml_loadings; do
    git show "805a247e:superRA/showcase-analysis/02-analysis/attachments/$f.png" > "$mi/02-analysis/attachments/$f.png"
  done
  ```

The fixtures are intentionally frozen — they are **not** synced with later edits to the live `showcase-analysis` prose; the staleness shows the tree at a past moment. The build-script header comment near the fixture exports flags this so a future reader does not "fix" the drift, and points back here for the capture commands.

### Build wiring

The two new exports use the same full-chrome `generate` (never `--doc-mode`) and `--repo-file-prefix superRA/showcase-analysis` as the complete-state export, so in-task repo-file links resolve to the live tree. The `index.html` doc-mode build gained `--doc-local-link showcase-after-planning.html` and `--doc-local-link showcase-mid-implement.html` so the Quickstart's links to them stay relative. The required-input check, output-verification loop, final echo, and header comment all cover the four output files.

### Validation

`docs/build_site.sh <scratch>` exited 0 and wrote all four files non-empty: `index.html` (2.29 MB), `showcase-analysis-tree.html` (1.95 MB), `showcase-after-planning.html` (1.17 MB), `showcase-mid-implement.html` (1.68 MB).

Headless system-Chrome renders (`--headless --screenshot`) of the rendered DOM, not a file-exists check:

- **after-planning** — root pill `not-started (0/3)`; all three children `not-started`; no inlined figures (`data:image/png` count = 0 in the export).
- **mid-implement** — root pill `in-progress (1/3)`; 01-data `approved` (green), 02-analysis `implemented` (yellow), 03-writeup `not-started` (grey). Deep-linking `#/02-analysis` renders its four matplotlib figures inlined (alpha grids, realized-vs-predicted, cumulative factors, HML loadings) plus result tables; `data:image/png` count = 4 in the export, matching the four 02-analysis attachments.
- Both pages render with full task-tracker chrome — sidebar status pills, DAG legend, the Subtasks Kanban cards, and the Kanban toggle.

`git diff --stat superRA/showcase-analysis` is empty (the live tree is untouched), and the fixture PNGs are not gitignored (`git check-ignore` reports them not ignored), so they commit.
