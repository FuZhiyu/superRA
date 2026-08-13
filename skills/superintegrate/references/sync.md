# Sync

Sync brings the branch onto the current base before permanent documentation and refactoring. A trivial sync (Step 3) lands inline and commits as `integrate(sync): …` per `SKILL.md` §Stop Points; a non-trivial sync is dispatched under its own `Stage: sync`, commits under the `sync` stage verb, and is serialized — one generic sync author, then one generic sync reviewer, no parallelization.

## Step 1: Resolve the target base

Resolve a candidate base ref from prior task context or git — a branch/ref name, not a merge-base SHA:

```bash
if git rev-parse --verify --quiet origin/main >/dev/null; then
  BASE_REF=origin/main
elif git rev-parse --verify --quiet origin/master >/dev/null; then
  BASE_REF=origin/master
else
  BASE_REF=
fi
```

No prior decision records the base: ask.

```text
This integration will sync the branch against <base-ref>.
Is that correct, or did it split from a release branch, co-authored track,
or sibling branch?
```

Confirm `BASE_REF` before fetching, computing anchors, or dispatching. A working value for this pass, not a stored field — the sync merge commit records which base was synced (pinning `BASE_HEAD_SHA` as its base-side parent), so a resumed session recovers it from git.

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

- `PRE_SYNC_BASE_SHA` — evidence for incoming intent: `PRE_SYNC_BASE_SHA..BASE_HEAD_SHA`.
- `BASE_HEAD_SHA` — the post-sync governing baseline for Mature & Consolidate and Integrate: `BASE_HEAD_SHA..HEAD`.

## Step 3: Sync the branch when needed

`git merge-base --is-ancestor "$BASE_HEAD_SHA" HEAD` succeeds: already synced — proceed to Mature & Consolidate.

Otherwise size the sync against `semantic-merge §Scope the merge first`. Trivial: announce the inline path, land the merge following that section, skip the author and reviewer dispatches, proceed to Mature & Consolidate.

Non-trivial: dispatch one generic sync author.

```text
Prompt:
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
  task-specific context. Defer permanent-record work to Mature & Consolidate,
  and codebase coherence — convention fit, utility reuse, PR-friendly diffs,
  Project Doc Audit walk-up, minimum net diff — to Integrate.
```

Sync author returns `NEEDS_CONTEXT` or `BLOCKED` on a required user decision: the orchestrator asks the user, folds the decision into the relevant task objective, commits, and re-dispatches with the decision context.

## Step 4: Dispatch the sync reviewer

Before Mature & Consolidate begins:

```text
Prompt:
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

On REVISE, re-dispatch the sync author for accepted items, then re-dispatch the reviewer. Mature & Consolidate starts only after sync review APPROVES.
