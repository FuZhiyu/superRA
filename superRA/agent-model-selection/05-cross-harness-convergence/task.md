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

- [`test_contract.py`](../../../tests/harness-instruction-following/test_contract.py) and [`check-harness-compatibility.sh`](../../../tests/check-harness-compatibility.sh) require both manifests to run the same shared guard at `PreToolUse(Agent)` and retain harness-specific events. The contract makes `agent-orchestration` the sole owner of the model-tier and generic-call sections, requires the Codex adapter to map both controls back to that owner, and keeps model names out of the adapter and guard.
- The [load contract](../../../tests/harness-instruction-following/load_contract.json), [verification guide](../../../tests/harness-instruction-following/README.md), and [Codex setup guide](../../../docs/README.codex.md) distinguish CI-safe wiring/raw-input coverage from live runtime behavior.
- Six synthetic hook suites pass: 86 cases. The harness compatibility script passes, including generated-agent drift checks. The focused registry/ownership tests pass: 2 tests. The complete instruction-following suite passes: 128 tests, including all 16 tests in [`test_contract.py`](../../../tests/harness-instruction-following/test_contract.py).
- Claude's opt-in Agent SDK smoke command is `RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk python tests/hooks/claude-agent-model-live.py`. Claude Agent SDK 0.2.139 with Claude Code 2.1.233 printed `PASS Claude live model guard: denied=1 allowed=1 starts=1`; the captured calls show a model-less denial, an explicit `model: haiku` retry, and one `SubagentStart`.
- Codex's opt-in CLI smoke command is `RUN_LIVE_HARNESS=1 bash tests/hooks/codex-agent-model-live.sh`. Codex CLI 0.147.0 printed `LIMITATION Codex did not route spawn_agent through PreToolUse(Agent); SubagentStart still fired` and `{"pretooluse_payloads": 0, "start": "default"}`, then exited 3. This is runtime-bypass evidence, not successful enforcement: the official wiring and deterministic raw-input behavior are implemented, but Codex 0.147.0's specialized `spawn_agent` path bypasses the enforcement point.
- The final branch diff contains no generated-agent edits, model-name allowlist, or unrelated hook behavior changes.

## Review Notes

1. **MAJOR:** [`test_contract.py:374-386`](../../../tests/harness-instruction-following/test_contract.py#L374-L386) does not establish the result's claim that policy ownership is single-sourced and adapters “map only syntax.” It proves that the owner phrase, adapter placeholders, and owner pointers exist, but a duplicated rubric in either adapter or another active document would still pass. Strengthen the contract to detect policy restatement on non-owning surfaces, or narrow the result claim and record the evidence that directly verifies the no-duplication requirement.
   → implemented: [`test_contract.py`](../../../tests/harness-instruction-following/test_contract.py) enforces one structural owner for the rubric and Claude call shape, checks the Codex mapping and owner pointer, and rejects model-name policy in the adapter and guard; `## Results` states that bounded claim.
2. **MAJOR:** The objective requires every opt-in live test to be reported with its exact command and evidence, but [`task.md:28-29`](task.md#L28-L29) records only outcomes. Add both exact commands and the observed output/version evidence to `## Results`; keep the Codex exit-3 result explicitly classified as the Codex 0.147.0 runtime bypass rather than successful enforcement.
   → implemented: [`task.md`](task.md) records both opt-in commands, harness versions, observed output, exit status, and the Codex runtime-bypass classification.
3. **MAJOR:** [`docs/README.codex.md:77-83`](../../../docs/README.codex.md#L77-L83) says the hook set uses “reliable Codex-native events,” then documents that Codex 0.147.0 does not emit the `PreToolUse(Agent)` event for `spawn_agent`. Make the preamble consistent with the table's accurate runtime limitation so the guide does not describe the bypassed enforcement point as reliable.
   → implemented: [`docs/README.codex.md`](../../../docs/README.codex.md) describes Codex-native events with per-hook runtime limits instead of claiming uniform reliability.
