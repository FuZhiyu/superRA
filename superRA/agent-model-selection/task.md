---
title: Explicit Model Selection for Generic Agent Dispatches
status: not-started
depends_on: []
---

## Objective

Require every generic agent dispatch in Claude Code and Codex to carry a conscious, explicit model configuration before the subagent starts, whether or not `agent-orchestration` was loaded or a superRA workflow is active.

- Deny a noncompliant dispatch and require the caller to choose and retry; never inject an automatic default.
- Target Claude Code's `general-purpose` agent and Codex's `default` or omitted generic agent type. Leave non-default specialized agent types outside this hook.
- Require a concrete Claude `model` value and reject missing, empty, or `inherit` selections.
- Require both `model` and `reasoning_effort` on Codex generic dispatches because they are separate per-dispatch cost and capability controls.
- Enforce at `PreToolUse` for the `Agent` tool alias. Do not use `SubagentStart` as the enforcement point because both harnesses start the subagent before that event can affect creation.
- Avoid a model-name allowlist; the harness owns model availability and value validation.
- Preserve valid unrelated tool calls and agent dispatches, and fail open only when the hook input itself is unreadable.

### Conventions

- Follow the repository's contributor discipline and DRY / Necessity gate in [`CLAUDE.md`](../../CLAUDE.md); this work changes workflow instructions and hooks, so implementation must load `skill-creator` before editing any `skills/*/SKILL.md`.
- Preserve v0.4's single dispatch mechanism established by [`v04-lean-workflow/role-skills`](../v04-lean-workflow/role-skills/task.md): general-purpose/default agents load role skills at dispatch. Do not reintroduce `agents/`, `.codex/agents/`, or named-agent generator plumbing.

## Planner Guidance

Both harnesses now document the same usable interception point: `PreToolUse` can inspect raw local-function arguments, `spawn_agent` matches the `Agent` alias in Codex, and a deny decision prevents the call. `SubagentStart` is useful only for audit/context because it cannot stop creation. The raw tool input, not the hook payload's top-level effective model, is the evidence that the caller made an explicit choice.

Keep the policy in [`skills/agent-orchestration/SKILL.md`](../../skills/agent-orchestration/SKILL.md), Claude's argument shape in the shared `Agent` dispatch templates and call sites, Codex's translation in [`skills/using-superra/references/codex-instructions.md`](../../skills/using-superra/references/codex-instructions.md), and deterministic enforcement in one shared hook script. In v0.4, every dispatched seat uses a generic/default agent that loads its role skill, so sweep every `Agent` call site across planning, implementation, integration, and interactive-mode references.

Official capability references consulted during planning:

- [Claude Code hooks: `PreToolUse` and `SubagentStart`](https://code.claude.com/docs/en/hooks)
- [Claude Code subagent model selection](https://code.claude.com/docs/en/sub-agents#choose-a-model)
- [Codex hooks: tool coverage and `PreToolUse`](https://learn.chatgpt.com/docs/hooks#tool-coverage)
- [Codex subagent model and reasoning selection](https://learn.chatgpt.com/docs/agent-configuration/subagents#choosing-models-and-reasoning)

This remains a new top-level workstream because the concern crosses orchestration policy, every role-skill dispatch, shared hook code, and both harnesses. The approved `v04-lean-workflow/role-skills` task owns role loading and `v04-lean-workflow/workflow-defaults` owns cadence and review defaults; neither owns per-dispatch model selection. The `task-tree/codex-task-hooks` subtree owns task-file reconciliation rather than generic-agent admission.

## Critical Files

- [`skills/agent-orchestration/SKILL.md`](../../skills/agent-orchestration/SKILL.md) — authoritative model-tier policy and dispatch mechanics
- [`skills/using-superra/references/codex-instructions.md`](../../skills/using-superra/references/codex-instructions.md) — Codex translation of the shared `Agent` dispatch contract
- [`hooks/hooks.json`](../../hooks/hooks.json) — Claude Code lifecycle-hook wiring
- [`hooks/hooks-codex.json`](../../hooks/hooks-codex.json) — Codex lifecycle-hook wiring
- [`tests/harness-instruction-following/test_contract.py`](../../tests/harness-instruction-following/test_contract.py) — cross-harness static contract checks

## Results

(empty)

## Revision Notes

- Adapted during transfer to the v0.4 worktree: every dispatched seat now uses a generic/default agent with a role skill, so the contract covers all `Agent` call sites; removed v0.3 named-agent, generator, and Claude-adapter assumptions.
