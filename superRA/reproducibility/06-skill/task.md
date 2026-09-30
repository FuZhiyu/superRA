---
title: "The `reproducibility` Utility Skill"
status: approved
depends_on: [01-section-contract]
---

## Objective

Own `skills/reproducibility/`, the discipline agents follow to register, build, diagnose, and review a reproduction graph. Mechanics stay in `task-tree` (contract, CLI, dashboard); the skill points to them and teaches judgment, loaded by the moment the agent is in. Every file passes the [CLAUDE.md](../../../CLAUDE.md) three-test gate and the terse style.

The skill teaches these researcher decisions:

- **Registration follows placement.** Code retained in the codebase or a task's `attachments/` is registered, drift tests and validation scripts included; exploration in scratch is not. A task companion feeds only its own task; once anything else consumes it, it is promoted to the project's conventional path.
- **Retained results come from `repro build`,** or from `accept` when an expensive result was already produced from the same committed code.
- **A step that is not fresh is resolved by role, then cost:** leave a task-local step stale and say so; run a cheap significant step (about a minute is a guideline, not a cap); ask the researcher about a costly one with a build / accept / leave recommendation, a subagent through its return. A diff that proves no result can move is accepted on the agent's own authority with the reason recorded.
- **Significance is inferred from graph facts,** not marked: a step is task-local when its producer sits under `attachments/` and nothing outside the task reads its outs.
- **Graph design is script design.** One step per script by default; split scripts at saved artifacts and helper modules by consumer set to keep reruns selective; never drop a true dependency to save a rerun.
- **Retire a step only when its result or check is no longer retained and no retained consumer reads its outs;** moved or merged tasks keep step names.

## Results

[SKILL.md](../../../skills/reproducibility/SKILL.md) defines the model (step, producer, saved and external input, `fresh`), target selection, the core commands, and the gate for recording a result, then routes each other moment to one reference:

| Reference | Moment | Carries |
|---|---|---|
| [designing-the-graph.md](../../../skills/reproducibility/references/designing-the-graph.md) | registering retained code; planning, moving, or retiring steps | what earns a step, the step unit, the dependency ladder, declaring from the script, step lifecycle, graph review |
| [rerun-or-accept.md](../../../skills/reproducibility/references/rerun-or-accept.md) | a step is not `fresh` | the stale rule, the cannot-move-a-result exception, the accept recipe, what acceptance never covers |
| [diagnosing.md](../../../skills/reproducibility/references/diagnosing.md) | an unexpected state | one action per `explain` row, environment changes |
| [protect-and-completion.md](../../../skills/reproducibility/references/protect-and-completion.md) | the completion gate, `Stage: protection` | `status .`, the stale rule, `status .` again; the external-inputs decision at Protect |
| [adoption.md](../../../skills/reproducibility/references/adoption.md) | first use in a project | a whole existing project or a one-task trial, then the first build by slices |

### Each rule lives once

- **Gates sit in the reference loaded when they apply:** registration in §What earns a step, the stale rule at the top of `rerun-or-accept.md`, the claim gate in SKILL.md §Recording a Result, the completion gate in `protect-and-completion.md`.
- **Flags and record semantics stay in the mechanics docs.** Subagents are not sent into `commands.md`; SKILL.md names `superra repro <command> --help`, and the contract's §What invalidates a step carries the rerun rules. Record formats, lock history, and `explain` source mechanics live in [internals.md §Reproduction records](../../../skills/task-tree/references/internals.md#reproduction-records), outside every agent load.
- **One word per concept.** SKILL.md defines producer, saved input, and external input; "completion targets", "canonical result", and "boundary input" are gone from agent-facing text.

### Lessons from real pipelines

- **BondElasticity:** a figure declares a deterministic `*_data.csv` beside the PNG and drift checks read the CSV, since a clean-room rerun left all seven PNGs byte-different with identical numbers. One interpreter pin lives in the `runners` template. Frozen upstream artifacts stay external inputs.
- **[TreasuryGIV](../08-pilot-treasurygiv/task.md):** an out is the artifact a consumer reads, never a write stamp, since a restamped directory out restaled 36 downstream steps. A drift pin declares the published root, not a rehearsal mirror. Each step pays its own interpreter start-up, and enumerating outs from disk picks up leftovers.

### Behavior verified in live sessions

- **Diagnosis from `explain` alone.** A fresh Sonnet agent given a two-clone scenario with six non-fresh steps chose the right action for every step in three `repro` calls and 11 commands, against the ~20-call manual baseline. It never accepted sync-lag outputs and ran no manual `git log -S`, `shasum`, or `stat`. Both frictions it hit are fixed: `status` now points at `explain`, and a unique bare step name works in every command.
- **Registration and the stale rule.** Fresh Sonnet implementers on scratch projects registered and built new steps, read the claim gate before recording a result, accepted a comment-only change under the exception with the reason recorded, and escalated a costly rerun with a recommendation instead of running it.
- **Dependency separation.** On a three-step pipeline, a plotting-helper edit reran only plotting, changed estimates reran all three steps, and a comment-only estimation edit reran estimation alone.
