---
title: "Delete Low-Value Wording Assertions"
status: approved
depends_on:  []
---

## Objective

Delete exact diagnostic, warning, UI-label, heading-count, and remediation-copy assertions across the audited test surfaces. Keep an existing behavioral assertion when it already exposes a cheap important outcome such as exit status, unchanged files, JSON shape, event order, or secret absence. Do not modify production code or add helper APIs. Success: the test diff is net-negative, no new execution cost is introduced, and the remaining assertions protect stable behavior rather than wording.

## Details

Use the completed audit as navigation across harness contract/diagnostics, task-tree CLI/dashboard/comments, worktree-data-sync, hook adapter, Zotero CLI, and report-in-markdown. Replacements are allowed only when they reuse an existing result/state in a few local assertions; otherwise delete. Preserve the branch-specific interactive transcript/seat behavioral checks already present before this task.

## Results

Deleted copy-sensitive diagnostics and presentation assertions across all
audited test surfaces without changing production code:

- Harness checks now retain success/failure, event ordering, interactive
  canvas/seat routing, task reads, and artifact mismatch behavior without
  pinning observation or missing-item prose
  ([test_transcript_assertions.py](../../../../tests/harness-instruction-following/test_transcript_assertions.py),
  [test_contract.py](../../../../tests/harness-instruction-following/test_contract.py)).
- Task-tree tests retain exit codes, dependency and file state, parse-error
  state, JSON shapes, paths, and IDs while dropping warning, help, human-output,
  label, heading-count, and workflow-copy oracles
  ([test_task_tree.py](../../../../skills/task-tree/scripts/test_task_tree.py),
  [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py),
  [test_comments.py](../../../../skills/task-tree/scripts/tests/test_comments.py)).
- Worktree sync, hook, and Zotero tests retain raise/exit behavior, endpoint and
  filesystem state, hook JSON branches, secret absence, and byte-preserving
  citation guards without matching diagnostic text
  ([test_worktree_data_sync.py](../../../../skills/worktree-data-sync/scripts/test_worktree_data_sync.py),
  [test-codex-hooks.sh](../../../../tests/hooks/test-codex-hooks.sh),
  [test-zotero-tool.sh](../../../../tests/test-zotero-tool.sh)).
- Residual Markdown and generated-agent tests retain rule/line identity and
  verify an unmanaged file remains unchanged instead of matching remediation
  copy
  ([test_md_integrity.py](../../../../skills/communicate/scripts/test_md_integrity.py),
  and `test_sync_codex_agents.py`, since retired with its generator).

The test-only diff is 122 insertions and 1,002 deletions across 16 existing
files. It adds no files, helpers, subprocesses, live calls, or production
surface.

Verification:

- Focused Python suite: `801 passed` in `75.57s`.
- Codex hook shell suite: `11 passed`, `0 failed`.
- Zotero shell suite: `18 passed`, `0 failed`.
- Full Python suite: `896 passed`, `0 failed`, with four expected warnings in
  `78.90s`.
- Python compilation, shell syntax, and `git diff --check` passed.

Revision:

- Restored the four Codex Stop-parser routing branches using only structured
  `decision` or empty-JSON outcomes, plus the missing-dashboard dependency
  branch's exit code
  ([test-codex-hooks.sh:282](../../../../tests/hooks/test-codex-hooks.sh#L282),
  [test_cli.py:500](../../../../skills/task-tree/scripts/test_cli.py#L500)).
- Restored superplan routed-reference existence and generated dashboard
  workflow schema, permission, branch-trigger, configured-path, and
  cleanup-before-upload ordering coverage without checking labels or diagnostic
  prose
  ([test_contract.py:259](../../../../tests/harness-instruction-following/test_contract.py#L259),
  [test_dashboard.py:4058](../../../../skills/task-tree/scripts/test_dashboard.py#L4058)).
- Revision verification: `15 passed` focused Python tests; `15/15` Codex hook
  cases; `18/18` Zotero cases; full suite `899 passed`, `0 failed`, with four
  expected warnings in `84.58s`.
