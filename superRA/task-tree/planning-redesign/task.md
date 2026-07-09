---
title: "Planning Workflow Redesign"
status: not-started
depends_on: []
---

## Objective

Redesign the superRA planning workflow (`skills/superplan/SKILL.md`) to be domain-neutral, harness-independent, exploration-first, and existing-task-aware, across six concerns:

1. **Core workflow redesign** — a 5-phase structure (Entry Assessment → Exploration → Domain Setup & Scope → Design & Task Decomposition → Review & Commit), with a domain-neutral core and domain skills plugging in at Phase 2.
2. **Plan update mechanism** — drop the `## Decisions` log; replace it with self-sufficient objective rewrites plus `## Revision Notes` as a temporary delta signal (same cleanup lifecycle as review notes).
3. **Harness plan-mode compatibility** — teach agents to use harness plan mode with direct `superRA/` output, eliminating the two-step migration.
4. **Terminology convention** — "Plan" is the verb; everything in `superRA/` is a task.
5. **PLAN.md remnant cleanup** — migrate PLAN.md/RESULTS.md references to `superRA/` task files across the skills, agents, and docs.
6. **Review and planning protocol** — add the `## Planner Guidance` body section; make implementation review objective-first; add `Stage: planning-review` to the manifest; extend planning review to critique tree-design quality.

## Results

The redesign shipped across all six concerns.

- **Core workflow and entry/placement.** `skills/superplan/SKILL.md` carries the 5-phase domain-neutral structure with a `## Revision Notes` mechanism replacing the `## Decisions` log. Entry Assessment reads the existing task tree and offers an update-vs-new-top-level decision; placement is defined by durable home, and the update-task lifecycle now lives in `skills/superplan/references/task-tree-design.md §Placing Work by Durable Home`.
- **Plan update mechanism.** The `## Decisions` section and User Decisions Log are replaced by `## Revision Notes` across `task-file-contract.md`, `task-tree/SKILL.md`, `agents/implementer.md`, and `agent-orchestration/SKILL.md`.
- **Harness plan mode.** `skills/superplan/references/harness-plan-mode.md` teaches direct `superRA/`-output in plan mode.
- **Terminology and migration prep.** The terminology convention lives in `CLAUDE.md §Terminology`; `plan_migrate.py` parser expectations and a normalization checklist are in `skills/task-tree/references/internals.md`; `skills/using-superra/references/main-agent.md` was rewritten to use `superRA/` task-tree operations throughout.
- **PLAN.md remnant cleanup.** PLAN.md/RESULTS.md and "plan as noun" references were swept from `superimplement`, `superintegrate`, `using-superra`, `agent-orchestration`, `agents/`, `README.md`, and `CATEGORIES.md`; the Codex named-agent artifacts were regenerated.
- **Review and planning protocol.** The `## Planner Guidance` body section was added; reviewer evaluation is objective-first; `Stage: planning-review` is in the manifest; material deviation reporting is required in `## Results`; `task_read.py` ancestor rendering was updated (the render header is `=== Context ===` with a focused tree). Planning review now critiques tree design (durable ownership, branching quality, dependency quality, update-task lifecycle), with the mode definitions owned by `skills/superplan/references/planning-review.md`.

The superseded placement layers (two-step placement, then recursive descent in the since-deleted `task-tree/references/planning.md`) were folded here at consolidation; the current policy lives in `skills/superplan/references/task-tree-design.md`.
