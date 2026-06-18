---
title: "Site-Wide Link Repoint + Build/Render-Integrity Verification"
status: not-started
depends_on: 
  - 02-domain-skills
  - 03-utility-skills
  - 04-task-tree-reference-nesting
  - 05-dissolve-reference

tags: []
created: 2026-06-17
---

## Objective

Final task: repoint every cross-page link that the restructure invalidated, remove the emptied `05-reference/` parent, and verify the whole site builds and renders with no broken links. This is the gate that catches the seam bugs a per-page edit cannot see.

**Site-wide link repoint.** Sweep every page under `docs/site/` (welcome, quickstart, both skills overviews and all their per-skill/detail pages, glossary, faq, hooks, showcase) and repoint every stale `#/…` hash link to its new path:

- `#/05-reference/01-task-file` → `#/04-utility-skills/01-task-tree/01-task-file`
- `#/05-reference/02-cli-commands` → `#/04-utility-skills/01-task-tree/02-cli-commands`
- `#/05-reference/03-status-and-frontier` → `#/04-utility-skills/01-task-tree/03-status-and-frontier`
- `#/05-reference/05-glossary` → `#/05-glossary`; `#/05-reference/06-faq` → `#/06-faq`; `#/05-reference/07-hooks` → `#/07-hooks`
- `#/06-showcase` → `#/08-showcase`
- `#/05-reference/04-skills-and-agents` → retarget to the relevant skills overview or skill page, or remove the link if nothing replaces it (the page is dropped)
- In-page anchors that pointed at the old flat skills pages (e.g. glossary's "Utility Skills: The Task Tree", "Protecting Results") → repoint to the specific skill subpage, e.g. `#/04-utility-skills/01-task-tree`, `#/04-utility-skills/03-result-protection`.

Find them with a repo-wide search for `#/05-reference`, `#/06-showcase`, and `#/04-utility-skills`/`#/03-domain-skills` bare-page anchors; fix the source files. Also fix any links that point *into* the relocated task-file/cli/status pages from outside (quickstart, welcome, other reference pages).

**Remove the empty `05-reference/` parent** once tasks `04` and `05` have moved all its children out.

**Build + render-integrity verification.** Run the markdown render-integrity checker over the doc sources; build the doc-mode export (or live serve) and confirm: every page renders, the new nesting shows correctly in the nav, and **no hash link 404s** — click through the moved targets (task-file/cli/status under task-tree, glossary/faq/hooks at top level, showcase at 08). Verify through the real build, not a `file://` open (`feedback_preview_dashboard_css_live_not_file`); check the rendered result, not just the source (`feedback_verify_real_user_path_for_ui`).

Load `writing` for any link-context prose touched.

Validation: a repo grep for `#/05-reference` and `#/06-showcase` returns nothing in `docs/site/`; the render-integrity check passes; a built/served walkthrough reaches every moved page with no dead link.

## Results

