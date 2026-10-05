---
title: "worktree-data-sync"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Git moves your code between worktrees but not your gitignored data. This skill seeds a new worktree with the data it needs, compares data between two worktrees after parallel runs, and copies back only the changes you pick. Without it, an agent in a fresh worktree finds an empty `Data/` and either fails or regenerates a partial dataset.

## Ask in plain language

- "Seed this worktree from main before you run anything."
- "Diff the data between expA and expB, then bring expA's results into expB without clobbering expB's versions."

In a superRA parallel run the orchestrator seeds each worktree when it creates it, so you only ask for the reconciliation afterward.

## Seeding shares read-only data and copies the rest

Each seeded path arrives as a symlink or a copy:

| Arrives as | Behavior | Suits |
|---|---|---|
| Symlink | Points at the source worktree's file; a write in either worktree changes both | Read-only inputs: raw `Data/`, download caches |
| Copy | The worktree's own file; writes stay local | Anything the worktree writes: `output/`, intermediate files |

- **Copies are cheap on macOS.** They are copy-on-write clones on APFS, using near-zero disk until a file changes; elsewhere they are full copies.
- **Paths you mark read-only are symlinked; everything else is copied.** Override for one seed:
  - "seed with symlinks" shares every path. It is the lightest, but a stray write reaches back into the source.
  - "seed everything with COW clones" copies every path, read-only ones included.
- **Re-seeding is safe.** Seed only adds files the destination is missing.
- **Nothing is downloaded.** An online-only cloud file (a Dropbox or iCloud placeholder) is symlinked to the source instead of copied.

## Mark read-only paths in `.gitignore`

Every gitignored path counts as data to seed. To mark one read-only, add a duplicate of its ignore line with a `# data-sync:symlink` tag:

```gitignore
Data/
Data/  # data-sync:symlink
```

Git ignores `Data/` through the first line and treats the tagged duplicate as a no-op. A tagged path is symlinked on seed and left out of diff and apply.

## Syncing back never deletes

After parallel runs, a diff lists each data file as `new` (only in the source) or `modified` (different in both). You pick which changes to apply, and each one either:

- **overwrites** the destination file, or
- **lands beside it** under a suffix such as `_from_expA`, keeping both versions.

There is no delete action, and nothing to tear down: seeded data disappears with the worktree, and the source's data is never touched.

## Run it by hand

The agent drives one CLI, which you can run yourself. `<skill-dir>` holds `SKILL.md`; `--from` defaults to the worktree you run it from.

```bash
# From the main worktree, seed a new worktree before dispatching an agent into it
python3 <skill-dir>/scripts/sync_worktree_data.py --to ../MyRepo-expA --mode seed

# Save what expA changed relative to expB
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --from ../MyRepo-expA --to ../MyRepo-expB --mode diff --json > /tmp/changes.json

# Bring two files across without clobbering expB's versions
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --from ../MyRepo-expA --to ../MyRepo-expB --mode apply \
  --files output/result.csv notes/draft.md --action rename --suffix _from_expA
```

Flags (`--seed-sync-mode force-symlink|force-cow`, `--from-json`), discovery rules, and the paths never treated as data (`.venv`, `node_modules`, caches) are in [`worktree-data-sync`](skills/worktree-data-sync/SKILL.md).
