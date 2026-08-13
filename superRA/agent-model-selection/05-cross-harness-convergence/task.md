---
title: Converge the Cross-Harness Contract and Verification
status: implemented
depends_on:
  - 03-claude-wiring
  - 04-codex-wiring
---

## Objective

Reconcile the completed Claude Code and Codex wiring into one coherent, documented hook contract and prove the combined plugin state preserves both harnesses' enforcement behavior.

- Own shared cross-harness surfaces, including `tests/harness-instruction-following/test_contract.py`, `tests/check-harness-compatibility.sh`, the hook load contract/inventory, and shared hook documentation; the two upstream wiring tasks must not edit these files.
- Verify both manifests register the same shared hook at `PreToolUse(Agent)` while retaining their unrelated harness-specific lifecycle hooks and output requirements.
- Verify the shared policy remains single-sourced in `agent-orchestration`, with the shared dispatch surface and Codex adapter expressing only harness syntax and active docs pointing to the owner rather than restating the rubric.
- Run the complete synthetic hook suites, harness compatibility checks, instruction-following contract tests, and the two recorded live-smoke paths. Report any live test that remains opt-in with its exact command and evidence instead of presenting it as CI coverage.
- Ensure the final diff contains no model-name allowlist, reintroduced named-agent/generator plumbing, or unrelated hook behavior changes.

## Planner Guidance

This task is the sole owner of files that compare or describe both harnesses. Read the upstream tasks' `## Results` and their captured payload evidence before changing shared assertions so the combined tests reflect demonstrated behavior rather than assumed schema symmetry.

## Results

- [`test_contract.py`](../../../tests/harness-instruction-following/test_contract.py) and [`check-harness-compatibility.sh`](../../../tests/check-harness-compatibility.sh) require both manifests to run the same shared guard at `PreToolUse(Agent)`, retain harness-specific events, keep the policy in `agent-orchestration`, map only syntax in adapters, and keep model names out of the guard.
- The [load contract](../../../tests/harness-instruction-following/load_contract.json), [verification guide](../../../tests/harness-instruction-following/README.md), and [Codex setup guide](../../../docs/README.codex.md) distinguish CI-safe wiring/raw-input coverage from live runtime behavior.
- Six synthetic hook suites pass: 86 cases. The harness compatibility script passes, including generated-agent drift checks. The instruction-following contract passes: 16 tests.
- Claude's opt-in Agent SDK smoke passed with one denied model-less call, one explicit `haiku` retry, and one `SubagentStart`.
- Codex's opt-in CLI smoke exited 3 with `pretooluse_payloads: 0` and `start: default` on version 0.147.0. The official `PreToolUse(Agent)` wiring and deterministic raw-input behavior are implemented, but this runtime's specialized `spawn_agent` path bypasses the enforcement point.
- The final branch diff contains no generated-agent edits, model-name allowlist, or unrelated hook behavior changes.
