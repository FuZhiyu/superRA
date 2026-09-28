---
title: "Workflow Call Sites Apply the Reproduction Gates Consistently"
status: not-started
depends_on:
  - 07-instruction-rewrite
---

## Objective

Every workflow and role call site that touches reproduction points to the owning skill, applies its gates in the right order, and uses 07's terms, so an agent loading only what the manifest names acts correctly in both interactive and autonomous mode.

- **The completion gate applies the stale rule before building.** [completion.md:18](../../../../skills/superimplement/references/completion.md#L18), [integrate.md:9](../../../../skills/superintegrate/references/integrate.md#L9), and [finish.md:39](../../../../skills/superintegrate/references/finish.md#L39) build `--upstream` first, running costly stale producers the stale rule says to ask about. Order: status, the stale rule with `--dry-run` cost, then build; add the costly-rerun ask to `main-agent.md` §Proceeding and Pausing; one owner holds the command pair and the others point to it.
- **Planner seeding produces valid steps.** [build-and-review.md:13](../../../../skills/superplan/references/build-and-review.md#L13) seeds outs-only steps; a step without `cmd` is an `[ERROR]` that fails `task check`, `task frontier`, and `task create`. Reconcile with the implementer ownership at [task-file-contract.md:29](../../../../skills/task-tree/references/task-file-contract.md#L29).
- **Trees with no reproduction steps pass completion.** `repro status` and `build` exit 1 with "selects no steps"; the condition and fallback are stated once, in `protect-and-completion.md`, instead of three wordings ([main-agent.md:10](../../../../skills/using-superra/references/main-agent.md#L10), `using-superra/SKILL.md` §Task Interface, finish.md:39).
- **The manifest carries the load trigger.** A Domain row in the `using-superra` Skill-Load Manifest (mirrored in CLAUDE.md §Agent Load Surface and the load contract); interactive self-review ([interactive-mode.md:17](../../../../skills/using-superra/references/interactive-mode.md#L17)) applies every loaded skill's gates; [implement-task:50](../../../../skills/implement-task/SKILL.md#L50) and [review-task:28](../../../../skills/review-task/SKILL.md#L28) become pointers.
- **Reviewers verify evidence.** A review item covers all reproduction gates, including stale-step resolution, and names the evidence: `status <targets> --upstream` output and the committed `repro-lock.json` and acceptance records.
- **Parallel work and Sync handle the root records.** [parallel-dispatch.md:15](../../../../skills/agent-orchestration/references/parallel-dispatch.md#L15) promises branches that "typically merge cleanly"; `semantic-merge` gets resolution guidance for `repro-lock.json` ([01](../01-engine-freshness/task.md)) and the acceptance format [02](../02-portable-records/task.md) settles; the implement-task commit guidance names the records.
- **Protect records its reproduction decisions.** The researcher template and commit body in `superintegrate/references/protect.md` include completion targets, selected checks, and the input boundary; completion targets get a durable home in the task tree, with a defined first-cycle default.
- **One escalation status** for a costly stale step a subagent cannot resolve.
- **One name per concept:** kept / key / retained / maintained / canonical result, and "final deliverable tasks" versus "completion targets"; "canon" is gone.
- **The harness contract is current:** `load_contract.json` anchors (off by two since `3a548e98`; LC008 now lands on the planning-review row), LC008 citing routing rather than model text, `ALL_STAGE_SKILLS` not counting a conditional `reproducibility` load at `Stage: implementation` as an over-load, and a live run of the protection row.

Validation: a realistic harness session walks the three scenarios in [wiring.md](../attachments/wiring.md) (a new regression table; a shared-helper edit fanning out to a costly estimation from a subagent; the completion gate and Protect with a check step), and the harness-instruction-following tests pass.

Owning task: [unified-dependency-workflow](../../07-workflow-integration/unified-dependency-workflow/task.md).

## Details

Prose fixes from [wiring.md](../attachments/wiring.md):

- `completion.md` §Verify Pipeline and Reproducibility is still headed "Pipeline", and `econ-data-analysis/SKILL.md:151` cites it.
- `integrate.md:9` "among them" has no clear referent.
- `CATEGORIES.md:52` states the trigger more narrowly than `using-superra`.
- `changing-the-tree.md:42` points to §What earns a step for moves and removals, which live in §Step lifecycle.
- `result-protection/SKILL.md:8` counts "a registered step with its committed lock" as protection; only a check step guards values.
- `completion.md:19` "not ad-hoc REPL state" sits against accepting interactive runs.
- `main-agent.md:10` routes session-start status through the stale rule, implying builds before the first response.
