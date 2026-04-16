---
name: worktree-data-sync
description: Use when an analysis needs an isolated git worktree — a multi-session analysis spanning days, parallel analyses on different branches, work needing its own data copy or environment setup, a destructive refactor sandbox — OR when syncing non-git data files between existing worktrees (seeding a new worktree, diffing data across worktrees, reconciling changes after parallel work), OR when cleaning up a worktree after a branch ships or is discarded. Triggers include "set up a worktree for this", "isolate this analysis", "I'll run two analyses in parallel", "this will take multiple sessions", "copy data to the new worktree", "seed this worktree from main", "diff the data files between worktrees", "sync my worktree data", "clean up this worktree", or any time you would otherwise hand-roll `git worktree add` / `cp` / `rsync` / `git worktree remove` between two worktrees. Optional for simple single-session analyses — a feature branch without a worktree is sufficient there.
user-invocable: true
---

# Worktree Data Sync Skill

Isolated git worktrees plus non-git data sync plus cleanup. The workspace-isolation, data-copy, and teardown concerns live together because they share the same `git worktree` mechanics and the same "what counts as managed data" question.

## When to Use a Worktree

Worktrees are optional. For simple single-session analyses, a feature branch without a worktree is sufficient — skip this skill.

| Scenario | Recommendation |
|---|---|
| Single-session analysis, no parallel work, no data copy needed | **Optional.** Feature branch is sufficient — skip this skill. |
| Multi-session analysis (expected to span days) | **Recommended.** Resume without affecting other work. |
| Parallel analyses (two branches worked on concurrently) | **Recommended.** Each analysis gets its own isolated checkout. |
| Analysis needs its own data copy or environment setup | **Recommended.** Data seeding lives cleanly inside the worktree. |
| Parallel work involving cloud-synced data directories (e.g., Dropbox) | **Mandatory.** Sandbox + worktree isolation prevents cross-session clobbering. |
| Destructive refactor you want to sandbox from main work | **Recommended.** Experiment without touching the main checkout. |

**Announce at start:** "I'm using the worktree-data-sync skill to set up an isolated workspace."

## When to Use (non-git data sync only)

Activate the data-sync CLI below (no worktree creation / removal) when the request is about:
- comparing non-git files across existing worktrees
- copying managed data from one worktree into another
- reconciling non-git differences after parallel work

Do **not** use the data-sync CLI for:
- branch checkout / merge / switch logic
- sandbox permission setup

## Creating a Worktree

### 1. Directory Selection

Priority order:

```bash
ls -d .worktrees 2>/dev/null     # Preferred (hidden)
ls -d worktrees 2>/dev/null      # Alternative
```

If neither exists, check `CLAUDE.md` for a preference (`grep -i "worktree.*director" CLAUDE.md`). If no preference, ask the user:

```
No worktree directory found. Where should I create worktrees?

1. .worktrees/ (project-local, hidden)
2. ~/.config/superpowers/worktrees/<project-name>/ (global location)
```

### 2. Safety Verification

For project-local directories (`.worktrees` / `worktrees`), verify they are gitignored before creating the worktree:

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

If not ignored: add the appropriate line to `.gitignore`, commit, then proceed. Global-location worktrees (`~/.config/superpowers/worktrees/`) need no gitignore check — they live outside the project.

### 3. Create the Worktree + Set Up Environment

```bash
project=$(basename "$(git rev-parse --show-toplevel)")

case $LOCATION in
  .worktrees|worktrees)
    path="$LOCATION/$BRANCH_NAME" ;;
  ~/.config/superpowers/worktrees/*)
    path="~/.config/superpowers/worktrees/$project/$BRANCH_NAME" ;;
esac

git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"

# Auto-detect environment
[ -f Project.toml ]     && julia --project=. -e 'using Pkg; Pkg.instantiate()'
[ -f pyproject.toml ]   && (uv sync 2>/dev/null || pip install -e .)
[ -f requirements.txt ] && (uv pip install -r requirements.txt 2>/dev/null || pip install -r requirements.txt)
```

### 4. Seed Data

Materialize managed data files in the new worktree using the data-sync CLI below:

```bash
python3 "${SKILL_DIR}/scripts/sync_worktree_data.py" \
    --to "$(pwd)" --mode seed --seed-sync-mode auto
```

This discovers gitignored data, tracked symlinks, and annotated paths from the main worktree and materializes them in the new one (via symlink, copy-on-write, or regular copy depending on the `auto` mode). If seeding fails, report what failed and ask the user whether to proceed without full data or investigate.

### 5. Verify Data Accessibility

Check that key data files are actually readable (not cloud-only placeholders):

```bash
for f in $(git ls-files --others --ignored --exclude-standard | head -10); do
    [ -e "$f" ] && echo "✓ $f accessible" || echo "✗ $f not accessible (cloud-only?)"
done
```

If files are cloud-only, warn the user — they may need to download specific files before the analysis can proceed.

### 6. Report Location

```
Worktree ready at <full-path>
Environment: <Julia/Python version>
Data seeded: <N> files/directories materialized
Ready to analyze <topic>
```

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

## Cleanup

Called when a branch ships (options 1 or 2 in execution-workflow Step 4), is kept as-is (option 3 — do not clean up), or is discarded (option 4), and also as the final step of `merge-workflow` after a successful merge.

```bash
# If the worktree is the current working directory, step out first
cd "$(git rev-parse --show-toplevel)"/..
git worktree remove <worktree-path>
```

**When the worktree was seeded via `--mode seed` from this skill**, `git worktree remove` also removes the materialized data (regular copies, COW clones) and the symlinks. There is no separate "unseed" step — removal of the worktree directory is removal of its data. The source worktree's data is untouched.

**For Option 4 (Discard) in execution-workflow Step 4**, the full teardown is:

```bash
git checkout <base-branch>
git branch -D <analysis-branch>
git worktree remove <worktree-path>   # only if running in a worktree
```

**Only delete after all desired commits have been merged or pushed.** `git worktree remove` refuses to remove a worktree with uncommitted changes unless `--force` is passed; never pass `--force` without checking `git status` in the worktree first.
