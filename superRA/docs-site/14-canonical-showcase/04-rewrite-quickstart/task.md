---
title: "Re-narrate the Quickstart Around the Real Study"
status: approved
depends_on:
  - 02-progression-exports
  - 03-rewrite-showcase-page
tags: []
created: 2026-06-17
---

## Objective

Make the real CAPM-vs-FF3 [showcase-analysis](../../../showcase-analysis/task.md) study the Quickstart's single running example, replacing the simulated toy throughout [docs/site/02-quickstart/task.md](../../../../docs/site/02-quickstart/task.md), and spine the page with **links to the live progression exports** rather than embedded screenshots.

- **Running-example framing.** Replace the "toy size-and-momentum sort on *simulated* equity returns" framing (the intro and the "A typical workflow" / Superplan prompt) with the real study: estimate CAPM and the Fama-French three-factor model on Ken French's 25 size–B/M portfolios and run the GRS joint test. The data are public (Ken French), so the example stays reproducible. Keep the day-one "point superRA at work you already have" advice intact.
- **Inline results block.** Replace the simulated-panel `## Results` excerpt with the real study's data-task results — drawn from [showcase-analysis/01-data](../../../showcase-analysis/01-data/task.md)'s `## Results` — so the example output is the real one the reader can open in the Showcase.
- **Link the live progression exports instead of embedding screenshots.** [02-progression-exports](../02-progression-exports/task.md) builds three live, full-chrome study pages; the Quickstart links them at the natural points in the workflow arc rather than embedding any PNG:
  - **After planning** → `showcase-after-planning.html` (the freshly-planned frontier, all `not-started`).
  - **Mid-implement** → `showcase-mid-implement.html` (the mixed-status moment that shows the rollup and pills doing real work).
  - **Complete** → `showcase-analysis-tree.html` (the all-`approved` tree). For "reading a finished task" use a deep link into it (`showcase-analysis-tree.html#/02-analysis`); for the at-a-glance board, tell the reader to toggle the Kanban view in that page (it has no URL route). Phrase each as an invitation to open and explore the live tracker, noting the reader can click any task and switch views.
  - These pages are local to the built site, so use bare relative hrefs (e.g. `[Open the freshly-planned tree →](showcase-after-planning.html)`); `02-progression-exports` registers them with `--doc-local-link` so they are not rebased to GitHub blob URLs.
- **Delete the orphaned screenshot PNGs.** The five dashboard PNGs under `13-real-analysis-showcase/02-quickstart-screenshots/attachments/` (`showcase-after-planning.png`, `showcase-mid-implement.png`, `showcase-complete.png`, `showcase-task-detail.png`, `showcase-kanban.png`) are no longer embedded anywhere once the Quickstart links the live pages — remove them. Confirm via `grep` that no `docs/**` markdown still references them. (The matplotlib study-result figures under `showcase-analysis/*/attachments/` are unrelated; leave them.)
- **Fold the "same arc on a real project" coda.** The whole Quickstart is now the real study, so the separate `#### The same arc on a real project` section is redundant; use the three progression links as the natural spine of the Superplan / Superimplement / Watch sections, and make sure no link is duplicated.
- **Sweep toy wording.** Fix "this toy", "rather than this toy", "simulated", and the closing pointer to the Showcase so it reads as "open and explore the same study" rather than "a real project rather than this toy".

Hold the page's structure (Superplan → Superimplement → Watch & read → Superintegrate → Where to go next) and voice; audience is academic researchers new to superRA. Verify all links resolve and `report-in-markdown` self-diagnose is clean.

**Validation:** the Quickstart narrates the real study end to end with no simulated-toy remnants; the three progression links and the deep link resolve in the built `index.html` (open the built page and click through); the page embeds no dashboard screenshots; the five orphaned PNGs are gone and nothing under `docs/**` references them; `report-in-markdown` self-diagnose clean.

## Results

Re-narrated [docs/site/02-quickstart/task.md](../../../../docs/site/02-quickstart/task.md) so the real CAPM-vs-FF3 study is its single running example and the workflow arc is spined by **links to the live progression exports** instead of embedded screenshots. The intro and running-example framing already named the real study (from an earlier pass); this pass removed the screenshot scaffolding and the toy/screenshot framing that remained.

**Embeds → live links.** Replaced all five embedded dashboard PNGs with bare relative links to the three progression exports, placed at the natural points in the arc:

- **Superplan section** → `[Open the freshly-planned tree →](showcase-after-planning.html)` (the all-`not-started` frontier; invites clicking a task and the dependency-graph view).
- **Superimplement section** → `[Open the study mid-implement →](showcase-mid-implement.html)` (the mixed-status moment; invites clicking the `implemented` task to see results awaiting review).
- **Watch & read section** → `[Open the finished study →](showcase-analysis-tree.html)` (all-`approved`) plus a deep link `[Read the finished regression task →](showcase-analysis-tree.html#/02-analysis)`. The Kanban board has no URL route, so the prose tells the reader to toggle the view switch at the top of the page rather than linking it.

The links are bare relative hrefs (basename only), matching `02-progression-exports`'s `--doc-local-link` registration; verified in the build that none was rebased to a GitHub blob URL.

**Toy/screenshot sweep.** No `toy`, `simulated`, `screenshot`, or "same arc on a real project" remnants remain (`grep -niE` clean). There was no separate `#### The same arc on a real project` coda to fold — the whole page is now the real study, so the three progression links are the spine of Superplan / Superimplement / Watch with no duplicated link. The inline `## Results` block and the closing Showcase pointer were already faithful to the real study (panel 754 months × 29 cols, 1:1 inner merge, market premium 0.597%/mo, vol 4.47%/mo — matching [showcase-analysis/01-data](../../../showcase-analysis/01-data/task.md)).

**Orphaned PNGs deleted.** Removed all five PNGs under `13-real-analysis-showcase/02-quickstart-screenshots/attachments/` (`showcase-after-planning.png`, `showcase-mid-implement.png`, `showcase-complete.png`, `showcase-task-detail.png`, `showcase-kanban.png`). `grep -rn` over `docs/**` finds zero references to any of them.

**Verification (built the site to a scratch dir and inspected the rendered output, not just the source).**

- `bash docs/build_site.sh /tmp/qs-build` produced all four files (`index.html`, `showcase-analysis-tree.html`, `showcase-after-planning.html`, `showcase-mid-implement.html`).
- Extracted the quickstart task body from the embedded JSON in `index.html`: **0 `.png` references, 0 `![` image embeds** — no dashboard screenshots survive. All three progression links and the `#/02-analysis` deep link present exactly once each and not rebased to blob URLs.
- All three link targets exist and are non-trivial (1.1 / 1.7 / 1.9 MB); the `02-analysis` route is present in `showcase-analysis-tree.html` (4 occurrences), so the deep link resolves.
- `report-in-markdown` self-diagnose on the quickstart page: clean.

**Caveat — stale sibling task (out of my scope).** The approved task [13-real-analysis-showcase/02-quickstart-screenshots](../../13-real-analysis-showcase/02-quickstart-screenshots/task.md) captured and embedded the five PNGs I just deleted; its `## Results` and table now reference attachments that no longer exist, and its deliverable (screenshots embedded in the Quickstart) is superseded by this `14-canonical-showcase` subtree. It is a different, already-`approved` task, so I did not edit it. The orchestrator/planner should retire or annotate it. The task spec's grep target (`docs/**`) is clean; the dangling references are confined to `superRA/docs-site/...` task files.
