---
title: "Elaborate the Over-Concise Reading-Flow Pages (Reader-Followability Pass)"
status: approved
depends_on:
  - 13-nest-skills-and-dissolve-reference
  - 14-canonical-showcase
tags: []
created: 2026-06-18
---

## Objective

The nested-IA and canonical-showcase rewrites condensed the reading-flow pages to the agent-first / non-obvious-only bar, but on read-back twelve pages came out too terse for a new adopter to follow. This pass elaborates each flagged page just enough to close the reader gap, then removes the inline directive markers.

The direction is captured as inline `<!-- ... -->` comments and rough draft prose the researcher left in the page bodies (committed at `f5574800`). Each marker is authoritative direction for that page: treat it as assigned work per `writing`'s inline-directive convention, and treat the adjacent rough prose as a polish target to land *with* the researcher's direction rather than revert toward the old terse text. A page is done only when every marker on it is resolved — elaborated into clean prose, then deleted.

### Conventions

This pass inherits the binding docs-site gates from the [parent objective](../task.md): agent-first framing, no AI-flavored prose, link-to-`SKILL.md`-as-authority, one paragraph per line. Two reconciliations are specific to this pass:

- **Elaborate to close reader gaps, not to re-narrate discipline.** The "explain only the non-obvious" gate still holds. Legitimate elaboration fills a real adopter gap the condensing dropped — how to actually invoke a skill, where to get an API key, the choice between two real modes, the design idea a reader needs to trust a phase. It is not license to re-expose a skill's internal step list, gate catalog, or pitfall inventory; that still lives in the `SKILL.md` the page links to.
- **Ground every elaboration in the actual skill source.** Where a marker asks for behavior detail (data-sync modes, the Mistral API key, Better BibTeX, the integrate-stage design ideas), read the owning `skills/<name>/SKILL.md` and its scripts/references and describe what is true. Do not invent flags, env-var names, or modes.

### Revision standard — second pass (depth bar)

The first pass resolved every marker but stayed too terse for a new adopter to follow. This second pass redoes each page to the depth demonstrated on [04-utility-skills/06-worktree-data-sync](../../../docs/site/04-utility-skills/06-worktree-data-sync/task.md) — that page is the worked reference; match its level. The before/after that defines the bar is commit `db54356c` (`git show db54356c` — read it before starting). Hold every redone page to:

- **Explain the important concepts, do not just name them.** Define any term an adopter may not know in plain language at first use — on the reference page, *symlink*, *copy-on-write (COW) clone*, and *APFS* each get a one-sentence plain explanation before they are relied on. A term the `SKILL.md` uses freely is not automatically known to a docs reader; if a sentence would stop a non-expert, explain the concept.
- **Lead with the user-facing decision; reach the mechanism through the prompt.** Open a section with the choice the reader actually makes ("there are two modes…"), and show how to invoke each option as the natural-language request to the agent ("seed with symlinks", "seed everything with COW clones"), not as a CLI flag. Flag names and raw commands stay in the page's hand-run / command section.
- **Make each non-obvious choice concrete with a worked example.** A vague mechanism (e.g. "add a tagged duplicate ignore line") gets a real code block and a short walk-through of what each part does, plus a sizing or consequence illustration where it helps a reader picture it.
- **State why the choice matters.** Give the consequence that makes an option meaningful — a copy isolates parallel worktrees, a symlink shares one file so a stray write reaches the source — not just what it is.
- **Break dense multi-topic paragraphs into scannable `###` subsections**, one idea per section, and forward-reference any mechanism explained later rather than assuming the reader already knows it.

This does not loosen the non-obvious-only gate: the added depth goes into closing real adopter gaps (what the term means, how to ask for it, why it matters), never into re-narrating a skill's internal step list, gate catalog, or pitfall inventory.

## Critical Files

- [docs/site/02-quickstart/task.md](../../../docs/site/02-quickstart/task.md) — quickstart narrative (child `01`)
- [docs/site/03-domain-skills/](../../../docs/site/03-domain-skills/) — three domain-skill pages (child `02`)
- [docs/site/04-utility-skills/](../../../docs/site/04-utility-skills/) — four utility-skill pages (child `03`)
- [docs/site/05-workflows/](../../../docs/site/05-workflows/) and [docs/site/06-hooks/task.md](../../../docs/site/06-hooks/task.md) — three workflow pages + hooks (child `04`)
- The owning `skills/*/SKILL.md` for each flagged skill — the authority each elaboration is grounded in

## Planner Guidance

Four children, each a same-domain (writing) bundle over disjoint files, all parallelizable — no inter-child dependencies. Group is by docs section: `01` quickstart, `02` domain skills, `03` utility skills, `04` workflows + hooks. Dispatch as four parallel implementer+reviewer pairs, or sequentially if running inline. Each child carries its page-by-page marker list verbatim so the implementer works from the researcher's own direction; the build/render-integrity check belongs to whoever lands the last child (a quick `plan_dashboard.py generate --doc-mode` over the docs tree, per the existing build path).
