---
title: "Rewrite the execution-mode contract: two axes as presets + seat knob"
status: approved
depends_on:
  - interactive-reference
---

## Objective

Rewrite the execution-mode contract in `skills/using-superra/references/main-agent.md §Execution Modes` and the one-line pointer in `skills/using-superra/SKILL.md §Execution Modes` to describe the two-dial model as **named presets + a seat knob**:

- **Axis A — human cadence:** subagent/autonomous is the default; interactive is an explicit opt-in. Selection is by autonomy and human cadence. Remove the current "Direct mode is a fallback: only for trivial tasks" framing.
- **Axis B — seat assignment:** state that each task's implementer and reviewer seats can each be filled by the main agent or a subagent, chosen per task. Name the model here but **defer the seat-assignment mechanics to `agent-orchestration`** (implemented in the `seat-assignment` task) — point, don't duplicate.
- **Two modes:** `subagent` (autonomous, Axis B picks the seat structure; when the main agent fills a seat it runs that seat's role spec and dispatches the other; default), `interactive` (or `direct`) — main executes directly and **asks before dispatching a reviewer**; route the how-to to `superplan/references/interactive-mode.md`. No `manual` preset — a user wanting the main agent on both seats gets it via interactive with review deferred.
- Remove the instruction to load the direct-mode role references (dropped in `drop-direct-generated`).

Success: the contract presents the two-mode model on the autonomy axis; no "trivial fallback" or `manual` language remains; it points to the superplan interactive reference and to `agent-orchestration` for seat mechanics, and no longer references any direct-mode role file.

## Planner Guidance

This contract *names* the model; the `seat-assignment` task implements the mechanics in `agent-orchestration`, and `superimplement-mode-default` adds the selection default. Keep the three DRY: the contract owns the model vocabulary, the other two point to it. Depends on `interactive-reference` so the contract can point to a reference that exists.

## Results

Rewrote the execution-mode contract as the authoritative home of the two-mode model.

**`skills/using-superra/references/main-agent.md §Execution Modes`** ([main-agent.md](../../../skills/using-superra/references/main-agent.md)) states that two dials set how a task runs; selection is by autonomy and human cadence:

- **Axis A — human cadence:** autonomous (default) vs interactive (explicit opt-in).
- **Axis B — seat assignment:** each task's implementer and reviewer seat filled by main or subagent; `superRA:agent-orchestration §Seat Assignment` owns the structures and the per-task choice (pointer only, no duplication).
- **Two modes:** `subagent` (default) — autonomous; Axis B picks the seat structure, and when the main agent fills a seat it runs that seat's role spec (`implementer.md`/`reviewer.md`) and dispatches the other; everything routes through `agent-orchestration`. `interactive` (or `direct`) — main executes the task itself at high human cadence via `superplan/references/interactive-mode.md`, and **asks the researcher** before dispatching a reviewer rather than dispatching on its own.

Removed the old "Direct mode is a fallback: only for trivial tasks" framing and the "Direct mode protocol" block (the dropped `direct-mode-implementer.md` / `direct-mode-reviewer.md` reads). The Codex-agents pointer is retained unchanged.

**Follow-up revision (interactive-mode branch review).** Per researcher feedback the `manual` preset was dropped (it duplicated interactive-with-deferred-review) and the "not task difficulty" mandate removed; the interactive bullet now states the ask-before-review behavior. `skills/using-superra/SKILL.md §Execution Modes` one-line pointer unchanged in intent. Routing review found one un-swept remnant: `references/codex-instructions.md` still framed Direct mode as a trivial-task fallback — realigned to "interactive is an explicit opt-in by human cadence, not a trivial-task fallback," keeping the legitimate not-Codex-default and tools-unavailable-forced-fallback points.

**DRY held:** the contract owns the model vocabulary; the interactive how-to points to the superplan reference, seat mechanics point to `agent-orchestration`.

**Verification:** `grep -i "trivial\|fallback\|manual\|direct-mode-implementer\|direct-mode-reviewer"` over `main-agent.md §Execution Modes` returns no matches.
