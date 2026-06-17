---
title: "Condense & Restructure: Quickstart-Centered Docs + Two Skills Pages"
status: approved
depends_on:
  - 11-dashboard-first-messaging
tags: []
created: 2026-06-17
---

## Objective

Restructure the documentation site from the original Diátaxis-style six-section layout (Welcome / Quickstart / Concepts / How-To / Reference / Showcase) into a lean, quickstart-centered structure. The current site is repetitive and verbose: concepts are explained in a standalone section *and* re-explained in the quickstart *and* again in how-to guides. This subtree collapses that into one narrative spine plus two new skill-introduction pages, and **prunes aggressively** — the Concepts and How-To sections are deleted, not migrated.

This supersedes the IA decision made in [`01-information-architecture`](../01-information-architecture/task.md) (Diátaxis split). That task's `## Results` is updated to record the new structure as the authoritative sitemap.

### Target structure

Six top-level pages (down from 21):

| Dir | Page | Disposition |
|---|---|---|
| `01-welcome` | Front door | **Keep** — pitch, why-not-Superpowers, three-phase shape. Light alignment only (fix "Start here" links to the new pages). |
| `02-quickstart` | The walkthrough | **Rewrite** — one end-to-end narrative (setup → superplan → superimplement → superintegrate), introducing every concept *inline along the way*, with details linked to Reference. Dashboard-first. Ends by directing the reader to the two skills pages. |
| `03-domain-skills` | Domain Skills | **New** — introduce each domain skill one by one with its high-level design idea. |
| `04-utility-skills` | Utility Skills | **New** — introduce each utility skill one by one with its high-level design idea. |
| `05-reference` | Reference | **Keep as-is** — a lookup/fallback home, *not* part of the reading flow. Do not condense it; just repoint any links that pointed at dropped pages. |
| `06-showcase` | Showcase | **Keep** — embedded real task-tree export. |

**Dropped entirely:** `03-concepts` (5 pages) and `04-how-to` (6 pages). Their essential ideas survive only inline in the quickstart and the two skills pages; everything that does not fit there is cut. Do not recreate how-to/concepts content inside Reference.

The numbering works out: deleting `03-concepts` and `04-how-to` frees `03`/`04` for the two new pages; `05-reference` and `06-showcase` keep their numbers.

### Audience — write for adopters, not contributors

This is the governing principle for every page in this subtree. Readers are researchers deciding whether and how to adopt superRA. They need the **high-level design ideas** that let them adopt it well — not internal implementation detail.

- **Surface behavior and the design intent.** Example: "saying `superra` triggers the workflow" is what the reader needs.
- **Omit the wiring.** Example: *how* the hook is registered or fires is contributor detail — leave it in `CLAUDE.md`/skill files, out of the docs.
- When in doubt, ask: does the reader need this to *use or extend* superRA, or only to *understand its internals*? If the latter, cut it.

### Writing header (inherited by all children)

**Writing workflow:** Draft / Polish workflow

**Writing targets:** all pages under `docs/site/` — rewrite `02-quickstart`, create `03-domain-skills` and `04-utility-skills`, align `01-welcome`, delete `03-concepts` and `04-how-to`, sweep links in `05-reference`/`06-showcase`/`build_site.sh`.

**Audience:** academic researchers evaluating or adopting superRA — comfortable with git and an AI harness (Claude Code or Codex), not assumed to know plugin internals or superRA terminology. Teach high-level design ideas, not internals (see above).

**Mode:** Draft

**Build command:** `docs/build_site.sh` (or `uv run --script skills/task-tree/scripts/plan_dashboard.py dashboard --doc-mode --root docs/site` for live preview).

**Writing output:** edited/created `task.md` doc pages.

### Conventions

- Doc-page authoring contract (frontmatter `title` only at render; numeric-prefix ordering; `#/<path>` cross-page hash links; `--repo-file-base` repo-file links; `attachments/` for screenshots) is set by [`01-information-architecture`](../01-information-architecture/task.md) — follow it unchanged except for the structural changes above.
- The user's design sketch for `02-quickstart` (section headers + inline `<!-- ... -->` comments) is committed on this branch as the **design baseline**. It encodes the user's intent; the child task objectives below distill that intent so implementers do not depend on reading the raw comments. Resolve and remove the `<!-- -->` comments in the rewrite.

## Planner Guidance

`skills/CATEGORIES.md` is the authoritative grouping for the Domain vs Utility split used by `03`/`04`. `skills/using-superRA/SKILL.md §Skill-Load Manifest` is the runtime authority. Keep the skill pages thin — a framing plus the design idea beats a paraphrase of each SKILL.md that will drift.
