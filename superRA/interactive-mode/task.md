---
title: "Execution Mode Model & Interactive Canvas"
status: not-started
depends_on: []
---

## Objective

Reshape superRA's execution-mode model and add an interactive canvas mode. Model the choice as **two dials, surfaced as named presets plus a seat knob**:

- **Axis A — human cadence (autonomy).** Autonomous (runs to completion) ↔ interactive (pauses often for the researcher). Default is autonomous/subagent; interactive is an explicit opt-in. `superimplement` on a built tree defaults to subagent unless interactive is requested.
- **Axis B — seat assignment.** Each task has an implementer seat and a reviewer seat; each is filled by the main agent or a dispatched subagent. The orchestrator chooses **per task** — subagent reviewer for large/routine subtrees (lean main context), main-agent reviewer for small or high-stakes tasks (strongest model on the critical, adversarial seat). Main-agent-fills-both (manual) only on explicit request.

Named presets over these dials: **subagent** (both seats subagents, autonomous — default), **interactive** (main participates as co-editor + high human cadence — the canvas), **manual** (main fills both seats, explicit only). Seat-assignment is a documented knob `agent-orchestration` supports, not a fourth mode.

**Interactive mode** replaces the old direct mode's behavior (same non-subagent slot; renamed `interactive`, `direct` kept as a backward-compat alias; old full-gate behavior retired). It is a fused **light-plan → execute-yourself → record** loop, not only an implementer mode: it spans lightly scoping a target into a task and executing it, through **retroactive capture** — doing the work first and writing it down after, the ultimate interactive form (embedding superplan's retroactive documentation mode). In it: co-edit the task file as a live canvas, **self-review always**, **independent review elective** (now / defer / skip) reusing `implemented` / `approved` — no new status, positioning retained, full gate ceremony and automatic reviewer dispatch dropped. The selection axis is autonomy/human-involvement, **not task difficulty** — interactive is for work the researcher steers closely, often hard and concentrated. Routed through `superplan` (which already owns both light planning and retroactive documentation).

Success: the contract documents the two axes as presets + seat knob on the autonomy axis; the interactive canvas is a loadable superplan reference sized for concentrated work; `agent-orchestration` supports per-task seat assignment; `superimplement` defaults to subagent unless interactive is requested; the generated direct-mode role references are removed and their generator updated; no gate is silently weakened by the superplan de-crowd.

### Context

superRA-internal skill authoring. Follow `CLAUDE.md` — the DRY + Necessity gate, ownership boundaries, generated-artifact rules, and "instruct, don't justify." No domain skill governs this work; `skill-creator` governs `skills/*/SKILL.md` edits where available.

### Conventions

- Route interactive-mode procedure through `superplan`; `task-tree` remains the tooling (CLI/dashboard) the mode drives, not the procedure home.
- The contract *names* the seat model; `agent-orchestration` owns the seat-assignment *mechanics* — point, do not duplicate.
- Reuse the existing status enum; no new status for the elective-review state.
- Editable-from-dashboard is out of scope — the dashboard is a read-only live canvas view for this workstream.
