---
title: "Grilling: Frontier-Rounds Questions as Planning's Only Approval Gate"
status: not-started
depends_on: []
---

## Objective

Make frontier-ordered grilling the researcher-facing approval gate of the PLAN phase, and the only one. The mechanism is adapted from [mattpocock/skills](https://github.com/mattpocock/skills) `grilling`; the research adaptation is superRA's.

- Planning puts **decisions** to the researcher in rounds ordered by a design tree, each question carrying a recommended answer. Facts the environment holds are the agent's job to find.
- The domain planning **approval gates** are retired. What each forced the researcher to sign off becomes a named frontier question owned by that domain's planning reference.
- Every domain planning **survey** lands in `## Planner Guidance`. Only the decisions grilling settles enter `## Objective`, as contract.
- Grilling runs by default at standard and thorough depth; quick depth skips it unless asked. A `grill me` request forces it at any depth.
- No new skill — the mechanism lives in `superplan`.

Validation: both children approved, and a dry run over a genuinely under-specified data request produces rounds whose later questions were unaskable in the earlier round, then a tree whose objectives carry the settled decisions and whose guidance carries the survey.

### Context

superRA-internal skill authoring. `CLAUDE.md` is the authority: the §Teach the Protocol three tests applied line by line, the ownership boundaries table, and §Skill Prose Style (terse — bolded imperative plus short elaboration, no rationale clauses). Load `skill-creator` before editing any `skills/*/SKILL.md`.

The objective-vs-guidance split this task enforces is defined in [task-tree-design.md §Writing Objectives and Planner Guidance](../../skills/superplan/references/task-tree-design.md) — the objective is rejectable contract, guidance is what planning discovered that the implementer would otherwise re-derive. A survey is discovery.

### Constraints

- Keep `skills/superplan/SKILL.md` a routing spine. [interactive-mode/superplan-decrowd](../interactive-mode/superplan-decrowd/task.md) cut it to 103 lines; grilling enters as a slim routing section plus one reference, never as a new inline mechanism.
- PLAN-phase researcher-approval stops only. Domain `[BLOCKING]` implementation and review checklists, the pipeline-file requirement, and the anti-speculation red flags stay intact.
- Out of scope: the interactive canvas loop ([interactive-mode.md](../../skills/using-superra/references/interactive-mode.md)), grilling at `superintegrate` Protect, a stateful grill-with-docs variant, a multi-session wayfinder map, and `docs/site` pages (that workstream is postponed).

## Planner Guidance

- **Upstream shape.** Upstream splits a ~10-line mechanism skill from a `grill-me` front door that carries `disable-model-invocation: true` and only calls it. superRA needs neither the split nor a skill: `superplan`'s frontmatter description carries the trigger phrases and its spine carries the load condition.
- **Placement.** Kept top-level on the `econ-data-efficiency` precedent — a discrete discipline addition to existing skills is its own concern. Considered [task-tree/planning-redesign](../task-tree/planning-redesign/task.md), a shipped six-concern redesign rather than an open home for new mechanisms, and [interactive-mode](../interactive-mode/task.md), which owns execution-mode dials and the canvas loop rather than planning question discipline.
- **Split rationale.** The mechanism is one edit surface inside `superplan`; the gate retirement is a sweep across four domain skills carrying a real risk of silently softening discipline. Different verdicts, so different tasks.
- Nothing here is high-stakes. The pass worth having is quick and focused on the `CLAUDE.md` line gate over new instruction prose, plus the no-silent-loss audit in `02-domain-gates`.
