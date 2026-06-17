---
title: "Propagate Dashboard-First Framing Across Docs"
status: not-started
depends_on: 
  - 01-front-door-and-welcome

tags: []
created: 2026-06-17
---

## Objective

Propagate the dashboard-first framing (subtree-root §Context) from the front door into the docs-site pages that describe what superRA is or where the dashboard already appears, so the elevation is coherent site-wide rather than confined to the welcome page. Depends on `01-front-door-and-welcome` — reuse the canonical dashboard wording established there; do not invent a competing phrasing.

This is a targeted sweep, not a rewrite of every page. Touch a page only where the dashboard is under-sold or its monitoring/handoff role is missing:

- **`docs/site/03-concepts/02-the-task-tree/task.md`** — the task-tree concept page is the natural home for "the tree is also a live dashboard": add a short framing that the same committed tree is what the dashboard renders (monitoring + handoff), linking to the See-Your-Work how-to as the operational guide. Read the page first; integrate, don't bolt on.
- **`docs/site/04-how-to/04-see-your-work/task.md`** — the dashboard how-to. It already documents the mechanics well; add at most a one-line lead establishing the dashboard as the primary way to monitor and hand off work (not merely "see" it), and ensure it is reachable as a lead feature. Do not duplicate the welcome page's pitch here.
- **`docs/site/06-showcase/task.md`** — strengthen the dogfooding hook only if it is not already explicit: the showcase is rendered by the same dashboard, and this whole site is a dashboard export.

Survey the other dashboard-mentioning pages (`03-concepts/*`, reference pages) and leave them unchanged unless a mention actively undersells or contradicts the elevated framing — record any you deliberately left alone in `## Results`.

Follow the authoring contract (`01-information-architecture` §3): link to owning skill/reference files as authority rather than paraphrasing; terminology matches the glossary ("task tree", "frontier", "stage"); one paragraph per line; hash/`#/` cross-page links; public-safe content.

Validation: render the touched pages in doc-mode (subtree-root Build command); every new cross-link resolves to a real node; the dashboard framing is consistent with the wording in `01`; `## Results` lists both the pages changed and the dashboard-mentioning pages deliberately left unchanged.

## Results

