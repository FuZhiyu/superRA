---
title: "The Workflow"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

superRA runs every project through three phases — **PLAN → IMPLEMENT → INTEGRATE** — and each phase has a skill that teaches the agent how to carry it out. The phases are domain-agnostic: the same shape governs a data analysis, a theory derivation, or a writing pass, and the [domain skill](#/03-concepts/04-skills-and-agents) supplies the discipline that applies inside each phase. The authoritative behavior for each phase lives in its skill — [superplan](skills/superplan/SKILL.md), [superimplement](skills/superimplement/SKILL.md), and [superintegrate](skills/superintegrate/SKILL.md) — with the shared, cross-phase disciplines in [using-superra](skills/using-superra/SKILL.md).

## The three phases

**PLAN** scopes your request and decomposes it into a [task tree](#/03-concepts/02-the-task-tree): a directory of small `task.md` files, one per unit of work, with the dependencies between them recorded. Planning is where the work is sized and the intended approach is written down, before any code is generated. The output is a committed task tree that the rest of the workflow reads from and writes to.

**IMPLEMENT** executes the tree one task at a time. For each task, an implementer agent does the work and a separate reviewer agent inspects it; the task advances only on `APPROVE`, and a `REVISE` loops it back with specific findings to fix. The [Roles and Review](#/03-concepts/03-roles-and-review) page covers this loop in detail. Implementation optimizes for speed and correctness of the research itself — the strict, codebase-level discipline comes later.

**INTEGRATE** turns finished work into something that can land. It protects the key results against future drift, syncs the branch with your base intent-aware, refactors the post-sync changes to fit the codebase, matures the documentation, and ships via PR or merge. The [Integration and Protection](#/03-concepts/05-integration-and-protection) page explains why this is a phase of its own rather than a final commit.

## A cycle, not a pipeline

The phases are ordered, but research rarely runs straight through them once. A discovery while implementing, a reviewer request during integration, or a scope change after a merge all route back through planning, which walks the task dependency graph and resumes at the right re-entry point. Re-entry is the normal case, not an error path: unrelated finished tasks keep their state while the affected part of the tree is replanned and re-run. This is what lets a superRA project absorb the mid-course corrections that real research demands without throwing away work that was already approved.

## Autonomous, with a human in the loop

The agent drives the work forward on its own and stops only for things that are genuinely yours to decide — a hard blocker, a choice beyond its authority, or a milestone you asked to be consulted on. It does not pause for routine approval at every step, and it does not run unsupervised past decisions that should be yours. Because the project's state lives in the [task tree](#/03-concepts/02-the-task-tree) rather than in a single agent's context window, you can read where things stand at any time, edit a task's objective to redirect the work, or leave a comment the next agent will see.
