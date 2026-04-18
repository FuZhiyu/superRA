# Worktree Lifecycle — Harness Tools and Raw-Git Fallback

Loaded by the orchestrator when it needs to **create**, **enter**, or **remove** a git worktree and no dedicated harness tool is available. Worktree lifecycle is an orchestration concern — see `SKILL.md` §Concurrent Writers Require Worktree Isolation for when parallel implementers require their own worktrees, and `skills/worktree-data-sync/SKILL.md` for seeding non-git data into an existing worktree (out of scope here).

## Prefer Harness Tools

If the harness exposes worktree-management tools (e.g., `EnterWorktree`, `ExitWorktree`, `CreateWorktree`, IDE-integrated worktree panels), use them. They handle cwd tracking, environment activation, and teardown more cleanly than raw git. Check the available tool list before falling through to the raw-git path.

## Raw-Git Fallback

### Create

```bash
git worktree add <path> -b <branch-name> <base-ref>
```

- `<path>` — absolute or repo-relative. Placement convention below.
- `<branch-name>` — new branch to create at `<base-ref>`. For orchestrator-managed parallel slots, use `parallel/<analysis-branch>/<slug>`.
- `<base-ref>` — typically the current analysis branch (`HEAD` is fine when already on it).

After creation, the orchestrator seeds non-git data via `skills/worktree-data-sync` §`--mode seed` if the task needs data access.

### Enter

```bash
cd <path>
git rev-parse --show-toplevel   # verify we landed where we expected
```

Agents dispatched with a `Worktree:` field are instructed to do this themselves (see `agents/implementer.md` §Before You Start).

### Remove

```bash
cd "$(git rev-parse --show-toplevel)"/..   # step out if currently inside
git worktree remove <path>
git branch -D <branch-name>                # only after merge or explicit discard
```

`git worktree remove` refuses to remove a worktree with uncommitted changes unless `--force` is passed. **Never pass `--force` without first confirming `git status` inside the worktree.** Seeded data inside the worktree directory (including symlinks created by `worktree-data-sync --mode seed`) is removed implicitly when the directory is deleted; the source worktree's data is untouched.

## Placement

Priority order when choosing where to put the worktree:

1. **Project-level override.** Grep the repo-root `CLAUDE.md` / `AGENTS.md` for a `worktree` directive (`grep -i "worktree.*director" CLAUDE.md`). If a path is specified, use it.
2. **Existing convention.** If `./.worktrees/` or `./worktrees/` already exists at the repo root, reuse it.
3. **Default.** `./.worktrees/<branch-name>` at the repo root.

Before first use of a project-local directory (`.worktrees/`, `worktrees/`), verify it is gitignored:

```bash
git check-ignore -q .worktrees 2>/dev/null || echo "NOT IGNORED — add to .gitignore first"
```

Global-location worktrees (e.g., `~/.config/superpowers/worktrees/<project>/`) need no gitignore entry — they live outside the project.

## Gotchas

- **Clean state before remove.** Always `git status` inside the worktree before removing. An unclean state means uncommitted work is about to be discarded.
- **Branch deletion lag.** `git branch -D <branch>` only after the branch has been merged into its intended target, or the orchestrator has explicitly decided to discard. A parallel-slot branch that hasn't been harvested yet must not be deleted.
- **Detached HEAD on add.** If `<base-ref>` is a SHA rather than a branch name and `-b` is omitted, the worktree lands in detached HEAD. Always pass `-b <new-branch>`.
- **Cloud-synced directories.** If the repo is inside a cloud-synced folder (Dropbox, iCloud), worktrees in sibling directories can conflict across machines. Prefer global-location worktrees for cloud-synced projects.

## Example Orchestrator Invocation

This example shows the complete lifecycle for a single parallel slot: create a dedicated worktree, seed shared data, dispatch a subagent, merge the result, and clean up.

```bash
#!/bin/bash
set -e

ANALYSIS_BRANCH="feedback/agent-dispatch-fixes"
SLOT_SLUG="beta"
PARALLEL_BRANCH="parallel/${ANALYSIS_BRANCH}/${SLOT_SLUG}"
WORKTREE_PATH=".worktrees/parallel/${ANALYSIS_BRANCH}/${SLOT_SLUG}"

# 1. Create worktree
git worktree add "${WORKTREE_PATH}" -b "${PARALLEL_BRANCH}" "${ANALYSIS_BRANCH}"

# 2. Seed non-git data (symlink mode for shared read-only inputs)
python3 skills/worktree-data-sync/scripts/sync_worktree_data.py \
  --to "${WORKTREE_PATH}" \
  --mode seed \
  --seed-sync-mode force-symlink

# 3. Dispatch subagent with Worktree field set to absolute path
# (placeholder: dispatch orchestrator sends this worktree path to implementer)

# 4. Merge result (run from main worktree after subagent completes)
cd "$(git rev-parse --show-toplevel)"
git merge --no-ff "${PARALLEL_BRANCH}"

# 5. Clean up
git worktree remove "${WORKTREE_PATH}"
git branch -D "${PARALLEL_BRANCH}"
```

For harness-provided worktree tools, use them in place of the raw-git commands above: `EnterWorktree` to enter the path in Step 2, `ExitWorktree` for cleanup.

