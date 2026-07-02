# Sync

Sync brings the branch onto the current base before refactor starts. A trivial sync (per Step 3) lands inline in Direct mode; a non-trivial sync is serialized — one generic sync author followed by one generic sync reviewer, no parallelization. A dispatched sync (its own `Stage: sync`) commits under the `sync` stage verb; an inline Direct-mode sync lands as `integrate(sync): …` per `SKILL.md` §Stop Points.

## Step 1: Resolve the target base

Resolve and record a candidate base ref from prior task context or git. This is a branch/ref name, not a merge-base SHA:

```bash
if git rev-parse --verify --quiet origin/main >/dev/null; then
  BASE_REF=origin/main
elif git rev-parse --verify --quiet origin/master >/dev/null; then
  BASE_REF=origin/master
else
  BASE_REF=
fi
```

If no prior decision records the base, ask:

```text
This integration will sync the branch against <base-ref>.
Is that correct, or did it split from a release branch, co-authored track,
or sibling branch?
```

Confirm `BASE_REF` before fetching, computing anchors, or dispatching. It is a working value for this integration pass, not a stored field — the sync merge commit records which base was synced (and pins `BASE_HEAD_SHA` as its base-side parent), so a resumed session recovers it from git rather than from a task section.

## Step 2: Compute sync anchors

Fetch the confirmed base when it is a remote-tracking ref and record two anchors from that same ref:

```bash
REMOTE=${BASE_REF%%/*}
REMOTE_BRANCH=${BASE_REF#*/}
if git remote get-url "$REMOTE" >/dev/null 2>&1; then
  git fetch "$REMOTE" "$REMOTE_BRANCH:refs/remotes/$REMOTE/$REMOTE_BRANCH"
fi
PRE_SYNC_BASE_SHA=$(git merge-base HEAD "$BASE_REF")
BASE_HEAD_SHA=$(git rev-parse "$BASE_REF")
```

- `PRE_SYNC_BASE_SHA` is evidence for incoming intent: `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`.
- `BASE_HEAD_SHA` is the post-sync governing baseline for Integrate: `BASE_HEAD_SHA..HEAD`.

## Step 3: Sync the branch when needed

If `git merge-base --is-ancestor "$BASE_HEAD_SHA" HEAD` succeeds, the branch is already synced — proceed to Integrate.

Otherwise size the sync against `semantic-merge §Scope the merge first`. When it scopes trivial, announce the Direct-mode switch and land the merge inline following that section, then skip the author and reviewer dispatch that follow and proceed to Integrate — its reviewer pass over `BASE_HEAD_SHA..HEAD` verifies the landed merge.

When the sync is non-trivial, dispatch one generic sync author:

```text
Agent(generic):
  Stage: sync
  Role: sync author
  References:
    - semantic-merge/references/workflow-sync-author.md

  Task: Sync this branch with <base-ref>
  Base branch: <base-ref>
  PRE_SYNC_BASE_SHA: <PRE_SYNC_BASE_SHA>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Incoming range: <PRE_SYNC_BASE_SHA>..<BASE_HEAD_SHA>

  Use semantic-merge workflow sync author mode. Land the merge commit plus
  any propagation commits needed to reach semantic coherence — `SKILL.md
  §Semantic Coherence Checklist §Scope boundary` is the stopping rule. The
  branch-level sync narrative is the commit messages; add a task-local
  `## Sync Impact` section to each affected task.md whose post-sync diff needs
  task-specific context. Defer codebase coherence — convention fit, utility
  reuse, PR-friendly diffs, Project Doc Audit walk-up, minimum net diff — to
  `refactor-and-integrate` via Integrate.
```

If the sync author returns `NEEDS_CONTEXT` or `BLOCKED` because a user decision is required, the orchestrator asks the user, folds the decision into the relevant task objective, commits, and re-dispatches the sync author with the decision context.

## Step 4: Dispatch the sync reviewer

Before Integrate begins, dispatch one generic sync reviewer:

```text
Agent(generic):
  Stage: sync
  Role: sync reviewer
  References:
    - semantic-merge/references/workflow-sync-reviewer.md

  Task: Review the semantic sync with <base-ref>
  Base branch: <base-ref>
  PRE_SYNC_BASE_SHA: <PRE_SYNC_BASE_SHA>
  BASE_HEAD_SHA: <BASE_HEAD_SHA>
  Incoming range: <PRE_SYNC_BASE_SHA>..<BASE_HEAD_SHA>
  Sync commits: <MERGE_COMMIT_SHA>[, <PROPAGATION_OR_DOC_SHAS>...]

  Use semantic-merge workflow sync reviewer mode. Verify anchors, incoming
  intent, current-branch intent, conflict resolution, user-decision logging,
  task-local `## Sync Impact` coverage, and scope boundary. Record any
  sync-review finding via the standard mechanism (affected task's
  `## Review Notes`, or the REVISE return for a branch-level finding with no
  task home). Return APPROVE or REVISE.
```

On REVISE, re-dispatch the sync author for accepted items, then re-dispatch the sync reviewer. Integrate starts only after sync review APPROVES.
