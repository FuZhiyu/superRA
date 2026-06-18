---
title: "Dissolve Reference: Promote Hooks, Drop Glossary/FAQ/skills-and-agents, Renumber Showcase"
status: not-started
depends_on: 
  - 01-ia-and-scaffold
  - 03-utility-skills
  - 04-task-tree-reference-nesting
  - 06-workflows

tags: []
created: 2026-06-17
---

## Objective

Dissolve the standalone `05-reference/` section: promote the one cross-cutting page worth a top-level home, drop the three pages the rest of the restructure makes redundant, and renumber the showcase. The glossary and FAQ are not promoted — their useful content is folded into the relevant pages first, then the pages are deleted.

**Promote to a top-level page:**

- `05-reference/07-hooks` → `06-hooks`
- `06-showcase` → `07-showcase`

Sequence the moves to avoid transient prefix collisions. Use `./superRA/superra task move --root docs/site …` so frontmatter/ordering stay correct, or `git mv` with a manual pass. Repoint only the moved pages' own internal `#/…` links; the site-wide repoint of links *into* them is task `07`.

**Drop `05-reference/05-glossary` and `05-reference/06-faq`, folding their useful facts into the relevant pages first.** The site carries no standalone glossary or FAQ; terms are met inline where they first matter, and each genuinely-useful FAQ answer has a natural home. Before deleting, confirm each fact is carried:

- Phase questions (skip PLAN / skip INTEGRATE, direct vs. subagent mode, resuming an old project) → the `05-workflows/` pages (task `06`).
- The `merge-guard` reminder and intent-aware merging → the `04-utility-skills/02-semantic-merge` page; drift tests → `03-result-protection`.
- Public-repo data hygiene and sharing an export → the `04-utility-skills/01-task-tree/04-dashboard` page (and the site-wide hygiene convention).
- Harness choice (Claude Code vs. Codex) → already the Welcome install pointer.
- Glossary term definitions → introduced inline in the quickstart / the owning skill page where each term first appears.

If any genuinely user-facing fact has no home after this pass, add it to the most relevant page rather than losing it. Do not create a replacement glossary or FAQ page.

**Drop `05-reference/04-skills-and-agents`.** Confirm its content is carried or intentionally dropped: the domain/utility skill inventory is now the two overview pages plus their per-skill pages; implementer/reviewer and Stage are taught inline in the quickstart and the workflows pages; the Stage→skill load manifest is agent-internal and stays in `using-superRA`, not the user-facing site.

**Leave the empty `05-reference/` parent for task `07` to remove** after all relocations (task `04` also moves pages out of it); removing it here would race with `04`.

User-facing framing throughout: hooks is a reader lookup — what runs automatically and on which harness, not internal wiring. Load `writing`.

Validation: hooks renders at `06` with its content intact; showcase renders at `07`; glossary, FAQ, and `skills-and-agents` are gone with no user-facing fact orphaned (each fact traceable to a home page above); `05-reference/` holds only the pages task `04` is relocating.

## Results

