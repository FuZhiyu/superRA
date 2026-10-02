---
title: "Wire the Graph into the PLAN / IMPLEMENT / INTEGRATE Workflow"
status: approved
depends_on:
  - 01-section-contract
  - 02-runner
  - 06-skill
---

## Objective

Keep reproduction integrated into planning, implementation, review, protection, and completion through the owning workflow and role skills, each call site pointing to the one `reproducibility` reference that owns its rule. Workflow prose consumes the task tooling's effective dependencies rather than restating dependency or runner mechanics.

- **Planning** names each retained artifact and its planned script; the implementer registers the step. Dependency guidance authors only logical `depends_on` prerequisites and uses effective dependencies for invalidation.
- **Implementation and review** apply the registration, claim, and stale-rule gates; the Skill-Load Manifest loads `reproducibility` for any task that plans, produces, changes, records, or reviews a result computed by code.
- **Completion and Protect** run the completion gate over every step and report every `unverified` step to the researcher; Protect decides only which inputs are external.
- **Maturation and merges** preserve step identities and evidence when tasks fold or move, and resolve conflicted reproduction records by the stale rule.
- **Inventories and public docs** (manifest, `CATEGORIES.md`, `CLAUDE.md`, `README.md`, release notes, docs-site sources, harness load contracts) stay consistent with the skill.

## Results

The graph replaced the pipeline-file requirement at every phase; no workflow file mentions a pipeline file.

### Each call site points to its owning rule

| Phase | Call site | Points to |
|---|---|---|
| PLAN | [build-and-review.md §Artifact Pipeline](../../../skills/superplan/references/build-and-review.md#artifact-pipeline) names each artifact and its planned script in `## Details`; self-review checks they are named. [§Task Dependencies](../../../skills/superplan/references/build-and-review.md#task-dependencies), consolidation, and scope-change invalidation use effective dependencies. | [designing-the-graph.md](../../../skills/reproducibility/references/designing-the-graph.md) |
| IMPLEMENT | [implement-task](../../../skills/implement-task/SKILL.md) Self-Check 4; [interactive-mode.md](../../../skills/using-superra/references/interactive-mode.md) self-review walks every loaded skill's gates | SKILL.md [§Recording a Result](../../../skills/reproducibility/SKILL.md#recording-a-result) |
| Review | [review-task](../../../skills/review-task/SKILL.md) checks registration, the claim, and the reason behind any acceptance with read-only `status <targets>` and the committed records | the three gate references |
| Completion | [completion.md](../../../skills/superimplement/references/completion.md), [integrate.md](../../../skills/superintegrate/references/integrate.md), [finish.md](../../../skills/superintegrate/references/finish.md) | [§The completion gate](../../../skills/reproducibility/references/protect-and-completion.md#the-completion-gate) |
| Protect | [protect.md](../../../skills/superintegrate/references/protect.md) asks which inputs are external and records them in the `integrate(protect)` commit body | [§Reproduction choices at Protect](../../../skills/reproducibility/references/protect-and-completion.md#reproduction-choices-at-protect) |
| Maturation | [mature-consolidate.md](../../../skills/superintegrate/references/mature-consolidate.md), [consolidation.md](../../../skills/superplan/references/consolidation.md) §Prune, [changing-the-tree.md](../../../skills/superplan/references/changing-the-tree.md) | [§Step lifecycle](../../../skills/reproducibility/references/designing-the-graph.md#step-lifecycle) |
| Merge | [semantic-merge](../../../skills/semantic-merge/SKILL.md) "Reproduction records" role; [parallel-dispatch.md](../../../skills/agent-orchestration/references/parallel-dispatch.md) points there | the stale rule |

- **The main agent** ([main-agent.md](../../../skills/using-superra/references/main-agent.md)) runs `repro status .` at session start and reports the steps that are not `fresh`; a frontier input that is not fresh goes through the stale rule before work builds on it, and a costly rerun the stale rule sends to the researcher is a pre-set gate in autonomous mode.
- **One escalation status.** A subagent facing a costly rerun returns `DONE_WITH_CONCERNS` with the question in `## Results`, which keeps its finished work committed; `implement-task` §Escalation and `superimplement` point to the stale rule.
- **Seeded steps were rejected.** Planners name artifacts instead of seeding `## Reproduction` steps, because seeded steps read `missing` before any work and the session-start report would treat unbuilt plans as steps to resolve.

### Registration and inventories

- The `using-superra` manifest lists `reproducibility` in the `protection` Stage row and in a Domain row; [CATEGORIES.md](../../../skills/CATEGORIES.md), [README.md](../../../README.md), and the [CLAUDE.md](../../../CLAUDE.md) ownership rows split discipline (`reproducibility`) from mechanics (`task-tree`). [result-protection](../../../skills/result-protection/SKILL.md) counts drift tests registered as check steps as protection.
- [README §Upgrading](../../../README.md#upgrading), [RELEASE-NOTES.md](../../../RELEASE-NOTES.md), and the [docs-site task-tree pages](../../../docs/site/04-utility-skills/01-task-tree/task.md) describe readiness from `depends_on`, task/step navigation, `impact`, and reviewed acceptance. Docs HTML is generated by [docs/build_site.sh](../../../docs/build_site.sh).
- The harness load contract ([load_contract.json](../../../tests/harness-instruction-following/load_contract.json)) covers the protection row (LC008) and the Domain row (LC024).

### Live harness sessions

- **Stage and domain loads (2026-09-29, Sonnet via the SDK harness):** the protection row loaded both `result-protection` and `reproducibility`, and a reproducibility-worded task loaded `reproducibility` before its first edit.
- **Three wiring scenarios** on a scratch project with a 150-second estimation step:
  - A new table script was registered and built, and `## Results` named its saved input and that the step executed.
  - A shared-helper edit: the implementer rebuilt the cheap panel step, left the costly estimation stale, and returned `DONE_WITH_CONCERNS` with a recommendation.
  - Completion and Protect: the main agent ran `status`, `explain`, and a dry run, accepted a comment-only change under the exception, asked before the costly rerun, and recorded `External inputs:` in the Protect commit body.

## Review Notes

Tier: thorough. Focuses: correctness, results-writing (maturation of 11-local-builds into this task).

1. [ADVISORY] [§Each call site points to its owning rule:36](#L36) says "a frontier input that is not fresh goes through the stale rule", mirroring [main-agent.md:29](../../../skills/using-superra/references/main-agent.md#L29). The frontier now flags only inputs whose producer is `stale`, `missing`, or `failed` ([_task_snapshot.py:11](../../../skills/task-tree/scripts/_task_snapshot.py#L11)); an input from an `unverified` producer is not flagged. Fix: reword both lines together, as [03-task-interface](../03-task-interface/task.md) does.
