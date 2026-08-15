---
title: Implement the Shared Pre-Dispatch Model Gate
status: approved
depends_on:
  - 01-dispatch-contract
---

## Objective

Implement one cross-platform command hook that rejects validly parsed generic-agent tool calls lacking the explicit model configuration required by the dispatch contract.

- Read `PreToolUse` JSON from stdin and inspect the raw `tool_input`, not the top-level effective `model` field.
- Recognize Claude Code `general-purpose` and Codex `default` generic types, including the harness's valid omitted-type generic form; pass named/custom/specialized agents unchanged.
- For Claude Code, reject a missing, empty, or `inherit` model. For Codex, reject a missing or empty model or reasoning effort.
- Return the supported `PreToolUse` deny payload with a concise reason that tells the caller which explicit argument to choose before retrying. Return parseable empty success output for compliant or unrelated calls.
- Fail open on malformed/unreadable hook input so hook corruption cannot wedge all agent dispatches.
- Add deterministic synthetic tests for both harness payload shapes, every missing-field branch, inheritance rejection, compliant calls, unrelated agent types/tools, malformed input, and JSON validity.

## Details

Follow the existing extensionless Bash hook plus `run-hook.cmd` packaging pattern. A model allowlist would become stale and is unnecessary because each harness validates its own model and reasoning values. Keep `SubagentStart` out of the blocking path.

Before locking field names, capture representative raw `PreToolUse(Agent)` payloads from the installed harness versions or their supported SDK test surfaces. If the current Codex payload cannot distinguish explicit `reasoning_effort` despite the exposed tool schema, stop and replan rather than inferring it from effective defaults.

## Results

- [`hooks/agent-model-guard`](../../../hooks/agent-model-guard) inspects raw `tool_input` and denies only generic Claude `Agent` or Codex `spawn_agent` calls with missing explicit controls. It does not carry a model allowlist and emits `{}` for compliant, unrelated, or unreadable inputs.
- [`test-agent-model-guard.sh`](../../../tests/hooks/test-agent-model-guard.sh) covers 17 synthetic cases: both payload shapes, every missing or empty field, Claude `inherit`, omitted generic types, named agents, unrelated tools, malformed JSON, non-object payloads, and JSON-valid output.
- The synthetic hook suite passes: 17 tests.
