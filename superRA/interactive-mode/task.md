---
title: "Interactive Execution Mode"
status: not-started
depends_on: []
---

## Objective

Introduce an **interactive execution mode** for superRA: a human-in-the-loop, low-autonomy mode in which the researcher and main agent co-edit task files as a live canvas — capturing targets, objectives, and results with fast, iterative, instantly-committed edits — pausing frequently for researcher feedback. Paired with the live dashboard it forms a light-plan I/O surface: brainstorm together, capture into tasks, execute together.

The mode selection axis is **autonomy / human-involvement, not task difficulty** — interactive is for work the researcher wants to steer closely, which is often hard and concentrated, not trivial.

Interactive mode **replaces the behavior of the current direct mode** (same non-subagent slot; renamed to `interactive`, with `direct` retained as a backward-compat alias). The old direct-mode behavior — main agent playing implementer/reviewer with the full gate walk and mandatory reviewer dispatch — is retired. In interactive mode: **self-review is always performed; independent review is elective** (researcher chooses review-now / defer / skip), reusing the existing `implemented` (self-reviewed, awaiting/deferred) vs `approved` (independently reviewed) statuses — no new status values. **Positioning discipline is retained**; the full gate ceremony and automatic reviewer dispatch are dropped for this mode. Routed through `superplan` (positioning judgment lives there and references load with their owning skill).

Success: the two active modes (subagent, interactive) are documented on the autonomy axis; the interactive canvas loop is a loadable superplan reference sized for concentrated work; the generated direct-mode role references are removed and their generator updated; no gate is silently weakened by the superplan de-crowd.

### Context

This is superRA-internal skill authoring. Follow `CLAUDE.md` — the DRY + Necessity gate, ownership boundaries, generated-artifact rules, and "instruct, don't justify." No domain skill governs this work; `skill-creator` governs `skills/*/SKILL.md` edits where available.

### Conventions

- Route interactive-mode procedure through `superplan`; `task-tree` remains the tooling (CLI/dashboard) the mode drives, not the procedure home.
- Reuse the existing status enum; do not add status values for the elective-review state.
- Editable-from-dashboard is out of scope — the dashboard is a read-only live canvas view for this workstream.
