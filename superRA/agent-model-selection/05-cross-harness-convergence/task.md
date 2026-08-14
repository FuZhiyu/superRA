---
title: Converge the Cross-Harness Contract and Verification
status: revise
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

## Review Notes

1. **MAJOR:** [`test_contract.py:374-386`](../../../tests/harness-instruction-following/test_contract.py#L374-L386) does not establish the result's claim that policy ownership is single-sourced and adapters “map only syntax.” It proves that the owner phrase, adapter placeholders, and owner pointers exist, but a duplicated rubric in either adapter or another active document would still pass. Strengthen the contract to detect policy restatement on non-owning surfaces, or narrow the result claim and record the evidence that directly verifies the no-duplication requirement.
2. **MAJOR:** The objective requires every opt-in live test to be reported with its exact command and evidence, but [`task.md:28-29`](task.md#L28-L29) records only outcomes. Add both exact commands and the observed output/version evidence to `## Results`; keep the Codex exit-3 result explicitly classified as the Codex 0.147.0 runtime bypass rather than successful enforcement.
3. **MAJOR:** [`docs/README.codex.md:77-83`](../../../docs/README.codex.md#L77-L83) says the hook set uses “reliable Codex-native events,” then documents that Codex 0.147.0 does not emit the `PreToolUse(Agent)` event for `spawn_agent`. Make the preamble consistent with the table's accurate runtime limitation so the guide does not describe the bypassed enforcement point as reliable.
