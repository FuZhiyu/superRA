---
title: "Information Architecture + Docs-Tree Authoring Contract"
status: not-started
depends_on: []
tags: []
created: 2026-06-10
---

## Objective

Produce the researcher-approved information architecture for the site, then scaffold the empty docs tree from it. Four deliverables, committed as one IA document plus the scaffold:

1. **Audience model and teaching inventory.** Who reads each section and in what state of knowledge; map every concept and journey a researcher must learn to a page. The known human-facing gaps must each have a home: visual/dashboard guide, quickstart, worked task-tree example, task-design guidance, FAQ/glossary, and the "how do I collaborate with agents via task files" narrative.
2. **Sitemap.** The full nav tree with a one-line brief per page (what it teaches, which existing skill/reference file is its authority to link to). Top level follows the tutorial / how-to / explanation / reference split unless a better structure emerges — deviations are a researcher decision, not a silent change.
3. **Docs-tree authoring contract.** Source location (proposed: `docs/site/`), node frontmatter use (`title` only; status/depends_on unused and hidden by doc-mode), ordering via numeric directory prefixes, cross-page link convention (hash links `#/<path>`), repo-file link convention (`--repo-file-base` pointing at the GitHub blob URL), and figure/screenshot conventions.
4. **README front-door split.** Section-by-section disposition for the current `README.md`: stays, moves to which page, or is dropped. Every current section must have a disposition.

**Stop point:** researcher approves the IA document before any content task (03–07) is dispatched.

Validation: cross-check the sitemap against deliverable 1's own teaching inventory (including the named gap list above) and against the current README — no concept, journey, or README section left without a disposition.

## Planner Guidance

Useful raw material: README.md structure, `skills/CATEGORIES.md`, the task-tree skill references (`task-file-contract.md`, `commands.md`, `task-tree-design.md`), `docs/README.codex.md` and `docs/README.opencode.md` (candidates to absorb or link), and the role specs under `agents/`.

Keep reference pages thin where a skill file already serves humans well — a brief framing plus a link beats a paraphrase that will drift.
