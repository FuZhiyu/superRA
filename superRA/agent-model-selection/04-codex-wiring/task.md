---
title: Wire and Verify Codex Enforcement
status: not-started
depends_on:
  - 02-enforcement-hook
---

## Objective

Enable the shared model-selection gate on Codex's `PreToolUse(Agent)` alias for `spawn_agent` and verify that a default generic dispatch cannot inherit either its model or reasoning effort.

- Register the shared hook under an `Agent` matcher in the Codex plugin hook manifest without changing unrelated lifecycle hooks.
- Extend Codex-only hook and plugin-manifest tests to protect the matcher, raw-argument checks, and parseable output shapes.
- Run a realistic Codex session that captures the pre-dispatch payload and proves missing model configuration is denied before `SubagentStart`, while explicit `model` and `reasoning_effort` reach the generic subagent.
- Distinguish the raw spawn arguments from the hook payload's top-level active-model field and from `agents.default_subagent_model` / `agents.default_subagent_reasoning_effort`; none of those defaults satisfy the explicit-choice rule.
- Record the documented specialized-tool opt-out boundary honestly and update only Codex-specific setup/hook documentation where behavior or troubleshooting changes. Leave shared cross-harness contract tests and documentation to `05-cross-harness-convergence`.

## Planner Guidance

Current official Codex documentation states that `spawn_agent` matches the `Agent` hook alias and that `PreToolUse` can block or rewrite local-function calls. The installed tool schema exposes `model` and `reasoning_effort`; capture the live stdin shape before fixing parser keys. `SubagentStart` remains useful as the positive proof that the compliant call started, not as enforcement.

## Results

(empty)
