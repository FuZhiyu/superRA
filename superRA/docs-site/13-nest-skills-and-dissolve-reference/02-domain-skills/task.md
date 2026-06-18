---
title: "Domain Skills: Overview + One Page Per Skill"
status: not-started
depends_on: 
  - 01-ia-and-scaffold

tags: []
created: 2026-06-17
---

## Objective

Turn `03-domain-skills/` from one flat page into an overview over one page per domain skill.

**Overview page (`docs/site/03-domain-skills/task.md`):** keep the framing paragraph (what a domain skill is — methodology for the agent, standard for the reviewer) and replace the three inline skill sections with a one-line entry per skill that links to its page: econ-data-analysis, theory-modeling, writing. Resolve the dangling `## On the roadmap` heading the current page ends on — either restore a short roadmap line (literature-review and simulation verticals are planned) or drop the heading; do not leave a bare heading.

**One page per skill** (the stubs scaffolded by `01`): `01-econ-data-analysis/`, `02-theory-modeling/`, `03-writing/`. Each page carries that skill's high-level design — the prose currently in the flat page is the starting material, kept or lightly expanded into a standalone page a reader lands on directly:

- `01-econ-data-analysis` — the Iron Law (describe before you transform), the describe–analyze–validate loop, pitfall catalogs; language-agnostic.
- `02-theory-modeling` — the four gates (Objects & Notation → Assumptions → Derivations → Verification & Rendering) and why their order is the order trust depends on.
- `03-writing` — preserve-substance / polish-prose across Review, Polish, Draft modes; note it is the domain skill most often invoked standalone on a manuscript.

Each page links to its `SKILL.md` as the authority and does not re-author agent-facing discipline (authority-not-paraphrase, per the root Conventions). One page per domain skill — no third level; the detail home is the SKILL.md.

Prose quality: this is reader-facing writing. Load the `writing` skill; no AI-flavored prose (`feedback_no_ai_flavored_prose`); lead each page with what the reader gets, then when to reach for it.

Validation: the overview links resolve to the three pages; each page stands on its own when landed on directly; no teaching from the current flat page is lost in the split.

## Results

