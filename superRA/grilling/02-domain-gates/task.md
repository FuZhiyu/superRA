---
title: "Retire the domain planning approval gates in favor of frontier questions"
status: not-started
depends_on: [01-mechanism]
---

## Objective

Replace every PLAN-phase domain approval gate with named frontier questions, and move every domain planning survey out of `## Objective` into `## Planner Guidance`.

`skills/superplan/SKILL.md` Phase 2 keeps the domain survey as a requirement that precedes decomposition and drops the researcher-approval stop: the decisions the survey raises enter the frontier instead of an artifact the researcher signs off.

Each domain planning reference gains a named list of the decisions it contributes to the frontier, each stated so a recommended answer can be attached:

- [econ-data-analysis](../../../skills/econ-data-analysis/references/planning.md) — disposition of each data gap (acquire, scope down, proceed), which robustness checks matter for this study, and whether a borderline sensitivity failure is meaningful.
- [theory-modeling](../../../skills/theory-modeling/references/planning.md) — functional form, solution concept and equilibrium selection, normalizations, and which verification modes each result gets. The existing "escalate methodology choices — ask, don't choose" rule is this list, made explicit.
- [academic-writing](../../../skills/academic-writing/references/planning.md) — mode, audience, review lanes, and output disposition. §Hard Gate is retired; targets and the build command are facts the agent finds.
- [slide-design](../../../skills/slide-design/references/planning.md) — venue and audience, the talk objective, and the main-versus-backup policy.

Survey artifacts move to `## Planner Guidance` on the governing task: theory-modeling's Model Inventory / Assumption Map, slide-design's audience-context inventory, and academic-writing's writing header stop being `## Objective` content, matching what econ-data-analysis already does with its data inventory. The decisions grilling settles stay in the objective as contract — for theory-modeling, the agreed notation and the assumptions the model commits to are decisions, while the symbol audit and the primitives and endogenous-object catalogues are survey.

Keep intact: the anti-speculation red flags, the pipeline-file requirement, every `[BLOCKING]` implementation and review checklist item, and `slide-design` SKILL.md's review-time check against the recorded audience context, repointed to its new home.

Sweep the retired gate's stale references, including the §Depth Tiers standard row, [harness-plan-mode.md](../../../skills/superplan/references/harness-plan-mode.md) "any domain hard gate is satisfied", and the §Self-Review inventory-coverage item in [build-and-review.md](../../../skills/superplan/references/build-and-review.md).

Validation: a no-silent-loss audit gate by gate — every decision a retired gate forced appears as a named frontier question or as a documented survey output, quoted side by side in `## Results`. `grep -rni "hard gate\|researcher approval\|get researcher\|present the inventory" skills/` returns nothing for planning gates, and all edited prose passes the `CLAUDE.md` §Teach the Protocol three tests.

## Planner Guidance

- The risk is softening discipline while removing the stop. Walk each gate's current text and place its content before deleting it: econ-data-analysis step 6 ("present the inventory to the researcher"), theory-modeling step 6 ("present the inventory and get researcher approval") plus its "never proceed to task drafting on a verbal description" red flag, academic-writing §Hard Gate, and slide-design's before-decomposition recording rule.
- Four planning references and one spine section, all prose, no code. `docs/plans/` holds dated historical records that keep the old gate language and stay untouched.
