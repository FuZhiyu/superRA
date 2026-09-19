---
title: "Replace tiers with task targets and define step retirement"
status: in-progress
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

Design decisions recorded from the researcher discussion and inspection of registration, task-tree revision, and integration-maturation instructions. Implementation has not started; the current CLI still supports tiers.
