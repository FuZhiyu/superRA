---
title: "Deprecate PLAN.md/RESULTS.md references in the task system"
status: not-started
depends_on:  []
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Complete the `.plan/`-native results migration so task files are the primary researcher-facing record of progress and findings. Major results belong in the relevant task's `## Results` section, and parent task `## Results` sections summarize the major results of their child tasks when a researcher needs a higher-level view. Status reports are secondary navigation aids: they should point to the task files, not substitute for them. The human-readable state of the work should be discoverable by opening the relevant task file: `## Objective` explains what should happen, `## Results` summarizes what happened and what was found, `## Review Notes` carries active review findings, and the status frontmatter carries the task state.

Parent-level summaries are orchestrator-owned rollups, not leaf implementer output. Leaf implementers update only their assigned task's `## Results`. Reviewers verify the assigned task's results are substantive enough before approval. After a child task is approved, the orchestrator updates the immediate parent's `## Results` when the child produced a major result worth surfacing. At subtree closeout and in the Documentation stage, summarize selectively upward: child tasks carry full evidence and caveats, parent tasks summarize direct children with links to child task files, and the root task carries only top-level findings across root workstreams. Do not recursively copy every result up the tree; propagate only the level-appropriate summary a researcher needs at that node.

During the Documentation stage, ask the researcher where results should be summarized or updated before dispatching doc work. The researcher may choose, for example, only leaf tasks, specific parent tasks, the root task, or a subset of workstreams. Fold that guidance into root or parent task `## Results` / `## Revision Notes` before executing the documentation pass.

Current review findings:

- The canonical implementer role already points in the right direction: it tells implementers to update their assigned `task.md`, cite source files as markdown links, and write every material finding into the task before reporting ([../../../agents/implementer.md:61-73](../../../agents/implementer.md#L61-L73), [../../../agents/implementer.md:146-158](../../../agents/implementer.md#L146-L158)).
- The direct-mode generated copy and Codex named-agent file inherit that role text from `agents/implementer.md`; they must be regenerated after any canonical role edit, not edited by hand. Generated artifacts in scope: [../../../skills/using-superRA/references/direct-mode-implementer.md](../../../skills/using-superRA/references/direct-mode-implementer.md) and [../../../.codex/agents/superra_implementer.toml](../../../.codex/agents/superra_implementer.toml). Regenerate with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` or the current documented equivalent if the script interface has changed.
- `superimplement` verifies that completed tasks have findings in `## Results`, but it does not yet make the stronger user-facing rule explicit: the major results summary belongs in the task file and the status report is only a navigation aid ([../../../skills/superimplement/SKILL.md:117-125](../../../skills/superimplement/SKILL.md#L117-L125)).
- `task-system/references/planning.md` is the current source of truth for per-task results shape and two-stage maturation ([../../../skills/task-system/references/planning.md:150-202](../../../skills/task-system/references/planning.md#L150-L202)).
- `report-in-markdown/references/final-form.md` is stale and should be deprecated or removed rather than rewritten: it still frames Stage 2 around a separate root `RESULTS.md`, four commits that move that file, and review against the relocated file ([../../../skills/report-in-markdown/references/final-form.md:1-71](../../../skills/report-in-markdown/references/final-form.md#L1-L71)). Any surviving markdown formatting guidance should move to the owning task-system results guidance or remain in `report-in-markdown`'s core / rich-content references; there should not be a separate final-results artifact workflow.
- `README.md` still describes `PLAN.md + RESULTS.md` as the handoff surface and should be updated to describe `.plan/` task files as the durable record ([../../../README.md:34](../../../README.md#L34), [../../../README.md:59](../../../README.md#L59), [../../../README.md:109-110](../../../README.md#L109-L110)).

Implementation scope:

1. Strengthen `agents/implementer.md` only where behavior is still unstable: require `## Results` to carry the primary summary of major outcomes, numbers, caveats, and verification evidence before the implementer returns `DONE`. The status report remains short and pointer-based, but only after the task file already contains the substantive result. Preserve the existing ownership boundary that implementers edit only their assigned task's body sections and status.
2. Update `skills/superimplement/SKILL.md` Step 3 so the orchestrator treats missing, thin, or status-report-only major results as a failed reproducibility/documentation gate. The check should read the task files and parent summaries, not trust the implementer report.
3. Add the parent-rollup rule in the owning workflow/task-system guidance: leaf implementers write assigned-task results; reviewers verify those results; orchestrators update immediate parent summaries after child approval when warranted; documentation-stage work asks the researcher where summaries should be updated before polishing or propagating summaries.
4. Deprecate or remove `skills/report-in-markdown/references/final-form.md` and remove its load-map references. Replace any needed Stage 2 guidance with a small task-system-owned rule: child task `## Results` holds task-level findings; parent task `## Results` summarizes child findings for researcher monitoring; both use `report-in-markdown` file links, figures, tables, and math rules. Use markdown links with relative paths for every cited source file per [../../../skills/report-in-markdown/SKILL.md:11-18](../../../skills/report-in-markdown/SKILL.md#L11-L18).
5. Sweep stale `PLAN.md` / `RESULTS.md` references in `README.md`, `skills/*`, `agents/*`, and hook docs. Keep migration-only references where the old files are intentional inputs, but label them as legacy migration paths.
6. Regenerate generated Codex role artifacts from canonical sources. Do not hand-edit generated files.

Validation:

- Run `rg -n "RESULTS\\.md|PLAN\\.md" README.md agents skills .codex hooks` and confirm surviving hits are either migration-only legacy references or intentionally documented old-file compatibility.
- Run the project-scoped named-agent regeneration command and inspect `git diff` to confirm generated implementer copies match the canonical role changes.
- Run any available task-system / role-generation tests that cover generated role references, `report-in-markdown` load-map references, or markdown guidance. If no targeted test exists, run the smallest relevant existing test suite and record the command and result in this task's `## Results`.
- Self-apply the AGENTS.md DRY and Necessity tests to every added instruction line. Prefer pointing to `task-system/references/planning.md` and `report-in-markdown` over restating their full rules.
- Ensure every file path cited in edited task files or docs is a markdown link with a relative path and line anchor when pointing at a specific source line.

## Results
