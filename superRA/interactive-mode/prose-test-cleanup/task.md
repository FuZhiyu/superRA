---
title: "Prune Prose-Specific Tests Conservatively"
status: approved
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

For the accepted range `6be18283..64440306`, the exact path scope `tests`,
`:(glob)skills/**/test*.py`, and `:(glob)skills/**/tests/**` adds 349 lines and
deletes 2,386 across 43 files. The accounting comes from `git diff --numstat`
over that range and pathspec. It introduced no production changes, new helper
APIs, live agents, or network/filesystem setup.

Verification:

- Rule-canary focused suite: `103 passed`.
- Diagnostic/presentation focused Python suite: `801 passed`.
- Codex hook and Zotero shell suites after the accepted revision: `15/15` and
  `18/18`.
- Final full Python suite after the accepted revision: `899 passed`, `0 failed`,
  with four expected warnings.

The integration re-audit confirmed that every non-task-record path in the
accepted cleanup range is a test, fixture, or test-documentation file; the range
adds no production API, helper framework, live agent/model call, or network
path. Across the full branch, the test surface remains net-negative at 663
additions and 2,551 deletions across 52 files, including the structured
interactive-order and main-seat routing coverage that predates the bounded
cleanup. Fresh verification reproduced `899 passed` with four expected warnings,
Codex hooks `15/15`, Zotero `18/18`, and harness compatibility exit `0`.

**Final diff self-check:** `git diff origin/main...HEAD`; surviving classes
within this task are deletion of authored-prose, diagnostic-copy, help/UI-label,
and layout oracles; local replacements using existing state/schema/path/exit/
ordering/mutation/secret observables; fixture and test-documentation
reconciliation; and retained structured interactive/seat behavior tests.
Suspicious broad deletion hunks are justified by this task's explicit
net-negative cleanup objective and the retained behavior inventory above; no
cleanup hunk changes production code or creates execution infrastructure.
