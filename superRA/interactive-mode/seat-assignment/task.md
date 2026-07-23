---
title: "Seat assignment: support main or subagent in either role"
status: not-started
depends_on:
  - execution-mode-contract
---

## Objective

Extend `agent-orchestration` to support **Axis B seat assignment**: a task's implementer seat and reviewer seat can each be filled by the main agent or a dispatched subagent, in any combination. Add orchestrator guidance for choosing per task:

- **subagent reviewer** for large/routine subtrees — keep main-agent context lean.
- **main-agent reviewer** for small or high-stakes tasks — put the strongest model on the critical, adversarial seat (subagent implements).
- **main implements / subagent reviews** (today's direct pattern) and **subagent implements / main reviews** are both first-class.
- **main fills both seats** (manual) only on explicit researcher request.

The reviewer stays adversarial regardless of who fills the seat.

Success: `agent-orchestration` documents the four seat configurations and a per-task choice heuristic (size / stakes / context-cost), and its dispatch mechanics cover the main-as-reviewer-over-subagent-implementer case; the reviewer's adversarial protocol is unchanged.

## Planner Guidance

`agent-orchestration` owns dispatch, role assignment, and verdict adjudication (`CLAUDE.md` ownership table) — this is the right home. Leave the role specs (`agents/implementer.md`, `agents/reviewer.md`) unchanged: they describe role behavior independent of which agent fills the seat. This task is orchestration-level assignment, not role protocol. Depends on `execution-mode-contract` for the shared model vocabulary.
