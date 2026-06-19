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

### Sync modes: shared symlink vs. owned copy

There are two modes of data sync, and the mode decides what happens when your code writes to a path. When you seed a worktree ("seed this worktree from main"), each path arrives either as a **symlink** that shares the source's file or as a **copy** the worktree owns.

A **symlink** is a pointer: the file in the worktree is a shortcut to the real file still sitting in the source worktree. It takes no extra disk space, but both worktrees resolve to the same bytes, so a write from one is a write to the other. Symlinks suit data a worktree only ever reads — a shared raw-`Data/` directory, a download cache — where you want every worktree pointing at one copy and nobody modifying it.

A **copy** is an independent duplicate, and it is what keeps parallel worktrees isolated: each worktree gets its own bytes, so it can overwrite them freely and a run in one worktree can never corrupt another worktree's data or the source. Copies suit anything the worktree will write — its `output/`, its intermediate files, its results. The cost is disk space: a copy of a 10 GB dataset is another 10 GB.

A **copy-on-write (COW) clone** is a copy that costs nothing until you change it. The filesystem hands you what behaves like a full duplicate instantly, and only stores the bytes that actually differ once you start writing — so you keep a copy's safety (writes stay local to the worktree) at close to a symlink's price (near-zero disk until modified). COW is available only on macOS's APFS filesystem.

By default data-sync chooses per path: anything you have flagged read-only (the `.gitignore` mechanism shown next) becomes a shared symlink, and everything else is copied — so a read-only `Data/` stays shared while an `output/` directory gets its own isolated copy. You can override that when you ask the agent to seed. Tell it **"seed with symlinks"** to share every path (lightest on disk, but the worktrees then share one set of files and a stray write reaches back into the source), or **"seed everything with COW clones"** to give every path its own isolated copy at almost no disk cost (macOS only).

### Marking read-only paths in `.gitignore`

You mark a path read-only in `.gitignore`. Data-sync already treats every gitignored path as data to seed; to flag one as symlink-only, add a **second copy of its ignore line** carrying a `# data-sync:symlink` tag:

```gitignore
# the normal ignore rule — git ignores Data/ as usual:
Data/
# a duplicate line, tagged — git treats it as a harmless no-op pattern,
# but data-sync reads the tag and symlinks Data/ instead of copying it:
Data/  # data-sync:symlink
```

The first line is your ordinary gitignore entry and does the actual ignoring. The second is the one data-sync parses (git itself only reads `#` as a comment at the *start* of a line, so it treats this duplicate as a pattern that matches nothing). A path tagged this way is symlinked when seeded and held out of diff and apply entirely, since a shared, read-only input is not something you reconcile.

### Syncing changes back

Syncing back is the diff-then-apply path. After the parallel runs you diff one worktree's data against another's, which lists each managed file as `new` (only in the source) or `modified` (in both but different), then apply only the changes you pick. Each applied change either overwrites the destination file or copies the source in beside it under a suffix you choose (`--suffix _from_expA`), so neither branch's version is lost. There is no delete action, so applying back never removes a file the destination already had.

### Discovery and teardown

The tool discovers what counts as "data" on its own — gitignored paths and symlinks that resolve outside the repo — so nobody enumerates files by hand. There is no unseed step: copies, clones, and symlinks vanish when you delete the worktree, and no mode touches the source worktree's data.

## Running it by hand

The agent drives one CLI; you can run the same commands. `<skill-dir>` holds `SKILL.md`, and `--from` defaults to your main worktree:

```bash
python3 <skill-dir>/scripts/sync_worktree_data.py --to <worktree-path> --mode <seed|diff|apply> [OPTIONS]
```

- **seed** copies only files missing in the destination, so re-running it is safe. Add `--seed-sync-mode force-symlink` or `force-cow` to override the default per-path placement (described above) for the whole run.
- **diff** reports which managed files are `new`, `modified`, or `unchanged`; `--json` writes a report that feeds straight into apply.
- **apply** executes only the changes you select. `--action overwrite` replaces the destination file; `--action rename` copies it in beside the existing one under `--suffix`, so neither branch's version is lost. There is no delete action.

```bash
# Seed a new parallel worktree from main before dispatching an agent into it
python3 <skill-dir>/scripts/sync_worktree_data.py --to ../MyRepo-expA --mode seed

# Same, but force COW clones for everything — independent copies at near-zero disk cost (macOS/APFS)
python3 <skill-dir>/scripts/sync_worktree_data.py --to ../MyRepo-expA --mode seed --seed-sync-mode force-cow

# After the parallel runs, save what expA changed relative to expB
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --from ../MyRepo-expA --to ../MyRepo-expB --mode diff --json > /tmp/changes.json

# Pull two specific files across without clobbering expB's versions
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --from ../MyRepo-expA --to ../MyRepo-expB --mode apply \
  --files output/result.csv notes/draft.md --action rename --suffix _from_expA
```

The full flag list, the managed-path discovery rules, and the symlink-only annotation format are the authoritative spec in [`worktree-data-sync`](skills/worktree-data-sync/SKILL.md).
