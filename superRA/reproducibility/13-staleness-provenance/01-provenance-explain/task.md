---
title: "Resolve Hash Provenance and Rebuild `explain` Around It"
status: approved
depends_on: []
---

## Objective

Build the provenance resolver and make `superra repro explain <target>` report, for every changed node, its recorded and current hash, where each came from, a named cause, and a runnable next command. Fix the two misleading statuses the case exposed.

- **Targets.** A task gives causes grouped across its stale steps; `task#step` or a unique bare step name gives one row per changed node; a path gives that file's provenance with its producer and consumers. `build`, `accept`, and `revoke` keep rejecting bare step names.
- **Sources.** Local receipt, acceptance ledger, lock history (`git log --all -- pytask.lock`, cached per revision in `.superra-repro/`), git blob history of each changed tracked dependency (sha256 of each blob until one matches the recorded hash, depth-capped), and Dropbox conflicted copies beside the file. A dependency matched on both sides shows `git <rev> → <rev>` with a diffstat and a capped diff.
- **Three causes, keyed by the node's role in the step.** JSON `cause` and text use the same words; everything finer is a `source` fact on the row, never a cause.
  - `input-changed` — a dependency (including another step's output) or the step definition differs from the last build. Source: the commit(s) or `uncommitted`, or the producer's lock entry the bytes match. Pointer: the `git diff` command.
  - `other-build` — an output's current bytes match a different recorded state: another lock revision, the acceptance, a conflicted copy, or this machine's receipt. Source states the revision and whether it is the lock at `HEAD`; no inferred direction or branch story.
  - `unknown-output` — an output's current bytes match no recorded state. Pointer: `explain <path> --json`.
  - `missing`, `failed`, `upstream`, and a check passed elsewhere stay status reasons, outside the cause set.
- **Tools and a basic hint, not a diagnosis.** Each cause carries one hint line and one tool pointer; the agent digs further with git itself. A `searched:` footer names the revisions and paths examined.
- **Acceptance fallback (report §4).** An acceptance that no longer validates no longer overrides a step whose bytes match its successful lock entry: the step is fresh, and its reason names the invalid acceptance and `repro revoke`.
- **Check stamps (report §5).** A check with no local stamp whose lock entry matches the current inputs reports `passed at these inputs in lock <rev>; not run here`, distinct from a never-run check; its status stays non-fresh.
- **Output budget and cost** per the group constraints; the raw JSON dump in text output is gone.
- **Validation:** a fixture replays the report's case — two clones, a coauthor lock commit, older output bytes restored to fake sync lag, a lock hash introduced by a merged side branch, a docstring edit to a tracked dependency, the §4 accept-then-sync sequence, and a check run only in the other clone — and asserts each cause, command, and footer; the full task-tree suite passes; [commands.md §Reproduction](../../../../skills/task-tree/references/commands.md#reproduction) documents the new targets, flags, and cause set.

## Details

- **Entry points.** [repro_run.py explain wiring](../../../../skills/task-tree/scripts/repro_run.py#L715-L740), [inspect_baseline](../../../../skills/task-tree/scripts/_repro_acceptance.py#L276), [format_explain](../../../../skills/task-tree/scripts/_repro_state.py#L877), [select_steps](../../../../skills/task-tree/scripts/_repro_state.py#L755). A new `_repro_provenance.py` keeps the resolver apart from status.
- **§4 origin.** The override is in [apply_to_status](../../../../skills/task-tree/scripts/_repro_acceptance.py#L247): `if entry.status == 'fresh' or …: entry.status = 'stale'`, added in `d4d0ca08`. Nothing in that commit's task justifies overriding a lock-fresh step.
- **Bare step names were deleted on purpose** in [01-cli-decision-support](../../12-agent-protocol/01-cli-decision-support/task.md) because they were ambiguous as build targets. Explain is read-only, and a unique name is unambiguous; keep the qualified-form error for non-unique names.
- **Lock ids are logical paths** (`${OUT}/…`), so lock-history matches key on the logical node id, not the resolved path.
- **Directory and `saved-input:` states** are not file hashes; resolve them against lock history and ledger only.
- Load `superRA:task-tree` and `superRA:reproducibility` before editing. High-stakes for agent behavior: a reviewer should run `explain` on the fixture and judge the text as a fresh agent would.

## Reproduction

```yaml
steps:
  - name: provenance-explain-check
    kind: check
    cmd: "uv run --with pytest --with 'pytask>=0.6,<0.7' --with pytask-parallel --with pyyaml python -m pytest skills/task-tree/scripts/test_repro_provenance.py -q -p no:cacheprovider"
    deps:
      - skills/task-tree/scripts/_apply_patch.py
      - skills/task-tree/scripts/_artifacts.py
      - skills/task-tree/scripts/_comments.py
      - skills/task-tree/scripts/_repro.py
      - skills/task-tree/scripts/_repro_acceptance.py
      - skills/task-tree/scripts/_repro_hooks.py
      - skills/task-tree/scripts/_repro_provenance.py
      - skills/task-tree/scripts/_repro_scope.py
      - skills/task-tree/scripts/_repro_state.py
      - skills/task-tree/scripts/_step_links.py
      - skills/task-tree/scripts/_task_dependencies.py
      - skills/task-tree/scripts/_task_io.py
      - skills/task-tree/scripts/_task_snapshot.py
      - skills/task-tree/scripts/_task_validate.py
      - skills/task-tree/scripts/_worktree_discovery.py
      - skills/task-tree/scripts/cli.py
      - skills/task-tree/scripts/dashboard_artifact_workflow.py
      - skills/task-tree/scripts/plan_dashboard.py
      - skills/task-tree/scripts/plan_migrate.py
      - skills/task-tree/scripts/repro_run.py
      - skills/task-tree/scripts/task_add_result.py
      - skills/task-tree/scripts/task_check.py
      - skills/task-tree/scripts/task_comment.py
      - skills/task-tree/scripts/task_create.py
      - skills/task-tree/scripts/task_hook.py
      - skills/task-tree/scripts/task_link.py
      - skills/task-tree/scripts/task_query.py
      - skills/task-tree/scripts/task_read.py
      - skills/task-tree/scripts/task_rename.py
      - skills/task-tree/scripts/task_update.py
      - skills/task-tree/scripts/wrapper_resolver.py
      - skills/task-tree/scripts/conftest.py
      - skills/task-tree/scripts/test_repro_runner.py
      - skills/task-tree/scripts/test_repro_provenance.py
```

## Results

`superra repro explain <target>` now gives, for every changed node, its recorded and current hash, the states that hold each (source facts), one of three causes keyed on the node's role, a one-line hint, and one tool pointer. On IntermediaryDemand, one call on `.` covers all 7 non-fresh steps in 0.4 s.

### What `explain` reports

- **Targets.** A task path groups rows by cause across its non-fresh steps; `task#step` or a unique bare step name gives one row per changed node; a declared file path gives its provenance, producer, and readers. `build`, `accept`, and `revoke` still reject bare names (`test_bare_names_stay_rejected_for_build_accept_and_revoke`).
- **Causes** ([row](../../../../skills/task-tree/scripts/_repro_provenance.py#L413-L422)):
  - `input-changed`: a dependency, including another step's output, or the step definition. Pointer: `git diff <recorded> [<current>] -- <path>` for a tracked file, `git diff [<rev>] -- <task.md> superRA/config.yaml` for the definition, or, for a produced input, the producer's `explain` while the producer is not fresh and `build <this step>` once it is ([_command](../../../../skills/task-tree/scripts/_repro_provenance.py#L464-L487)).
  - `other-build`: an output whose current bytes match another recorded state. Pointer: `git show --stat <rev>` of the lock or git revision the row prints.
  - `unknown-output`: an output whose current bytes match nothing recorded. Pointer: `explain <path> --json`.
  - A missing out, a failed run, an upstream step, or a check that passed elsewhere is a status reason, listed under `status (no hash to resolve)` in a task view.
- **Source facts.** Each side of a row names the first matching state:
  - a lock revision, as `lock <rev> (<author>, <date>; <relation>)` ([LockHistory.match](../../../../skills/task-tree/scripts/_repro_provenance.py#L228-L253)). `<rev>` is the introducing commit, preferring one in HEAD's history. `<relation>` is one fact:
    - `in HEAD's lock, entry <step>` (or `entries <step>, …`): the steps whose entry in HEAD's lock records that hash for the node, so a produced input's two sides read `entry <consumer>` and `entry <producer>`;
    - `earlier commit, N behind HEAD`: an ancestor of HEAD;
    - `not in HEAD's history; on <branch>, …`: up to three containing local or remote-tracking branches, then `and N more`.
  - `git <rev>`, or `uncommitted` for a tracked file;
  - `working lock (not committed)`, `built here <time>`, `snapshot from the build here`, or `reviewed <time>`;
  - `also in conflicted copy <path>` when a Dropbox copy holds the recorded bytes.

  JSON carries every source.
- **Output.** One line per node with 8-character hashes and a diffstat for tracked inputs, the first 20 diff lines (`--diff` for all), `next:` pointers per cause, with targets merged only for `build`/`status` (each `explain` pointer is its own line; the fixture parses every printed pointer with the real argparse), and a `searched:` footer naming the lock revisions and tracked-file histories.
- **The two status fixes.**
  - §4: an acceptance that no longer validates no longer overrides a step whose output bytes match its successful build. The step stays `fresh`, and its reason names the invalid acceptance and `superra repro revoke '<task>#<step>'`. The fallback compares actual output bytes, so a corrupted sidecar-tracked out still goes stale ([apply_to_status](../../../../skills/task-tree/scripts/_repro_acceptance.py#L246-L253)).
  - §5: a check with no local stamp whose lock entry matches its inputs reports `passed at these inputs in lock <rev>; not run here` (or `in the working lock`) and stays `missing` ([_compare](../../../../skills/task-tree/scripts/_repro_state.py#L655-L658)).
    - `<rev>` is the last commit touching the lock when the working lock equals HEAD's.
    - [lock_commit](../../../../skills/task-tree/scripts/_repro_provenance.py#L119-L148) caches that commit by lock content in `.superra-repro/lock-commit.json`. Git runs only for lock bytes not yet seen committed; a repeat `status` or dashboard refresh spawns none (`test_status_reuses_the_lock_commit_without_git`).

### Code

- [_repro_provenance.py](../../../../skills/task-tree/scripts/_repro_provenance.py) — git access, the per-revision lock index in `.superra-repro/lock-index/<sha>.json`, source resolution, causes, grouping, rendering.
- [repro_run.py `_explain`](../../../../skills/task-tree/scripts/repro_run.py#L622-L641) — target resolution and output; the old `format_explain` and the raw `baseline:` JSON dump are gone.

### Deviations from Details

- **Lock history walks local and remote-tracking branches plus HEAD** (`git log --full-history --topo-order --branches --remotes HEAD`), without fetching, rather than `--all`. `--topo-order` makes "introducing revision" topological when commit times tie.
- **Relation counts and branch lookups** are memoized per revision within one call, not persisted: both depend on HEAD and refs, which move.
- **Tracked-file history** lists the newest 50 revisions with `cat-file --batch-check`, then reads only distinct blobs of at most 16 MiB each and 64 MiB in total in one `--batch`, instead of stopping at the first match.
- **A check whose stamp is missing and whose inputs moved** shows the moved inputs as `input-changed` rows.
- **`inspect_baseline` stays** for the `accept` preview's `baseline_details`.
- **An untracked, unproduced dependency with a local receipt snapshot** diffs against it (pointer `explain <step> --diff`).

### Validation

- [test_repro_provenance.py](../../../../skills/task-tree/scripts/test_repro_provenance.py) covers these cases, asserting cause, source facts, pointer, and footer for each:
  - It replays the report's case with two git clones: coauthor lock commits, sync lag, a docstring edit, a `--no-ff` merged side-branch build, the §4 accept-then-sync sequence, a check run only in the other clone, a hand-edited output, a conflicted copy, and an uncommitted edit.
  - It covers the review's producer-rebuilt case in both clones.
  - It covers a git-tracked output edited and then committed.
  - It covers a lock revision off HEAD's history, on a local branch (`on wip`) and on a fetched coauthor branch (`on origin/wip`).
  - It checks that a repeat `status` reuses the cached lock commit without spawning git.
  - Registered as `provenance-explain-check`.
- Full task-tree suite: 1275 passed.

### IntermediaryDemand smoke test (read-only; wrote only gitignored `.superra-repro/` caches)

`explain .` on `code/reproduction-check`:

```
.: 7 of 16 step(s) not fresh
  input-changed — an input or the step definition differs from the last build
    post-slr-corner  dependency Code/Treasury_auction_shocks/treasury_ois_estimation.py  f1d3fbc0 → 918ab0be  recorded git c0b5e0d; current git 0216e63; 1 file changed, 29 insertions(+), 2 deletions(-)
    post-slr-backends  (same row)
    next: git diff c0b5e0d 0216e63 -- Code/Treasury_auction_shocks/treasury_ois_estimation.py
  status (no hash to resolve):
    check-heterogeneous-aggregation  [missing]  passed at these inputs in lock 0216e63; not run here
    post-slr-irf-fit  [missing]  output Output/Treasury_auction_shocks/post_slr_irf_level.png is missing (and 2 more)
    … post-slr-slopes-figure, assemble-paper-draft, assemble-ftg-slides: missing outputs
searched: … pytask.lock at 10 revision(s) on local and remote-tracking branches and HEAD [617b66f, …]; git history of Code/Treasury_auction_shocks/treasury_ois_estimation.py (3 revision(s)); …
```

A path target shows the relation fact: `explain Output/Futures/bbg_fv_clean.parquet` reads `recorded lock 727ec68 (Julie Zhiyu Fu, 2026-09-21 11:52 -0500; in HEAD's lock); current reviewed 2026-09-23 15:12`. Repeat `status .` takes 0.10 s with the lock commit cached.

The report's six steps had already been accepted or revoked there; the fixture covers the other paths.

### For review

- Run `explain` on the fixture (`test_explain_names_each_cause_across_two_clones`) and judge the text as a fresh agent would.
- Edits to `_repro_state.py`, `_repro_acceptance.py`, `repro_run.py`, and the runner tests stale other tasks' checks (`reviewed-baseline-regression-check`, `task-scoped-builds-check`, `task-scoped-builds-pilot`, `unified-dependency-workflow-check`, the dashboard checks); this task did not rebuild them.
