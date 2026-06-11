---
title: "README Front-Door Restructure"
status: not-started
depends_on:
  - 08-deploy
  - 04-quickstart-tutorial
  - 05-how-to-guides
  - 06-reference
tags: []
created: 2026-06-10
---

## Objective

Restructure `README.md` into the front door. The section-by-section disposition approved in `01-information-architecture` governs; the lists below are the planner-expected baseline the IA refines, not an independent second spec:

- **Keeps:** the pitch / why-superRA, the workflow diagram, one task-tree visual (screenshot or rendered-tree image), the Claude Code install path, a quickstart pointer, and prominent links into the site (tutorial, guides, reference, showcase).
- **Moves to the site:** the skill and hook inventory tables, multi-harness install detail, and extended principle prose — each replaced by a one-line pointer to its new page.
- README stays self-sufficient for the 60-second GitHub evaluation: a reader who never leaves the README still learns what superRA is, why it exists, and how to install it on Claude Code.

Sweep for coherence after the trim: no orphaned in-README anchors; inbound references to moved sections (`docs/README.codex.md`, `docs/README.opencode.md`, `CLAUDE.md`, contributing/marketplace surfaces) re-pointed; manifest homepage fields consistent with the live site URL from `08-deploy`.

Validation: every removed section's content is reachable from the README via exactly one link hop; repo-wide grep shows no dangling links to removed anchors.
