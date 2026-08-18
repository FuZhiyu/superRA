---
title: "Explicit Model Selection for Generic Agent Dispatches"
status: approved
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

## Details

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

Explicit model selection is contract, code, and wiring in both harnesses; Claude Code enforces it before a subagent starts, Codex 0.147.0 does not.

- **One call shape, one owner.** [`agent-orchestration`](../../skills/agent-orchestration/SKILL.md) defines `Agent(model: …, prompt: …)` and [`codex-instructions.md`](../../skills/using-superra/references/codex-instructions.md) maps it to Codex's `model` plus `reasoning_effort`. Dispatch templates carry only `Prompt:` bodies, and neither surface copies the tier rubric or names an agent type — see [01-dispatch-contract](01-dispatch-contract/task.md).
- **The gate is one shared script.** [`hooks/agent-model-guard`](../../hooks/agent-model-guard) inspects raw `tool_input` at `PreToolUse(Agent)`, denies only generic dispatches missing their explicit controls, and passes named and specialized agents through. It carries no model allowlist and emits `{}` for compliant, unrelated, or unreadable input — see [02-enforcement-hook](02-enforcement-hook/task.md).
- **Claude Code enforcement is proven end to end.** A live Agent SDK run captured a model-less dispatch denied, an explicit `model: haiku` retry, and exactly one `SubagentStart` — see [03-claude-wiring](03-claude-wiring/task.md).
- **Codex enforcement is wired but bypassed at runtime.** Codex CLI 0.147.0 starts `spawn_agent` without emitting `PreToolUse`, despite the documented `Agent` matcher; the deterministic raw-input behavior is verified by synthetic tests, and the live smoke exits 3 recording the bypass — see [04-codex-wiring](04-codex-wiring/task.md).
- **Shared cross-harness surfaces** — the contract tests, compatibility check, hook load contract, and Codex setup guide — assert both manifests run the same guard and separate CI-safe wiring coverage from live runtime behavior; see [05-cross-harness-convergence](05-cross-harness-convergence/task.md).

Both live smokes are opt-in because they spend an authenticated model turn: `RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk python tests/hooks/claude-agent-model-live.py` and `RUN_LIVE_HARNESS=1 bash tests/hooks/codex-agent-model-live.sh`.
