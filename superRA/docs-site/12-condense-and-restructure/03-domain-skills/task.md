---
title: "Author the Domain Skills Page"
status: implemented
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

## Results

Authored [docs/site/03-domain-skills/task.md](../../../docs/site/03-domain-skills/task.md). The page opens with the governing design idea — a domain skill loads *on top of* a workflow phase, not instead of it; the workflow supplies the choreography and the domain skill the discipline — and the adopter payoff (one new skill, not a workflow fork). It then carries one thin section per implemented domain skill, each a framing + flagship discipline + a link to its `SKILL.md` as the authority (no paraphrase of the skill body), and closes with the planned roadmap verticals.

Sections authored, framing confirmed against each `skills/<name>/SKILL.md`:

- **`econ-data-analysis`** — Iron Law (no transformation without first describing the data) + describe–analyze–validate loop. Verified against [skills/econ-data-analysis/SKILL.md](../../../skills/econ-data-analysis/SKILL.md).
- **`theory-modeling`** — four gates in trust order: Objects & Notation → Assumptions → Derivations → Verification & Rendering. Verified against [skills/theory-modeling/SKILL.md](../../../skills/theory-modeling/SKILL.md).
- **`writing`** — one principle (preserve substance, polish prose) across Review / Polish / Draft. Verified against [skills/writing/SKILL.md](../../../skills/writing/SKILL.md).
- Roadmap: literature review and simulation named as planned.

**Slide-design decision (objective asked to confirm and include "only at the level the codebase supports"): excluded.** The authoritative source [skills/CATEGORIES.md](../../../skills/CATEGORIES.md) lists only `econ-data-analysis`, `theory-modeling`, and `writing` under §Domain; there is no `skills/slide-design/` directory in the inventory (`ls skills/`), and the now-deleted Concepts › Skills & Agents page likewise scoped the implemented domains to those three. The `slide-design` skill available in this session is a separate plugin, not part of superRA's packaged domain-skill library. Advertising it would create a fourth authority pointing at a non-existent `skills/slide-design/SKILL.md`, so I did not include it.

**Cross-check discrepancy flagged for `05-finalize` (out of this task's scope).** The welcome page ([docs/site/01-welcome/task.md](../../../docs/site/01-welcome/task.md)) and `README.md` both still advertise "slide design" as a current domain skill, which contradicts CATEGORIES.md. Welcome alignment is owned by `05-finalize`; the welcome's domain list should be corrected there to match the authoritative three (plus roadmap), or slide-design should be packaged as a real `skills/slide-design/` domain skill if that is the intent. I did not edit the welcome page (not in this task's scope).

**Authoring-contract compliance.** Frontmatter `title` only; cross-page links as `#/<path>` hash links; skill-file citations written as repo-relative path targets (`skills/<name>/SKILL.md`) that the export rebases via `--repo-file-base` — never hardcoded GitHub URLs — matching the welcome page's `](README.md)` convention. One paragraph per line.

**Build verification.** `bash docs/build_site.sh /tmp/superra_site_check` exited 0 with no errors; the page content rendered into `index.html` (Iron Law and four-gate text present), the three `SKILL.md` links and the `CATEGORIES.md` link embed repo-relative for client-side rebasing, and the `#/04-utility-skills` next-page link is present. `report-in-markdown/scripts/check_markdown.py` reports the page clean.
