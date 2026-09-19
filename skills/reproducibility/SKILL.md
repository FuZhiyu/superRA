---
name: reproducibility
description: Register and verify task-declared reproduction graphs. Use when producing or citing maintained outputs, adopting reproduction with a bounded pilot, selecting protection checks, or judging reruns or evidence-backed reuse after code, data, or environment changes.
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

- **A maintained producer of a committed exhibit or a canonical result** — the script behind a table, figure, estimate, or dataset that the manuscript, the slides, or another task's `## Results` cites.
- **A task companion the results cite** — a script under a task's `attachments/` that produced a number in that task's `## Results`, at `tier: on-demand`.
- **A drift test or validation script** — as a `kind: check` step over the artifacts it reads; `[BLOCKING]` for drift tests protecting registered outs.

Leave unregistered: exploration that produced no cited number, anything regenerated per machine, and the boundary inputs a project receives rather than builds (`references/graph-authoring.md`).

## Tiers

- **`required`** — selected by build/status without targets and by the completion gate; chosen at Protect (`references/protect-and-completion.md`).
- **`on-demand`** (default) — built by explicit target; may remain stale between uses.

Legacy `canon` / `local` declarations and arguments remain accepted aliases. Use the new names when authoring.

## Build and Status

**Verify the claimed result's scope**, including its selected checks, using the same targets:

```bash
superra repro build <task-or-step> <selected-check>
superra repro status <task-or-step> <selected-check>
```

A task target includes its own steps and descendant tasks; producer ancestors are included across tiers. A check already included by the task target needs no separate argument. An empty selection verifies no result.

**Choose the forced scope:** `build <target> --force` reruns the selected targets, rebuilding ancestors only when stale or missing; `--force-all` reruns their entire producer chain. For every registered step, use `build --tier all --force-all`. Preview either mode with `--dry-run`.

**State what the evidence covers in `## Results`:** verified targets, boundary inputs, and check outcomes. Freshness covers successful execution or [reviewed acceptance](references/rerun-model.md#reviewed-acceptance); distinguish executed steps and checks from accepted results. End-to-end reproduction requires rebuilding the claimed pipeline from its agreed boundary. Commit changed execution or acceptance records with the work.

A step still stale after its own successful build is a diagnosis, not a rerun: `superra repro explain <step>` and `references/rerun-model.md`.

## Environment Changes

Keep project and lockfiles versioned but outside graph dependencies by default. Compare their Git diffs against the last successful run when judging reruns or investigating reproduction failures; choose affected producers and checks from the changes. A fresh graph does not establish that an environment change is harmless.

## Gates

- `[BLOCKING]` Every out a task's `## Results` cites is produced by a registered step or declared as an external input.
- `[BLOCKING]` Before claiming a result reproduces, its scoped build succeeds and every step reported by the matching status is `fresh`.
- `[ADVISORY]` A step whose script reads a few named files declares those files, not their directory.
