---
title: "Delete Low-Value Wording Assertions"
status: revise
depends_on:  []
---

## Objective

Delete exact diagnostic, warning, UI-label, heading-count, and remediation-copy assertions across the audited test surfaces. Keep an existing behavioral assertion when it already exposes a cheap important outcome such as exit status, unchanged files, JSON shape, event order, or secret absence. Do not modify production code or add helper APIs. Success: the test diff is net-negative, no new execution cost is introduced, and the remaining assertions protect stable behavior rather than wording.

## Planner Guidance

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
  ([test_md_integrity.py](../../../../skills/report-in-markdown/scripts/test_md_integrity.py),
  [test_sync_codex_agents.py](../../../../skills/codex-superra-setup/scripts/test_sync_codex_agents.py)).

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

## Review Notes

1. **MAJOR — Cheap branch and exit-status coverage was deleted together with
   diagnostic prose.** The Codex Stop-hook suite now covers only a heading-style
   plan, an already-active hook, and an ordinary non-plan turn
   ([test-codex-hooks.sh:268-306](../../../../tests/hooks/test-codex-hooks.sh#L268-L306)),
   after deleting the pre-existing cases for a `<proposed_plan>` tag, quoted
   tags outside plan mode, non-plan output in plan mode, and a negated
   proposed-plan phrase. Those cases exercise distinct routing branches in the
   marker parser
   ([codex-plan-stop:50-59](../../../../hooks/codex-plan-stop#L50-L59)) and can
   be retained using only the existing structured `decision` or empty-JSON
   result. The commit also deleted the missing-dashboard-dependency test instead
   of retaining its existing `SystemExit.code == 1` assertion for the
   `ImportError` branch
   ([cli.py:167-183](../../../../skills/task-tree/scripts/cli.py#L167-L183)).
   Restore these cheap behavioral cases without checking reminder/error wording.

2. **MAJOR — Stable path and ordering checks were removed as if they were prose
   assertions.** The cleanup deleted the superplan routed-reference existence
   check even though the referenced paths remain executable routing contracts
   ([SKILL.md:64-70](../../../../skills/superplan/SKILL.md#L64-L70),
   [SKILL.md:107-111](../../../../skills/superplan/SKILL.md#L107-L111)). It also
   deleted the generated dashboard-workflow contract that checked permissions,
   configured paths, cleanup-before-upload order, and branch/trigger ordering;
   the surviving tests cover installation and a few substitutions but not those
   invariants
   ([test_dashboard.py:3423-3511](../../../../skills/task-tree/scripts/test_dashboard.py#L3423-L3511)).
   Restore only the cheap reference-path and generated-workflow
   schema/command-order checks, omitting headings, labels, and remediation copy.
