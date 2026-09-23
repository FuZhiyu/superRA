---
title: "Staleness Provenance: Explain Where a Changed Hash Came From"
status: revise
depends_on: []
---

## Objective

`superra repro explain` tells an agent where each changed input's or output's current and recorded bytes came from, so a stale step is diagnosed in one to three calls instead of a manual `git log -S` / `shasum` / `stat` hunt. The motivating case: six stale steps on IntermediaryDemand took about 20 tool calls to diagnose, and none held a result-affecting change ([report](../../../docs/plans/2026-09-23-repro-staleness-explanations-report.md)).

### Decisions (researcher, 2026-09-23)

- **One resolver, several sources of known hash states.** Every hash `explain` prints, on both the recorded and the current side, resolves against the local receipt, the acceptance ledger, the committed lock history across all local branches, git blob history of tracked dependencies, and Dropbox conflicted copies beside the file. Each match carries its relation to `HEAD`: an older build synced here, a build from another branch, or the working lock.
- **Git answers "who".** Author and date come from the lock commit that introduced a hash. No host or user name is committed anywhere.
- **The committed build record carries only what git cannot know:** per-step build time, platform, and environment fingerprint. Details: [02-build-record](02-build-record/task.md).
- **No worktree scanning.** A recorded hash built in a worktree resolves through the lock history of that worktree's branch; whoever builds in a worktree handles its merge.
- **A check that passed elsewhere stays non-fresh** with a distinct reason naming the lock revision where it passed.
- **Agent usability is the acceptance bar.** One command, `explain <target>`, where the target is a task, a step, or a path; three causes (input changed, output from another recorded build, output of unknown source) with the finer provenance as source facts; one hint and one tool pointer per cause; a footer stating what was searched. Facts and a likely reading, never a build/accept verdict: that judgment stays in [rerun-or-accept](../../../skills/reproducibility/references/rerun-or-accept.md).

### Constraints

- **Cheap by construction.** Resolve only changed nodes; `status` stays unchanged except for reason strings; never hash a file outside this checkout; cache the per-revision lock index under `.superra-repro/` (a revision never changes, so the cache never invalidates).
- **Replace, don't add, output.** Default text is one line per changed node with 8-character hashes; environment details only on mismatch; diffs capped with the full diff behind `--diff`; `--json` carries full hashes and the same rows.
- This group folds back into [02-runner](../02-runner/task.md) and [06-skill](../06-skill/task.md) at integration.

## Details

### What `explain` lacks today (2026-09-23)

- **Output changes carry no diff row.** [inspect_baseline](../../../skills/task-tree/scripts/_repro_acceptance.py#L276-L305) diffs only the lock's `deps`.
- **Dependency diffs need a snapshot captured on this machine** ([source_snapshots](../../../skills/task-tree/scripts/_repro_acceptance.py#L116-L134)); a coauthor's build yields `history: "unavailable"` although git holds the recorded version.
- **Receipts, run records, logs, and check stamps live in gitignored `.superra-repro/`**, so all are `null` or missing on every machine but the builder's.
- **The text output ends in a raw JSON dump** ([repro_run.py:737](../../../skills/task-tree/scripts/repro_run.py#L737)).

### Measured cost on IntermediaryDemand (2026-09-23)

The lock has 8 revisions across all branches, 29 KB, 16 steps, 238 distinct hashes; `git cat-file --batch` over all revisions took 0.02 s. The tracked dependency in the case, `Code/plot_style.py`, has 4 revisions.
