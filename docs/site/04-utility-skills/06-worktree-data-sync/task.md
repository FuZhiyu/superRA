---
title: "worktree-data-sync"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

When you run work in parallel across worktrees, git moves your code but ignores the data your code reads. A fresh worktree's gitignored `Data/` starts empty, so an agent dropped into it finds no input and either fails or silently regenerates a partial dataset that disagrees with the other branch. This skill handles the data side: it seeds a worktree with the inputs it needs, diffs the data files between two worktrees after parallel runs, and applies the changes you choose to keep.

Ask the agent in plain language: "seed this worktree from main before you run anything," or "diff the data between expA and expB, then bring expA's results into expB without clobbering expB's versions." In a superRA parallel run the orchestrator seeds each worktree on creation, so you only ask for the reconciliation afterward.

The agent discovers what counts as "data" on its own — gitignored paths and symlinks that resolve outside the repo — so nobody enumerates files by hand. There is no unseed step: copies and symlinks vanish when you delete the worktree, and no mode touches the source worktree's data.

## Running it by hand

The agent drives one CLI; you can run the same commands. `<skill-dir>` holds `SKILL.md`, and `--from` defaults to your main worktree:

```bash
python3 <skill-dir>/scripts/sync_worktree_data.py --to <worktree-path> --mode <seed|diff|apply> [OPTIONS]
```

- **seed** copies only files missing in the destination, so re-running it is safe.
- **diff** reports which managed files are `new`, `modified`, or `unchanged`; `--json` writes a report that feeds straight into apply.
- **apply** executes only the changes you select. `--action overwrite` replaces the destination file; `--action rename` copies it in beside the existing one under `--suffix`, so neither branch's version is lost. There is no delete action.

```bash
# Seed a new parallel worktree from main before dispatching an agent into it
python3 <skill-dir>/scripts/sync_worktree_data.py --to ../MyRepo-expA --mode seed

# After the parallel runs, save what expA changed relative to expB
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --from ../MyRepo-expA --to ../MyRepo-expB --mode diff --json > /tmp/changes.json

# Pull two specific files across without clobbering expB's versions
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --from ../MyRepo-expA --to ../MyRepo-expB --mode apply \
  --files output/result.csv notes/draft.md --action rename --suffix _from_expA
```

The full flag list, the managed-path discovery rules, and the symlink-only annotation format are the authoritative spec in [`worktree-data-sync`](skills/worktree-data-sync/SKILL.md).
