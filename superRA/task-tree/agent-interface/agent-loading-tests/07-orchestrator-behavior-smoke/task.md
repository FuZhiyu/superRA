---
title: "Add Orchestrator Behavior Smoke"
status: not-started
depends_on:
  - 06-ci-safe-contract-tests
tags: []
created: 2026-06-19
---

## Objective

Add an opt-in live smoke that verifies workflow-orchestrator behavior for `superimplement`, using the smallest realistic mock task tree. The test should ask the main agent to run `superimplement` on a trivial frontier and verify structural evidence that it followed the documented dispatch path instead of silently implementing inline.

The smoke should check:

- The main agent enters the `superimplement` path and loads or references the owning workflow contract.
- The main agent loads `agent-orchestration` before writing a dispatch prompt.
- Default behavior attempts implementer subagent dispatch for the frontier task or same-parent bundle.
- Reviewer dispatch is attempted after implementation, or the transcript records a documented fallback reason if the harness cannot expose or run subagents.
- Direct-mode fallback is accepted only when it matches the documented exceptions: no harness subagent support, explicit user override, or task triviality with reviewer dispatch still preserved.

## Planner Guidance

Keep the mock frontier intentionally cheap. The assigned task should be a sentinel-collection or one-file artifact task that can complete in one short turn; the smoke is testing orchestrator dispatch behavior, not implementation quality.

Use structural transcript evidence, not prose claims. Claude evidence may be role-agent dispatch events; Codex evidence may be `spawn_agent(agent_type="superra_implementer")` and `spawn_agent(agent_type="superra_reviewer")` events or the closest JSONL-exposed equivalent. If a harness cannot expose subagent dispatch events, document the limitation and make the smoke skip or assert the strongest observable fallback rather than failing on invisible behavior.

## Results

