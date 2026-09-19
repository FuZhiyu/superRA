---
name: reproducibility
description: Register and verify task-declared reproduction graphs. Use when planning, producing, changing, or reviewing retained results that depend on executable steps, adopting reproduction, selecting protection checks, or judging reruns or evidence-backed reuse.
---

# Reproducibility

Section schema, config keys, and validation findings: `skills/task-tree/references/task-file-contract.md` §Reproduction Section. Command surface: `superra repro --help`.

## References

| Reference | Load when |
|---|---|
| `references/graph-authoring.md` | Declaring or changing steps, or presenting a graph for review. |
| [rerun-model.md](references/rerun-model.md) | Predicting reruns, diagnosing state, or reviewing stale results for acceptance. |
| `references/protect-and-completion.md` | At `Stage: protection`, or at the IMPLEMENT completion gate. |
| [pilot-acceptance.md](references/pilot-acceptance.md) | Adopting reproduction or changing its discovery/rerun mechanism. |

## What Gets a Step

**Register executable support before recording retained results.** Reuse existing registered producers/checks or declare them in their owning tasks, including unchanged scripts used for new findings. Cover the producer chain to the agreed external-input boundary; update declarations with result, input, or ownership changes in the same commit.

- **A maintained producer of a committed exhibit or a canonical result** — the script behind a table, figure, estimate, or dataset that the manuscript, the slides, or another task's `## Results` cites.
- **A task companion the results cite** — a script under a task's `attachments/` that produced a finding in that task's `## Results`.
- **A drift test or validation script** — as a `kind: check` step over the artifacts it reads; `[BLOCKING]` for drift tests protecting registered outs.

Leave unregistered: exploration whose findings are not retained, anything regenerated per machine, and the boundary inputs a project receives rather than builds (`references/graph-authoring.md`).

## Step Lifecycle

- **Retire a step only when its result or check is no longer retained and no retained consumer reads its output.**
- **Moving or merging tasks:** move surviving steps with their names unchanged, so successful evidence carries over.
- **Deleting or archiving an owner:** first move needed producers to a surviving task, or agree a frozen external-input boundary with the researcher.

## Build and Status

**Verify the claimed result's scope**, including its selected checks, using the same targets:

```bash
superra repro build <task> '<check-task>#<check-step>'
superra repro status <task> '<check-task>#<check-step>'
```

A task target includes its own steps and descendant tasks; `task#step` selects one step. Multiple targets select their union. A check already included by the task target needs no separate argument. An empty selection verifies no result.

**Use saved inputs outside the selection.** Existing files are usable regardless of upstream freshness or successful-build evidence; missing inputs block. Report their provenance without certifying their producers. Add `--upstream` to build/status for the producer chain.

**Force within scope:** `--force` reruns every selected step; combine with `--upstream` for a full-chain rerun. For every registered step, use `build . --force`. Preview with `--dry-run`.

**State what the evidence covers in `## Results`:** verified targets, boundary inputs, and check outcomes. Freshness covers successful execution or [reviewed acceptance](references/rerun-model.md#reviewed-acceptance); distinguish executed steps and checks from accepted results. End-to-end reproduction requires rebuilding the claimed pipeline from its agreed boundary. Commit changed execution or acceptance records with the work.

A step still stale after its own successful build is a diagnosis, not a rerun: `superra repro explain <step>` and `references/rerun-model.md`.

## Environment Changes

Keep project and lockfiles versioned but outside graph dependencies by default. Compare their Git diffs against the last successful run when judging reruns or investigating reproduction failures; choose affected producers and checks from the changes. A fresh graph does not establish that an environment change is harmless.

## Gates

- `[BLOCKING]` Retained results satisfy §What Gets a Step, including executable findings recorded without a separate output file.
- `[BLOCKING]` Before claiming a result reproduces, its scoped build succeeds and every step reported by the matching status is `fresh`.
- `[ADVISORY]` A step whose script reads a few named files declares those files, not their directory.
