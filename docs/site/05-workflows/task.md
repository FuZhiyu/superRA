---
title: "Workflows"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

A superRA project moves through three phases — **PLAN**, **IMPLEMENT**, **INTEGRATE** — and you steer it through each one. PLAN scopes the work into a task tree you approve. IMPLEMENT runs those tasks through an implementer–reviewer pair until each is approved. INTEGRATE folds the finished work into your codebase so the results stay reproducible, then ships it. The [Quickstart](#/02-quickstart) walks one piece of work through all three end to end; these pages go one phase at a time, for when you want to understand a single phase on its own.

You start each phase by saying its word — `superplan`, `superimplement`, `superintegrate` — or just `superra` to let the agent pick up wherever the work stands. The phases compose: run only the one you need. A small, self-contained task can skip PLAN; a throwaway experiment can stop after IMPLEMENT. Each page below says when its phase is reasonable to skip.

The cycle is re-enterable, not a one-way pipeline. A discovery mid-implementation or a scope change after integration routes back to planning and resumes at the right point, leaving finished work untouched. Re-entering a phase as the work changes is the normal way a project runs, not an exception.

- **[PLAN](#/05-workflows/01-plan)** — scope and decompose the work into a task tree you approve before any code is written.
- **[IMPLEMENT](#/05-workflows/02-implement)** — run each task through its implementer–reviewer pair, resuming from wherever the work stands.
- **[INTEGRATE](#/05-workflows/03-integrate)** — protect the results, sync with your base, refactor for fit, and open the PR.

