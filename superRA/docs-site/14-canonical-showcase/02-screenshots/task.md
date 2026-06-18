---
title: "Capture Task-Detail + Kanban Views and Compress All Quickstart Screenshots"
status: not-started
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Give the rewritten Quickstart the two dashboard views it still needs from the *real* study tree, and shrink every dashboard screenshot it uses.

- **Capture two new views** of the real [showcase-analysis](../../../showcase-analysis/task.md) tree, full chrome (the standard `generate` export, never `--doc-mode`), matching the existing progression shots in [13-real-analysis-showcase/02-quickstart-screenshots/attachments](../../13-real-analysis-showcase/02-quickstart-screenshots/attachments/):
  - **Task detail** — a single task open with its `## Objective` and `## Results` showing (e.g. `02-analysis`). Reachable headlessly via the hash route `#/<task-path>` the standalone export uses.
  - **Kanban** — the board view. The Kanban view is a `showView('kanban')` JS toggle with **no URL route** (documented in `13-real-analysis-showcase/02-quickstart-screenshots`), so a hash route will not reach it; capture it by invoking the toggle before the screenshot (Playwright `page.evaluate("showView('kanban')")`, or equivalent injected JS). If the toggle proves brittle on a three-task board — where a three-card Kanban is not very illustrative anyway — drop the dedicated Kanban shot and record that decision; `04-rewrite-quickstart` will lean on the Workspace views instead.
- **Compress all dashboard screenshots the Quickstart embeds** to 256-color palette PNG, in place, keeping the `.png` filenames so no markdown or inliner change is needed: the three existing progression shots (`showcase-after-planning.png`, `showcase-mid-implement.png`, `showcase-complete.png`) plus the two new captures. Use Pillow: `Image.open(p).convert("RGB").quantize(colors=256, method=Image.MEDIANCUT).save(p, optimize=True)`. Benchmarked ~60% reduction (≈400 KB → ≈170 KB) with no visible loss on flat-UI screenshots. Do **not** touch the matplotlib study-result figures under `showcase-analysis/*/attachments/`.
- **Commit** the new PNGs into the same `13-real-analysis-showcase/02-quickstart-screenshots/attachments/` directory as the existing shots, so the Quickstart's relative-path scheme stays uniform. Document the capture + compress recipe (commands, window size, the Kanban toggle step) so every image regenerates, extending the recipe already recorded in that task's `## Results`.

**Validation:** every committed PNG opens and shows its intended view/composition with text legible after quantization; each is meaningfully smaller than before (record before/after sizes); if the Kanban shot was dropped, the reason is recorded.
