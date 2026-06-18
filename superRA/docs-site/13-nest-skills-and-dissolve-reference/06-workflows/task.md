---
title: "Workflows: Overview + One Page Per Phase"
status: not-started
depends_on: 
  - 01-ia-and-scaffold

tags: []
created: 2026-06-17
---

## Objective

Build the new top-level `05-workflows/` section: an overview over one page per phase, giving the researcher more detail on the three workflows than the quickstart's inline walkthrough carries. The quickstart shows the loop in action end to end; these pages let a reader who wants to understand a single phase go deeper without re-reading the whole walkthrough. Written for the researcher *driving* the workflow — what they invoke, what happens, and the decisions that are theirs — not for the agent the workflow skills instruct.

Fill the stubs scaffolded by `01` (`docs/site/05-workflows/` plus `01-plan`/`02-implement`/`03-integrate`). Concise throughout: lead each page with what the phase does for the researcher and when they reach for it; link to the owning skill as authority rather than transcribing its procedure.

**Overview page (`05-workflows/task.md`):** frame the PLAN → IMPLEMENT → INTEGRATE cycle as the spine of a superRA project — three phases the researcher moves work through, re-enterable as work changes — and give a one-line entry per phase linking to its page. Note that the phases compose (you can run only the part you need) and that re-entry after a change is normal.

**One page per phase**, each user-facing and concise, linking to its skill (`superplan` / `superimplement` / `superintegrate`) as authority:

- `01-plan` — scoping and decomposing work into a task tree. What the researcher invokes (`superplan`), what they approve (the task tree before execution), and that planning is re-enterable when scope changes. Fold in the FAQ phase question: when it is reasonable to skip PLAN for small or exploratory work.
- `02-implement` — executing tasks through the implementer–reviewer loop. What `superimplement` dispatches, the adversarial review gate, status moving to `approved`, and resuming an interrupted or revised project from the frontier. Fold in the FAQ items on direct vs. subagent mode and resuming an old project.
- `03-integrate` — protecting results, syncing with the base, refactoring for fit, and the final PR. What `superintegrate` does for the researcher and the completion decisions that are theirs. Fold in the FAQ phase question on when INTEGRATE can be skipped for throwaway work.

These pages absorb the phase-level questions the dropped FAQ used to answer (task `05` relies on that). Do not duplicate agent-facing procedure from the workflow skills (authority-not-paraphrase, per the root Conventions); link to the `SKILL.md` for the mechanics.

Prose quality: load the `writing` skill; lead with what the reader gets, then when to reach for it; no AI-flavored prose (`feedback_no_ai_flavored_prose`).

Validation: the overview links resolve to the three phase pages; each phase page stands alone when landed on directly and links to its owning skill; the phase-level FAQ facts named above each have a home on these pages so task `05` can drop the FAQ with nothing orphaned.

## Results

