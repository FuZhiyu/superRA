---
title: "Workflows: Overview + One Page Per Phase"
status: implemented
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

Filled all four `05-workflows/` stubs with user-facing prose under `## Objective`, per the authoring contract in [01-information-architecture §3](../../01-information-architecture/task.md). Removed the scaffold's empty `## Results` heading from each page so the doc nodes carry only page content (per the contract's "no `## Results` on doc nodes" rule).

- [docs/site/05-workflows/task.md](../../../../docs/site/05-workflows/task.md) — overview: frames PLAN → IMPLEMENT → INTEGRATE as the project spine, states the phases compose (run only the part you need) and are re-enterable, and gives a one-line entry per phase linking down to `#/05-workflows/01-plan`, `02-implement`, `03-integrate`.
- [docs/site/05-workflows/01-plan/task.md](../../../../docs/site/05-workflows/01-plan/task.md) — PLAN: what `superplan` produces (the task tree), the one approval gate that is the researcher's, that planning is re-enterable on scope change; links to [superplan](skills/superplan/SKILL.md). Absorbs the dropped-FAQ "Can I skip PLAN?" item.
- [docs/site/05-workflows/02-implement/task.md](../../../../docs/site/05-workflows/02-implement/task.md) — IMPLEMENT: the implementer–reviewer pair, adversarial review, APPROVE/REVISE and advance to `approved`; links to [superimplement](skills/superimplement/SKILL.md) and the role specs. Absorbs the FAQ "direct vs. subagent mode" and "resuming a project" items.
- [docs/site/05-workflows/03-integrate/task.md](../../../../docs/site/05-workflows/03-integrate/task.md) — INTEGRATE: the five steps (Protect/Sync/Refactor/Document/Finish) and the decisions the researcher owns; links to [superintegrate](skills/superintegrate/SKILL.md). Absorbs the FAQ "Can I skip INTEGRATE?" item.

**FAQ coverage for task 05.** The four phase-level FAQ facts each have a home: skip-PLAN on 01-plan, direct-vs-subagent and resuming on 02-implement, skip-INTEGRATE on 03-integrate. The non-phase FAQ items (harness choice, data hygiene, plan-mode hook, merge-guard, authority pointer) belong to other pages owned by other tasks and are out of scope here.

**Validation.** Markdown self-diagnose clean on all four pages (`check_markdown.py`). Static export build succeeded (`plan_dashboard.py generate --plan-root docs/site`); every hash-link target used (`05-workflows/01-plan`, `02-implement`, `03-integrate`, `04-utility-skills/01-task-tree`, `04-utility-skills/01-task-tree/04-dashboard`, `02-quickstart`) resolves to a real node path in the export, and all four FAQ section headings render. Each phase page leads with what the reader gets, links to its owning skill as authority, and stands alone when landed on directly.
