---
title: "Teach Agents to Act on Provenance, and Verify They Do"
status: implemented
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
- Fresh-agent evaluation: pending, run by the orchestrator.
