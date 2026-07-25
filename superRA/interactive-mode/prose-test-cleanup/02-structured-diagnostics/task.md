---
title: "Replace Diagnostic Wording Assertions with Structured Findings"
status: implemented
depends_on:  []
---

## Objective

Replace tests that assert human diagnostic prose or authored instruction wording with structured finding codes/subjects and observable outcomes. Cover transcript assertions, SDK/Codex load evidence, contract tests, generated-agent conflict handling, and any interactive behavior evaluator reached by Protect. Preserve legitimate structural/generated contracts. Success: reports expose stable structured fields, CLI prose remains untested presentation, and targeted/full suites pass with red-green evidence.

## Planner Guidance

Audit inventory: test_contract prose/list/fixture scans; transcript_assertions and its tests; SDK/Codex evidence tests; stage/domain diagnostic-message assertions; sync_codex_agents unmanaged-conflict stderr assertion. The active protection fix already owns interactive transcript/seat behavior and should land into this child rather than exact prose assertions.

## Results

- Added a shared structured finding record with stable `code`, `outcome`,
  `subject`, `path`, event-index, and actual-value fields. Transcript,
  SDK/Codex load-evidence, and stage/domain evaluators now populate those
  records while retaining their human-readable messages for CLI presentation.
- Replaced tests of diagnostic wording with assertions on finding codes and
  structured fields. Transcript checks continue to enforce task/file reads,
  dispatches, interactive opt-in and event ordering, artifact paths/values, and
  parse-error line numbers.
- Replaced the generated-agent unmanaged-conflict stderr assertion with the
  observable safety contract: the unmanaged file remains byte-for-byte
  unchanged after the refused sync.
- Removed the contract test that scanned a live fixture for selected authored
  words; retained task-read JSON structure, hook paths/matchers, schemas, IDs,
  event ordering, file mutations, and generated-artifact contracts.
- Integrated five residual domain-test deletion hunks from the sibling canary
  cleanup after its shared source changes landed first; this keeps the domain
  tests aligned with the behavioral-only artifact API at the commit boundary.
- Red evidence: the focused suite initially failed during collection because
  `JsonEventParseError` and its structured `line_number` field did not exist.
  Green evidence: the focused suite passed 121 tests, the harness-wide suite
  passed 141 tests, and the repository-wide suite passed 946 tests with zero
  failures.
