---
title: "Rewrite the execution-mode contract: two axes as presets + seat knob"
status: not-started
depends_on:
  - interactive-reference
---

## Objective

Rewrite the execution-mode contract in `skills/using-superra/references/main-agent.md §Execution Modes` and the one-line pointer in `skills/using-superra/SKILL.md §Execution Modes` to describe the two-dial model as **named presets + a seat knob**:

- **Axis A — human cadence:** subagent/autonomous is the default; interactive is an explicit opt-in. Remove the current "Direct mode is a fallback: only for trivial tasks" framing — selection is autonomy, **not difficulty**.
- **Axis B — seat assignment:** state that each task's implementer and reviewer seats can each be filled by the main agent or a subagent, chosen per task; manual (main fills both) is explicit-only. Name the model here but **defer the seat-assignment mechanics to `agent-orchestration`** (implemented in the `seat-assignment` task) — point, don't duplicate.
- **Presets:** `subagent` (both seats subagents, default), `interactive` (name it "interactive (or `direct`, for backward compatibility)"; route the how-to to `superplan/references/interactive-mode.md`), `manual`.
- Remove the instruction to load the direct-mode role references (dropped in `drop-direct-generated`).

Success: the contract presents the presets + seat-knob model on the autonomy axis; no "trivial fallback" language remains; it points to the superplan interactive reference and to `agent-orchestration` for seat mechanics, and no longer references any direct-mode role file.

## Planner Guidance

This contract *names* the model; the `seat-assignment` task implements the mechanics in `agent-orchestration`, and `superimplement-mode-default` adds the selection default. Keep the three DRY: the contract owns the model vocabulary, the other two point to it. Depends on `interactive-reference` so the contract can point to a reference that exists.
