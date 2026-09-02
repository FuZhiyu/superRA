---
name: reproducibility
description: Reproduction-graph discipline for superRA task trees — when a producer needs a registered step in a task's `## Reproduction` section, which tier it belongs to, how to rebuild and evidence it with `superra repro`, and how to present a graph for review. Use whenever a task produces, changes, or cites a maintained output, before marking a canon task implemented, when configuring reproduction at Protect, and when a rerun or a stale state surprises you.
---

# Reproducibility

Every maintained output is rebuilt by a registered step, and the graph is current before a result is claimed.

Section schema, config keys, and validation findings: `skills/task-tree/references/task-file-contract.md` §Reproduction Section. Command surface: `superra repro --help`.

## References

| Reference | Load when |
|---|---|
| `references/graph-authoring.md` | Declaring or changing steps, or presenting a graph for review. |
| `references/rerun-model.md` | Predicting what a change reruns, or diagnosing a state you did not expect. |
| `references/protect-and-completion.md` | At `Stage: protection`, or at the IMPLEMENT completion gate. |

## What Gets a Step

- **A maintained producer of a committed exhibit or a canonical result** — the script behind a table, figure, estimate, or dataset that the manuscript, the slides, or another task's `## Results` cites.
- **A task companion the results cite** — a script under a task's `attachments/` that produced a number in that task's `## Results`, at `tier: local`.
- **A drift test or validation script** — as a `kind: check` step over the artifacts it reads.

Leave unregistered: exploration that produced no cited number, anything regenerated per machine, and the boundary inputs a project receives rather than builds (`references/graph-authoring.md`).

## Tiers

`canon` is an opt-in, not a measure of importance. A producer stays `local` while its result is in flight; tiering happens at Protect (`references/protect-and-completion.md`).

```bash
superra repro tier <task-path> canon
```

## Build and Status

`superra repro build` rebuilds the stale part of the canon tier — the default tier for `build` and `status`. A clean `superra repro status` afterwards is the evidence that a result reproduces; cite that state in `## Results`. Commit the `pytask.lock` the build updated together with the work.

A step still stale after its own successful build is a diagnosis, not a rerun: `superra repro explain <step>` and `references/rerun-model.md`.

## Gates

- `[BLOCKING]` Every out a task's `## Results` cites is produced by a registered step or declared as an external input.
- `[BLOCKING]` `superra repro status --tier canon` is clean before `status: implemented` on a canon task.
- `[BLOCKING]` Environment lockfiles are declared as `env_deps`, and every drift test protecting a registered out is a `kind: check` step.
- `[ADVISORY]` A step whose script reads a few named files declares those files, not their directory.
