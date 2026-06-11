---
title: "Skills and Agents"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

superRA is built from **skills** and **agents**. A skill is a unit of instruction the agent loads when it is relevant; an agent is a role — implementer or reviewer — that loads the skills it needs for the task in front of it. Skills split into three working categories, and an agent assembles the right set for each step rather than carrying everything at once. The authoritative grouping is in [CATEGORIES.md](skills/CATEGORIES.md), and the agent-facing map from each stage to its required skills is the Skill-Load Manifest in [using-superRA](skills/using-superRA/SKILL.md). The [Reference › Skills and Agents](#/05-reference/04-skills-and-agents) page lists every skill as a lookup.

## Three kinds of skill

**Workflow skills** own the procedural shape of each phase — what agent to dispatch, in what order, with what hand-off rules. These are the three phase skills you met in [The Workflow](#/03-concepts/01-the-workflow), plus the orchestration skill that coordinates the agents. They are domain-neutral: the same workflow governs a regression and a proof.

**Domain skills** carry the discipline of a particular kind of research. `econ-data-analysis` enforces the Iron Law that no data is transformed before it is described, and ships pitfall catalogs for merges, time series, and aggregations. `theory-modeling` makes the agent define objects and assumptions before manipulating equations. `writing` governs drafting, polishing, and reviewing prose. Each domain skill teaches *how to do that work well*, and the workflow skills stay out of its way.

**Utility skills** are domain-neutral tools any agent can reach for — protecting results with drift tests, merging branches by intent, rendering reports in markdown, syncing data across worktrees, and the task-tree tooling itself. They are called by workflow skills, by agents, or directly by you in an interactive session.

## When a domain skill loads

The key compositional idea is that a domain skill loads *on top of* a workflow phase, not instead of it. When a task touches data analysis, the implementer working that task loads `econ-data-analysis` alongside the implement-phase workflow skill, and the reviewer loads the same domain skill so it reviews against the right discipline. The workflow supplies the choreography — dispatch, review, advance — and the domain skill supplies the standards applied inside it. This is why adding a new kind of research to superRA means writing one new domain skill rather than forking the whole workflow: the implementer–reviewer pair, the task tree, and the integration phase all carry over unchanged. Currently implemented domains are data analysis, theory-modeling, and writing; literature review and simulation are planned.
