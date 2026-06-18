---
title: "Make the Real Study the Sole Showcase Example (Retire the Simulated Demo)"
status: not-started
depends_on:
  - 13-real-analysis-showcase
tags: []
created: 2026-06-17
---

## Objective

Retire the simulated demo tree everywhere it appears and make the real CAPM-vs-FF3 [showcase-analysis](../../showcase-analysis/task.md) study the single canonical example the documentation uses — in both the Showcase page and the Quickstart. Also drop the `superRA` development-tree export from the site: at ~13 MB it is the only genuinely-too-large page, and the real study (~1.9 MB, shrinking further after screenshot compression) is the better existence proof.

This supersedes the simulated-demo deliverable of [07-showcase](../07-showcase/task.md) and completes the transition [13-real-analysis-showcase](../13-real-analysis-showcase/task.md) began: `13` added the real study *alongside* the demo and dev trees; this subtree removes those two and leaves the real study as the only showcase tree.

### Context

- Today's site emits four files via [docs/build_site.sh](../../../docs/build_site.sh): `index.html` (docs, doc-mode), `demo-tree.html` (simulated), `superra-dev-tree.html` (dev tree, ~13 MB), `showcase-analysis-tree.html` (real study). The target is two: `index.html` + `showcase-analysis-tree.html`.
- The Quickstart's running example and its three inline screenshots (`docs/site/02-quickstart/attachments/dashboard-*.png`) are the simulated toy; the real study's three progression screenshots already exist under [13-real-analysis-showcase/02-quickstart-screenshots/attachments](../13-real-analysis-showcase/02-quickstart-screenshots/attachments/).
- Exports are single self-contained HTML files with all assets base64-inlined; there is no lazy loading, so inlined-figure weight is the only non-fixed page weight. Flat-UI dashboard screenshots quantize ~60% smaller at 256 colors with no visible loss; the matplotlib study-result figures are left as captured.

### Constraints

- The real study's exported tree keeps the **full task-tracker chrome** (the standard `generate`, never `--doc-mode`), exactly as `13` set up.
- Exports are CI-built, never committed; only sources (build script, framing/quickstart edits, committed screenshot PNGs) are committed.
- Public repo: no personal data, real group names, or private paths. The study uses public Ken French data, so the Quickstart example stays reproducible.

## Planner Guidance
Four children. `01` (build/CI) and `02` (screenshots) are independent and parallelizable; the two prose rewrites follow — `03` needs `01`'s build shape, `04` needs `02`'s screenshots.
