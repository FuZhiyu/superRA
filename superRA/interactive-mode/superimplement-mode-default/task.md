---
title: "superimplement mode-selection default"
status: implemented
depends_on:
  - execution-mode-contract
---

## Objective

Add the mode-selection default rule to `superimplement` (which owns execution-mode selection per `using-superra`): **default to subagent-driven execution unless the researcher explicitly requests interactive (or manual).** Applies at `superimplement` entry on a built tree; interactive can also be requested mid-flight.

State it as a short default rule that points to `main-agent.md §Execution Modes` for the mode definitions — do not restate the modes.

Success: `superimplement` carries the subagent-by-default rule with the explicit-opt-in exception, referencing the contract for the mode model rather than re-describing it.

## Planner Guidance

DRY: the contract owns the mode model; this task adds only the *default selection* rule. Depends on `execution-mode-contract` for the vocabulary it points to.

## Results

Replaced the stale mode line in [superimplement/SKILL.md:14](../../../skills/superimplement/SKILL.md#L14) with the mode-selection default rule. The prior text described the retired model ("Direct-mode fallback conditions and its never-skipped review"); the new line states the default and points to the contract for the mode definitions:

> Default to subagent-driven execution on a built tree unless the researcher explicitly requests interactive (or manual); interactive can also be requested mid-flight. The mode definitions are in `using-superra/references/main-agent.md §Execution Modes`.

This is one behavior-shaping default rule (subagent-by-default, explicit opt-in for interactive/manual, mid-flight interactive allowed) plus a pointer to `main-agent.md §Execution Modes` — the presets `subagent` / `interactive` / `manual` are defined there and not restated here (DRY + Necessity). The §Execution Modes heading is retained.

