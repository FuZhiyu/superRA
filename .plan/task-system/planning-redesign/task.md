---
title: "Planning Workflow Redesign"
status: in-progress
review_status: ~
integration_status: ~
depends_on: []
tags: []
created: 2026-05-24
updated: 2026-05-25
---

## Objective

Redesign the superRA planning workflow to be domain-neutral, harness-independent, exploration-first, and existing-plan-aware — then improve its behavioral quality so agents plan at the right depth, prefer updating over creating, handle retroactive documentation, and can consolidate messy trees.

**Phase 1 concerns (approved):**
1. **Core workflow redesign** — 5-phase structure: Task Tree Discovery → Exploration → Domain Setup & Scope → Design & Task Decomposition → Review & Commit. Domain-neutral core with domain skills plugging in at Phase 2.
2. **Plan update mechanism** — Self-sufficient objective rewrites + `## Revision Notes` as temporary delta signal.
3. **Harness plan mode compatibility** — Reference file for productive plan-mode use, outputting to `.plan/` at exit.
4. **Terminology convention** — "Plan" is the verb. Everything in `.plan/` is a task. `.plan/` is "the task tree."
5. **PLAN.md remnant cleanup** — Migration from PLAN.md/RESULTS.md references across all skills.

**Phase 2 concerns (in progress):**
6. **Entry assessment and task placement** — Replace Phase 0's conceptual split between "new plan" and "plan update" with a unified entry assessment. Add depth tiers (quick/standard/thorough) that modulate how deeply each phase executes. Embed a recursive task placement pecking order (update > nest > create) as the default entry path. Route retroactive planning and consolidation as entry modes, not separate workflows.
7. **Thorough planning dispatch** — New reference defining the dispatch pattern for deep planning: parallel exploration agents, multi-perspective design, exploration synthesis, critical files identification. Adapted from Claude Code's multi-agent plan mode.
8. **Task tree consolidation** — New reference for proactive tree cleanup: overlap detection, dependency repair, merge/prune/restructure mechanics. Triggered standalone or from integration-workflow.

**Conventions:**
- Planning-workflow SKILL.md is the primary file; references stay one level deep
- Domain skills' planning references continue to plug in unchanged at Phase 2
- Direct-mode implementer/reviewer refs are generated files — update canonical agent specs then regenerate
- Follow the DRY/Necessity gate from CLAUDE.md for every new line

## Revision Notes

- **2026-05-25 — Phase 2 scope added.** Three new children (entry-and-placement, thorough-planning, consolidation) cover planning depth, task placement pecking order, and tree consolidation. Status rolled back from approved to in-progress. Phase 1 children remain approved.
- **2026-05-25 — review_status vs status mismatch blocked DAG frontier.** Reviewers set `review_status: approved`, but the DAG frontier requires the task `status:` itself to be `approved`. Orchestrator rollup flip for Tasks 01–03 (skill-rewrite, revision-notes, harness-reference), dashboard regenerated via task-system command, committed as metadata-only updates.

## Results

