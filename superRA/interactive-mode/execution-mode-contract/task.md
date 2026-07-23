---
title: "Rewrite the execution-mode contract around the autonomy axis"
status: not-started
depends_on:
  - interactive-reference
---

## Objective

Rewrite the execution-mode contract in `skills/using-superra/references/main-agent.md §Execution Modes` and the one-line pointer in `skills/using-superra/SKILL.md §Execution Modes`.

- **Two active modes**, selected by autonomy / human-involvement — **not task difficulty**. Remove the current "Direct mode is a fallback: only for trivial tasks" framing.
  - **Subagent** — autonomous, orchestrated implementer/reviewer dispatch (unchanged).
  - **Interactive** — human-in-the-loop, low-autonomy, pauses frequently for feedback; the default non-subagent mode. Name it "interactive (or `direct`, for backward compatibility)."
- Route the interactive how-to to `superplan/references/interactive-mode.md`.
- Remove the instruction to load the direct-mode role references (`direct-mode-implementer.md` / `direct-mode-reviewer.md`) — they are being dropped in `drop-direct-generated`.

Success: no "trivial fallback" language remains; interactive is the named default non-subagent mode with the backward-compat alias noted; the contract points to the superplan reference and no longer to any direct-mode role file.

## Planner Guidance

Depends on `interactive-reference` so the contract can point to a reference that exists. Keep the subagent-mode contract intact. This task removes the *references* to the direct-mode role files; the files themselves and their generator are handled in `drop-direct-generated`.
