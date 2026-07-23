---
title: "superimplement mode-selection default"
status: not-started
depends_on:
  - execution-mode-contract
---

## Objective

Add the mode-selection default rule to `superimplement` (which owns execution-mode selection per `using-superra`): **default to subagent-driven execution unless the researcher explicitly requests interactive (or manual).** Applies at `superimplement` entry on a built tree; interactive can also be requested mid-flight.

State it as a short default rule that points to `main-agent.md §Execution Modes` for the mode definitions — do not restate the modes.

Success: `superimplement` carries the subagent-by-default rule with the explicit-opt-in exception, referencing the contract for the mode model rather than re-describing it.

## Planner Guidance

DRY: the contract owns the mode model; this task adds only the *default selection* rule. Depends on `execution-mode-contract` for the vocabulary it points to.
