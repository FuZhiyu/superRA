---
title: "Replace Worktree-Sync Prose Oracles"
status: approved
depends_on:  []
---

## Objective

Replace worktree-data-sync exception, failure-list, argparse, validation, and informational wording assertions with typed error identities/fields, SeedSummary data, return codes, chosen-mode arguments, and destination filesystem state. Success: behavior is protected without matching rendered prose.

## Planner Guidance

Own only skills/worktree-data-sync/**. Keep structural annotation IDs.

## Results

- Added stable discovery, endpoint-resolution, and sync-validation exception identities with machine-readable `code` values and contextual `fields`; human-readable messages remain presentation only ([worktree_data_discovery.py:12-36](../../../../skills/worktree-data-sync/scripts/worktree_data_discovery.py#L12-L36), [sync_worktree_data.py:23-46](../../../../skills/worktree-data-sync/scripts/sync_worktree_data.py#L23-L46)).
- Replaced exception-message regexes with typed exception/code/field assertions, seed failure rendering checks with `SeedSummary.errors` and `SeedSummary.failures`, argparse and validation wording checks with exit code `2`, and informational-label checks with forwarded `seed_sync_mode` plus destination filesystem state ([test_worktree_data_sync.py:105-172](../../../../skills/worktree-data-sync/scripts/test_worktree_data_sync.py#L105-L172), [test_worktree_data_sync.py:534-777](../../../../skills/worktree-data-sync/scripts/test_worktree_data_sync.py#L534-L777)).
- Preserved the structural `data-sync:symlink` and legacy `worktree:symlink` annotation identifiers and their parsed-root assertions ([test_worktree_data_sync.py:780-792](../../../../skills/worktree-data-sync/scripts/test_worktree_data_sync.py#L780-L792)).
- Verification:
  - Baseline: `44 passed`.
  - Red-green perturbation across typed error, seed summary, return-code, chosen-mode, and destination-state contracts: `5 failed, 39 deselected`; after restoration: `5 passed, 39 deselected`.
  - Fresh full suite: `44 passed`.
  - Owned-scope audit found no exception-message regex, captured-output wording, or informational-label assertions.
