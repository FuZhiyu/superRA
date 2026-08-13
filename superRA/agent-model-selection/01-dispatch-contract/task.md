---
title: Define the Explicit Generic-Dispatch Contract
status: approved
depends_on: []
---

## Objective

Make explicit generic-agent model selection a single, actionable orchestration contract that both harnesses and every generic dispatch call site implement without duplicating the tier rubric.

- Update `agent-orchestration` so every generic dispatch explicitly chooses its model configuration at the tool-call boundary after applying the existing tier rubric; inheritance is not a choice.
- Define the shared generic-dispatch template once with Claude Code's concrete `model` argument, then map it to Codex's concrete `model` plus `reasoning_effort` arguments in `codex-instructions.md`.
- Bring every generic `Agent` call site across planning, implementation, integration, and interactive-mode references into compliance by pointing to or using that owned dispatch shape.
- Preserve the existing model-tier heuristics and v0.4 role-skill dispatch behavior; do not create a second rubric or hard-code a list of currently available models.
- Apply the repository's line-by-line DRY and Necessity gate to every changed instruction line.

## Planner Guidance

The current rubric already selects Sonnet for Claude Code and medium thinking for Codex by default, but v0.4's generic dispatch templates omit explicit tool arguments. Keep the behavioral rule near that rubric. Claude uses the shared `Agent` surface; Codex-specific parameter translation belongs in `skills/using-superra/references/codex-instructions.md`.

## Results

Generic dispatches now require an explicit configuration at the tool boundary.

- [`agent-orchestration`](../../../skills/agent-orchestration/SKILL.md) owns the single Claude `Agent(model: …, prompt: …)` shape immediately after its existing tier rubric; the role templates now supply only the prompt.
- [`codex-instructions.md`](../../../skills/using-superra/references/codex-instructions.md) maps that selection to concrete `model` and `reasoning_effort` arguments without copying the rubric.
- The planning, autonomous implementation, integration, and interactive dispatch paths point to the owner; their stage templates no longer restate the Agent tool call.

**Verification.** `rg '^Agent:' skills --glob '*.md'` is empty, leaving one owned `Agent(model: …)` call shape. `uv run --with pytest python -m pytest tests/harness-instruction-following/test_contract.py` passes 12 of 15 checks. Two failures predate this task (`#### Seat execution` and `references/decomposition.md` assertions); the remaining stale Codex tool-map assertion belongs to the shared convergence task.
