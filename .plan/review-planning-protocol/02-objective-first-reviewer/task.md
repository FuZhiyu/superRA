---
title: "Objective-First Reviewer Protocol"
status: not-started
depends_on: [01-objective-guidance-task-anatomy]
tags: []
created: 2026-06-01
---

## Objective

Revise implementation-review workflow so reviewer approval requires task-local objective satisfaction before domain checklist approval. The reviewer must derive the required deliverables from the assigned task's `## Objective`, scope-defining frontmatter (`script`, `input`, `output`), implementer `## Results`, and the reviewed git range; verify the changed artifacts and outputs satisfy those obligations; independently check material claims; then walk the active domain skill's gates as additional blocking/advisory checks.

This is a generic reviewer-role change, not a domain-skill rewrite. Domain skills continue to own their specific checklists and operation-conditional gates. The implementation-stage review boundary remains task-local: objective, declared outputs, implementer results, changed files, and active domain gates. Do not pull full codebase integration review forward from `superintegrate`.

Update `skills/superimplement/SKILL.md` where it currently defines comprehensive review as checklist walking, replacing that with a pointer to the reviewer protocol and a task-local objective/output correctness boundary. The orchestrator adjudication protocol in `skills/agent-orchestration/SKILL.md` should remain unchanged unless a wording conflict is discovered.

## Planner Guidance

Likely files:
- `agents/reviewer.md`
- `skills/superimplement/SKILL.md`
- generated files after source edits: `skills/using-superRA/references/direct-mode-reviewer.md`, `.codex/agents/superra_reviewer.toml`

The compact behavior-shaping rule should be: the objective is the approval target; domain checklists are additional gates. Avoid adding per-domain examples to `agents/reviewer.md`; those belong in the domain skills.

Potential reviewer failure modes to close:
- reading the objective but never checking deliverable completeness;
- approving because checklist items pass while required output is missing;
- treating planner guidance as a binding implementation route;
- accepting implementer claims without checking the diff or outputs.

## Validation

- Regenerate Codex/direct-mode role artifacts from canonical agent specs.
- Run the generated-agent check and the reviewer/role generation tests.
- Use a tiny fixture or manual dry run where a task passes a domain checklist but misses a stated output; confirm the revised reviewer protocol would produce REVISE.
- Confirm an implementation that deviates from `## Planner Guidance` but satisfies `## Objective` is not a review failure.

## Results

