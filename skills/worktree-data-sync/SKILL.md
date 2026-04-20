---
name: worktree-data-sync
description: Use when syncing non-git-controlled data files between existing worktrees — seeding a new worktree from main, diffing data across worktrees, reconciling changes after parallel work, or data teardown. Triggers include "copy data to the new worktree", "seed this worktree from main", "diff the data files between worktrees", "sync my worktree data". Worktree lifecycle (create / enter / remove) is out of scope — see `skills/agent-orchestration/references/worktree-harness-fallback.md`. Caller is responsible for worktree existence before invoking the CLI.
user-invocable: true
---

# Worktree Data Sync Skill

Non-git data sync between existing worktrees — seed, diff, apply, and data teardown. Worktree lifecycle (create / enter / remove) is an orchestration concern and lives in `skills/agent-orchestration/references/worktree-harness-fallback.md`.

## When to Use

Activate the data-sync CLI below when the request is about:
- seeding non-git-controlled data from one existing worktree into another
- comparing non-git files across existing worktrees
- copying managed data from one worktree to another
- reconciling non-git differences after parallel work

Do **not** use this skill for:
- creating, entering, or removing worktrees (see `agent-orchestration/references/worktree-harness-fallback.md`)
- branch checkout / merge / switch logic
- sandbox permission setup

**Announce at start:** "I'm using the worktree-data-sync skill to sync non-git data."

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

## Data Teardown

Materialized data inside a worktree (regular copies, COW clones, and symlinks created by `--mode seed`) is removed implicitly when the worktree directory is deleted — there is no separate "unseed" step. The source worktree's data is untouched.

For worktree removal itself (`git worktree remove`, branch deletion, and safety checks), see `skills/agent-orchestration/references/worktree-harness-fallback.md` §Remove.

## See Also

- `skills/agent-orchestration/references/worktree-harness-fallback.md` — worktree lifecycle (create / enter / remove), harness tools preferred, raw-git fallback, placement conventions.
- `skills/agent-orchestration/SKILL.md` §Parallelization and Worktree Isolation — when parallel subagents each need their own worktree, and how data seeding fits into that flow.
