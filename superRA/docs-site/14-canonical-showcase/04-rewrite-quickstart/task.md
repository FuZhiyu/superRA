---
title: "Re-narrate the Quickstart Around the Real Study"
status: approved
depends_on:
  - 02-screenshots
tags: []
created: 2026-06-17
---

## Objective

Make the real CAPM-vs-FF3 [showcase-analysis](../../../showcase-analysis/task.md) study the Quickstart's single running example, replacing the simulated toy throughout [docs/site/02-quickstart/task.md](../../../../docs/site/02-quickstart/task.md).

- **Running-example framing.** Replace the "toy size-and-momentum sort on *simulated* equity returns" framing (the intro and the "A typical workflow" / Superplan prompt) with the real study: estimate CAPM and the Fama-French three-factor model on Ken French's 25 size–B/M portfolios and run the GRS joint test. The data are public (Ken French), so the example stays reproducible. Keep the day-one "point superRA at work you already have" advice intact.
- **Inline results block.** Replace the simulated-panel `## Results` excerpt with the real study's data-task results — drawn from [showcase-analysis/01-data](../../../showcase-analysis/01-data/task.md)'s `## Results` — so the example output is the real one the reader can open in the Showcase.
- **Screenshots.** Replace the three toy screenshots (`docs/site/02-quickstart/attachments/dashboard-workspace.png`, `dashboard-kanban.png`, `dashboard-task-detail.png`) with the real-tree shots in `13-real-analysis-showcase/02-quickstart-screenshots/attachments/` (compressed by `02-screenshots`): the Workspace shot for the post-plan view, the new task-detail shot for reading results, and the new Kanban shot for the at-a-glance view (or the Workspace views if `02` dropped the Kanban shot). Delete the now-orphaned toy PNGs under `docs/site/02-quickstart/attachments/`.
- **Fold the "same arc on a real project" coda.** The whole Quickstart is now the real study, so the separate `#### The same arc on a real project` section (which used the three progression shots) is redundant. Use the progression shots (after-planning → mid-implement → complete) as the natural spine of the Superplan / Superimplement / Watch sections instead, and make sure no screenshot is embedded twice.
- **Sweep toy wording.** Fix "this toy", "rather than this toy", "simulated", and the closing pointer to the Showcase so it reads as "open and explore the same study" rather than "a real project rather than this toy".

Hold the page's structure (Superplan → Superimplement → Watch & read → Superintegrate → Where to go next) and voice; audience is academic researchers new to superRA. Verify all links resolve and `report-in-markdown` self-diagnose is clean.

**Validation:** the Quickstart narrates the real study end to end with no simulated-toy remnants; the embedded screenshots are the real-tree ones and each appears once; the orphaned toy PNGs are gone; links resolve; self-diagnose clean. Render the built page and confirm the images inline and display in order.

## Results

Re-narrated [docs/site/02-quickstart/task.md](../../../../docs/site/02-quickstart/task.md) end to end around the real CAPM-vs-FF3 [showcase-analysis](../../../showcase-analysis/task.md) study. The simulated toy is gone; every screenshot, the running-example framing, the Superplan prompt, the inline results, and the closing pointer now describe the real study. The page keeps its structure (Superplan → Superimplement → Watch & read → Superintegrate → Where to go next) and its plain, substance-first voice.

**Edits made:**

- **Framing.** Intro now sets up the real study — estimate CAPM and FF3 on Ken French's 25 size-B/M portfolios, run the GRS joint test — and notes the public Ken French data make it reproducible, with a pointer to open the finished tree in the [Showcase](#/06-showcase). The "A typical workflow" lead and the Superplan prompt narrate the same study from scratch (download factors + 25 portfolios → regressions + GRS → writeup). The day-one "point superRA at work you already have" advice is untouched.
- **Inline results.** The simulated-panel `## Results` excerpt is replaced with a compact, faithful excerpt of the real data task's results drawn from [showcase-analysis/01-data](../../../showcase-analysis/01-data/task.md): the 754-month × 29-column panel over 1963-07 → 2026-04, the 1:1 inner merge with 0 unmatched, no within-sample gaps, and the published-scale factor magnitudes (market premium 0.597%/mo, σ 4.47%/mo).
- **Screenshots.** All three toy PNGs are deleted and the five compressed real-tree shots from [13-real-analysis-showcase/02-quickstart-screenshots/attachments](../../13-real-analysis-showcase/02-quickstart-screenshots/attachments/) now spine the page, each embedded once: `showcase-after-planning` (Superplan, post-plan Workspace), `showcase-mid-implement` (Superimplement, loop in flight), `showcase-kanban` (Watch, at-a-glance board), `showcase-task-detail` (Watch, reading the regression task), `showcase-complete` (the all-approved → INTEGRATE handoff). The redundant `#### The same arc on a real project` coda is removed — its three progression shots are now the natural spine.
- **Wording sweep.** No "toy", "simulat", "rather than this toy", or "real project rather than this toy" remains; the task-file path reference is corrected to `superRA/showcase-analysis/01-data/task.md`.

**Verification (this session):**

- `report-in-markdown` self-diagnose on the page: `clean`.
- All five screenshot relative paths resolve to real on-disk files from the quickstart directory.
- `docs/build_site.sh` builds the two intended files (`index.html`, `showcase-analysis-tree.html`) with no error.
- Real user path: rendered the built `index.html#/02-quickstart` in headless Chromium — all five `<img>` elements display from inlined `data:image` sources (naturalWidth > 0), in order: after-planning → mid-implement → kanban → task-detail → complete. The standalone export inlines figures via a client-side `{key → data-URI}` map (per `_build_standalone_images`), so each markdown ref keeps its relative path as the map key and resolves to base64 at render — the page is self-contained, no external fetch.
- `grep` confirms no `dashboard-workspace/-kanban/-task-detail` references remain anywhere under `docs/`, and the three orphaned PNGs are removed.
