---
title: Define the Explicit Generic-Dispatch Contract
status: approved
depends_on: []
---

## Objective

Make explicit generic-agent model selection a single, actionable orchestration contract that both harnesses and every generic dispatch call site implement without duplicating the tier rubric.

- Update `agent-orchestration` so every generic dispatch explicitly chooses its model configuration at the tool-call boundary after applying the existing tier rubric; inheritance is not a choice.
- Define the shared dispatch template once with Claude Code's concrete `model` argument, relying on the harness's default agent type; map it to Codex's concrete `model` plus `reasoning_effort` arguments in `codex-instructions.md`.
- Bring every generic `Agent` call site across planning, implementation, integration, and interactive-mode references into compliance by pointing to or using that owned dispatch shape.
- Preserve the existing model-tier heuristics and v0.4 role-skill dispatch behavior; do not create a second rubric or hard-code a list of currently available models.
- Apply the repository's line-by-line DRY and Necessity gate to every changed instruction line.

## Details

The current rubric already selects Sonnet for Claude Code and medium thinking for Codex by default, but v0.4's generic dispatch templates omit explicit tool arguments. Keep the behavioral rule near that rubric. Claude uses the shared `Agent` surface; Codex-specific parameter translation belongs in `skills/using-superra/references/codex-instructions.md`.

## Results

[`agent-orchestration`](../../../skills/agent-orchestration/SKILL.md) owns one default call shape, `Agent(model: …, prompt: …)`; dispatch templates contain only `Prompt:` bodies. [`codex-instructions.md`](../../../skills/using-superra/references/codex-instructions.md) maps it to explicit `model` and `reasoning_effort` arguments without specifying `agent_type` or copying the tier rubric.

**Verification.** The guard suite passes 17/17, focused contract tests pass 3/3, and harness compatibility plus task-tree checks pass. The full instruction suite passes 125/127; the two failures are unchanged v0.4 baseline assertions for `#### Seat execution` and `references/decomposition.md`.
