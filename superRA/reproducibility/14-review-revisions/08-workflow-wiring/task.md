---
title: "Workflow Call Sites Apply the Reproduction Gates Consistently"
status: not-started
depends_on:
  - 07-instruction-rewrite
---

## Objective

Every workflow step that touches reproduction points to the reproducibility skill for the rule, applies its gates in the right order, and uses 07's terms. An agent loading only what the Skill-Load Manifest names then acts correctly in both interactive and autonomous mode. The steps in scope are planning, the IMPLEMENT completion check, INTEGRATE, and the implementer and reviewer roles.

### The completion check asks before costly reruns

- **Status first, then the stale rule, then build.** [completion.md:18](../../../../skills/superimplement/references/completion.md#L18), [integrate.md:9](../../../../skills/superintegrate/references/integrate.md#L9), and [finish.md:39](../../../../skills/superintegrate/references/finish.md#L39) run `repro build <targets> --upstream` first, which executes every stale producer, including costly ones the stale rule says to ask the researcher about. In autonomous mode, a subagent correctly escalates a costly rerun, and the completion check then runs it anyway.
  - Order the check: `status`; the stale rule, with cost from `build --dry-run`'s recorded durations; then `build`.
  - Add the costly-rerun question to `main-agent.md` §Proceeding and Pausing.
  - One file holds the commands; the other two point to it.
- **Trees with no reproduction steps pass.** `repro status` and `build` exit 1 with "selects no steps", and `completion.md` treats that as a failure, so a theory or prose-only tree cannot finish. State the condition and its fallback once, in `protect-and-completion.md`. Today it is worded three ways: [main-agent.md:10](../../../../skills/using-superra/references/main-agent.md#L10), `using-superra/SKILL.md` §Task Interface, and `finish.md:39`.

### Planning produces valid steps

- [build-and-review.md:13](../../../../skills/superplan/references/build-and-review.md#L13) tells the planner to seed each producing task's `## Reproduction` section with its outputs only. A step without `cmd` is an error, so `task check`, `task frontier`, and `task create` then fail. Either seed name, command, and outputs, or keep the planned artifacts in `## Details` for the implementer; reconcile with [task-file-contract.md:29](../../../../skills/task-tree/references/task-file-contract.md#L29), which makes the section implementer-owned.

### Every role loads and applies the gates

- **The manifest carries the load trigger.** The trigger to load `reproducibility` is a prose sentence in `using-superra/SKILL.md` §Task Interface; the Skill-Load Manifest, CLAUDE.md §Agent Load Surface, and the harness load contract do not list it. Add a Domain row: load when a task produces, changes, or reviews a result from executable code.
- **Interactive self-review applies the gates.** In the default interactive mode, [interactive-mode.md:17](../../../../skills/using-superra/references/interactive-mode.md#L17) self-reviews against "active domain skills" only, so the reproducibility gates are skipped.
- **Role skills point instead of restating.** [implement-task:50](../../../../skills/implement-task/SKILL.md#L50) and [review-task:28](../../../../skills/review-task/SKILL.md#L28) paraphrase the gates.
- **Reviewers check evidence.** `review-task` drops the stale-step gate and names no evidence. A review item covers every gate and names the evidence: `status <targets> --upstream` output and the committed `repro-lock.json` and acceptance records.
- **One escalation status** for a costly stale step a subagent cannot resolve. Today it could be BLOCKED or DONE_WITH_CONCERNS.

### Parallel work, Sync, and Protect handle the records

- **Merges of the committed records have guidance.** [parallel-dispatch.md:15](../../../../skills/agent-orchestration/references/parallel-dispatch.md#L15) promises parallel branches "typically merge cleanly", but every branch writes the same root records. `semantic-merge` gets resolution guidance for `repro-lock.json` and for the acceptance format [02](../02-portable-records/task.md) settles, and implement-task's commit guidance names the records.
- **Protect records its reproduction decisions.** The researcher template and commit body in `superintegrate/references/protect.md` omit the completion targets, selected checks, and input boundary, and the targets then live only in a commit body. Give them a durable home in the task tree, with a default for the first IMPLEMENT exit, before Protect has run.

### One name per concept, and a current harness contract

- **Terminology.** Pick one of kept, key, retained, maintained, or canonical result; one of "final deliverable tasks" or "completion targets"; remove "canon".
- **Harness contract.**
  - `load_contract.json` anchors are two lines off since `3a548e98`, so LC008 lands on the planning-review row.
  - LC008 cites model text instead of routing.
  - `ALL_STAGE_SKILLS` counts a correct conditional load of `reproducibility` at `Stage: implementation` as an over-load.
  - The protection row is not yet verified in a live run.

### Validation

A realistic harness session walks the three scenarios in [wiring.md](../attachments/wiring.md):

1. An implementer on an econ task produces a regression table from a new script.
2. A subagent edits a shared helper that fans out to a costly estimation.
3. The main agent runs the completion check and Protect on a tree with a check step.

The harness-instruction-following tests pass.

Owning task: [unified-dependency-workflow](../../07-workflow-integration/unified-dependency-workflow/task.md).

## Details

Smaller prose fixes from [wiring.md](../attachments/wiring.md):

- `completion.md` §Verify Pipeline and Reproducibility still says "Pipeline", and `econ-data-analysis/SKILL.md:151` cites it.
- `integrate.md:9` "among them" has no clear referent.
- `CATEGORIES.md:52` states the load trigger more narrowly than `using-superra`.
- `changing-the-tree.md:42` points to §What earns a step for moves and removals, which §Step lifecycle covers.
- `result-protection/SKILL.md:8` counts "a registered step with its committed lock" as protection; only a check step guards values.
- `completion.md:19` "not ad-hoc REPL state" sits against accepting results from interactive runs.
- `main-agent.md:10` routes the session-start status through the stale rule, implying builds before the first response.
