---
title: "Author the Domain Skills Page"
status: not-started
depends_on:
  - 01-ia-and-scaffold
tags: []
created: 2026-06-17
---

## Objective

Author `docs/site/03-domain-skills/task.md`: introduce superRA's domain skills one by one, each with its **high-level design idea**, so an adopting researcher understands what discipline they get for their kind of research and how to pick the right one.

Open with the one design idea that makes domain skills matter: a domain skill loads *on top of* a workflow phase, not instead of it — the workflow supplies the choreography (dispatch, review, advance) and the domain skill supplies the discipline applied inside it. The payoff for the reader: adding a new kind of research means writing one domain skill, not forking the workflow. (This is the essential idea from the deleted Concepts › Skills & Agents page.)

Then one short section per currently-implemented domain skill, each stating its flagship discipline at a level a researcher can act on:

- **`econ-data-analysis`** — the Iron Law (no transformation without first describing the data) and the describe–analyze–validate loop.
- **`theory-modeling`** — the four-gate discipline (Objects & Notation, Assumptions, Derivations, Verification & Rendering).
- **`writing`** — preserve-substance / polish-prose over Review, Polish, and Draft modes.
- **`slide-design`** — if treated as a domain vertical; confirm its status against `skills/CATEGORIES.md` and the skill inventory and include it only at the level the codebase supports.

Close by naming the roadmap verticals (literature review, simulation) as "planned," so readers see the architecture is meant to grow.

Each skill gets a framing + design idea + a link to its `SKILL.md` as the authority — **not** a paraphrase of the skill body (which would drift). Keep it thin. No internal load-order or reference-file mechanics; that is contributor detail.

## Planner Guidance

`skills/CATEGORIES.md §Domain` is the source of truth for which skills are domain skills and their flagship disciplines — pull the framing from there and confirm against the actual `skills/<name>/SKILL.md` files. Treat the welcome page's current domain list as a cross-check for what to advertise.
