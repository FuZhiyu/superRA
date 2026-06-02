---
title: "Planning Workflow Redesign"
status: in-progress
depends_on: []
tags: []
created: 2026-05-24
---

## Objective

Redesign the superRA planning workflow to be domain-neutral, harness-independent, exploration-first, and existing-plan-aware. The current workflow is tightly coupled to harness plan mode, loses information during format migration, and lacks exploration and existing-plan-check phases. The new design borrows exploration and structured-planning patterns from Claude Code and Codex plan modes, adapted for multi-domain research workflows.

**Five concerns in scope:**
1. **Core workflow redesign** — New 5-phase structure: Task Tree Discovery → Exploration → Domain Setup & Scope → Design & Task Decomposition → Review & Commit. Domain-neutral core with domain skills plugging in at Phase 2. Discovery assesses relevance to existing tasks (only offers update when related). Task tree presented to user for review before commit.
2. **Plan update mechanism** — Drop `## Decisions` log (too bloated). Replace with: (a) self-sufficient objective rewrites (full context, not patches), and (b) `## Revision Notes` as a temporary delta signal (what changed, significance) — same cleanup lifecycle as review notes.
3. **Harness plan mode compatibility** — Reference file teaching agents to use harness plan mode productively while outputting directly to `.plan/` at exit. In plan mode, present a flattened view of the planned `.plan/` changes for user review. Eliminates the two-step migration that loses information.
4. **Terminology convention** — "Plan" is the verb (the planning process), not the noun. Everything in `.plan/` is a task. `.plan/` is "the task tree." Document this in CLAUDE.md, planning-workflow SKILL.md, and task-system references.
5. **PLAN.md remnant cleanup** — Complete the migration from PLAN.md/RESULTS.md references to `.plan/` task files across all remaining skill references (main-agent, domain planning refs, direct-mode refs, using-superRA).

**Conventions:**
- Planning-workflow SKILL.md is the primary file; references stay one level deep
- Domain skills' planning references (`econ-data-analysis/references/planning.md`, etc.) continue to plug in unchanged at Phase 2 — only their PLAN.md text references get updated
- Direct-mode implementer/reviewer refs are generated files — update canonical agent specs then regenerate
- Follow the DRY/Necessity gate from CLAUDE.md for every new line

## Results

