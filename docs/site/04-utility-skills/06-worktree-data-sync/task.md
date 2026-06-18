---
title: "worktree-data-sync"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

You branch off two worktrees to run a regression spec two ways in parallel — `../MyRepo-expA` and `../MyRepo-expB` — and both need the same multi-gigabyte panel under `Data/`. But `Data/` is gitignored, so each fresh worktree starts empty: the scripts run, find no input, and die — or worse, silently regenerate a partial dataset and produce results that don't line up with the other branch's. Git moves your code between worktrees; it does nothing for the data your code reads. A bare agent dropped into the empty worktree hits exactly this, and after the parallel runs the data each branch wrote is stranded in its own directory with no record of which files diverged.

This skill is the data half of that split. It seeds a new worktree with the inputs it needs, diffs the data files between two worktrees, applies the changes you choose to keep after the parallel runs, and leaves worktree teardown to `git worktree remove`. It discovers what counts as "data" on its own — gitignored paths, tracked symlinks that resolve outside the repo, and `.gitignore` lines you tag `# data-sync:symlink` — so you never enumerate files by hand.

Everything runs through one CLI (`<skill-dir>` is the directory holding `SKILL.md`; `--from` defaults to your main worktree):

```bash
python3 <skill-dir>/scripts/sync_worktree_data.py --to <worktree-path> --mode <seed|diff|apply> [OPTIONS]
```

**seed** populates a worktree before an agent runs there. It copies only files missing in the destination and never overwrites what is already present, so re-running it is safe. By default it symlinks the roots you annotated symlink-only and copies the rest; `--seed-sync-mode force-symlink` symlinks every managed root (skipping any path that already exists), and `--seed-sync-mode force-cow` copies or COW-clones everything, including the symlink-only roots. That flag is rejected outside seed mode.

**diff** reports, source against destination, which managed files are `new` (in source, missing in destination), `modified` (in both, differing), or `unchanged` (shown only with `--include-unmodified`). Run it after the parallel work to see what each branch changed before you reconcile anything. `--json` writes a report that feeds straight into apply.

**apply** executes only the changes you select. `--from-json` replays a saved diff; `--files` names explicit relative paths; omit both and it processes the current diff (`new` plus `modified`). `--action overwrite` replaces the destination file; `--action rename` copies it in beside the existing one under `--suffix`, so neither expA's nor expB's version is lost when both runs wrote results. There is no delete or discard action — apply only ever adds or replaces files you asked for.

There is no separate "unseed" step. The copies, COW clones, and symlinks that seed created inside a worktree all disappear when you delete the worktree directory, and no mode ever modifies the source worktree's data.

Usage recipes:

```bash
# Seed a new parallel worktree from main before dispatching an agent into it
python3 <skill-dir>/scripts/sync_worktree_data.py --to ../MyRepo-expA --mode seed

# After the parallel runs, see what expA changed relative to expB, and save it
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --from ../MyRepo-expA --to ../MyRepo-expB --mode diff --json > /tmp/changes.json

# Bring those changes into expB, overwriting in place
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --to ../MyRepo-expB --mode apply --from-json /tmp/changes.json --action overwrite

# Pull two specific files across without clobbering expB's versions
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --from ../MyRepo-expA --to ../MyRepo-expB --mode apply \
  --files output/result.csv notes/draft.md --action rename --suffix _from_expA
```

To share a path by reference rather than copy — a large read-only dataset every worktree reads but none rewrites — add a duplicate `.gitignore` line tagged `# data-sync:symlink`; seed then links it instead of copying, and diff/apply leave it alone. In a superRA parallel dispatch the orchestrator runs seed automatically right after creating each worktree, so you usually invoke this skill by hand only for the post-run diff/apply reconciliation, or when seeding a worktree you created outside the workflow.

The full flag list, the managed-path discovery rules, and the symlink-only annotation format are the authoritative spec in [`worktree-data-sync`](skills/worktree-data-sync/SKILL.md).
