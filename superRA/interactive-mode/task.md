---
title: "Execution Mode Model & Interactive Canvas"
status: in-progress
depends_on: []
---

## Objective

Reshape superRA's execution-mode model and add an interactive canvas mode. Model the choice as **two dials, surfaced as named presets plus a seat knob**:

- **Axis A — human cadence (autonomy).** Autonomous (runs to completion) ↔ interactive (pauses often for the researcher). Default is autonomous/subagent; interactive is an explicit opt-in. `superimplement` on a built tree defaults to subagent unless interactive is requested.
- **Axis B — seat assignment.** Each task has an implementer seat and a reviewer seat; each is filled by the main agent or a dispatched subagent. The orchestrator chooses **per task** — subagent reviewer for large/routine subtrees (lean main context), main-agent reviewer for small or high-stakes tasks (strongest model on the critical, adversarial seat). Whoever fills a seat runs that seat's role spec.

Two modes over these dials: **subagent** (autonomous — default; Axis B picks one of three seat structures, main-in-a-seat runs that seat's role spec) and **interactive** (main executes directly at high human cadence — the canvas). There is no `manual` preset; main-fills-both is served by interactive with review deferred. Seat assignment is a knob `agent-orchestration` owns, not a mode.

**Interactive mode** replaces the old direct mode's behavior (renamed `interactive`, `direct` kept as an alias; old full-gate behavior retired). It is a fused **light-plan → execute-yourself → record** loop, not only an implementer mode: it spans lightly scoping a target into a task and executing it, through **retroactive capture** — writing up work already done (a handoff note, or a task reflecting what changed) by running the same loop results-first. In it: co-edit the task file as a live canvas; **self-review always**; **keep the task updated** (results + status) and **ask before review with a tool** as required loop steps; independent review elective (now / defer / skip) reusing `implemented` / `approved` — no new status; positioning retained; full gate ceremony and automatic reviewer dispatch dropped. The selection axis is autonomy/human-involvement — interactive is for work the researcher steers closely, often hard and concentrated. Routed through `superplan`.

Success: the contract documents the two modes on the autonomy axis; the interactive canvas is a loadable superplan reference sized for concentrated work, with keep-updated and tool-ask-before-review as required steps; `agent-orchestration` supports per-task seat assignment (three structures); `superimplement` defaults to subagent unless interactive is requested; the generated direct-mode role references are removed and their generator updated; no gate is silently weakened by the superplan de-crowd.

### Context

superRA-internal skill authoring. Follow `CLAUDE.md` — the DRY + Necessity gate, ownership boundaries, generated-artifact rules, and "instruct, don't justify." No domain skill governs this work; `skill-creator` governs `skills/*/SKILL.md` edits where available.

### Conventions

- Route interactive-mode procedure through `superplan`; `task-tree` remains the tooling (CLI/dashboard) the mode drives, not the procedure home.
- The contract *names* the seat model; `agent-orchestration` owns the seat-assignment *mechanics* — point, do not duplicate.
- Reuse the existing status enum; no new status for the elective-review state.
- Editable-from-dashboard is out of scope — the dashboard is a read-only live canvas view for this workstream.
