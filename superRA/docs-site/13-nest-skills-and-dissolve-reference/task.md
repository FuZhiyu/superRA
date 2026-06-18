---
title: "Nest Skills Pages + Dissolve Reference into Progressive Subpages"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Restructure the `docs/site/` documentation tree so it uses the task tree's own nesting for progressive disclosure instead of flat pages plus a separate Reference section. The site already dogfoods the task tree (each node's `## Objective` renders as one page); this work makes the *shape* of that tree teach the material — a high-level overview at the top, a page per skill below it, and the operational detail one level deeper still, revealed only when the reader descends.

Three structural moves, detailed in the child tasks:

1. **Domain Skills and Utility Skills become overviews with a page per skill.** `03-domain-skills/` and `04-utility-skills/` keep only a short framing plus a one-line entry per skill; each skill's high-level design moves to its own child page. Domain skills get one page each. Utility skills get one page each, and may get a further detail subpage where genuine human-facing internals overflow the page.
2. **The task-tree skill's reference detail nests under it.** The current `05-reference/01-task-file`, `02-cli-commands`, and `03-status-and-frontier` pages move to become children of `04-utility-skills/01-task-tree/`, so the task-tree page explains the high-level design and its subpages carry the field tables, CLI surface, and status mechanics.
3. **The standalone Reference section is dissolved.** Its cross-cutting pages — `05-glossary`, `06-faq`, `07-hooks` — are promoted to top-level pages; `04-skills-and-agents` is dropped (its inventory is already carried by the two skills overview pages, and its Stage→load manifest is internal); `06-showcase` is renumbered to keep its place at the end.

### Conventions

- **Authoring contract.** Every page follows the docs-tree authoring contract in `superRA/docs-site/01-information-architecture` §3 — `title`-only frontmatter, page body under `## Objective`, numeric-prefix ordering, hash links `#/<path>` for cross-page links, repo-file links re-based by the export, `attachments/` for figures, public-repo hygiene. Task `01-ia-and-scaffold` revises that contract for this structure before any content task runs; build to the revised contract, not this summary.
- **Audience model is unchanged.** The reader model and teaching inventory in `01-information-architecture` §1 carry over verbatim — a researcher who knows git and a harness but none of superRA's vocabulary. Progressive disclosure serves that reader; it does not change who the reader is.
- **User-facing, not agent-facing.** Every page is written for the researcher *using* the skill — the commands they run, the dashboard features they click, the moments they reach for it — not for the agent the skill instructs. When a skill exposes user-visible functionality, surface it: the task-tree dashboard's static export (shareable HTML snapshots), task comments (the human-in-the-loop steering channel), and running tasks across parallel worktrees all belong on the page, framed as things the researcher does. See `feedback_docs_audience_high_level_not_internals`.
- **Writing domain.** Implementers load the `writing` skill for every page — this is reader-facing prose. Apply its audience-first discipline; lead each page with what the reader gets, then when to reach for it; no AI-flavored prose (`feedback_no_ai_flavored_prose`).
- **Authority, not paraphrase.** Doc pages teach the human journey and link to the canonical skill/agent file for behavior detail. A detail subpage is a human-facing orientation plus a link to the authoritative skill reference — never a second copy of agent-facing discipline that would drift (`CLAUDE.md` §Ownership Boundaries).
- **Relocations preserve content and repoint links.** Moving a page keeps its prose and updates every `#/...` link that targeted it. No page's teaching is dropped in a move except the deliberately-dropped `skills-and-agents`.

### Context

This is the next iteration of the `docs-site` restructure line that `12-condense-and-restructure` began; that subtree (approved, 9/9) built the current two flat skills pages and the quickstart-centered spine. This task tree nests those pages and dissolves the Reference section it left in place. The current site tree is inspectable with `./superRA/superra task tree --root docs/site`.

### Constraints

- Doc sources under `docs/site/` are committed; generated site HTML is CI-built and never committed.
- Verify rendering through the doc-mode build (the live serve or static export), not a `file://` open — inlined CSS and hash routing need the real build to exercise links. See `feedback_preview_dashboard_css_live_not_file`.

## Results

