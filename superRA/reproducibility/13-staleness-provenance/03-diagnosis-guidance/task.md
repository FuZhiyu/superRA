---
title: "Teach Agents to Act on Provenance, and Verify They Do"
status: approved
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
      - skills/task-tree/scripts/_apply_patch.py
      - skills/task-tree/scripts/_artifacts.py
      - skills/task-tree/scripts/_comments.py
      - skills/task-tree/scripts/_repro.py
      - skills/task-tree/scripts/_repro_acceptance.py
      - skills/task-tree/scripts/_repro_builds.py
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
```

## Results

`diagnosing.md` §Read what explain names now maps each `explain` row to one action, and a companion script materializes the 01 two-clone scenario for the fresh-agent evaluation.

### Skill edit

- **[diagnosing.md §Read what explain names](../../../../skills/reproducibility/references/diagnosing.md#read-what-explain-names)** is one `Row | Act` table over the shipped causes and status reasons ([commands.md §Explain](../../../../skills/task-tree/references/commands.md#explain)):
  - `input-changed` on a tracked file or the step definition → read the pointer's diff, apply the stale rule; narrow an over-broad directory dep.
  - `other-build` with the current side an earlier commit behind HEAD → sync lag: wait for the sync, or rebuild when outputs are not shared; never accept the older bytes.
  - `other-build` with the current side off HEAD's history → rebuild or wait for the branch to merge.
  - `other-build` with any other current side (`built here`, `reviewed`, `git <rev>`, in HEAD's lock) → rebuild; accept only reviewed bytes.
  - `unknown-output` → rebuild; fix determinism when repeated builds disagree.
  - `env: differs` → report the difference; a rebuild here may not reproduce the recorded bytes.
  - a check `passed at these inputs in lock <rev>; not run here` → run it here.
  - `external` on a generated file → unchanged from the old table.
- **The intro** names `explain <target>` as the replacement for manual `git log -S` / `shasum` / `stat` and points at commands.md for format instead of restating it.
- **[rerun-or-accept.md](../../../../skills/reproducibility/references/rerun-or-accept.md)** points to that table before the stale rule.
- **Deviations:** dropped rows the resolver or pointers now carry — the produced-input and `upstream` cases (the `explain` pointer already names the producer) and "a file you did not know the step read" (explanation, no action).

### Evaluation scenario

[two_clone_scenario.py](attachments/two_clone_scenario.py) `<empty-dir>` builds `coauthor/` and `you/` clones and prints the `you/` path; each clone's `superRA/superra` shim runs this checkout's CLI. `--check` asserts the causes below and the `earlier commit, N behind HEAD` fact on the sync-lag rows; it is registered as `diagnosis-scenario-check`, which declares the same task-tree module set as `provenance-explain-check`.

Grading key for `you/` (`explain .` groups all six non-fresh steps in one call):

| Step | Row(s) | Correct diagnosis and action |
|---|---|---|
| `est` | `other-build`; current = lock "Build all results", earlier commit 5 behind HEAD | Sync lag of the coauthor's rebuild. Do not accept; wait for the sync, or rebuild (the scenario shares no outputs). |
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
