---
title: "Revise IA Contract + Scaffold New Page Stubs"
status: not-started
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Make the new structure authoritative and lay down empty homes for the two new pages, so the content tasks (`02`–`04`) and the finalize task (`05`) have a stable contract and stable link targets to build against.

Two deliverables:

1. **Revise the authoritative IA.** Update `## Results` in [`docs-site/01-information-architecture`](../../01-information-architecture/task.md) so its sitemap and disposition tables reflect the new six-page structure (per the parent objective's target-structure table), replacing the Diátaxis quadrant model. Keep the audited audience model and the doc-tree authoring contract; only the sitemap/section split changes. Note the supersession in place (this is a state update, not an append — no "Previously…" block).

2. **Scaffold the two new page directories** under `docs/site/`:
   - `03-domain-skills/task.md`
   - `04-utility-skills/task.md`

   Each stub carries frontmatter (`title`, `status: not-started`, empty `depends_on`/`tags`, `created`) and a one-paragraph `## Objective` placeholder naming what the page will teach. Content is authored by `03`/`04`. Match the frontmatter shape of the existing `docs/site/*/task.md` pages.

Do **not** delete `03-concepts` or `04-how-to` yet — they remain valid link targets until the content tasks have repointed away from them; deletion happens in `05-finalize`.

## Planner Guidance

The new page directories sit beside the existing `docs/site/03-concepts` and `04-how-to` during the transition (two `03-*`/`04-*` siblings temporarily). The doc-mode renderer orders by directory name, so the temporary collision is cosmetic and resolved when `05` deletes the old dirs.
