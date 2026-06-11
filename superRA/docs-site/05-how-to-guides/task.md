---
title: "How-To Guides for the Researcher Journeys"
status: implemented
depends_on:
  - 01-information-architecture
tags: []
created: 2026-06-10
---

## Objective

Write one task-focused guide per researcher journey, per the approved IA. The journey set (final list per IA) covers at least:

- Give feedback or change scope mid-flight (comments on tasks, what counts as a material change, what the agent does with it).
- Monitor progress (`superra task tree`, `frontier`, the dashboard, reading commits).
- Review and approve work (reading `## Results` and `## Review Notes`, when you are asked questions and why).
- Integrate and PR (what the INTEGRATE phase does for you: protection, sync, doc maturation, finish).
- Adopt superRA in an existing project, including retroactive task-tree creation for work already done.
- Migrate a legacy `PLAN.md`/`RESULTS.md` project.
- Install on other harnesses — Codex, OpenCode, Gemini — absorbing or linking `docs/README.codex.md` and `docs/README.opencode.md` per the IA disposition.

Constraints: each guide is goal-first ("you want X — do this"), short, and links to the owning skill for mechanism detail; public-safe examples; one paragraph per line.

Validation: every journey in the IA's audience model has a guide or an explicit IA-recorded reason it does not need one.

## Results

Seven how-to guide pages authored in [docs/site/04-how-to/](../../../docs/site/04-how-to/), one per IA-defined researcher journey, plus a hub page.

**Pages produced:**

- [docs/site/04-how-to/task.md](../../../docs/site/04-how-to/task.md) — hub page listing all guides with one-line descriptions
- [docs/site/04-how-to/01-install-and-set-up/task.md](../../../docs/site/04-how-to/01-install-and-set-up/task.md) — Claude Code one-command install, Codex two-piece install (plugin + named agents), other harnesses; what gets installed
- [docs/site/04-how-to/02-plan-a-project/task.md](../../../docs/site/04-how-to/02-plan-a-project/task.md) — triggering superplan, reviewing and approving the task tree, writing good objectives (links to task-tree-design.md), retroactive task-tree creation, PLAN.md/RESULTS.md migration
- [docs/site/04-how-to/03-work-with-task-files/task.md](../../../docs/site/04-how-to/03-work-with-task-files/task.md) — reading agent output, review/approve lifecycle and when agents ask questions, giving feedback vs. scope changes (material-change boundary), direct editing, tree/frontier CLI
- [docs/site/04-how-to/04-see-your-work/task.md](../../../docs/site/04-how-to/04-see-your-work/task.md) — launching the live dashboard, three views (tree/DAG/kanban), GitHub Actions artifact share, local static export
- [docs/site/04-how-to/05-integrate-and-ship/task.md](../../../docs/site/04-how-to/05-integrate-and-ship/task.md) — Protect (drift tests, researcher decision point), Sync (semantic merge, why not bare git merge), Integrate (refactor review), Document (results maturation), Finish (PR)
- [docs/site/04-how-to/06-resume-and-revise/task.md](../../../docs/site/04-how-to/06-resume-and-revise/task.md) — resuming from durable task-tree state, handling REVISE verdicts, revising the task tree mid-flight via superplan

**Journey coverage check (task objective vs. delivered):**

| Journey from objective | Covered in |
|---|---|
| Give feedback or change scope mid-flight | 03-work-with-task-files §Give feedback |
| Monitor progress | 03-work-with-task-files §Read the current tree; 04-see-your-work |
| Review and approve work | 03-work-with-task-files §Review and approve work |
| Integrate and PR | 05-integrate-and-ship |
| Adopt superRA in an existing project | 02-plan-a-project §Adopt superRA on an existing project |
| Migrate a legacy PLAN.md/RESULTS.md | 02-plan-a-project §Migrate from PLAN.md / RESULTS.md |
| Install on other harnesses | 01-install-and-set-up |

All seven task-objective journeys covered. All seven IA §1 journey-table rows covered by the corresponding guide pages.

**Authoring contract compliance:** goal-first framing ("you want X — do this"), one paragraph per line, no paraphrasing of agent-facing skill bodies (links to owning skill files instead), public-safe hypothetical examples only, markdown checker returns clean on all seven pages.
