---
title: "Planning Workflow Redesign"
status: revise
depends_on: []
tags: []
created: 2026-05-24
---

## Objective

Redesign the superRA planning workflow to be domain-neutral, harness-independent, exploration-first, and existing-plan-aware. The current workflow is tightly coupled to harness plan mode, loses information during format migration, and lacks exploration and existing-plan-check phases. The new design borrows exploration and structured-planning patterns from Claude Code and Codex plan modes, adapted for multi-domain research workflows.

**Six concerns in scope:**
1. **Core workflow redesign** — New 5-phase structure: Task Tree Discovery → Exploration → Domain Setup & Scope → Design & Task Decomposition → Review & Commit. Domain-neutral core with domain skills plugging in at Phase 2. Discovery assesses relevance to existing tasks (only offers update when related). Task tree presented to user for review before commit.
2. **Plan update mechanism** — Drop `## Decisions` log (too bloated). Replace with: (a) self-sufficient objective rewrites (full context, not patches), and (b) `## Revision Notes` as a temporary delta signal (what changed, significance) — same cleanup lifecycle as review notes.
3. **Harness plan mode compatibility** — Reference file teaching agents to use harness plan mode productively while outputting directly to `.plan/` at exit. In plan mode, present a flattened view of the planned `.plan/` changes for user review. Eliminates the two-step migration that loses information.
4. **Terminology convention** — "Plan" is the verb (the planning process), not the noun. Everything in `.plan/` is a task. `.plan/` is "the task tree." Document this in CLAUDE.md, planning-workflow SKILL.md, and task-tree references.
5. **PLAN.md remnant cleanup** — Complete the migration from PLAN.md/RESULTS.md references to `.plan/` task files across all remaining skill references (main-agent, domain planning refs, direct-mode refs, using-superRA).
6. **Review and planning protocol** — Distinguish binding `## Objective` content from advisory `## Planner Guidance`, make implementation review objective-first, and support semantic planning review for thorough planning and handoff scenarios.

**Conventions:**
- Planning-workflow SKILL.md is the primary file; references stay one level deep
- Domain skills' planning references (`econ-data-analysis/references/planning.md`, etc.) continue to plug in unchanged at Phase 2 — only their PLAN.md text references get updated
- Direct-mode implementer/reviewer refs are generated files — update canonical agent specs then regenerate
- Follow the DRY/Necessity gate from CLAUDE.md for every new line

## Results

## Review Notes

1. **[CRITICAL]** [task.md](task.md) — `## Results` is empty while all 12 children are approved. The rollup discipline this workstream itself codified ([superimplement completion gate #3](../../../skills/superimplement/SKILL.md), [task-file-contract.md §Section Ownership](../../../skills/task-tree/references/task-file-contract.md)) requires an orchestrator-written parent rollup; a reader landing on the workstream root learns nothing about what shipped. Fix: write a selective rollup of the six concerns with links down to child `## Results`.
2. **[MAJOR]** [task.md](task.md) — `## Objective` is stale on every Stale Content Checklist axis: it still says `.plan/` throughout (the tree is `superRA/`), names `planning-workflow SKILL.md` (renamed `superplan`), describes concern 1 as "Task Tree Discovery" (replaced by Entry Assessment), and the Conventions block pins "Planning-workflow SKILL.md is the primary file". Objectives are current-state contracts. Fix: rewrite as the current-state contract, or trim once the Results rollup carries the record.
3. **[MINOR]** Supersession chain left standing across children: `entry-and-placement` (two-step placement) superseded by `placement-and-update-lifecycle` (recursive descent in the since-deleted `task-tree/references/planning.md`), superseded by `task-tree-design/01+02` (policy now in [task-tree-design.md](../../../skills/superplan/references/task-tree-design.md)). Three layers of update tasks survive as approved siblings — the Merge/Prune symptom named in [consolidation.md](../../../skills/superplan/references/consolidation.md) — and `placement-and-update-lifecycle` Results promise a fold-back "at integration" that has not happened. Fix: merge/prune the superseded layers into durable owners at the next consolidation gate.
