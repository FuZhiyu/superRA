---
title: "Revise IA Contract + Scaffold New Page Stubs"
status: approved
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

## Results

Both deliverables are in place; the new six-page structure is now the authoritative IA contract and the two new pages have stable, renderable homes.

**1. IA contract revised.** Rewrote `## Results` in [docs-site/01-information-architecture/task.md](../../01-information-architecture/task.md) to make the quickstart-centered structure authoritative, replacing the Diátaxis quadrant model:

- **Supersession noted in place** (not appended): a single labeled paragraph records that the original six-section Diátaxis layout (approved 2026-06-11) was superseded 2026-06-17, why (the Concepts/Quickstart/How-To repetition), and points at the [`12-condense-and-restructure`](../task.md) subtree. The document otherwise reads as one current-state description — no "Previously…" blocks or strikethroughs.
- **§2 sitemap** now lists the six top-level pages (`01-welcome`, `02-quickstart`, `03-domain-skills`, `04-utility-skills`, `05-reference`, `06-showcase`) with teaches/authority/owning-task columns, plus an explicit "Dropped from the tree" note for `03-concepts` (5 pages) and `04-how-to` (6 pages) marking deletion as deferred to `05-finalize`.
- **§1 audience model kept**, with only the section-label dependent pieces updated: the knowledge-state table and the teaching-inventory "owning page" columns now point at the surviving pages (concepts fold inline into the Quickstart; journeys map to Quickstart stages; domain/utility skills get their two pages). The audience reasoning itself is unchanged.
- **§3 authoring contract kept** verbatim except the one stale cross-page-link example (now `#/03-domain-skills`) and a numbering reference.
- **§4 README split** dispositions repointed off the dropped pages onto surviving homes (workflow → welcome + quickstart; dashboard → quickstart; domain/utility skills → the two new pages + reference; install pointer → welcome).

Stale-reference sweep confirms only the intentional supersession-note mentions of "Diátaxis" remain; the old content-task slugs (`03-landing-and-concepts`, `04-quickstart-tutorial`, `05-how-to-guides`, `06-reference`, `07-showcase`) and quadrant page labels are gone. Markdown self-diagnose reports the file clean.

**2. New page stubs scaffolded** under `docs/site/`, matching the existing pages' frontmatter shape (`title`, `status: not-started`, `depends_on:  []`, `tags: []`, `created`), each with a one-paragraph `## Objective` placeholder naming what the page teaches and its owning content task:

- [docs/site/03-domain-skills/task.md](../../../../docs/site/03-domain-skills/task.md) — introduces each domain skill with its high-level design idea.
- [docs/site/04-utility-skills/task.md](../../../../docs/site/04-utility-skills/task.md) — introduces each utility skill with its cross-cutting capability.

`./superRA/superra task tree --root docs/site` renders both new stubs with their titles, sitting beside the still-present `03-concepts`/`04-how-to` directories (cosmetic numeric collision, resolved in `05-finalize` per Planner Guidance). The old directories were left in place as valid link targets, per the objective.
