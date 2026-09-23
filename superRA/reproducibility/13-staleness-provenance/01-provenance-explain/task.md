---
title: "Resolve Hash Provenance and Rebuild `explain` Around It"
status: implemented
depends_on: []
---

## Objective

Build the provenance resolver and make `superra repro explain <target>` report, for every changed node, its recorded and current hash, where each came from, a named cause, and a runnable next command. Fix the two misleading statuses the case exposed.

- **Targets.** A task gives causes grouped across its stale steps; `task#step` or a unique bare step name gives one row per changed node; a path gives that file's provenance with its producer and consumers. `build`, `accept`, and `revoke` keep rejecting bare step names.
- **Sources.** Local receipt, acceptance ledger, lock history (`git log --all -- pytask.lock`, cached per revision in `.superra-repro/`), git blob history of each changed tracked dependency (sha256 of each blob until one matches the recorded hash, depth-capped), and Dropbox conflicted copies beside the file. A dependency matched on both sides shows `git <rev> → <rev>` with a diffstat and a capped diff.
- **Closed cause set** in JSON `cause` and the same words in text, at least: older build synced here; recorded build from another branch; dependency edited in commit X; reviewed bytes replaced; no known source. Each group or row ends with an exact runnable command. A `searched:` footer names the revisions, branches, and paths examined.
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

`superra repro explain <target>` now names, for every changed node, where its recorded and current hashes came from, one cause from a closed set, and a runnable next command. On IntermediaryDemand one call on `.` explains all seven non-fresh steps in 0.65 s.

### What `explain` reports

