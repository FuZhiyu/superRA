---
title: "Welcome Why-Sections + Feature slide-design"
status: not-started
depends_on: 
  - 01-front-door-and-welcome
  - 02-propagate-dashboard
  - 03-new-user-audit

tags: []
created: 2026-06-17
---

## Objective

Two user-directed refinements to the front-door messaging, decided after the audit (`03`). Edit the doc-source pages (`docs/site/**/task.md`) and `README.md`, not the `superRA/` task files.

**A. Welcome page — give the "why" area two sections.** The user likes the current welcome page (`docs/site/01-welcome/task.md`) but wants its single "Why superRA rather than … Superpowers?" passage split into the same two-part motivation the README carries:

- Add a **"Why superRA?"** section that repeats the README's motivation — agents are fast but undisciplined (generate more code than anyone reviews; drift as the context window fills; silently drop half the sample while reporting "everything looks good") — adapted to the welcome page's voice. This currently exists only on the README ([README.md §"Why superRA?"](../../../../README.md)); the welcome page lacks it.
- Keep (and follow it with) the existing **"Why not an existing framework like Superpowers?"** contrast already on the welcome page (lines ~19–21): software-engineering frameworks target verifiable, unit-testable tasks and push to remove the human; social-science research is fluid/exploratory and needs the human in the loop.
- Place both after "What it is" and before "How it works": *What it is → Why superRA? → Why not existing frameworks? → How it works → Start here.* Keep the rest of the welcome page (intro, "What it is", the diagram, "Start here") as-is — the user explicitly prefers the current version.

**B. Feature slide-design alongside the domain skills.** The user has decided to feature `slide-design` now, listed **alongside** the domain skills (their original draft style), on both front doors and the skills surfaces, kept consistent:

- Welcome "What it is" domain-skills bullet and README "It ships" item 3 / the lower "Skills, Agents, and Hooks" line: add slide design to the list (e.g. "data analysis, theory modeling, academic writing, and slide design"). Keep the two front doors consistent with each other.
- This **reverses** the audit's accuracy-driven drop and **resolves** the open finding in [`03-new-user-audit` §"Left for the user"](../03-new-user-audit/task.md). Recorded user decision: feature it ahead of the `slide-design-vertical` → trunk merge. **This is intentional — do not re-flag "slide-design is not shipped on this branch" as a defect.** Frame it as a real capability (turning results into slide decks); do not claim a specific install path for it.

Follow the authoring contract (`01-information-architecture` §3): one paragraph per line; hash/`#/` cross-page links; public-safe content; link to authority rather than paraphrasing. Keep the welcome ↔ README "what it ships / what it is" lists consistent.

Validation: render the welcome page and README in doc-mode (subtree Build command) and confirm both build; the welcome page shows two distinct why-sections in the stated order; slide-design appears alongside the domain skills on both front doors with consistent wording; no other welcome content changed.

## Results

