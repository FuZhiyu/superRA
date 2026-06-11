---
title: "Roles and Review"
status: not-started
depends_on:  []
tags: []
created: 2026-06-11
---

## Objective

Every task in superRA is done by one agent and checked by another. The **implementer** executes the task; the **reviewer** inspects the result independently and decides whether it can advance. They are separate agents with separate prompts, and the reviewer is adversarial by design — its job is to find the problems the implementer missed, not to rubber-stamp the work. The canonical role behavior lives in the agent specs, [implementer](agents/implementer.md) and [reviewer](agents/reviewer.md); an orchestrator coordinates the hand-off between them per [agent-orchestration](skills/agent-orchestration/SKILL.md).

## The loop

For each task, the implementer reads the objective, does the work, records what it found in `## Results`, and commits. The reviewer then reads the committed result — not the implementer's summary, but the actual files and diff — and checks it against the task's stated objective and the discipline of the relevant [domain skill](#/03-concepts/04-skills-and-agents). It returns one of two verdicts:

- **APPROVE** — no blocking problems. The task moves to `approved` and the work advances.
- **REVISE** — one or more blocking problems. The reviewer writes them up as numbered findings in the task's `## Review Notes`, and the task loops back to the implementer to fix.

On a `REVISE`, the implementer addresses each finding, annotates what it did, and hands back; the reviewer re-reads narrowly to confirm the fixes before approving. Work never advances past a `REVISE`, no matter how trivial the task looks — review is not skippable.

## Why adversarial review

An agent reviewing its own work shares its own blind spots: if it dropped half the sample, it will report that everything looks fine, because from inside its own reasoning it does. A fresh reviewer with a different prompt and the explicit mandate to look for failure catches the silent many-to-many merge, the wrong aggregation, the missing description before a transformation, the unreproducible output. The reviewer grades findings by severity — **CRITICAL** for something that will produce wrong results, **MAJOR** for a likely problem or significant violation, **MINOR** for a suggestion — so the implementer knows what must be fixed before the work can ship and what is merely advice. The full severity rubric and verdict protocol are in the [reviewer spec](agents/reviewer.md). The result is that what advances through a superRA project has survived a second, hostile read at every step — which is the whole point.
