---
title: "Propagate Dashboard-First Framing Across Docs"
status: approved
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

Propagated the dashboard-first framing established in sibling `01` (canonical wording: "a live tree, dependency DAG, and kanban view … that auto-update as work progresses, so you both monitor and steer it"; "the dashboard doubles as a handoff surface: you, or a fresh agent session a week later, can pick up exactly where work left off"; "this documentation site is itself a dashboard export — you are reading one"). Reused that phrasing rather than inventing a competing one.

### Pages changed

- **[docs/site/03-concepts/02-the-task-tree/task.md](../../../../docs/site/03-concepts/02-the-task-tree/task.md)** — added a new `## The tree is also a live dashboard` section after the frontier section. It ties the committed tree to what the dashboard renders (monitoring + handoff, reusing the canonical wording) and links to `#/04-how-to/04-see-your-work` as the operational how-to. Integrated as a new concept section following the existing flow (state → contents → status → dependencies → dashboard), not bolted onto an unrelated paragraph.
- **[docs/site/04-how-to/04-see-your-work/task.md](../../../../docs/site/04-how-to/04-see-your-work/task.md)** — replaced the opening "you want to see what the agents have done" lead with a one-line lead establishing the dashboard as the **primary way to monitor and hand off** a project (not merely "see" it), keeping the existing tree/DAG/kanban sentence. No welcome-page pitch duplicated; the mechanics sections are untouched.
- **[docs/site/06-showcase/task.md](../../../../docs/site/06-showcase/task.md)** — the dogfooding hook ("rendered by the same dashboard you get when you run superRA yourself", plus the handoff-surface line and the "How these are built" section) was already strong, but the self-referential "this page itself is a dashboard export" hook was missing. Added one clause: "The documentation site you are reading is itself a dashboard export, so the chrome around these trees is the chrome around this page."

### Dashboard-mentioning pages deliberately left unchanged

Surveyed every page that mentions "dashboard". All remaining mentions are operational/incidental references that correctly point to the See-Your-Work guide as the operational home and neither undersell nor contradict the elevated monitoring/handoff framing:

- `docs/site/02-quickstart/task.md` — walkthrough references (launch the dashboard, screenshots, "covered in See Your Work"); already carries the handoff idea ("a fresh agent — or you, next week — can reopen the repository").
- `docs/site/04-how-to/task.md` — index line: "monitor progress with the live dashboard" (already aligned).
- `docs/site/04-how-to/03-work-with-task-files/task.md` — comment-pinning mechanics + a pointer to See Your Work.
- `docs/site/04-how-to/06-resume-and-revise/task.md` — "for the visual version, run … dashboard" pointer.
- `docs/site/05-reference/01-task-file/task.md`, `02-cli-commands/task.md`, `04-skills-and-agents/task.md`, `06-faq/task.md` — reference-section lookups (CLI commands, field definitions, skill table, FAQ pointer); reference tone is intentionally terse, elevation belongs on the welcome/concept/how-to pages.

### Validation

- `report-in-markdown/scripts/check_markdown.py` on all three touched files: clean.
- Rendered the full `docs/site` tree in doc-mode export (`plan_dashboard.py generate --plan-root docs/site`): builds without error; all three edited bodies and the `#/04-how-to/04-see-your-work` cross-link are present in the output.
- Cross-link `#/04-how-to/04-see-your-work` resolves to a real node (`docs/site/04-how-to/04-see-your-work/task.md` exists).
- Authoring contract followed: links to the See-Your-Work node as authority (no skill-body paraphrase), glossary terminology ("task tree", "frontier", "dashboard"), one paragraph per line, `#/` hash cross-links, public-safe content.
