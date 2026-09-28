# Repro Staleness Explanations Report

`superra repro status` and `explain` say *that* a node changed but not *where its current bytes came from*, so agents rebuild the provenance by hand.

- In one session on IntermediaryDemand, six stale steps took about 20 tool calls of `git log -S`, `shasum`, `stat`, log-file reading, and pickle diffs to diagnose. The diagnosis: none held a result-affecting change.
- Every missing fact was already available to superRA: lock history in git, file hashes, and build metadata at execution time.
- One bug surfaced along the way: an invalidated acceptance hides a lock-fresh step (§4).

## 1. The case: six stale steps, none with a real change

Two coauthors build the same graph. `pytask.lock` is committed; `Output/` is a shared Dropbox folder. Two machines are involved: home-studio (macOS 27, M1 Max) and a coauthor's Mac (build commits dated +0100).

| Step | Status reason | Actual cause | Found by |
|---|---|---|---|
| `estimate-auction-models`, `estimate-crisis-robustness` | `output … changed` | On-disk pickle is the coauthor's build from the *previous* lock commit; the newer build had not synced yet | `git log -S <hash> -- pytask.lock`, `stat`, `/Users/<coauthor>/…` paths inside the step's stdout log |
| `paper-auction-estimates`, `paper-crisis-robustness-japan` | `dependency <pkl> changed` | Inherits the row above | following the upstream step |
| `clean-bloomberg-fv-panel` | `output … changed` | Lock hash came from a worktree build; one of 1,344,816 rows differs | hashing the worktree copy, `pandas` diff |
| `paper-numerical-example` | `dependency Code/plot_style.py changed` | One docstring line (`c0b5e0d`) | hashing each `git show <rev>:Code/plot_style.py` against the lock |

A local rebuild then showed a second source of drift: identical code and data give different pickle bytes under the OpenBLAS and Accelerate NumPy wheels. Nothing records which environment produced a locked output.

## 2. Evidence `explain` returns today

`explain` for each of these steps returned `baseline.receipt: null` with either empty `diffs` or `history: "unavailable"`.

- **Output changes carry no diff row.** [inspect_baseline](../../skills/task-tree/scripts/_repro_acceptance.py#L276-L305) diffs only the lock's `deps`, so an `output changed` step reports `diffs: []`.
- **Dependency diffs need a local snapshot.** The unified diff is produced only from a snapshot in this machine's receipt ([source_snapshots](../../skills/task-tree/scripts/_repro_acceptance.py#L116-L134)). A dependency changed in a commit built on another machine gets `history: "unavailable"`, even though git holds the exact recorded version.
- **Receipts, run records, and logs are machine-local.** [receipt_path](../../skills/task-tree/scripts/_repro_acceptance.py#L112-L113) writes under the gitignored `.superra-repro/`. After a coauthor's build, `receipt`, `last_run`, and `log` are all `null` on every other machine.
- **Receipts record no builder or environment.** The run record holds `duration`, `ended_at`, `exit_code`, `forced`, `log`, and `outcome`, but no host, user, commit, package versions, or BLAS.

## 3. Proposal: input-level provenance in `explain`

Each changed node (dependency, output, spec, saved input) should report its recorded hash, its current hash, and where the current bytes come from.

### 3.1 Classify the current bytes against known states

| Provenance | Meaning | Lookup |
|---|---|---|
| `matches lock at <rev>` | An earlier or later committed build (someone else's, or a sync lag) | Hash search over `git log -p -- pytask.lock` |
| `matches accepted baseline` | A reviewed state | `repro-acceptance.json` |
| `matches worktree <path>` | A build that lives in another worktree | Hash the same logical path in `git worktree list` entries |
| `matches no recorded state` | A genuinely new or hand-edited file | Fallthrough |

In the case above, this one column would have explained four of the six stale steps directly.

### 3.2 Diff tracked dependencies from git history

Find the revision whose blob for the path hashes to the recorded SHA-256 by walking `git log --format=%H -- <path>`, then show `git diff <rev> -- <path>`. This replaces the snapshot requirement for any git-tracked dependency and would have shown the `plot_style.py` docstring change without a local receipt.

### 3.3 Record builder and environment in a shared record

Add a small, committed per-step record written at successful build: host, user, git commit, timestamp, interpreter, key package versions, and BLAS identity (`numpy.show_config`). Store it beside the lock, e.g. `repro-builds.json`, since pytask's lock format holds only hashes. `explain` then answers "who built the locked output, with what" on every machine.

### 3.4 One query per input

Agents need a direct input-level view, not the step-level summary:

```
superra repro explain '<task>#<step>' --inputs
node                                         role    recorded  current  provenance
Output/Treasury_auction_shocks/…weekly.pkl   output  c1e3…     ce98…    matches lock at 889f86a (coauthor, 10:57 +0100)
Code/plot_style.py                           dep     4ee6…     3256…    git a479d92 → c0b5e0d, 1 docstring line
```

`--json` carries the same rows. Also accept a unique bare step name ([_repro_state.py:798](../../skills/task-tree/scripts/_repro_state.py#L798) currently rejects it while naming the one valid selector).

## 4. Bug: an invalidated acceptance overrides a lock-fresh step

A stale acceptance leaves a step stale even when its bytes match the successful lock entry.

- **Sequence:**
  1. The committed lock records the coauthor's `robustness_estimates_weekly.pkl` (`b49c…`), but the local file is an older build (`8e80…`).
  2. `repro accept` records the local `8e80…`.
  3. The coauthor's `b49c…` then syncs in, matching the lock.
- **Result:** the step shows `stale — reviewed state changed` ([validate_record](../../skills/task-tree/scripts/_repro_acceptance.py#L214-L215)), and its consumer shows stale too. `repro revoke` restores both to `fresh — up to date`.
- **Expected:** when the acceptance no longer validates, status should fall back to the lock comparison, and the reason should name which state the bytes now match.

## 5. Related: check stamps look identical to never-run checks

Check steps write their stamp to gitignored `.superra-repro/stamps/`, while their lock entry is committed. On any other machine, a check that passed at the locked inputs reports `missing — output .superra-repro/stamps/<check>.stamp is missing`, the same message as a check that never ran. Status should separate "passed elsewhere at these inputs (lock)" from "never run". Whether that state counts as fresh is a policy choice, since acceptance deliberately supplies no check stamp.

## Out of scope

- **Sync lag and unsynced worktree outputs** are Dropbox and workflow issues, not graph design. §3.1 only makes them visible.
- **Cross-machine numerical tolerance** (a custom fingerprint function per output) is a separate feature. §3.3's environment record is the diagnostic prerequisite for it.
