---
title: "Resolve Hash Provenance and Rebuild `explain` Around It"
status: implemented
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
- **Causes** ([row](../../../../skills/task-tree/scripts/_repro_provenance.py#L409-L418)):
  - `input-changed`: a dependency, including another step's output, or the step definition. Pointer: `git diff <recorded> [<current>] -- <path>` for a tracked file, `git diff [<rev>] -- <task.md> superRA/config.yaml` for the definition, or the producer's `explain` for a produced input.
  - `other-build`: an output whose current bytes match another recorded state. Pointer: `git show --stat <rev>`.
  - `unknown-output`: an output whose current bytes match nothing recorded. Pointer: `explain <path> --json`.
  - A missing out, a failed run, an upstream step, or a check that passed elsewhere is a status reason, listed under `status (no hash to resolve)` in a task view.
- **Source facts.** Each side of a row names the first matching state:
  - a lock revision, as `lock <rev> (<author>, <date>; <relation>)` ([LockHistory.match](../../../../skills/task-tree/scripts/_repro_provenance.py#L225-L249)). `<rev>` is the introducing commit, preferring one in HEAD's history. `<relation>` is one fact:
    - `in HEAD's lock`: HEAD's lock records that hash for the node in some step's entry;
    - `earlier commit, N behind HEAD`: an ancestor of HEAD;
    - `not in HEAD's history; on <branch>, …`: up to three containing local or remote-tracking branches, then `and N more`.
  - `git <rev>`, or `uncommitted` for a tracked file;
  - `working lock (not committed)`, `built here <time>`, `snapshot from the build here`, or `reviewed <time>`;
  - `also in conflicted copy <path>` when a Dropbox copy holds the recorded bytes.

  JSON carries every source.
- **Output.** One line per node with 8-character hashes and a diffstat for tracked inputs, the first 20 diff lines (`--diff` for all), one `next:` per cause with step targets merged, and a `searched:` footer naming the lock revisions and tracked-file histories.
- **The two status fixes.**
  - §4: an acceptance that no longer validates no longer overrides a step whose output bytes match its successful build. The step stays `fresh`, and its reason names the invalid acceptance and `superra repro revoke '<task>#<step>'`. The fallback compares actual output bytes, so a corrupted sidecar-tracked out still goes stale ([apply_to_status](../../../../skills/task-tree/scripts/_repro_acceptance.py#L246-L253)).
  - §5: a check with no local stamp whose lock entry matches its inputs reports `passed at these inputs in lock <rev>; not run here` (or `in the working lock`) and stays `missing` ([_compare](../../../../skills/task-tree/scripts/_repro_state.py#L655-L658)).
    - `<rev>` is the last commit touching the lock when the working lock equals HEAD's.
    - [lock_commit](../../../../skills/task-tree/scripts/_repro_provenance.py#L118-L147) caches that commit by lock content in `.superra-repro/lock-commit.json`. Git runs only for lock bytes not yet seen committed; a repeat `status` or dashboard refresh spawns none (`test_status_reuses_the_lock_commit_without_git`).

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

## Review Notes
Tier: thorough. Focus: correctness (§4 fallback, cause classification), agent usability of text and JSON output, cost on large histories. The §4 and §5 status changes are correct: the fallback compares actual output bytes against the successful baseline, so a sidecar lock alone cannot make a step fresh. The blocking problems are in cause selection: in three reproducible cases the cause and `next:` command point the wrong way.

1. **[BLOCKING] The most common staleness case is reported backwards.** When a producer is rebuilt and committed but its consumer is not, the consumer's changed dependency is classified `older-build`, with `next: superra repro status`. The current bytes are actually the newest build, and the consumer needs a rebuild. Reproduced from the `clones` fixture. In A, rebuild only `01-est` and commit. In B, pull and sync `output/est.txt`, then run `explain 02-paper`. The output reads `older build synced here — the newer build recorded in the lock has not synced here yet`, with `recorded lock d543cc9 … current superseded lock 5d393a7`, but 5d393a7 is HEAD.
   - **Cause.** [_repro_provenance.py:306](../../../../skills/task-tree/scripts/_repro_provenance.py#L306) sets `relation='working'` only when the value is in *this step's* lock entry. A produced dependency's current hash sits in the producer's working entry, so it is labelled `older`, and [line 456](../../../../skills/task-tree/scripts/_repro_provenance.py#L456) then picks `older-build`.
   - **Same case with a local receipt snapshot (clone A).** [line 443](../../../../skills/task-tree/scripts/_repro_provenance.py#L443) takes the snapshot path, and the row reads `dependency edited, not committed` for `${OUT}/est.txt`, a produced output that nobody edited.
   - **Fix.** Compute `working` against every working-lock entry for the node. Allow `older-build` only when the current revision is an ancestor of the recorded one. Keep produced dependencies (`graph.producers`) off the snapshot/`uncommitted-edit` path. Give this case its own reading, for example "producer rebuilt in lock X; this step has not run on it", with `repro build <consumer>`. Add it to the fixture in both clones.
   → implemented: [row](../../../../skills/task-tree/scripts/_repro_provenance.py#L409-L418) keys the cause on role, so a changed dependency is always `input-changed`; its current source reads `lock <producer rev> (…; in HEAD's lock)` and it points to the producer's `explain`. The snapshot path skips produced inputs ([line 439](../../../../skills/task-tree/scripts/_repro_provenance.py#L439)). The fixture covers both clones.

2. **[BLOCKING] `recorded-from-branch` takes merge parentage as proof that the bytes are elsewhere, and it outranks `older-build`.**
   - **The fixture shows it.** In `04-panel`, A builds on `side` into the shared `output/` and merges. Once B's sync delivers `panel.txt`, the step is fresh with no rebuild. Before that sync, `explain` says `that build's bytes are not here` and recommends `repro build` ([_repro_provenance.py:38](../../../../skills/task-tree/scripts/_repro_provenance.py#L38), [:433](../../../../skills/task-tree/scripts/_repro_provenance.py#L433), [:454](../../../../skills/task-tree/scripts/_repro_provenance.py#L454)), even though the current bytes match an older HEAD lock, which is the sync-lag signature.
   - **Real projects make it the default.** Under a PR-merge workflow, every lock commit made on a PR branch is off HEAD's first-parent chain. On IntermediaryDemand, all 7 output rows from PR #142 (`via merge 617b66f`) get this cause. A feature branch that has merged main in the same way classifies main's lock commits as another branch's builds.
   - **Fix.** Report the merge as a fact and name the source branch; the merge subject or `branch --contains` gives it. Let `older-build` win when the current bytes match an ancestor lock. Keep the "bytes are not here, build" reading only for a missing output, or phrase it conditionally: "if that branch built in another worktree or checkout, its bytes live there."
   → implemented: the merge and branch narratives are gone. [LockHistory.match](../../../../skills/task-tree/scripts/_repro_provenance.py#L225-L249) reports the introducing revision and whether HEAD's lock records the hash; the `04-panel` row is `other-build`, with `recorded lock <side> (…; in HEAD's lock); current lock <first> (…; earlier commit, 5 behind HEAD)`.

3. **[BLOCKING] Git-tracked outputs get dependency wording, and the `git` path ignores direction.** [_repro_provenance.py:447-450](../../../../skills/task-tree/scripts/_repro_provenance.py#L447-L450) apply to any row with a git blob match, whatever its `kind`.
   - **A hand-edited tracked output** reads `dependency edited, not committed`. Once committed, it reads `dependency edited in commit X — the step last ran on the version before this edit`.
   - **A tracked output holding older bytes** (recorded = newer commit, current = older commit) reads `dependency edited in commit <older commit>`, with a reversed diff (`-v2 +v1`).
   - **Why it matters.** Research projects often commit tables and figures, and an agent reading "the step last ran on the version before this edit" will treat an output change as a code edit.
   - **Fix.** Limit `dependency-edited`/`uncommitted-edit` to `kind == 'dependency'`. For outputs, keep the git revision as evidence and classify through lock and receipt. Name "edited in commit X" only when X descends from the recorded revision.
   → implemented: git diffs and diff pointers apply only to inputs. A tracked output's git revision or `uncommitted` is a source fact under `other-build` or `unknown-output` (`test_tracked_output_edits_are_output_causes`).

4. **[ADVISORY] Unbounded blob reads on large tracked files.** [blob_history](../../../../skills/task-tree/scripts/_repro_provenance.py#L270-L284) loads up to 50 full blobs of every changed tracked file into memory in one `cat-file --batch`. Fix: filter with `--batch-check` sizes first; only a blob whose size equals the recorded file's size can match.
   → implemented: [blob_history](../../../../skills/task-tree/scripts/_repro_provenance.py#L289-L309) sizes blobs with `--batch-check` and reads distinct blobs of at most 16 MiB each and 64 MiB in total. The recorded file's size is unknown on this machine, so there is a cap rather than a size-equality filter.

5. **[ADVISORY] `git branch --contains` runs once per source and is not memoized.** [containing_branches](../../../../skills/task-tree/scripts/_repro_provenance.py#L210-L211) is called from `describe` for each other-branch source on both sides of every row. Memoize it per sha, as `merge_into_head` already is.
   → implemented: branch names now appear only as a fact for a lock revision outside HEAD's history; [LockHistory.branches](../../../../skills/task-tree/scripts/_repro_provenance.py#L235-L241) runs one `for-each-ref --contains` per revision, memoized.

6. **[ADVISORY] `status` now spawns git.** A missing check stamp makes [_compare](../../../../skills/task-tree/scripts/_repro_state.py#L657) build a full `LockHistory`: `rev-list HEAD`, first-parent, `for-each-ref`, and lock parsing, repeated on every `compute_status` call, including dashboard refreshes. It cost 0.24 s on IntermediaryDemand, which is acceptable today. Consider loading the history lazily from the lock-index cache.
   → implemented: [lock_commit](../../../../skills/task-tree/scripts/_repro_provenance.py#L118-L147) replaces `LockHistory` in status and caches its commit by lock content, so a repeat `status` or dashboard refresh spawns no git.

7. **[ADVISORY] The 14-cause set.** Each cause maps to one command, and the text reads plainly, so the set is acceptable at this size. `failed`, `upstream`, and `missing` are status facts rather than provenance and belong in the set for completeness. The unstable members are `recorded-from-branch` against `older-build`/`missing` (finding 2) and the missing "producer rebuilt" reading (finding 1). Once those are fixed, the set should come out the same size or smaller; no further merge is needed.
   → implemented: three causes, per the revised objective.
