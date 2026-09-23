---
title: "Teach Agents to Act on Provenance, and Verify They Do"
status: revise
depends_on:
  - 01-provenance-explain
  - 02-build-record
---

## Objective

Agents resolve a stale step from `explain` output alone, and the claim is verified in a real harness session.

- **Skill.** [diagnosing.md §Read what explain names](../../../../skills/reproducibility/references/diagnosing.md#read-what-explain-names) becomes one table mapping each cause from [01](../01-provenance-explain/task.md) to the action it calls for; `rerun-or-accept.md` points there rather than restating it. Edits pass the [CLAUDE.md §Teach the Protocol gate](../../../../CLAUDE.md#teach-the-protocol-dont-prescribe-each-action).
- **Validation:** a fresh subagent given only "these steps are stale; decide what to do" on the 01 fixture reaches the correct diagnosis for every step in at most three `repro` calls, runs no manual `git log -S`, `shasum`, or `stat`, and does not accept the sync-lag steps. Record the transcript's call count against the ~20-call baseline in `## Results`.

## Details

- The current table in `diagnosing.md` names symptoms ("an out you did not edit") and investigation steps that the resolver now performs; most rows shrink to an action.
- Load `skill-creator` and `superRA:reproducibility` before editing.

## Reproduction

```yaml
steps:
  - name: diagnosis-scenario-check
    kind: check
    cmd: "sh -c 'python3 superRA/reproducibility/13-staleness-provenance/03-diagnosis-guidance/attachments/two_clone_scenario.py \"$(mktemp -d)/scenario\" --check'"
    deps:
      - superRA/reproducibility/13-staleness-provenance/03-diagnosis-guidance/attachments/two_clone_scenario.py
      - skills/task-tree/scripts/cli.py
      - skills/task-tree/scripts/repro_run.py
      - skills/task-tree/scripts/_repro_state.py
      - skills/task-tree/scripts/_repro_provenance.py
      - skills/task-tree/scripts/_repro_builds.py
```

## Results

`diagnosing.md` §Read what explain names now maps each `explain` row to one action, and a companion script materializes the 01 two-clone scenario for the fresh-agent evaluation.

### Skill edit

- **[diagnosing.md §Read what explain names](../../../../skills/reproducibility/references/diagnosing.md#read-what-explain-names)** is one `Row | Act` table over the shipped causes and status reasons ([commands.md §Explain](../../../../skills/task-tree/references/commands.md#explain)):
  - `input-changed` on a tracked file or the step definition → read the pointer's diff, apply the stale rule; narrow an over-broad directory dep.
  - `other-build` with the current side an earlier commit behind HEAD → sync lag: wait for the sync and recheck; never accept the older bytes.
  - `other-build` with the current side off HEAD's history → rebuild or wait for the branch to merge.
  - `unknown-output` → rebuild; fix determinism when repeated builds disagree.
  - `env: differs` → report the difference; a rebuild here may not reproduce the recorded bytes.
  - a check `passed at these inputs in lock <rev>; not run here` → run it here.
  - `external` on a generated file → unchanged from the old table.
- **The intro** names `explain <target>` as the replacement for manual `git log -S` / `shasum` / `stat` and points at commands.md for format instead of restating it.
- **[rerun-or-accept.md §Preview](../../../../skills/reproducibility/references/rerun-or-accept.md#preview-the-cost-and-the-cause)** points to that table before the stale rule.
- **Deviations:** dropped rows the resolver or pointers now carry — the produced-input and `upstream` cases (the `explain` pointer already names the producer) and "a file you did not know the step read" (explanation, no action).

### Evaluation scenario

[two_clone_scenario.py](attachments/two_clone_scenario.py) `<empty-dir>` builds `coauthor/` and `you/` clones and prints the `you/` path; each clone's `superRA/superra` shim runs this checkout's CLI. `--check` asserts the causes below, registered as `diagnosis-scenario-check`.

Grading key for `you/` (`explain .` groups all six non-fresh steps in one call):

| Step | Row(s) | Correct diagnosis and action |
|---|---|---|
| `est` | `other-build`; current = lock "Build all results", earlier commit 5 behind HEAD | Sync lag of the coauthor's rebuild. Do not accept; wait for the sync (a local rebuild is tolerable, not preferred). |
| `paper` | `input-changed` on `${OUT}/est.txt` + own `other-build`, same revisions | Same sync lag, downstream of `est`. Do not accept. |
| `panel` | `other-build`; recorded = lock from the merged `panel-fix` branch, in HEAD's lock | Sync lag of a build merged into main, not a branch conflict. Do not accept. |
| `figure` | `input-changed` on `Code/style.py`, diff is one docstring word | Cannot move the result: accept with the reason recorded (or rerun; it is cheap). |
| `summary` | `unknown-output`, current matches no recorded build | A local hand edit: rebuild; never accept. |
| `check-robust` | status `missing`: passed at these inputs in the coauthor's lock | Run the check here; acceptance cannot supply its stamp. |
| `robust` | fresh (synced) | Nothing to do. |

Pass bar: every step above diagnosed correctly, at most three `repro` calls, no manual `git log -S`, `shasum`, or `stat`, and no `accept` on `est`, `paper`, or `panel`.

### Validation

- `diagnosis-scenario-check` passes; `explain .` on the materialized `you/` clone prints each row above.
- **Fresh-agent evaluation (Sonnet, prompt "several steps are stale; decide what to do", 2026-09-23): passed on decisions, with two CLI frictions.**
  - All six non-fresh steps got a correct action: `figure` accepted with a docstring-only reason; `summary` rebuilt over the hand edit; `check-robust` run; `est`, `panel`, `paper` rebuilt, never accepted. Rebuilding the sync-lag steps is the key's tolerated option: the scratch scenario has no Dropbox to wait on, and every step is a sub-second `echo`.
  - 11 shell commands in total against the ~20-call baseline; 3 were `repro` diagnosis calls (one failed `status`, one `status .`, one shell loop of six per-step `explain`s). No `git log -S`, `shasum`, or `stat`. Three commands read scripts, task files, and `git log`, one of them to confirm `figure.sh` never reads `Code/style.py`.
  - **Friction 1:** `status` never points at `explain .`, so the agent explained each step separately instead of reading the grouped view.
  - **Friction 2:** `explain` accepts bare step names but `build` rejects them; the agent copied bare names into `build`, which failed once before it used the qualified form the error named.

## Review Notes
Tier: quick. Focus: the CLAUDE.md §Teach the Protocol gate, applied line by line to the `skills/reproducibility` diff; whether the table rows match the shipped causes and facts; the scenario script and its registered check. The skill diff passes the gate. `diagnosis-scenario-check` passes, and `explain .` on the materialized `you/` clone prints every row in the grading key.

1. **[BLOCKING] `diagnosis-scenario-check` does not declare most of the code it runs.** The check runs the task-tree CLI end to end, including `build` and `explain`. Its deps list only `cli.py`, `repro_run.py`, `_repro_state.py`, `_repro_provenance.py`, and `_repro_builds.py`. The modules those import are missing, among them `_repro.py`, `_repro_acceptance.py`, `_repro_hooks.py`, and `_repro_scope.py`, so an edit to any of them leaves the check fresh. [designing-the-graph.md §Declare every true read](../../../../skills/reproducibility/references/designing-the-graph.md) treats a missing dep as a silently wrong result. Fix: declare the same module set that `provenance-explain-check` and `build-record-check` declare.
2. **[ADVISORY] Some `other-build` rows match no row in the table.** [diagnosing.md](../../../../skills/reproducibility/references/diagnosing.md#read-what-explain-names) keys `other-build` only on the two lock relations, "earlier commit behind HEAD" and "off HEAD's history". `explain` also prints `other-build` rows whose current side is `built here …`, `reviewed …`, `git <rev>` (a tracked output), or `in HEAD's lock`, and those have no row. Add one fallback row for any other current source.
3. **[ADVISORY] The sync-lag row assumes a sync exists.** "Wait for the sync" has no end when outputs are not shared, for example with no Dropbox and a single machine. Add "or rebuild when outputs are not shared", which is the option the fresh agent took.
4. **[ADVISORY] The check does not assert the relation facts the table keys on.** [two_clone_scenario.py `check`](attachments/two_clone_scenario.py) asserts only the set of causes per step. Asserting `earlier commit, N behind HEAD` on `est`, `paper`, and `panel` would catch a wording change that silently breaks the table mapping.
