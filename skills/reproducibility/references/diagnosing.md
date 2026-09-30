# Diagnosing an Unexpected State

What invalidates a step: [task-file-contract.md §What invalidates a step](../../task-tree/references/task-file-contract.md#what-invalidates-a-step).

## Act on the rerun rules

- **`touch` reruns nothing;** force a rerun with `build --force`.
- **An `include` the loader reports as unresolved, or a helper in another language:** declare it as a dep.
- **Repeated builds that disagree:** make the producer deterministic ([volatile bytes](designing-the-graph.md#declare-from-the-script-not-from-memory)).
- **An accepted step stops staleness propagating downstream;** a downstream step with its own changed inputs is still stale.
- **A declaration or input edited while its step ran:** retry that step.

## Read what explain names

`superra repro explain <target>` resolves where each changed hash came from; act on its rows instead of reconstructing them with `git log -S`, `shasum`, or `stat`. `superra repro impact <path...>` predicts invalidation, not changed output values.

| Row | Act |
|---|---|
| `input-changed` on a tracked file or the step definition | Read the diff the pointer prints and apply [the stale rule](rerun-or-accept.md#the-stale-rule). A changed file the script does not read, under a declared directory: narrow the declaration. |
| `other-build`, current side an earlier commit behind HEAD | Sync lag: the recorded build ran elsewhere and its outputs have not arrived. Wait for the sync, or rebuild when outputs do not sync between machines, then recheck `status`; never accept the older bytes. |
| `other-build`, current side off HEAD's history | A build from another branch: rebuild here, or wait for that branch to merge. |
| `other-build`, any other current side | Rebuild; accept only current bytes you have reviewed. |
| `unknown-output` | Rebuild. |
| `env: differs` on any row | A rebuild here may not reproduce the recorded bytes; name the difference when you report. |
| `passed at these inputs in lock <rev> on <platform>; not run here` | Fresh on the lock's record. Run the check here before reporting its result from this machine. |

## Environment changes

Keep language environment files (`Project.toml`/`Manifest.toml`, `uv.lock`) versioned but outside graph dependencies by default. When judging a rerun or investigating a reproduction failure, compare their Git diffs against the last successful run and choose the affected producers and checks from what changed. A fresh graph does not establish that an environment change was harmless.
