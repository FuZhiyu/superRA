---
title: "Welcome Why-Sections + Feature slide-design"
status: implemented
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

Both user-directed refinements applied to the doc-source pages; no `superRA/` task files edited as content targets.

**A. Welcome page — two why-sections.** Split the single "Why superRA rather than … Superpowers?" passage on [docs/site/01-welcome/task.md](../../../../docs/site/01-welcome/task.md) into two `##` sections matching the README's two-part motivation:

- `## Why superRA?` (new) repeats the README's "fast but undisciplined" motivation — agents generate more code than anyone reviews, drift as the context window fills, silently drop half the sample while reporting "everything looks good" — adapted to the welcome page's prose voice (one paragraph, not the README's bulleted list).
- `## Why not an existing framework like Superpowers?` carries the existing software-engineering-vs-social-science contrast forward unchanged in substance; only re-headed and lightly rephrased to open as a standalone section.

Final order: Objective (intro + "What it is" list) → Why superRA? → Why not an existing framework? → How it works → Start here. The intro, "What it is" bullets, the HTML phase diagram, "How it works" prose, and "Start here" are untouched — verified by diff, only the why-area plus the one slide-design bullet edit changed.

**B. slide-design featured alongside the domain skills.** Added slide design to the domain-skills list on both front doors, kept consistent:

- Welcome "What it is" domain-skills bullet ([docs/site/01-welcome/task.md:17](../../../../docs/site/01-welcome/task.md#L17)): "data analysis, theory modeling, academic writing, and slide design".
- README item 3 ([README.md:11](../../../../README.md#L11)) and the "Skills, Agents, and Hooks" line ([README.md:61](../../../../README.md#L61)): same four-vertical wording. Also normalized the README's prior "economic data analysis, theory-modeling" phrasing to the welcome page's "data analysis, theory modeling" form so the two front doors match exactly. Framed as a real capability; no install path claimed. This reverses the audit's accuracy-driven drop per the recorded user decision; the open finding in [03-new-user-audit §"Left for the user"](../03-new-user-audit/task.md) is already marked RESOLVED, deferring to this task.

**Validation.** Markdown self-diagnose clean on both files (`check_markdown.py`). Doc-mode export built successfully (`plan_dashboard.py generate --plan-root docs/site --doc-mode`); grepped the rendered HTML and confirmed both new welcome sections and the "academic writing, and slide design" wording rendered.
