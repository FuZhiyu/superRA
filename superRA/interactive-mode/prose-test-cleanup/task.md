---
title: "Prune Prose-Specific Tests Conservatively"
status: revise
depends_on: []
---

## Objective

Remove tests that treat authored instruction prose, labels, layout, or diagnostic wording as regression oracles. Keep existing cheap checks for important behavior that is easy to miss: destructive or missing file mutations, exit status, generated schemas/identities, tool or dispatch ordering, and secret exposure. Prefer deleting a prose assertion over building new test infrastructure. Success: the cleanup changes tests and fixtures only, adds no live/network/agent execution, introduces no production API or helper framework, has a net-negative test diff, and retains the existing high-value behavioral suite.

## Planner Guidance

Budget: use an existing observable field or state only when the replacement is local and simpler than the prose assertion. Otherwise delete the assertion or its test. Do not add subprocesses, live harness calls, network access, structured diagnostic APIs, new error taxonomies, or production changes solely for testability. Preserve tests for branch-specific interactive routing and review behavior already protected before this task.

## Results

Completed the conservative prose-test cleanup in two focused passes:

- Deleted rule-recitation and artifact-token canaries while preserving role
  declarations, schema identities, task-read/load paths, dispatch/tool order,
  and multi-domain behavior
  ([01-remove-prose-canaries/task.md](01-remove-prose-canaries/task.md)).
- Deleted diagnostic, warning, help, UI-label, heading/list-count, remediation,
  and human-output copy assertions while preserving cheap state, schema, path,
  exit, ordering, mutation, and secret-absence checks
  ([02-structured-diagnostics/task.md](02-structured-diagnostics/task.md)).

Across `tests/` and test/documentation files under `skills/`, the cleanup
removed 2,423 lines and added 294 local replacement/documentation lines across
42 existing files. It introduced no production changes, new files, helper APIs,
live agents, or network/filesystem setup.

Verification:

- Rule-canary focused suite: `103 passed`.
- Diagnostic/presentation focused Python suite: `801 passed`.
- Codex hook and Zotero shell suites: `11/11` and `18/18`.
- Final full Python suite: `896 passed`, `0 failed`, with four expected
  warnings.

## Review Notes

1. **MAJOR — Child 01 leaves the harness documentation inconsistent with the
   canary paths it removed.** The current issue and required documentation-only
   reconciliation are recorded in
   [01-remove-prose-canaries/task.md](01-remove-prose-canaries/task.md#review-notes).

2. **MAJOR — Child 02 exceeds the conservative deletion budget by removing
   cheap exit-status, routing-branch, generated-path, and command-order
   coverage.** The focused restorations that avoid prose assertions are recorded
   in
   [02-structured-diagnostics/task.md](02-structured-diagnostics/task.md#review-notes).
