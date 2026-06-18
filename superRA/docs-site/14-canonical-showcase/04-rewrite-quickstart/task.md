---
title: "Re-narrate the Quickstart Around the Real Study"
status: not-started
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
