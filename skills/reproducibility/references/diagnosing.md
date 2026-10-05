# Diagnosing an Unexpected State

What invalidates a step: [task-file-contract.md §What invalidates a step](../../task-tree/references/task-file-contract.md#what-invalidates-a-step).

## Common surprises

- **`touch` reruns nothing;** force a rerun with `build --force`.
- **An `include` the loader reports as unresolved, or a helper in another language:** declare it as a dep.
- **Repeated builds that disagree:** make the producer deterministic ([volatile bytes](designing-the-graph.md#declare-from-the-script-not-from-memory)).
- **A downstream step stale despite an accepted producer:** acceptance stops staleness from propagating, but a step whose own inputs changed is still stale.
- **A declaration or input edited while its step ran:** retry that step.

## Read what explain names

`superra repro explain <target>` names where each changed hash came from. Act on its rows instead of reconstructing them with `git log -S`, `shasum`, or `stat`. For planning, `superra repro impact <path...>` predicts which steps go stale, not whether their output values change.

| Row | Act |
|---|---|
| `input-changed` on a tracked file or the step definition | Read the diff from the command the row prints, then apply [the stale rule](rerun-or-accept.md#the-stale-rule). A changed file under a declared directory that the script does not read: narrow the declaration. |
| `other-build`, current side an earlier commit behind HEAD | Sync lag: the recorded build ran elsewhere and its outputs have not arrived. Wait for the sync, or rebuild when outputs do not sync between machines, then recheck `status`. Never accept the older bytes. |
| `other-build`, current side off HEAD's history | A build from another branch: rebuild here, or wait for that branch to merge. |
| `other-build`, any other current side | Rebuild; accept only current bytes you have reviewed. |
| `unknown-output` | Rebuild. |
| `env: differs` on any row | A rebuild here may not reproduce the recorded bytes; name the difference when you report. |
| `passed at these inputs in lock <rev> on <platform>; not run here` | Fresh on the lock's record. Run the check here before reporting its result from this machine. |

## Environment changes

Keep language environment files (`Project.toml`/`Manifest.toml`, `uv.lock`) versioned but outside graph dependencies by default. A fresh graph therefore says nothing about whether an environment change was harmless. When judging a rerun or investigating a reproduction failure, compare their Git diffs against the last successful run, and pick the affected producers and checks from what changed.
