---
title: "Objective-First Reviewer Protocol"
status: not-started
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
- generated files after source edits: `skills/using-superRA/references/direct-mode-reviewer.md`, `.codex/agents/superra_reviewer.toml`

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
