---
title: "Planning Workflow Redesign"
status: approved
depends_on: []
---

## Objective

Own the superRA planning workflow (`skills/superplan/SKILL.md`): domain-neutral, harness-independent, exploration-first, existing-task-aware, and gated by researcher decisions rather than artifact sign-offs. Seven concerns:

1. **Core workflow** — a 5-phase structure (Entry Assessment → Exploration → Domain Setup & Scope → Design & Task Decomposition → Review & Commit), with a domain-neutral core and domain skills plugging in at Phase 2.
2. **Plan update mechanism** — no `## Decisions` log; self-sufficient objective rewrites plus `## Revision Notes` as a temporary delta signal, on the same cleanup lifecycle as review notes.
3. **Harness plan-mode compatibility** — harness plan mode writes `superRA/` directly, with no two-step migration.
4. **Terminology convention** — "Plan" is the verb; everything in `superRA/` is a task.
5. **PLAN.md remnant cleanup** — PLAN.md/RESULTS.md references migrated to `superRA/` task files across the skills, agents, and docs.
6. **Review and planning protocol** — the `## Details` body section; objective-first implementation review; `Stage: planning-review` in the manifest; planning review critiques tree-design quality.
7. **Grilling as the only researcher-facing approval gate.** Planning puts unsettled *decisions* to the researcher in rounds ordered by a design tree, each question carrying its recommended answer; facts the environment holds are the agent's to find. The domain planning approval gates are retired — what each forced the researcher to sign off becomes a named frontier question owned by that domain's planning reference. Domain surveys land in `## Details`; only settled decisions enter `## Objective`. Runs by default at standard and thorough depth, on request at quick depth, and lives in `superplan` rather than a new skill.

## Results

All seven concerns shipped.

- **Core workflow and placement.** [superplan/SKILL.md](../../../skills/superplan/SKILL.md) carries the 5-phase domain-neutral structure. Entry Assessment reads the existing tree and decides update-vs-new-top-level; placement is by durable home, with the update-task lifecycle in [task-tree-design.md](../../../skills/superplan/references/task-tree-design.md).
- **Plan updates.** `## Revision Notes` replaced the `## Decisions` log and the User Decisions Log across the contract, the task-tree skill, and `agent-orchestration`.
- **Harness plan mode.** [harness-plan-mode.md](../../../skills/superplan/references/harness-plan-mode.md) writes `superRA/` directly from plan mode.
- **Terminology and migration prep.** [CLAUDE.md §Terminology](../../../CLAUDE.md) owns "plan is the verb"; `plan_migrate.py` parser expectations and a normalization checklist are in [internals.md](../../../skills/task-tree/references/internals.md); [main-agent.md](../../../skills/using-superra/references/main-agent.md) speaks in task-tree operations throughout.
- **PLAN.md remnants** are swept from the workflow skills, `using-superra`, `agent-orchestration`, `README.md`, and `CATEGORIES.md`.
- **Review protocol.** Reviewer evaluation is objective-first, `Stage: planning-review` is in the manifest, material deviations must appear in `## Results`, and `task_read.py` renders ancestors under a `=== Context ===` header with a focused tree. Planning review critiques tree design — durable ownership, branching, dependencies, update-task lifecycle — with modes owned by [planning-review.md](../../../skills/superplan/references/planning-review.md). The objective/details split is sorted by the binding test that [task-tree/skill-definition](../skill-definition/task.md) owns.
- **Grilling** ships in [grilling.md](../../../skills/superplan/references/grilling.md), 32 lines over four headings. `AskUserQuestion` is batched call after call until the frontier is empty, recommended answer first and labeled `(Recommended)`; a decision with no discrete alternatives rides the same round as plain numbered `❓`/`➡️` text. Facts split three ways: the environment's are the agent's to read or explore, the researcher's own are questions, and a fact only work can produce is a task boundary — split with `depends_on`, dependents written open-ended, re-grilled when the evidence lands. An empty frontier ends the round and returns to whichever step entered it. §Substantive Questions is gone; §Entry Assessment runs a scoping round when the request is too vague to aim exploration, Phase 3 opens with "Grill before decomposing", [changing-the-tree.md](../../../skills/superplan/references/changing-the-tree.md) routes reopened scope back in, and the frontmatter description names grill, stress-test, and interrogate as triggers.

**No planning gate survived the retirement, and none was silently dropped.** Each of the four domain planning references replaced its approval step with a §Frontier Contributions list: [econ-data-analysis](../../../skills/econ-data-analysis/references/planning.md) (gap disposition, which robustness checks matter, whether a borderline sensitivity failure is meaningful), [theory-modeling](../../../skills/theory-modeling/references/planning.md) (functional form, solution concept and equilibrium selection, normalizations, verification mode per result), [academic-writing](../../../skills/academic-writing/references/planning.md) (mode, audience, review lanes, disposition — targets and the build command are facts to find), and [slide-design](../../../skills/slide-design/references/planning.md) (venue, audience makeup, talk objective, main-vs-backup policy). Phase 2 keeps the survey as a requirement that precedes decomposition. Every `[BLOCKING]` implementation and review item, the anti-speculation red flags, and the pipeline-file requirement stayed intact.

**Where a survey lands is decided by force, not by artifact name.** Two `[BLOCKING]` domain checks read content this work had moved into ancestor guidance, which a descendant never sees — theory-modeling requires the solution concept named before derivation starts, slide-design judges the deck against the recorded audience context — so both stayed binding and moved back into `## Objective`. econ-data-analysis's data inventory is explicitly not binding and keeps its `## Details` home. That episode is what produced the binding test now stated in the task-file contract.

The superseded placement layers — two-step placement, then recursive descent in the since-deleted `task-tree/references/planning.md` — were folded here at an earlier consolidation.
