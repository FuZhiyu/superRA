---
title: "Utility Skills: Overview + One Page Per Skill"
status: not-started
depends_on: 
  - 01-ia-and-scaffold

tags: []
created: 2026-06-17
---

## Objective

Turn `04-utility-skills/` from one flat page into an overview over one page per utility skill.

**Overview page (`docs/site/04-utility-skills/task.md`):** keep the framing (domain-neutral capabilities the workflow composes; several usable directly; agents reach for them automatically or you name them) and replace the eight inline skill sections with a one-line entry per skill that links to its page.

**One page per skill** (stubs scaffolded by `01`), each carrying the skill's high-level design from the current flat page as a standalone page linking to its `SKILL.md`:

- `01-task-tree` — high-level design only: filesystem-is-the-task-hierarchy, status rollup, the dispatchable frontier, the live dashboard. Its operational detail (task-file anatomy, CLI surface, status mechanics) is **not** on this page — those become its child pages in task `04`. This page should read as the conceptual top of that subtree and point down to the detail children.
- `02-semantic-merge`, `03-result-protection`, `04-refactor-and-integrate`, `05-report-in-markdown`, `06-worktree-data-sync`, `07-zotero-paper-reader`, `08-mistral-pdf-to-markdown` — one page each, the current per-skill prose as a standalone page.

**Detail subpages where internals overflow (judgment, not mandate).** Domain skills get one page; utility skills may get a further detail page where genuine human-facing internals would bloat the overview page. Apply this test per skill: *is there a body of human-facing operational detail (a CLI surface, mode mechanics, a flag table) too large for the skill page and useful to a reader who descends?* If yes, create a detail child; if the detail authority is just the SKILL.md, keep one page and link. Likely candidates: `06-worktree-data-sync` (seed / diff / apply modes and their CLI) and `05-report-in-markdown` (figure / math / table conventions). `01-task-tree`'s detail children are out of scope here — task `04` owns them. Do not invent detail pages that only paraphrase a SKILL.md.

This task owns the `01-task-tree` page itself but **not** its children; task `04` depends on this page existing and adds the three reference subpages beneath it.

Prose quality: load the `writing` skill; lead each page with what the reader gets, then when to reach for it; no AI-flavored prose (`feedback_no_ai_flavored_prose`); authority-not-paraphrase per the root Conventions.

Validation: the overview links resolve to all eight pages; each page stands alone; any detail subpage created passes the overflow test rather than duplicating its SKILL.md; no teaching from the current flat page is lost.

## Results

