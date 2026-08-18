---
title: "Seat assignment: support main or subagent in either role"
status: approved
depends_on:
  - execution-mode-contract
---

## Objective

Extend `agent-orchestration` to support **Axis B seat assignment**: a task's implementer seat and reviewer seat can each be filled by the main agent or a dispatched subagent, in any combination. Add orchestrator guidance for choosing per task:

- **subagent reviewer** for large/routine subtrees — keep main-agent context lean.
- **main-agent reviewer** for small or high-stakes tasks — put the strongest model on the critical, adversarial seat (subagent implements).
- **main implements / subagent reviews** and **subagent implements / main reviews** are both first-class.

These are the three seat structures of **subagent** mode (autonomous). Whoever fills a seat runs that seat's role spec (`implementer.md` / `reviewer.md`), main agent or subagent alike — the reviewer stays adversarial regardless of who fills it. There is no main-fills-both preset; that is served by interactive mode with review deferred.

Success: `agent-orchestration` documents the three seat configurations and a per-task choice heuristic (size / stakes / context-cost), and its dispatch mechanics cover the main-as-reviewer-over-subagent-implementer case; the reviewer's adversarial protocol is unchanged.

## Details

`agent-orchestration` owns dispatch, role assignment, and verdict adjudication (`CLAUDE.md` ownership table) — this is the right home. Leave the role specs (`agents/implementer.md`, `agents/reviewer.md`) unchanged: they describe role behavior independent of which agent fills the seat. This task is orchestration-level assignment, not role protocol. Depends on `execution-mode-contract` for the shared model vocabulary.

## Results

[agent-orchestration §Seat Assignment](../../../skills/agent-orchestration/SKILL.md) owns the Axis-B mechanics the execution-mode contract defers to it.

- **Three seat configurations**, as a table over implementer × reviewer: subagent/subagent (default), subagent/main (high stakes), main/subagent (small, or context-heavy but review-worthy). There is no main/main row — that case is served by interactive mode with review deferred.
- **Whoever fills a seat runs that seat's role spec**, main agent or subagent alike.
- **The per-task choice reads three signals:** size and routineness argue for a subagent reviewer to keep main context lean; stakes and silent-error risk argue for the main agent on the adversarial seat; context cost decides which seat cannot be carried inline.
- **A main-filled reviewer seat dispatches nothing.** The main agent loads the reviewer spec plus the task's stage and domain skills, reviews the same `Git range:` adversarially, writes `## Review Notes`, and either folds findings into §Handling Reviewer Feedback and re-dispatches the implementer or sets `approved`. The mirror runs the implementer spec over its own work, then dispatches a reviewer.

The autonomous main-implementer seat is deliberately not the interactive canvas: that seat runs the implementer spec, and interactive is a separate mode.

**Protection is structural, not prose-matching.** [test_contract.py](../../../tests/harness-instruction-following/test_contract.py) parses the seat table and requires exactly the three supported pairs; two transcript fixtures in [transcript_assertions.py](../../../tests/harness-instruction-following/transcript_assertions.py) require each main-filled route to read its role spec and dispatch the other seat. Red-green verification removed each required event, observed the failure, and restored it.

The role specs this task pointed at were `agents/implementer.md` and `agents/reviewer.md`; [v04-lean-workflow/role-skills](../../v04-lean-workflow/role-skills/task.md) replaced them with the `implement-task` and `review-task` skills, and the seat routing follows.
