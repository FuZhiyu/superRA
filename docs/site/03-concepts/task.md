---
title: "Concepts"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

These pages explain the model behind superRA — the *why* under the mechanisms you meet in the [Quickstart](#/02-quickstart) and use in the [How-To guides](#/04-how-to). Read them in order for the full picture, or jump to the one you need. Each page links to the skill or agent file that owns the behavior it describes, so the canonical detail is always one hop away.

- [The Workflow](#/03-concepts/01-the-workflow) — the PLAN → IMPLEMENT → INTEGRATE cycle, why it is a cycle rather than a pipeline, and what "autonomous with a human in the loop" means in practice.
- [The Task Tree](#/03-concepts/02-the-task-tree) — how a directory of `task.md` files becomes the project's living state, with status rollup, sibling dependencies, and the frontier of ready work.
- [Roles and Review](#/03-concepts/03-roles-and-review) — the implementer–reviewer pair, the APPROVE/REVISE protocol, and what adversarial review buys you.
- [Skills and Agents](#/03-concepts/04-skills-and-agents) — how workflow, domain, and utility skills compose, and when a domain skill loads on top of a workflow.
- [Integration and Protection](#/03-concepts/05-integration-and-protection) — drift tests, intent-aware semantic merge, and why integration is a distinct phase rather than a final commit.
