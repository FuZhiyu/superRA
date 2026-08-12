---
title: Converge the Cross-Harness Contract and Verification
status: not-started
depends_on:
  - 03-claude-wiring
  - 04-codex-wiring
---

## Objective

Reconcile the completed Claude Code and Codex wiring into one coherent, documented hook contract and prove the combined plugin state preserves both harnesses' enforcement behavior.

- Own shared cross-harness surfaces, including `tests/harness-instruction-following/test_contract.py`, `tests/check-harness-compatibility.sh`, the hook load contract/inventory, and shared hook documentation; the two upstream wiring tasks must not edit these files.
- Verify both manifests register the same shared hook at `PreToolUse(Agent)` while retaining their unrelated harness-specific lifecycle hooks and output requirements.
- Verify the shared policy remains single-sourced in `agent-orchestration`, with adapters expressing only harness syntax and active docs pointing to the owner rather than restating the rubric.
- Run the complete synthetic hook suites, harness compatibility checks, instruction-following contract tests, and the two recorded live-smoke paths. Report any live test that remains opt-in with its exact command and evidence instead of presenting it as CI coverage.
- Ensure the final diff contains no model-name allowlist, generated-agent edits, or unrelated hook behavior changes.

## Planner Guidance

This task is the sole owner of files that compare or describe both harnesses. Read the upstream tasks' `## Results` and their captured payload evidence before changing shared assertions so the combined tests reflect demonstrated behavior rather than assumed schema symmetry.

## Results

(empty)
