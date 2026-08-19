---
title: "Workflows"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

A superRA project moves through three phases — **PLAN**, **IMPLEMENT**, **INTEGRATE** — and you steer it through each one. PLAN scopes the work into a task tree you approve. IMPLEMENT runs those tasks with you by default, taking independent review where it earns its cost, and runs them autonomously through implementer and reviewer seats when you ask. INTEGRATE folds the finished work into your codebase so the results stay reproducible, then ships it. The [Quickstart](#/02-quickstart) walks one piece of work through all three end to end; these pages go one phase at a time, for when you want to understand a single phase on its own.

You start each phase by saying its word — `superplan`, `superintegrate`, and `superimplement` for autonomous execution — or `superra` to let the agent pick up wherever the work stands. The phases compose: run only the one you need. A small, self-contained task can skip PLAN; a throwaway experiment can stop after IMPLEMENT. Each page below says when its phase is reasonable to skip.

The cycle is re-enterable. A discovery mid-implementation or a scope change after integration routes back to planning and resumes at the right point, leaving finished work untouched. Re-entering a phase as the work changes is how a project normally runs.

- **[PLAN](#/05-workflows/01-plan)** — scope and decompose the work into a task tree you approve before any code is written.
- **[IMPLEMENT](#/05-workflows/02-implement)** — run tasks with the agent at your cadence, or hand the frontier to autonomous implementer and reviewer seats.
- **[INTEGRATE](#/05-workflows/03-integrate)** — choose the permanent record and its protection, sync with your base, approve one refactoring proposal, execute it, and open the PR.
