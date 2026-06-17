---
title: "Shorten README into a Front Door Pointing at the Docs"
status: not-started
depends_on:
  - 01-ia-and-scaffold
tags: []
created: 2026-06-17
---

## Objective

Now that the docs site is the condensed, authoritative source, shorten the repo-root `README.md` into a true front door: a tight pitch plus pointers into the docs, rather than a second copy of the content. The earlier [`09-readme-front-door`](../../09-readme-front-door/task.md) pass split README into a front door against the *old* six-section docs; this pass tightens it further and repoints it at the new structure.

- Keep: the one-paragraph pitch, the install commands, and the contributor/license essentials a GitHub visitor needs without leaving the README.
- Cut: anything the docs now own — extended concept explanations, the full workflow narrative, per-skill detail. Replace with links to the new pages (Welcome, Quickstart, Domain Skills, Utility Skills).
- Point links at the deployed docs site (use the same link convention `09-readme-front-door` established for README→docs links).
- Do not duplicate the docs audience principle's failure mode: the README should make a visitor want to read the docs, not substitute for them.

Verify no README link points at a dropped docs page (Concepts/How-To).

## Planner Guidance

Read the current `README.md` and `docs/README.codex.md` / `docs/README.opencode.md` to see what front-door material already exists. This is a trim-and-repoint pass, not a rewrite — preserve the existing voice and the contributor-facing sections.
