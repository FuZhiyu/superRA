---
title: "Planning Workflow Redesign"
status: approved
depends_on: []
tags: []
created: 2026-05-24
---

## Objective

Redesigned the superRA planning workflow (`skills/superplan/SKILL.md`, formerly `planning-workflow`) to be domain-neutral, harness-independent, exploration-first, and existing-task-aware. Shipped in twelve children across six concerns:

1. **Core workflow redesign** — New 5-phase structure (Entry Assessment → Exploration → Domain Setup & Scope → Design & Task Decomposition → Review & Commit) in `skills/superplan/SKILL.md`. Domain-neutral core with domain skills plugging in at Phase 2.
2. **Plan update mechanism** — Dropped `## Decisions` log; replaced with self-sufficient objective rewrites plus `## Revision Notes` as a temporary delta signal (same cleanup lifecycle as review notes).
3. **Harness plan mode compatibility** — `skills/superplan/references/harness-plan-mode.md` teaches agents to use harness plan mode with direct `superRA/` output. Eliminates the two-step migration.
4. **Terminology convention** — "Plan" is the verb; everything in `superRA/` is a task. Documented in `CLAUDE.md §Terminology`, `superplan/SKILL.md`, task-tree references, and swept across all remaining skill files.
5. **PLAN.md remnant cleanup** — Completed migration from PLAN.md/RESULTS.md references to `superRA/` task files across `main-agent.md`, `using-superra`, `superimplement`, `superintegrate`, `agent-orchestration`, `agents/`, `README.md`, `CATEGORIES.md`.
6. **Review and planning protocol** — Added `## Planner Guidance` body section; made implementation review objective-first; added `Stage: planning-review` to the manifest; extended planning review to cover tree design quality (`task-tree-design.md` policy).

## Results

Twelve children across six concerns delivered the planning workflow redesign. All twelve are approved.

**Concern 1 — Core workflow redesign and entry/placement:**
- [skill-rewrite](skill-rewrite/task.md) — Rewrote `skills/superplan/SKILL.md` with a 5-phase domain-neutral structure (Entry Assessment, Exploration, Domain Setup & Scope, Design & Task Decomposition, Review & Commit). Dropped `## Decisions` log; added `## Revision Notes` mechanism. Renamed all sections to use "task tree" terminology.
- [entry-and-placement](entry-and-placement/task.md) — Added Entry Assessment to Phase 0: read existing task tree, assess new-work relevance, offer update-vs-new-root decision; added two-step placement heuristic to Phase 3.
- [placement-and-update-lifecycle](placement-and-update-lifecycle/task.md) — Defined placement by durable home and the update-task lifecycle in `skills/task-tree/references/planning.md §Placing Work` (now superseded by `task-tree-design.md §Placing Work by Durable Home`).

**Concern 2 — Plan update mechanism:**
- [revision-notes](revision-notes/task.md) — Replaced `## Decisions` section and User Decisions Log with `## Revision Notes` across `task-file-contract.md`, `task-tree/SKILL.md`, `agents/implementer.md`, and `agent-orchestration/SKILL.md`.

**Concern 3 — Harness plan mode compatibility:**
- [harness-reference](harness-reference/task.md) — Created `skills/superplan/references/harness-plan-mode.md`: teaches direct `superRA/`-output in plan mode, eliminating the two-step migration.

**Concern 4 — Terminology convention and migration prep:**
- [consolidation](consolidation/task.md) — Consolidated `skills/planning-workflow/references/consolidation.md` (now at `skills/superplan/references/consolidation.md`) and moved terminology convention into `CLAUDE.md §Terminology`.
- [migration-prep](migration-prep/task.md) — Added `plan_migrate.py` parser expectations and normalization checklist to `skills/task-tree/references/internals.md`.
- [main-agent-update](main-agent-update/task.md) — Rewrote `skills/using-superra/references/main-agent.md` to replace all PLAN.md/RESULTS.md references with `superRA/` task-tree operations; renamed §Changes of the Plan to §Changes of the Task Tree.

**Concern 5 — PLAN.md remnant cleanup (planmd-sweep):**
- [planmd-sweep](planmd-sweep/task.md) — Swept PLAN.md/RESULTS.md and "plan as noun" references from `superimplement`, `superintegrate`, `using-superra`, `agent-orchestration`, `agents/`, `README.md`, `CATEGORIES.md`; regenerated Codex named-agent artifacts.

**Concern 6 — Review and planning protocol:**
- [review-planning-protocol](review-planning-protocol/task.md) — Six children shipped: added `## Planner Guidance` body section; made reviewer evaluation objective-first; added `Stage: planning-review` to manifest; required material deviation reporting in `## Results`; updated `task_read.py` ancestor rendering and task anatomy; renamed render header to `=== Context ===` and added focused tree.
- [task-tree-design/04-planning-review](task-tree-design/04-planning-review/task.md) — Extended planning review to critique tree design (durable ownership, branching quality, dependency quality, update-task lifecycle); moved mode definitions into `planning-review.md` (reviewer mechanics owner); reduced `thorough-planning.md §Planning Review` to planner-side context provisioning.

## Review Notes

1. **[MINOR]** Supersession chain left standing across children: `entry-and-placement` (two-step placement) superseded by `placement-and-update-lifecycle` (recursive descent in the since-deleted `task-tree/references/planning.md`), superseded by `task-tree-design/01+02` (policy now in [task-tree-design.md](../../../skills/superplan/references/task-tree-design.md)). Three layers of update tasks survive as approved siblings — the Merge/Prune symptom named in [consolidation.md](../../../skills/superplan/references/consolidation.md) — and `placement-and-update-lifecycle` Results promise a fold-back "at integration" that has not happened. Fix: merge/prune the superseded layers into durable owners at the next consolidation gate.
