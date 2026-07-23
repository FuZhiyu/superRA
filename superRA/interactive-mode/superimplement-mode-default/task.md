---
title: "superimplement mode-selection default"
status: approved
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

Two stale lines in `superimplement/SKILL.md` were replaced to match the new execution-mode model.

1. **§Execution Modes ([SKILL.md:14](../../../skills/superimplement/SKILL.md#L14))** — replaced the old model line ("Direct-mode fallback conditions and its never-skipped review") with the mode-selection default rule, pointing to the contract for definitions:

   > Default to subagent-driven execution on a built tree unless the researcher explicitly requests interactive (or manual); interactive can also be requested mid-flight. The mode definitions are in `using-superra/references/main-agent.md §Execution Modes`.

2. **Step 2 mode note ([SKILL.md:83](../../../skills/superimplement/SKILL.md#L83))** — the prior line named `direct mode` as the primary term and asserted the retired auto-dispatch full-gate default ("Steps 3–4 still dispatch reviewer subagents unless the user overrides"). Replaced with the interactive-mode behavior, pointing to the loop's owner for mechanics:

   > **In interactive mode:** the main agent executes the task directly and runs the canvas loop — self-review always, independent review elective — per `superplan/references/interactive-mode.md`.

Both are one behavior-shaping line plus a pointer; the mode presets and the canvas-loop mechanics are owned by `main-agent.md §Execution Modes` and `superplan/references/interactive-mode.md` respectively and not restated (DRY + Necessity). Verified no other stale `direct mode` / auto-dispatch-default framing remains in the file (remaining "direct" occurrences are "directory" and "direct children").

