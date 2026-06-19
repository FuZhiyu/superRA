---
title: "Utility Skills: Overview + One Page Per Skill"
status: approved
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

Reshaped `04-utility-skills/` from one flat page into an overview over one page per utility skill.

**Overview page** ([docs/site/04-utility-skills/task.md](../../../../docs/site/04-utility-skills/task.md)): kept the original framing (domain-neutral capabilities the workflow composes, several usable directly, agents reach for them automatically or you name them) and replaced the eight inline skill sections with a one-line entry per skill, each linking down to its page. All eight links resolve to the scaffolded page directories.

**Eight per-skill pages**, each leading with what the reader gets then when to reach for it, each linking to its `SKILL.md` as the authority:

- [01-task-tree](../../../../docs/site/04-utility-skills/01-task-tree/task.md) — high-level design only: filesystem-is-the-task-hierarchy, status rollup, the dispatchable frontier, the live dashboard. Operational detail is deliberately absent; the page reads as the conceptual top of the subtree and points down to the four detail children (`01-task-file`, `02-cli-commands`, `03-status-and-frontier`, `04-dashboard`) whose paths match the IA sitemap. Those children are owned by task `04` (and `04-dashboard` is already scaffolded); the down-links are intentional forward references that task `07` verifies site-wide.
- [02-semantic-merge](../../../../docs/site/04-utility-skills/02-semantic-merge/task.md), [03-result-protection](../../../../docs/site/04-utility-skills/03-result-protection/task.md), [04-refactor-and-integrate](../../../../docs/site/04-utility-skills/04-refactor-and-integrate/task.md), [05-report-in-markdown](../../../../docs/site/04-utility-skills/05-report-in-markdown/task.md), [06-worktree-data-sync](../../../../docs/site/04-utility-skills/06-worktree-data-sync/task.md), [07-zotero-paper-reader](../../../../docs/site/04-utility-skills/07-zotero-paper-reader/task.md), [08-mistral-pdf-to-markdown](../../../../docs/site/04-utility-skills/08-mistral-pdf-to-markdown/task.md) — the current per-skill prose carried over as standalone pages. The mistral page also links across to the Zotero page (it is the conversion step behind it).

**Detail-subpage decision: none created.** Applied the overflow test to the two named candidates and both failed it:

- `06-worktree-data-sync` — its `SKILL.md` is already a complete, human-readable CLI reference (command surface, three modes, flags, worked examples). A detail subpage would either paraphrase that CLI surface (forbidden by the objective and a drift risk per the authoring contract) or be a thin framing-plus-link that adds nothing over the skill page's own link. The page names the three modes (seed / diff / apply) conceptually and links to the SKILL.md for the exact CLI.
- `05-report-in-markdown` — the figure/math/table conventions are exactly the SKILL.md content; a subpage listing them would be pure paraphrase. Kept one page that frames the style guide and links to the SKILL.md.

Per-page `## Results` scaffold sections were removed from the eight content pages (doc nodes carry only `## Objective` per the authoring contract §3); frontmatter `status`/`depends_on` left at scaffold defaults (hidden by doc-mode).

**Validation.** All page bodies render under doc-mode: built `plan_dashboard.py generate --plan-root docs/site --doc-mode --root 04-utility-skills` clean (exit 0), and a content-presence check confirmed every page's distinctive prose and the task-tree down-links landed in the export. `report-in-markdown` self-diagnose reports all nine files clean. No teaching from the current flat page was dropped — every per-skill paragraph survives on its page, and the overview keeps the framing prose.

**Operating-manual rewrite (researcher feedback).** The eight per-skill pages were rewritten from the initial nest-and-frame pass to the §Conventions skill-page quality bar — they had read like pitches, not manuals (zotero-paper-reader was nearly empty). A two-draft-then-synthesize pass (two independent drafters per page reading the real `SKILL.md` + references, a synthesizer fact-checking both against the skill file and merging the best) now makes each page state, concretely: the failure a bare agent produces that the skill prevents, what the skill does, and how a researcher invokes it with example commands. Highlights: semantic-merge leads with the silent-revert of a bare `git merge`; result-protection with the silently-moved key number; zotero-paper-reader now documents its real search / read-PDF / BibTeX-export / `\cite`-insertion capabilities with example requests; report-in-markdown corrected a wrong `check_markdown.py` path; semantic-merge dropped an invented `SEMANTIC_MERGE.md` filename during fact-check. The task-tree page stays high-level and links down to its four detail children. The overview one-liners were rewritten to match. Doc-mode build clean; `check_markdown` clean on all nine.
