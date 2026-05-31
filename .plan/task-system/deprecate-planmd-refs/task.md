---
title: "Deprecate PLAN.md/RESULTS.md references in the task system"
status: not-started
depends_on:  []
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Complete the `.plan/`-native results migration so major findings are summarized in each task's `task.md` rather than in a separate root-level `RESULTS.md` or only in the implementer's status report. The human-readable state of the work should be discoverable by opening the relevant task file: `## Objective` explains what should happen, `## Results` summarizes what happened and what was found, `## Review Notes` carries active review findings, and the status frontmatter carries the task state.

Current review findings:

- The canonical implementer role already points in the right direction: it tells implementers to update their assigned `task.md`, cite source files as markdown links, and write every material finding into the task before reporting ([../../../agents/implementer.md:61-73](../../../agents/implementer.md#L61-L73), [../../../agents/implementer.md:146-158](../../../agents/implementer.md#L146-L158)).
- The direct-mode generated copy and Codex named-agent file inherit that role text from `agents/implementer.md`; they must be regenerated after any canonical role edit, not edited by hand. Generated artifacts in scope: [../../../skills/using-superRA/references/direct-mode-implementer.md](../../../skills/using-superRA/references/direct-mode-implementer.md) and [../../../.codex/agents/superra_implementer.toml](../../../.codex/agents/superra_implementer.toml). Regenerate with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` or the current documented equivalent if the script interface has changed.
- `superimplement` verifies that completed tasks have findings in `## Results`, but it does not yet make the stronger user-facing rule explicit: the major results summary belongs in the task file and the status report is only a navigation aid ([../../../skills/superimplement/SKILL.md:117-125](../../../skills/superimplement/SKILL.md#L117-L125)).
- `task-system/references/planning.md` is the current source of truth for per-task results shape and two-stage maturation ([../../../skills/task-system/references/planning.md:150-202](../../../skills/task-system/references/planning.md#L150-L202)).
- `report-in-markdown/references/final-form.md` is stale: it still frames Stage 2 around a separate root `RESULTS.md`, four commits that move that file, and review against the relocated file ([../../../skills/report-in-markdown/references/final-form.md:1-71](../../../skills/report-in-markdown/references/final-form.md#L1-L71)). Rewrite this reference so Stage 2 matures task-local `## Results` sections in place, uses task-local `attachments/`, and applies the same citation/fact-check discipline to task files.
- `README.md` still describes `PLAN.md + RESULTS.md` as the handoff surface and should be updated to describe `.plan/` task files as the durable record ([../../../README.md:34](../../../README.md#L34), [../../../README.md:59](../../../README.md#L59), [../../../README.md:109-110](../../../README.md#L109-L110)).

Implementation scope:

1. Strengthen `agents/implementer.md` only where behavior is still unstable: require a concise `## Results` summary of major outcomes, numbers, caveats, and verification evidence before the implementer returns `DONE`; keep the status report short and pointer-based. Preserve the existing ownership boundary that implementers edit only their assigned task's body sections and status.
2. Update `skills/superimplement/SKILL.md` Step 3 so the orchestrator treats missing or status-report-only major results as a failed reproducibility/documentation gate. The check should read the task files, not trust the implementer report.
3. Rewrite `skills/report-in-markdown/references/final-form.md` from separate `RESULTS.md` maturation to task-local result maturation. Keep the useful fact-check, citation, figure, limitations, and prohibited-language discipline, but apply it to each in-scope task's `## Results` section. Use markdown links with relative paths for every cited source file per [../../../skills/report-in-markdown/SKILL.md:11-18](../../../skills/report-in-markdown/SKILL.md#L11-L18).
4. Sweep stale `PLAN.md` / `RESULTS.md` references in `README.md`, `skills/*`, `agents/*`, and hook docs. Keep migration-only references where the old files are intentional inputs, but label them as legacy migration paths.
5. Regenerate generated Codex role artifacts from canonical sources. Do not hand-edit generated files.

Validation:

- Run `rg -n "RESULTS\\.md|PLAN\\.md" README.md agents skills .codex hooks` and confirm surviving hits are either migration-only legacy references or intentionally documented old-file compatibility.
- Run the project-scoped named-agent regeneration command and inspect `git diff` to confirm generated implementer copies match the canonical role changes.
- Run any available task-system / role-generation tests that cover generated role references or markdown guidance. If no targeted test exists, run the smallest relevant existing test suite and record the command and result in this task's `## Results`.
- Self-apply the AGENTS.md DRY and Necessity tests to every added instruction line. Prefer pointing to `task-system/references/planning.md` and `report-in-markdown` over restating their full rules.
- Ensure every file path cited in edited task files or docs is a markdown link with a relative path and line anchor when pointing at a specific source line.

## Results
