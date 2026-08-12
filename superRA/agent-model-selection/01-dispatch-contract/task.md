---
title: Define the Explicit Generic-Dispatch Contract
status: implemented
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

- [`agent-orchestration`](../../../skills/agent-orchestration/SKILL.md) owns the single Claude `Agent(subagent_type="general-purpose", model: …, prompt: …)` shape immediately after its existing tier rubric; the role templates now supply only the prompt.
- [`codex-instructions.md`](../../../skills/using-superra/references/codex-instructions.md) maps that selection to concrete `model` and `reasoning_effort` arguments on a bounded `fork_turns="none"` call without copying the rubric.
- The planning, autonomous implementation, integration, interactive, thorough-exploration, and grilling-exploration paths load or point to the owner; their stage templates no longer restate the Agent tool call.

**Verification.** `rg '^Agent:' skills --glob '*.md'` is empty, leaving one owned generic call shape. `uv run --with pytest python -m pytest tests/harness-instruction-following/test_contract.py tests/harness-instruction-following/test_transcript_assertions.py` passes 30 of 33 checks. Two failures predate this task (`#### Seat execution` and `references/decomposition.md` assertions); the remaining stale Codex tool-map assertion belongs to the shared convergence task.

## Review Notes

**Tier:** thorough  
**Focus:** correctness; complete generic-dispatch call-site coverage; Codex/Claude ownership boundaries; DRY and Necessity line gate; test implications

1. **[BLOCKING] The owned Claude call shape omits the generic-agent selector.** [`agent-orchestration/SKILL.md:52`](../../../skills/agent-orchestration/SKILL.md#L52) emits `Agent(model: …, prompt: …)`, but Claude generic dispatches are identified by `subagent_type: "general-purpose"` in the repository's harness evidence ([`test_transcript_assertions.py:76`](../../../tests/harness-instruction-following/test_transcript_assertions.py#L76)). Add the concrete generic selector to the owned call shape so it is an actionable Claude tool call and targets the dispatch class this contract governs.
   → implemented: [`agent-orchestration/SKILL.md`](../../../skills/agent-orchestration/SKILL.md) — the owned shape now passes `subagent_type="general-purpose"`.
2. **[BLOCKING] The Codex adapter's explicit override is not callable without a bounded fork.** [`codex-instructions.md:38`](../../../skills/using-superra/references/codex-instructions.md#L38) supplies `model` and `reasoning_effort` while leaving `fork_turns` implicit; the current Codex dispatch contract does not accept either override on an omitted/full-history fork. Include `fork_turns="none"` or a positive bounded history in the Codex mapping while keeping model-tier judgment in `agent-orchestration`.
   → implemented: [`codex-instructions.md`](../../../skills/using-superra/references/codex-instructions.md) — the mapping now includes `fork_turns="none"`.
3. **[BLOCKING] Planning can dispatch before loading the contract owner, and one planning call site remains unbound.** Thorough planning starts parallel exploration in Phase 1 ([`superplan/SKILL.md:42`](../../../skills/superplan/SKILL.md#L42)) and tells the caller to apply the generic configuration ([`thorough-planning.md:16`](../../../skills/superplan/references/thorough-planning.md#L16)), but `superplan` loads `agent-orchestration` only later for Phase 4 review ([`superplan/SKILL.md:70`](../../../skills/superplan/SKILL.md#L70)). Standard planning can also dispatch exploration from grilling without any generic-shape pointer ([`grilling.md:13`](../../../skills/superplan/references/grilling.md#L13)). Load `superRA:agent-orchestration` before every planning dispatch path and route both exploration sites through its owned shape.
   → implemented: [`superplan/SKILL.md`](../../../skills/superplan/SKILL.md) and [`grilling.md`](../../../skills/superplan/references/grilling.md) — Phase 1 and grilling load the owner before generic exploration; [`thorough-planning.md`](../../../skills/superplan/references/thorough-planning.md) supplies the owned prompt shape.
