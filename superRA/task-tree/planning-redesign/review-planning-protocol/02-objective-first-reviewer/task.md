---
title: "Objective-First Reviewer Protocol"
status: approved
depends_on: [01-objective-guidance-task-anatomy]
tags: []
created: 2026-06-01
---

## Objective

Revise implementation-review workflow so reviewer approval reflects broad task-local judgment rather than checklist-only compliance. The reviewer must use their general research and engineering judgment, the assigned task's `## Objective`, scope-defining frontmatter (`script`, `input`, `output`), implementer `## Results`, the reviewed git range, and the active domain skill's gates together while evaluating whether the implementation is correct, complete, well-supported, and fit for the task. Domain checklists are mandatory additional requirements and any blocking gate failure still requires REVISE, but they are not the reviewer's whole job.

This is a generic reviewer-role change, not a domain-skill rewrite. Domain skills continue to own their specific checklists and operation-conditional gates. The implementation-stage review boundary remains task-local: objective, declared outputs, implementer results, changed files, active domain gates, and issues a capable reviewer can identify from that evidence. Do not pull full codebase integration review forward from `superintegrate`.

Update `skills/superimplement/SKILL.md` where it currently defines comprehensive review as checklist walking, replacing that with a pointer to the reviewer protocol and a task-local broad-review boundary. The orchestrator adjudication protocol in `skills/agent-orchestration/SKILL.md` should remain unchanged unless a wording conflict is discovered.

## Planner Guidance

Likely files:
- `agents/reviewer.md`
- `skills/superimplement/SKILL.md`
- generated files after source edits: `skills/using-superra/references/direct-mode-reviewer.md`, `.codex/agents/superra_reviewer.toml`

The compact behavior-shaping rule should be: review the task broadly using the reviewer's own judgment and the active domain discipline; domain checklists are mandatory gates, not the review boundary. Avoid adding per-domain examples to `agents/reviewer.md`; those belong in the domain skills.

Potential reviewer failure modes to close:
- reading the objective but never checking deliverable completeness;
- approving because checklist items pass while required output is missing;
- treating the checklist as exhaustive and missing obvious task-level problems outside its enumerated items;
- treating planner guidance as a binding implementation route;
- accepting implementer claims without checking the diff or outputs.

## Validation

- Regenerate Codex/direct-mode role artifacts from canonical agent specs.
- Run the generated-agent check and the reviewer/role generation tests.
- Use a tiny fixture or manual dry run where a task passes explicit checklist items but has an obvious task-level defect outside the enumerated checklist; confirm the revised reviewer protocol would produce REVISE.
- Confirm an implementation that deviates from `## Planner Guidance` but satisfies `## Objective` is not a review failure.

## Results

### Key Findings
- Revised the canonical reviewer protocol so review is explicitly task-local and objective-first: reviewers evaluate `## Objective`, scope frontmatter, implementer `## Results`, reviewed git range, changed outputs, and active domain gates together; domain checklists remain mandatory gates but are no longer the review boundary ([../../../agents/reviewer.md:43](../../../../../agents/reviewer.md#L43)).
- Updated reviewer verdict semantics so CRITICAL and MAJOR task-level findings block approval even when no domain checklist item names the issue, while failed `[BLOCKING]` domain gates still force REVISE ([../../../agents/reviewer.md:82](../../../../../agents/reviewer.md#L82), [../../../agents/reviewer.md:86](../../../../../agents/reviewer.md#L86), [../../../agents/reviewer.md:90](../../../../../agents/reviewer.md#L90)).
- Updated first-review mechanics to check objective satisfaction, declared outputs, implementer results, reviewed diff, and active domain gates before setting `approved` or `revise` ([../../../agents/reviewer.md:131](../../../../../agents/reviewer.md#L131), [../../../agents/reviewer.md:134](../../../../../agents/reviewer.md#L134)).
- Replaced `superimplement`'s checklist-only review description with pointers to `agents/reviewer.md` §Review Protocol and the task-local review boundary; updated stale workflow shorthand so REVISE means reviewer-found blocking findings, including CRITICAL/MAJOR task-level findings and failed `[BLOCKING]` domain gates ([../../../skills/superimplement/SKILL.md:12](../../../../../skills/superimplement/SKILL.md#L12), [../../../skills/superimplement/SKILL.md:30](../../../../../skills/superimplement/SKILL.md#L30), [../../../skills/superimplement/SKILL.md:93](../../../../../skills/superimplement/SKILL.md#L93), [../../../skills/superimplement/SKILL.md:161](../../../../../skills/superimplement/SKILL.md#L161), [../../../skills/agent-orchestration/SKILL.md:195](../../../../../skills/agent-orchestration/SKILL.md#L195)).

### Generated Artifacts
- Regenerated with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`.
- Generated outputs updated from `agents/reviewer.md`: [../../../skills/using-superra/references/direct-mode-reviewer.md](../../../../../skills/using-superra/references/direct-mode-reviewer.md), [../../../.codex/agents/superra_reviewer.toml](../../../../../.codex/agents/superra_reviewer.toml).

### Validation
- `python3 skills/task-tree/scripts/task_check.py --plan-root superRA` passed after the task-root rename: all checks passed, no issues found.
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` passed: generated agent files and direct-mode role references are up to date.
- `python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py` passed: 6 tests.
- Manual dry run passed by assertion against the revised reviewer protocol text: a checklist-passing task missing a declared output produces REVISE as a blocking task-level finding, while an implementation that deviates from `## Planner Guidance` but satisfies `## Objective` is not a review failure.
- DRY/Necessity self-check: added role lines change reviewer verdict behavior at the canonical role surface; workflow-skill edits only route to the role protocol and preserve `superimplement`'s ownership of dispatch and interim review scope.
