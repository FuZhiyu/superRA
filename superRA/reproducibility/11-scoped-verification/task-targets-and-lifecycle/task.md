---
title: "Replace tiers with task targets and define step retirement"
status: approved
depends_on: []
---

## Objective

Use task targets and their producer dependencies to express completion work, removing the separate reproduction-tier classification. Define registration, maintenance, and retirement of steps around retained task results and active consumers.

- Remove tier-based selection, classification, and workflow gates from the CLI, schema, dashboard, and instructions. Preserve task/subtree unions, qualified step targets, `.` for all registered steps, explicit `--upstream`, and independent `--force`.
- Completion names final deliverable tasks and their selected checks, then assesses their producer chains. Checks must be selected explicitly or belong to the target task; being a downstream consumer does not automatically select them.
- Register executable support before exploratory results become retained task results, reusing existing producer/check declarations where possible. Unretained exploratory scratch needs no registration.
- Maintain declarations when their scripts, inputs, outputs, or owning tasks change. Moving or merging a task moves surviving steps and updates affected references while preserving stable identities and valid evidence where possible.
- Retire a step only when its result/check is no longer retained and no retained consumer needs its output. Before deleting or archiving an owner, preserve needed producers in a surviving task or explicitly agree a frozen external-input boundary. Finishing a task or shortening its prose is not grounds to discard reproduction support.
- Keep lifecycle discipline in the reproducibility skill; task-tree revision and integration cleanup load or reference that owner. Verify scratch-to-retained registration, rehoming, retirement with a surviving consumer, named completion checks, and existing scoped-execution invariants.

## Details

The researcher accepted dropping tiers after identifying final task targets as the source of required work. This is a follow-up to [task-scoped builds](../task-scoped-builds/task.md), whose approved runtime still supports tiers.

- No-target `build` / `status` require an explicit target; `.` selects every registered step. No configured or inferred default set replaces tiers, so an accidental full rebuild needs a deliberate `.`.
- Retired inputs fail with an actionable message, following the `--force-all` precedent: `--tier` and `repro tier` name the target-based replacement. A `tier:` key in an existing section is a `[WARNING]` and is otherwise ignored; tier never entered the step spec hash, so dropping it preserves every successful lock.
- Migration must address existing tier declarations, flags, and links without silently changing their meaning or discarding successful evidence.
- Current registration owner: [reproducibility §What Gets a Step](../../../../skills/reproducibility/SKILL.md#what-gets-a-step). Its exclusion based on a cited number should cover retained results generally, including qualitative findings.
- Current cleanup coverage: [integration maturation](../../../../skills/superintegrate/references/mature-consolidate.md) preserves steps during task folds. General step retirement and archive/deletion handling need an explicit owning rule; cleanup must not leave a needed producer undeclared merely because its old output still exists.

## Results

Reproduction tiers are gone: `repro build` / `status` run the named task or `task#step` targets, `.` selects every registered step, and a bare command fails with that instruction. The [reproducibility skill](../../../../skills/reproducibility/SKILL.md#step-lifecycle) replaces §Tiers with the step lifecycle.

- **Runtime.** [Parser](../../../../skills/task-tree/scripts/_repro.py), [selection/status](../../../../skills/task-tree/scripts/_repro_state.py), [runner](../../../../skills/task-tree/scripts/repro_run.py), task read/tree, and the dashboard route and client carry no tier field, filter, badge, or `set_tier`. Library callers with no targets still assess every step; only the CLI requires a target.
- **Migration.** `--tier` and `repro tier` exit 2 naming the target-based replacement, under both `--plan-root` and `--root`. A leftover `tier:` key is one `[WARNING]` per section and changes no step state: a disposable two-task fixture stayed 2 of 2 `fresh` with `tier: canon` / `tier: gold` added or removed, and rebuilt nothing. This repository's three sections dropped the key.
- **Completion.** [Protect](../../../../skills/reproducibility/references/protect-and-completion.md) names completion targets — tasks owning kept-result producers plus selected checks — in the `integrate(protect)` commit body; the IMPLEMENT, Integrate, and Finish gates run `repro build <targets> --upstream` and a clean matching `status`. A check runs only when targeted or owned by a target task.
- **Lifecycle.** Retire a step only when its result or check is no longer retained and no retained consumer reads its output; moved or merged tasks keep step names; deleting or archiving an owner first rehomes needed producers or agrees a frozen boundary. [Maturation](../../../../skills/superintegrate/references/mature-consolidate.md) points there. Registration now covers retained findings generally, not only cited numbers.
- **Verification.** The task-tree suite passed **1,173 tests** and the dashboard browser suite **35**; `test_artifact_ui.py` keeps its two earlier sidebar/attachment failures, outside this change. Seven new tests cover the retired key, flag, and subcommand, bare commands, `.`, and lock preservation; ten tier-only tests were deleted. The [workflow journey](../../07-workflow-integration/unified-dependency-workflow/attachments/verify_workflow.py) passes on explicit targets after qualifying its ambiguous `source` selectors, which task-scoped builds had already broken. `repro build` on [task-scoped builds](../task-scoped-builds/task.md) reran its check and pilot with the new CLI; both are `fresh`. Skill, Markdown, harness-compatibility, and `task check` passes are clean.

An independent quick correctness review approved the change after three stale reference statements were removed. Step-lifecycle scenarios (scratch-to-retained registration, rehoming, retirement with a surviving consumer) are instruction changes without an agent-level run.
