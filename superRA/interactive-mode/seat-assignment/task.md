---
title: "Seat assignment: support main or subagent in either role"
status: implemented
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

## Planner Guidance

`agent-orchestration` owns dispatch, role assignment, and verdict adjudication (`CLAUDE.md` ownership table) — this is the right home. Leave the role specs (`agents/implementer.md`, `agents/reviewer.md`) unchanged: they describe role behavior independent of which agent fills the seat. This task is orchestration-level assignment, not role protocol. Depends on `execution-mode-contract` for the shared model vocabulary.

## Results

Added a `## Seat Assignment` section to [skills/agent-orchestration/SKILL.md](../../../skills/agent-orchestration/SKILL.md), placed after `## Dispatch Templates` and before `## Orchestrator Duties`. It adds the Axis-B mechanics the execution-mode contract defers here; the role specs `agents/implementer.md` and `agents/reviewer.md` are untouched.

Delivered against the success criteria:

- **Three seat configurations** as a table (implementer × reviewer, each main or subagent): subagent/subagent (default), subagent/main (high-stakes), main/subagent (context-heavy but review-worthy). No main/main row.
- **Per-seat role spec** — the section states that whoever fills a seat runs that seat's role spec (`implementer.md` for the implementer, `reviewer.md` for the reviewer), main agent or subagent alike.
- **Per-task choice heuristic** on three signals: size/routineness → subagent reviewer (lean main context); stakes/silent-error risk → main-agent reviewer (strongest model on the adversarial seat); context cost → delegate whichever seat can't be carried inline.
- **Dispatch mechanics for the main-as-reviewer-over-subagent-implementer case** (`### Main agent in the reviewer seat`): no reviewer dispatch — the main agent loads `agents/reviewer.md` + the task's stage/domain manifest skills, reviews the same `Git range:` adversarially, writes `## Review Notes`, folds findings into §Handling Reviewer Feedback and re-dispatches the implementer, or sets `approved` on a clean pass. The mirror (main in the implementer seat) runs `agents/implementer.md` over its own work, then dispatches a reviewer.

**Follow-up revision (interactive-mode branch review).** Per researcher feedback the `main/main` (manual) row was dropped (→ three configs), and the autonomous main-implementer seat was decoupled from the interactive canvas: that seat runs `implementer.md`; the interactive canvas loop is the separate **interactive** mode.

DRY + Necessity: the section does not restate the modes model (owned by `main-agent.md §Execution Modes`, which defers seat mechanics here) and points to `agents/implementer.md`, `agents/reviewer.md`, `interactive-mode.md`, and §Handling Reviewer Feedback rather than paraphrasing them.
