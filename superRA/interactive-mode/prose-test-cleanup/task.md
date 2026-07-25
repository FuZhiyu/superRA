---
title: "Replace Prose-Specific Tests with Behavioral Contracts"
status: not-started
depends_on:  []
---

## Objective

Remove existing tests that treat authored instruction prose, labels, or diagnostic wording as exact regression oracles. Preserve only structured contracts and observable behavior: parsed tables/frontmatter/schema/path identities, generated-artifact equality, tool/event ordering, file/status mutations, command execution, and dispatch evidence. Refactor affected reports to expose structured finding codes/subjects where tests currently match human messages. Update harness documentation and fixtures so no deleted prose canary remains. Success: a whole-repo test audit finds no exact authored-instruction sentence/phrase oracle; behavior-oriented replacements pass with red-green evidence; no legitimate structural or generated-artifact contract is weakened.

## Planner Guidance

The read-only integration audit identified affected surfaces across harness test_contract, always-loaded/stage/domain live canaries and fixtures, transcript diagnostics, SDK/Codex evidence tests, and sync_codex_agents stderr wording. Use that inventory as navigation, reclassifying each assertion before deletion. This is the researcher-confirmed cleanup prompted during Protect.

## Results
