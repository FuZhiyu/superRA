# Finish

Finish executes the user's completion choice from `superimplement`. The `superRA/` directory is committed as-is — it is part of the permanent branch record; any closeout commit here lands as `integrate(finish): …` per `SKILL.md` §Stop Points.

## Step 1: Freshness check

`BASE_REF` and `BASE_HEAD_SHA` carry over within a session. On a resumed session, recover them from the sync merge commit: its base-side parent is `BASE_HEAD_SHA`, and the commit message records the base that was synced. If Sync was a no-op (the branch was already current), use the pre-Integrate base ref directly.

Fetch `BASE_REF` when it is a remote-tracking ref and check whether it advanced since Integrate:

```bash
REMOTE=${BASE_REF%%/*}
REMOTE_BRANCH=${BASE_REF#*/}
if git remote get-url "$REMOTE" >/dev/null 2>&1; then
  git fetch "$REMOTE" "$REMOTE_BRANCH:refs/remotes/$REMOTE/$REMOTE_BRANCH"
fi
CURRENT_BASE_HEAD_SHA=$(git rev-parse "$BASE_REF")
```

If `CURRENT_BASE_HEAD_SHA` differs from `BASE_HEAD_SHA`, re-enter Sync before publishing or landing the work.

## Step 2: Publish or land

For a PR:

```bash
git push -u origin <analysis-branch>
gh pr create --title "<title>" --body "<summary, data, reproducibility, quality gates>"
```

For a local fast-forward into the base:

```bash
git checkout <base-branch>
git pull
git merge --ff-only <analysis-branch>
```

Run the project pipeline or targeted verification on the final tree. If it fails, investigate before cleanup.

## Step 3: Cleanup

If the work used a worktree, remove it per `superRA:agent-orchestration/references/worktree-harness-fallback.md`. Seeded non-git data disappears with the worktree; see `superRA:worktree-data-sync` for data teardown.

Report what was published or landed and what was cleaned up.