- **Targets.** A task path groups rows by cause across its non-fresh steps; `task#step` or a unique bare step name gives one row per changed node; a declared file path gives its provenance, producer, and readers. `build`, `accept`, and `revoke` still reject bare names, verified by `test_bare_names_stay_rejected_for_build_accept_and_revoke`.
- **Row shape.** One line per node: kind, logical node id, 8-character recorded → current hash, and the evidence (`recorded lock 8b31fd4 (Co Author, 2026-09-23 16:05 -0500); current superseded lock 2bd5d09 (…)`, or `git 0ce5fc8 → 8b30e7d, 1 file changed, 1 insertion(+), 1 deletion(-)` plus the first 20 diff lines). Each cause group ends in `next:`, with step-target commands merged across steps; a `searched:` footer names lock revisions, branches, HEAD's branch, tracked-file histories, and conflicted-copy locations. `--json` carries full hashes, every matched source, rows, and groups; `--diff` lifts the diff cap.
- **Causes.** The five required (`older-build`, `recorded-from-branch`, `dependency-edited`, `reviewed-replaced`, `no-known-source`) plus nine the real project and edge cases needed: `current-from-branch`, `uncommitted-edit`, `conflicted-copy`, `local-build`, `definition-changed`, `check-elsewhere`, `upstream`, `failed`, `missing`. The table with each command is in [commands.md §Explain](../../../../skills/task-tree/references/commands.md#explain).
- **The two status fixes.**
  - §4: an acceptance that no longer validates no longer overrides a step whose output bytes match its successful build; the step stays `fresh`, and its reason names the invalid acceptance and the `superra repro revoke '<task>#<step>'` that clears it. The fallback compares actual output bytes against the successful baseline, so a sidecar-tracked out whose bytes were corrupted still goes stale (`test_sidecar_corruption_with_restored_lock_inputs_forces_repair` caught this).
  - §5: a check with no local stamp whose lock entry matches its current inputs reports `passed at these inputs in lock <rev>; not run here` (or `in the working lock` outside git) and stays `missing`.

### Code

- [_repro_provenance.py](../../../../skills/task-tree/scripts/_repro_provenance.py) — git access, the per-revision lock index cached in `.superra-repro/lock-index/<sha>.json`, the resolver, cause selection, grouping, and rendering.
- [repro_run.py `_explain`](../../../../skills/task-tree/scripts/repro_run.py#L622-L641) — target resolution and output; the old `format_explain` and the raw `baseline:` JSON dump are gone.
- [apply_to_status](../../../../skills/task-tree/scripts/_repro_acceptance.py#L246-L253) (§4) and [_compare](../../../../skills/task-tree/scripts/_repro_state.py#L655-L658) (§5). `StepStatus.acceptance_invalid` carries the invalid reason to `explain`; status JSON is unchanged.

### Deviations from Details

- **Lock history walks local branches plus HEAD** (`git log --full-history --branches HEAD`), per the group decision, not `--all`; `--full-history` keeps merge commits, which is how a merged branch's hash resolves to `via merge <rev>`.
- **Blob history hashes the newest 50 revisions in one `cat-file --batch`** instead of stopping at the first match; one subprocess is cheaper than walking.
- **A check whose stamp is missing and whose inputs moved** shows the moved inputs as rows, not just the missing stamp.
- **`inspect_baseline` stays** for the `accept` preview's `baseline_details`; only `explain` stopped using it.
- **An untracked dependency with a local receipt snapshot** diffs against that snapshot (`uncommitted-edit`, command `explain --diff`).

### Validation

- [test_repro_provenance.py](../../../../skills/task-tree/scripts/test_repro_provenance.py) replays the report's case with two git clones: coauthor lock commits, sync lag, a docstring edit, a `--no-ff` merged side-branch build, the §4 accept-then-sync sequence, a check run only in the other clone, a hand-edited output, a conflicted copy, and an uncommitted edit. It asserts each cause, command, and footer; a second test covers `upstream` and `definition-changed` outside git. Registered as `provenance-explain-check`.
- Full task-tree suite: 1272 passed (baseline before this task: 1267).

### IntermediaryDemand smoke test (read-only; wrote only gitignored `.superra-repro/` caches)

`explain .` on `code/reproduction-check`, 7 of 16 steps non-fresh:

```
.: 7 of 16 step(s) not fresh
  check passed elsewhere, not run here — its lock entry matches the current inputs; the stamp is local
    check-heterogeneous-aggregation  passed at lock 727ec68 (Julie Zhiyu Fu, 2026-09-21 11:52 -0500)
  recorded build from another branch — the lock records a build made on a merged branch; that build's bytes are not here
    post-slr-irf-fit  output  Output/Treasury_auction_shocks/post_slr_irf.json  6e74ae40 → —  recorded lock e97c795 (Julie Zhiyu Fu, …) via merge 617b66f; missing here
    … 6 more missing outputs from the same merge (post-slr-irf-fit, post-slr-slopes-figure, assemble-paper-draft, assemble-ftg-slides)
  dependency edited in commit 0216e63 — the step last ran on the version before this edit
    post-slr-corner   dependency Code/Treasury_auction_shocks/treasury_ois_estimation.py  f1d3fbc0 → 918ab0be  git c0b5e0d → 0216e63, 1 file changed, 29 insertions(+), 2 deletions(-)
    post-slr-backends (same row)
    next: git diff c0b5e0d 0216e63 -- Code/Treasury_auction_shocks/treasury_ois_estimation.py
searched: … pytask.lock at 10 revision(s) […] on 66 local branch(es) (…); HEAD is code/reproduction-check; …
```

- The original six steps from the report were already accepted or revoked there, so this run exercises `check-elsewhere`, `recorded-from-branch`, and `dependency-edited`; the fixture covers the rest.
- The first run took 15 s because finding the merge that brought a side-branch commit into HEAD ran one `git merge-base` per first-parent merge; one `rev-list --ancestry-path` per matched revision brought it to 0.65 s.

### For review

- Run `explain` on the fixture (`test_explain_names_each_cause_across_two_clones`) and judge the text as a fresh agent would, per Details.
- Changing `_repro_state.py`, `_repro_acceptance.py`, `repro_run.py`, and the runner tests stales other tasks' registered checks (`reviewed-baseline-regression-check`, `task-scoped-builds-check`, `task-scoped-builds-pilot`, `unified-dependency-workflow-check`, and the dashboard checks); this task did not rebuild them.
