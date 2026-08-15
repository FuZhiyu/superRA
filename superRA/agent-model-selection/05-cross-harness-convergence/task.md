---
title: Converge the Cross-Harness Contract and Verification
status: approved
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

## Details

This task is the sole owner of files that compare or describe both harnesses. Read the upstream tasks' `## Results` and their captured payload evidence before changing shared assertions so the combined tests reflect demonstrated behavior rather than assumed schema symmetry.

## Results

- [`test_contract.py`](../../../tests/harness-instruction-following/test_contract.py) and [`check-harness-compatibility.sh`](../../../tests/check-harness-compatibility.sh) require both manifests to run the same shared guard at `PreToolUse(Agent)` and retain harness-specific events. The dispatch contract omits redundant default agent-type selectors; the guard still distinguishes omitted/default calls from specialized agents.
- The [load contract](../../../tests/harness-instruction-following/load_contract.json), [verification guide](../../../tests/harness-instruction-following/README.md), and [Codex setup guide](../../../docs/README.codex.md) distinguish CI-safe wiring/raw-input coverage from live runtime behavior.
- Rebase verification passes the 17-case shared guard suite, harness compatibility, task-tree validation, and focused contract tests. The instruction-following suite passes 125 of 127 checks; the two failures are unchanged v0.4 baseline assertions for the retired `#### Seat execution` table and `references/decomposition.md` route.
- Claude's opt-in Agent SDK smoke command is `RUN_LIVE_HARNESS=1 uv run --with claude-agent-sdk python tests/hooks/claude-agent-model-live.py`. Claude Agent SDK 0.2.139 with Claude Code 2.1.233 printed `PASS Claude live model guard: denied=1 allowed=1 starts=1`; the captured calls show a model-less denial, an explicit `model: haiku` retry, and one `SubagentStart`.
- Codex's opt-in CLI smoke command is `RUN_LIVE_HARNESS=1 bash tests/hooks/codex-agent-model-live.sh`. Codex CLI 0.147.0 printed `LIMITATION Codex did not route spawn_agent through PreToolUse(Agent); SubagentStart still fired` and `{"pretooluse_payloads": 0, "start": "default"}`, then exited 3. This is runtime-bypass evidence, not successful enforcement: the official wiring and deterministic raw-input behavior are implemented, but Codex 0.147.0's specialized `spawn_agent` path bypasses the enforcement point.
- The final branch diff contains no generated-agent edits, model-name allowlist, or unrelated hook behavior changes.
