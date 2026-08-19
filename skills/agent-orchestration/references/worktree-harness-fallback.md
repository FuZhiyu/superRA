# Worktree Lifecycle — Harness Tools and Raw-Git Fallback

Loaded by the orchestrator to **create**, **enter**, or **remove** a git worktree when no dedicated harness tool is available. When parallel subagents need their own worktrees: `references/parallel-dispatch.md`. Seeding non-git data into an existing worktree: `skills/worktree-data-sync/SKILL.md`.

## Prefer Harness Tools

Use a harness worktree tool only when the orchestrator can choose the worktree path from §Placement. Hidden harness scratch locations are not superRA worktrees. No path-controlled tool: use raw git.

## Raw-Git Fallback

### Create

```bash
git worktree add <path> -b <branch-name> <base-ref>
```

- `<path>` — absolute or repo-relative, per §Placement.
- `<branch-name>` — new branch at `<base-ref>`. Orchestrator-managed parallel slots: `<current-branch>-agent/parallel/<slug>`.
- `<base-ref>` — typically the current branch (`HEAD` when already on it).

Then seed non-git data via `skills/worktree-data-sync` §`--mode seed` if the task needs data access.

### Enter

```bash
cd <path>
git rev-parse --show-toplevel   # verify we landed where we expected
```

Agents dispatched with a `Worktree:` field do this themselves via the dispatch's `Additionally:` steering.

### Remove

```bash
cd "$(git rev-parse --show-toplevel)"/..   # step out if currently inside
git worktree remove <path>
git branch -D <branch-name>                # only after merge or explicit discard
```

`git worktree remove` refuses a worktree with uncommitted changes unless `--force`. **Never pass `--force` without first confirming `git status` inside the worktree.** Seeded data inside the directory (including `worktree-data-sync --mode seed` symlinks) goes with it; the source worktree's data is untouched.

## Placement

Priority order:

1. **Project-level override.** Grep the repo-root `CLAUDE.md` / `AGENTS.md` for a `worktree` directive (`grep -i "worktree.*director" CLAUDE.md`); use any path it specifies.
2. **Default for ephemeral parallel worktrees:** `${TMPDIR:-/tmp}/superRA-worktrees/<repo-name>/<branch-name>`.
3. **Existing project convention** (`./.worktrees/`, `./worktrees/`) — only when the project-level directive names it.

Before first use of a project-local directory, verify it is gitignored:

```bash
git check-ignore -q .worktrees 2>/dev/null || echo "NOT IGNORED — add to .gitignore first"
```

Global-location worktrees (e.g. `~/.config/superpowers/worktrees/<project>/`) live outside the project and need no gitignore entry.

**Cloud-synced repos** (Dropbox, iCloud): prefer global-location worktrees — sibling-directory worktrees conflict across machines.

## Gotchas

- **Clean state before remove.** `git status` inside the worktree first; unclean means uncommitted work is about to be discarded.
- **Branch deletion lag.** `git branch -D <branch>` only after the branch merged into its target, or on an explicit discard decision. Never delete an unharvested parallel-slot branch.
- **Detached HEAD on add.** A SHA `<base-ref>` without `-b` lands the worktree in detached HEAD. Always pass `-b <new-branch>`.

## Example Orchestrator Invocation

One parallel slot's full lifecycle (create → seed → dispatch → merge → cleanup):

```bash
WT="${TMPDIR:-/tmp}/superRA-worktrees/$(basename "$(git rev-parse --show-toplevel)")/${BR}-agent/parallel/$SLUG"
mkdir -p "$(dirname "$WT")"
git worktree add "$WT" -b "${BR}-agent/parallel/$SLUG" "$BR"
python3 skills/worktree-data-sync/scripts/sync_worktree_data.py \
  --to "$WT" --mode seed   # add --seed-sync-mode force-symlink for top-level symlinks instead of copies
# dispatch implementer with Worktree: <absolute path to $WT>
git merge --no-ff "${BR}-agent/parallel/$SLUG"
git worktree remove "$WT" && git branch -D "${BR}-agent/parallel/$SLUG"
```
