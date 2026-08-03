# Finish

Finish executes the user's choice from the IMPLEMENT completion menu. `superRA/` is committed as-is — part of the permanent branch record; any closeout commit lands as `integrate(finish): …` per `SKILL.md` §Stop Points.

## Step 1: Freshness check

`BASE_REF` and `BASE_HEAD_SHA` carry over within a session. Resumed session: recover them from the sync merge commit — its base-side parent is `BASE_HEAD_SHA`, its message records the base synced. Sync was a no-op: use the pre-Integrate base ref directly.

Fetch `BASE_REF` when it is a remote-tracking ref and check whether it advanced since Integrate:

```bash
REMOTE=${BASE_REF%%/*}
REMOTE_BRANCH=${BASE_REF#*/}
if git remote get-url "$REMOTE" >/dev/null 2>&1; then
  git fetch "$REMOTE" "$REMOTE_BRANCH:refs/remotes/$REMOTE/$REMOTE_BRANCH"
fi
CURRENT_BASE_HEAD_SHA=$(git rev-parse "$BASE_REF")
```

`CURRENT_BASE_HEAD_SHA` differs from `BASE_HEAD_SHA`: re-enter Sync before publishing or landing.

## Step 2: Publish or land

PR:

```bash
git push -u origin <analysis-branch>
gh pr create --title "<title>" --body "<summary, data, reproducibility, quality gates>"
```

Local fast-forward into the base:

```bash
git checkout <base-branch>
git pull
git merge --ff-only <analysis-branch>
```

Run the project pipeline or targeted verification on the final tree; investigate any failure before cleanup.

## Step 3: Cleanup

Work used a worktree: remove it per `superRA:agent-orchestration/references/worktree-harness-fallback.md`. Seeded non-git data disappears with the worktree — data teardown in `superRA:worktree-data-sync`.

Report what was published or landed and what was cleaned up.
