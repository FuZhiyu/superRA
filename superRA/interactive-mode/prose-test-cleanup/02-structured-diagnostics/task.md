---
title: "Replace Diagnostic Wording Assertions with Structured Findings"
status: not-started
depends_on:  []
---

## Objective

Replace tests that assert human diagnostic prose or authored instruction wording with structured finding codes/subjects and observable outcomes. Cover transcript assertions, SDK/Codex load evidence, contract tests, generated-agent conflict handling, and any interactive behavior evaluator reached by Protect. Preserve legitimate structural/generated contracts. Success: reports expose stable structured fields, CLI prose remains untested presentation, and targeted/full suites pass with red-green evidence.

## Planner Guidance

Audit inventory: test_contract prose/list/fixture scans; transcript_assertions and its tests; SDK/Codex evidence tests; stage/domain diagnostic-message assertions; sync_codex_agents unmanaged-conflict stderr assertion. The active protection fix already owns interactive transcript/seat behavior and should land into this child rather than exact prose assertions.

## Results
