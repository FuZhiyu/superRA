---
title: "superimplement mode-selection default"
status: revise
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

## Review Notes

1. **MAJOR** — [superimplement/SKILL.md:83](../../../skills/superimplement/SKILL.md#L83) still carries the retired model. The line 14 fix replaced the stale mode line, but Step 2 still says: "**In direct mode:** the main agent does Steps 1–2 directly; Steps 3–4 still dispatch reviewer subagents unless the user overrides." This is stale on two counts. (a) Terminology: `direct` is now only a backward-compat alias; the primary term is `interactive` per [main-agent.md:52](../../../skills/using-superra/references/main-agent.md#L52). (b) Behavior: it asserts that the non-subagent mode *auto-dispatches reviewer subagents at Steps 3–4 unless overridden* — exactly the "old full-gate behavior / automatic reviewer dispatch" the parent workstream retires. The new contract is self-review always, independent review elective (now/defer/skip). Line 83 therefore directly contradicts the new model. No sibling task edits `superimplement/SKILL.md`, and the dispatch directs the stale-framing check here, so this line is in scope for this task. Fix: update or remove line 83 so it no longer names `direct mode` as the primary term or asserts the retired auto-dispatch default; align it with interactive's elective-review behavior (or drop it if interactive procedure now lives entirely in `superplan/references/interactive-mode.md`). The `## Results` claim that "the prior text described the retired model" is only partially true — line 83 also described it and remains.

