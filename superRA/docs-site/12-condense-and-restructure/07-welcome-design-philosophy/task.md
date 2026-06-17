---
title: "Add a Design Philosophy Section to the Welcome Page"
status: implemented
depends_on:
  - 05-finalize
tags: []
created: 2026-06-17
---

## Objective

Add a `## Design Philosophy` section to `docs/site/01-welcome/task.md` that highlights the high-level design ideas behind superRA — the ones a prospective adopter should grasp to decide the tool is for them. Adopter-facing, not contributor internals (no hooks, file formats, or load-order wiring): teach the *idea* and *why it matters to a researcher*.

The Welcome page already has a "Three ideas carry most of the discipline" paragraph at the end of "How it works" (implementer–reviewer pair, domain skills, task tree). **Absorb that paragraph into this new section** rather than duplicating it — the three ideas are a subset of the five below. Place `## Design Philosophy` after "How it works"; keep the pitch, why-sections, and three-phase diagram intact.

The five ideas, in this order (researcher-approved framing, 2026-06-17). Each gets a short bold name, a 1–2 sentence adopter-facing description, and a one-line "why it matters" — scannable on a front-door page, not an essay:

1. **Everything important is in the repo.** All project state — each task's objective, status, and results — lives in committed files, not in chat or an agent's working memory. *Why it matters:* a fresh agent session, or you a week later, resumes from the repo alone; you never lose the thread between sessions or get locked into one long chat. (This is the core idea; handoff/resume is its consequence — state it as one idea, clearly.)
2. **Adversarial review at every step.** A separate reviewer agent must APPROVE each task before it advances; a REVISE loops back until it passes. *Why it matters:* catches the "everything looks good" failure where an agent silently drops half the sample — the biggest risk of fast AI output.
3. **Domain discipline, enforced as the work happens.** A domain skill applies your field's methodology while the agent works (describe-before-transform for data, assumptions-before-algebra for theory) and the reviewer re-checks it. *Why it matters:* you get methodology you can defend, not just code that runs.
4. **Autonomous by default, human-in-the-loop by design.** The agent drives the workflow forward on its own and stops only for a hard blocker, a decision that's genuinely yours, or a milestone you set — never for procedural "should I proceed?" check-ins. *Why it matters:* momentum without babysitting; interruptions are reserved for the judgment calls only a researcher can make.
5. **Composable and adaptive.** superRA gives the agent reusable mechanisms it assembles for the situation rather than a fixed script, and the phases form a cycle, not a pipeline — discoveries and scope changes route back to the right point, leaving finished work untouched. A new research type is one new domain skill, not a workflow fork. *Why it matters:* the tool bends to research's exploratory rhythm and grows with your work.

## Planner Guidance

This is a single-page, single-section edit — keep it tight and front-door appropriate. Lean on prose already on the Welcome page and the two new skills pages for phrasing; do not re-explain mechanics the rest of the page or the Quickstart already cover. One paragraph per line.

## Results

Added a `## Design Philosophy` section to [docs/site/01-welcome/task.md](../../../../docs/site/01-welcome/task.md), placed after "How it works" and before "Start here", per the objective. The pitch, both why-sections, and the three-phase diagram are intact.

The pre-existing "Three ideas carry most of the discipline" paragraph was **absorbed** into the new section, not duplicated — its three ideas (implementer–reviewer pair, domain skills, task tree) map onto the new bullets 2/3, 3, and 1 respectively, so the standalone paragraph was deleted. Verified absent in the rendered HTML (grep for "Three ideas carry most of the discipline" returns 0 hits in the build output).

The section is a scannable bulleted list of the five researcher-approved ideas in the specified order, each with a bold name, a 1–2 sentence adopter-facing description, and an italic "Why it matters" line. Lead-in sentence ("Five ideas carry most of the discipline. If they fit how you work, superRA is for you.") frames it as an adoption-decision aid. Phrasing reuses prose already on the page (the cycle-not-pipeline framing from "How it works", the silent-drop-half-the-sample failure from "Why superRA?") rather than re-explaining mechanics. No contributor internals (hooks, file formats, load order). One paragraph per line.

Verification:
- `python3 skills/report-in-markdown/scripts/check_markdown.py docs/site/01-welcome/task.md` → `clean`.
- `docs/build_site.sh _site_check` → built `index.html`, `demo-tree.html`, `superra-dev-tree.html` with no errors; "Design Philosophy" and "Everything important is in the repo" both render in `index.html`. Build output removed after the check (generated site is never committed).
