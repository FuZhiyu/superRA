---
title: Explicit Model Selection for Generic Agent Dispatches
status: not-started
depends_on: []
---

## Objective

Require every generic agent dispatch in Claude Code and Codex to carry a conscious, explicit model configuration before the subagent starts, whether or not `agent-orchestration` was loaded or a superRA workflow is active.

- Deny a noncompliant dispatch and require the caller to choose and retry; never inject an automatic default.
- Target Claude Code's `general-purpose` agent and Codex's `default` or omitted generic agent type. Leave named, custom, and specialized agent types outside this hook.
- Require a concrete Claude `model` value and reject missing, empty, or `inherit` selections.
- Require both `model` and `reasoning_effort` on Codex generic dispatches because they are separate per-dispatch cost and capability controls.
- Enforce at `PreToolUse` for the `Agent` tool alias. Do not use `SubagentStart` as the enforcement point because both harnesses start the subagent before that event can affect creation.
- Avoid a model-name allowlist; the harness owns model availability and value validation.
- Preserve valid unrelated tool calls and agent dispatches, and fail open only when the hook input itself is unreadable.

### Conventions

- Follow the repository's contributor discipline and DRY / Necessity gate in [`CLAUDE.md`](../../CLAUDE.md); this work changes workflow instructions and hooks, so implementation must load `skill-creator` before editing any `skills/*/SKILL.md`.
- The generated Codex agent files [`.codex/agents/superra_implementer.toml`](../../.codex/agents/superra_implementer.toml) and [`.codex/agents/superra_reviewer.toml`](../../.codex/agents/superra_reviewer.toml) remain out of scope because this task does not change their canonical `agents/*` sources. If that boundary changes, edit the canonical agent source and regenerate with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --project` rather than editing either TOML directly.

## Planner Guidance

Both harnesses now document the same usable interception point: `PreToolUse` can inspect raw local-function arguments, `spawn_agent` matches the `Agent` alias in Codex, and a deny decision prevents the call. `SubagentStart` is useful only for audit/context because it cannot stop creation. The raw tool input, not the hook payload's top-level effective model, is the evidence that the caller made an explicit choice.

Keep the policy in [`skills/agent-orchestration/SKILL.md`](../../skills/agent-orchestration/SKILL.md), harness syntax in the existing Claude/Codex adapter references, and deterministic enforcement in one shared hook script. Current generic call sites are the sync author and reviewer dispatches in [`skills/superintegrate/references/sync.md`](../../skills/superintegrate/references/sync.md).

Official capability references consulted during planning:

- [Claude Code hooks: `PreToolUse` and `SubagentStart`](https://code.claude.com/docs/en/hooks)
- [Claude Code subagent model selection](https://code.claude.com/docs/en/sub-agents#choose-a-model)
- [Codex hooks: tool coverage and `PreToolUse`](https://learn.chatgpt.com/docs/hooks#tool-coverage)
- [Codex subagent model and reasoning selection](https://learn.chatgpt.com/docs/agent-configuration/subagents#choosing-models-and-reasoning)

This is a new top-level workstream because the concern crosses orchestration policy, integration's generic sync dispatches, shared hook code, and two harness adapters. The approved `interactive-mode` subtree owns human cadence and seat assignment, while `task-tree/codex-task-hooks` owns task-file reconciliation; neither owns per-dispatch model selection.

## Critical Files

- [`skills/agent-orchestration/SKILL.md`](../../skills/agent-orchestration/SKILL.md) — authoritative model-tier policy and dispatch mechanics
- [`skills/superintegrate/references/sync.md`](../../skills/superintegrate/references/sync.md) — current generic author and reviewer dispatches
- [`hooks/hooks.json`](../../hooks/hooks.json) — Claude Code lifecycle-hook wiring
- [`hooks/hooks-codex.json`](../../hooks/hooks-codex.json) — Codex lifecycle-hook wiring
- [`tests/harness-instruction-following/test_contract.py`](../../tests/harness-instruction-following/test_contract.py) — cross-harness static contract checks

## Review Notes

1. **[BLOCKING] The Claude and Codex wiring siblings have overlapping mutable ownership but no ordering or convergence contract.** The Claude task claims shared manifest/compatibility tests and active hook documentation ([03-claude-wiring/task.md:13-16](03-claude-wiring/task.md#L13-L16)); the Codex task separately claims instruction-following/compatibility tests and the same active hook documentation surface ([04-codex-wiring/task.md:13-16](04-codex-wiring/task.md#L13-L16)). Both become frontier-ready after `02-enforcement-hook`, while the parent explicitly identifies one cross-harness contract file as shared ([task.md:39-45](task.md#L39-L45)). That makes them unsafe for the workflow's normal parallel-frontier execution and leaves no single task accountable for the final cross-harness test/document state. Assign disjoint files plus one owner for every shared cross-harness surface, serialize one wiring task after the other and give the downstream task the combined-state check, or add a small convergence task depending on both.

## Results

(empty)
