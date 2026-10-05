---
title: "Workflows"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

A superRA project moves through three phases, and you steer each one. The [Quickstart](#/02-quickstart) walks one piece of work through all three; these pages cover one phase at a time.

| Phase | What it does | Say |
|---|---|---|
| **[PLAN](#/05-workflows/01-plan)** | Scopes the work into a task tree you review before any code is written. | `superplan` |
| **[IMPLEMENT](#/05-workflows/02-implement)** | Runs the tasks with you, taking independent review where it earns its cost; autonomous on request. | ask to work a task, or `superimplement` for autonomous |
| **[INTEGRATE](#/05-workflows/03-integrate)** | Protects the results you keep, syncs with your base branch, refactors, and ships. | `superintegrate` |

Say `superra` to let the agent pick up wherever the work stands.

## Run only the phases you need

- **Skip a phase when the work is small.** A self-contained task can skip PLAN; a throwaway experiment can stop after IMPLEMENT. Each phase page says when skipping is reasonable.
- **Re-enter freely.** A discovery mid-implementation or a scope change after integration routes back to PLAN and resumes at the right point, leaving finished work untouched.
- **Existing project: start with onboarding.** Ask the agent to bring the project into superRA; [onboarding](skills/onboarding/SKILL.md) writes a task tree and [reproduction graph](#/04-utility-skills/09-reproducibility) for the work already done.
