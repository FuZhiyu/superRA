---
name: worktree-data-sync
description: Utility (infrastructure). Sync non-git data files between existing git worktrees — compare, copy, or reconcile large datasets across parallel analysis workspaces without switching branches. Supports seed, diff, and apply modes using explicit --from/--to endpoints. Does not create/remove worktrees or manage sandbox settings (use using-analysis-worktrees for that).
user-invocable: true
---

# Worktree Data Sync Skill

Sync non-git files between existing git worktrees.

## When to Use

Activate this skill when the request is about:
- comparing non-git files across worktrees
- copying managed data from one worktree into another
- reconciling non-git differences after parallel work

Do **not** use this skill for:
- creating/removing worktrees
- branch checkout/merge/switch logic
- sandbox permission setup

## Command Surface

Single CLI entrypoint:

```bash
python3 <skill-dir>/scripts/sync_worktree_data.py --to <worktree-path> --mode <seed|diff|apply> [OPTIONS]
```

Replace `<skill-dir>` with the directory that contains this `SKILL.md`.

### Endpoints

- `--to` is required (destination worktree)
- `--from` is optional (source worktree)
- when `--from` is omitted, source defaults to the main worktree
- both endpoints must be existing worktrees in the same repository

## Modes

### `--mode seed`

Materialize missing managed files in destination from source.

Rules:
- copies only missing files
- never overwrites existing destination files
- applies stateless managed-path discovery

Optional: `--seed-sync-mode <auto|force-symlink|force-cow>` (default: `auto`)

- `auto`: preserve current per-path behavior (symlink-only roots get symlinks, others get copies)
- `force-symlink`: create top-level symlinks for all managed roots when the destination path does not already exist; conflicting paths are skipped
- `force-cow`: copy/COW all managed roots, including symlink-only annotated paths

`--seed-sync-mode` is only valid with `--mode seed`; the CLI rejects it for other modes.

### `--mode diff`

Report source-to-destination differences for managed files.

Statuses:
- `new`: exists in source but missing in destination
- `modified`: exists in both but differs
- `unchanged`: identical (only shown with `--include-unmodified`)

Output options:
- human-readable report (default)
- JSON report (`--json`), compatible with apply mode

### `--mode apply`

Execute sync actions for selected changes.

Actions:
- `--action overwrite`: copy source file to destination path
- `--action rename`: copy source file to destination with suffix

Selection options:
- `--from-json <file>` from prior diff output
- `--files <path...>` for explicit relative paths
- omit both to auto-process current diff (`new` + `modified`)

No delete/discard action is provided.

## Managed Path Discovery

Discovery is stateless and source-driven. Managed roots come from:
- gitignored paths via `git ls-files --others --ignored --exclude-standard --directory`
- tracked symlinks that resolve outside the repo
- top-level symlink safety net
- `.gitignore` symlink-only annotations

Annotate a path as symlink-only by adding a **duplicate line** with the tag comment:

```gitignore
Data/
Data/  # data-sync:symlink
```

The first line is the actual gitignore rule; the second is the annotation the discovery script parses.
Legacy tag `# worktree:symlink` is also supported.

Symlink-only roots are symlinked in seed auto mode and excluded from diff/apply actions.

## Examples

```bash
# Seed from main worktree into destination
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --to ../MyRepo-feature \
  --mode seed

# Seed using top-level symlinks for all managed roots
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --to ../MyRepo-feature \
  --mode seed \
  --seed-sync-mode force-symlink

# Seed using copy/COW for all managed roots (including symlink-only)
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --to ../MyRepo-feature \
  --mode seed \
  --seed-sync-mode force-cow

# Diff explicit source -> destination
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --from ../MyRepo-expA \
  --to ../MyRepo-expB \
  --mode diff --json

# Apply overwrite using diff json
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --to ../MyRepo-expB \
  --mode apply \
  --from-json /tmp/changes.json \
  --action overwrite

# Apply rename for explicit files
python3 <skill-dir>/scripts/sync_worktree_data.py \
  --from ../MyRepo-expA \
  --to ../MyRepo-expB \
  --mode apply \
  --files output/result.csv notes/draft.md \
  --action rename \
  --suffix _from_expA
```
