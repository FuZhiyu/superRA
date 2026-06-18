---
title: "Nest Skills Pages + Dissolve Reference into Progressive Subpages"
status: approved
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Restructure the `docs/site/` documentation tree so it uses the task tree's own nesting for progressive disclosure instead of flat pages plus a separate Reference section. The site already dogfoods the task tree (each node's `## Objective` renders as one page); this work makes the *shape* of that tree teach the material — a high-level overview at the top, a page per skill below it, and the operational detail one level deeper still, revealed only when the reader descends.

Four structural moves, detailed in the child tasks:

1. **Domain Skills and Utility Skills become overviews with a page per skill.** `03-domain-skills/` and `04-utility-skills/` keep only a short framing plus a one-line entry per skill; each skill's high-level design moves to its own child page. Domain skills get one page each. Utility skills get one page each, and may get a further detail subpage where genuine human-facing internals overflow the page.
2. **The task-tree skill's reference detail nests under it.** The current `05-reference/01-task-file`, `02-cli-commands`, and `03-status-and-frontier` pages move to become children of `04-utility-skills/01-task-tree/`, rewritten concise and user-oriented, so the task-tree page explains the high-level design and its subpages carry the field tables, CLI surface, and status mechanics.
3. **The standalone Reference section is dissolved.** Its `07-hooks` page is promoted to a top-level `06-hooks`; `04-skills-and-agents` is dropped (its inventory is already carried by the two skills overview pages, and its Stage→load manifest is internal); `05-glossary` and `06-faq` are dropped, not promoted — their genuinely-useful facts are introduced on the relevant pages instead (phase questions on the workflows pages, merge-guard on the semantic-merge page, sharing/data-hygiene on the dashboard page), so the site carries no standalone glossary or FAQ; `06-showcase` is renumbered to `07-showcase` to keep its place at the end.
4. **A new top-level Workflows section is added.** `05-workflows/` is an overview over a page per phase — `01-plan`, `02-implement`, `03-integrate` — giving the researcher more detail on the three workflows than the quickstart's inline walkthrough, written user-facing and concise: what each phase does for them, what they invoke (`superplan`/`superimplement`/`superintegrate`), and the decisions they make along the way.

### Conventions

- **Authoring contract.** Every page follows the docs-tree authoring contract in `superRA/docs-site/01-information-architecture` §3 — `title`-only frontmatter, page body under `## Objective`, numeric-prefix ordering, hash links `#/<path>` for cross-page links, repo-file links re-based by the export, `attachments/` for figures, public-repo hygiene. Task `01-ia-and-scaffold` revises that contract for this structure before any content task runs; build to the revised contract, not this summary.
- **Audience model is unchanged.** The reader model and teaching inventory in `01-information-architecture` §1 carry over verbatim — a researcher who knows git and a harness but none of superRA's vocabulary. Progressive disclosure serves that reader; it does not change who the reader is.
- **Agent-first, not command-first.** Every page is written for the researcher *using* the skill, and the researcher uses it by asking an AI agent — they say `superra plan this`, "polish §3", "sync this branch" — not by running the CLI themselves. Lead with how to ask the agent; demote the command surface to a secondary section or subpage (full gate in the workstream `docs-site/task.md` §Conventions). When a skill exposes user-visible functionality the agent cannot stand in for — the task-tree dashboard's static export (shareable HTML snapshots), task comments (the human-in-the-loop steering channel), running tasks across parallel worktrees — surface it as something the researcher does. See `feedback_docs_audience_high_level_not_internals`.
- **Writing domain.** Implementers load the `writing` skill for every page — this is reader-facing prose. Apply its audience-first discipline; lead each page with what the reader gets, then when to reach for it; no AI-flavored prose (`feedback_no_ai_flavored_prose`).
- **Authority, not paraphrase.** Doc pages teach the human journey and link to the canonical skill/agent file for behavior detail. A detail subpage is a human-facing orientation plus a link to the authoritative skill reference — never a second copy of agent-facing discipline that would drift (`CLAUDE.md` §Ownership Boundaries).
- **Relocations preserve content and repoint links.** Moving a page keeps its prose and updates every `#/...` link that targeted it. The only deliberate drops are `skills-and-agents` (inventory absorbed into the overviews) and the standalone glossary/FAQ (facts folded into the pages that own them); no other page's teaching is lost in a move.
- **Skill-page quality bar (per-skill pages under `02`/`03`).** Each per-skill page is a concise operating manual, not a pitch and not a re-exposition of the skill. It does two things and stops: (1) names the specific failure a *bare* agent produces that this skill prevents — concretely, not gestured at (e.g. theory-modeling: an unaided agent invents fresh notation and lets one symbol silently mean two things; the skill forces reuse of existing, consistent notation); (2) shows how a researcher gets the value, where that is *not obvious* — the non-obvious usage and a concrete example prompt or two (e.g. writing: edit a section, leave it unstaged, ask the agent to polish the unstaged diff; drop an inline `% TODO:`/`[fill in]`; fence a block `DO NOT EDIT`), plus CLI/script usage or a genuinely tricky concept where one applies. Do not re-narrate the skill's internal discipline — modes, gates, checks, pitfall catalogs live in the `SKILL.md`, which is plain English; state the core idea in a sentence and link. Cut the obvious (an invocation line that just says "ask for it by name"). Per the workstream `docs-site/task.md` §Conventions conciseness gate, if a line does not change what the reader would do, cut it.

### Context

This is the next iteration of the `docs-site` restructure line that `12-condense-and-restructure` began; that subtree (approved, 9/9) built the current two flat skills pages and the quickstart-centered spine. This task tree nests those pages and dissolves the Reference section it left in place. The current site tree is inspectable with `./superRA/superra task tree --root docs/site`.

### Constraints

- Doc sources under `docs/site/` are committed; generated site HTML is CI-built and never committed.
- Verify rendering through the doc-mode build (the live serve or static export), not a `file://` open — inlined CSS and hash routing need the real build to exercise links. See `feedback_preview_dashboard_css_live_not_file`.

## Results

