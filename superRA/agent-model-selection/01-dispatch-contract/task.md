---
title: Define the Explicit Generic-Dispatch Contract
status: not-started
depends_on: []
---

## Objective

Make explicit generic-agent model selection a single, actionable orchestration contract that both harness adapters and every generic dispatch call site implement without duplicating the tier rubric.

- Update `agent-orchestration` so every generic dispatch explicitly chooses its model configuration at the tool-call boundary after applying the existing tier rubric; inheritance is not a choice.
- Define the shared generic-dispatch template once, then map it to Claude Code's concrete `model` argument and Codex's concrete `model` plus `reasoning_effort` arguments in their owning adapter references.
- Bring the sync author and sync reviewer examples into compliance by pointing to or using that owned dispatch shape.
- Preserve the existing model-tier heuristics and named-role dispatch behavior; do not create a second rubric or hard-code a list of currently available models.
- Apply the repository's line-by-line DRY and Necessity gate to every changed instruction line.

## Planner Guidance

The current rubric already selects Sonnet for Claude Code and medium thinking for Codex by default, but the dispatch templates and generic sync examples omit tool arguments. Keep the behavioral rule near that rubric. Harness-specific parameter names belong in `skills/using-superra/references/{claude,codex}-instructions.md`.

## Results

(empty)
