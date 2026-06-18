---
title: "Make the Real Study the Sole Showcase Example (Retire the Simulated Demo)"
status: in-progress
depends_on:
  - 13-real-analysis-showcase
tags: []
created: 2026-06-17
---

## Objective

Retire the simulated demo tree everywhere it appears and make the real CAPM-vs-FF3 [showcase-analysis](../../showcase-analysis/task.md) study the single canonical example the documentation uses — in both the Showcase page and the Quickstart. Also drop the `superRA` development-tree export from the site: at ~13 MB it is the only genuinely-too-large page, and the real study (~1.9 MB) is the better existence proof. The Quickstart presents the workflow arc through **links to live, explorable study exports** at three workflow moments rather than embedded screenshots — crisper to read and lighter on the framing page (no inlined PNGs).

This supersedes the simulated-demo deliverable of [07-showcase](../07-showcase/task.md) and completes the transition [13-real-analysis-showcase](../13-real-analysis-showcase/task.md) began: `13` added the real study *alongside* the demo and dev trees; this subtree removes those two and leaves the real study as the only showcase tree.

### Context

- The site started emitting four files via [docs/build_site.sh](../../../docs/build_site.sh): `index.html` (docs, doc-mode), `demo-tree.html` (simulated), `superra-dev-tree.html` (dev tree, ~13 MB), `showcase-analysis-tree.html` (real study). `01` retired the demo and dev trees; `02` adds two fixture-built progression exports. Final target is four: `index.html`, `showcase-analysis-tree.html` (complete state), `showcase-after-planning.html`, `showcase-mid-implement.html`.
- The Quickstart's running example was the simulated toy, narrated with embedded dashboard screenshots. It now narrates the real study and links the three live progression exports (after-planning / mid-implement / complete) instead of embedding any screenshot — crisper text, deep links, and the Kanban toggle, all in the reader's hands. The toy PNGs and the real-tree screenshot PNGs are both removed.
- Exports are single self-contained HTML files with all assets base64-inlined; there is no lazy loading. Linking the progression pages (loaded only on click) instead of inlining their screenshots keeps `index.html` light. The two historical states are not durably reachable from git at CI build time (shallow checkout + squash-merge to `main` collapse the source commits), so they are committed as frozen fixtures under `docs/showcase-fixtures/` and exported from there; the matplotlib study-result figures are left as captured.

### Constraints

- The real study's exported tree keeps the **full task-tracker chrome** (the standard `generate`, never `--doc-mode`), exactly as `13` set up.
- Exports are CI-built, never committed; only sources (build script, framing/quickstart edits, and the committed historical-state fixtures under `docs/showcase-fixtures/`) are committed.
- Public repo: no personal data, real group names, or private paths. The study uses public Ken French data, so the Quickstart example stays reproducible.

## Planner Guidance
Four children. `01` (retire demo + dev tree, two-export baseline) and `03` (rewrite Showcase page) are done. `02` (fixture-built progression exports) extends `01`'s build script; `04` (re-narrate Quickstart, link the live exports, delete orphaned PNGs) depends on `02`'s exports and `03`'s page. Implement `02` then `04`.
