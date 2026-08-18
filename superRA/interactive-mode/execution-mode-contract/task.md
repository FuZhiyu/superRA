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

## Details

This contract *names* the model; the `seat-assignment` task implements the mechanics in `agent-orchestration`, and `superimplement-mode-default` adds the selection default. Keep the three DRY: the contract owns the model vocabulary, the other two point to it. Depends on `interactive-reference` so the contract can point to a reference that exists.

## Results

[main-agent.md §Execution Modes](../../../skills/using-superra/references/main-agent.md) owns the mode vocabulary: two dials, selection by autonomy and human cadence.

- **Axis A — human cadence:** autonomous (default at the time) versus interactive, an explicit opt-in.
- **Axis B — seat assignment:** each task's implementer and reviewer seat filled by main or subagent, with the structures and the per-task choice owned by [agent-orchestration §Seat Assignment](../../../skills/agent-orchestration/SKILL.md) — pointed at, not duplicated.
- **Two modes.** `subagent` is autonomous: Axis B picks the seat structure, a main-filled seat runs that seat's role spec and dispatches the other, and everything routes through `agent-orchestration`. `interactive` (alias `direct`) has the main agent execute the task itself at high human cadence and **ask the researcher** before dispatching a reviewer.

The `manual` preset is gone — it duplicated interactive with review deferred. So are the "direct mode is a fallback for trivial tasks" framing and the direct-mode protocol block that read the since-deleted generated mirrors. The Codex adapter separates three capability states in a structured table: normal dispatch, a missing-agent setup path, and a harness-forced in-session implementer→reviewer pass when Codex exposes no agent tool at all.

**Protection is structural.** [test_contract.py](../../../tests/harness-instruction-following/test_contract.py) parses the Codex availability table and distinguishes unavailable agent tooling from a missing installation; interactive and seat behavior are checked by the transcript evaluators in [test_transcript_assertions.py](../../../tests/harness-instruction-following/test_transcript_assertions.py).

v0.4 flipped Axis A's default to interactive and retired the named-agent Codex path; see [v04-lean-workflow](../../v04-lean-workflow/task.md).
