---
title: "Update agent specs and workflow skills"
status: not-started
review_status: ~
integration_status: ~
depends_on:
  - 01-design
tags: [docs, protocol]
script: ""
input: []
output: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Update all agent role specs and workflow skills to use the unified `status` field instead of the `status` + `review_status` + `integration_status` triple. The core change: where agents previously set two fields on one event, they now set one.

**Out of scope:** Rearchitecting the integration workflow for scope-flexible operation. That is tracked separately. This task removes field references and updates protocols to use `status` only.

**Agent specs:**

`agents/implementer.md`:
- §What You Own: remove `review_status:` and `integration_status:` from owned fields. Replace with: "Implementer owns `status:` transitions up to `implemented` (and `revise → implemented` on fix rounds)."
- §Update the Task and Commit: replace "Set `status: implemented` and `review_status: implemented`" with "Set `status: implemented`"
- §How You Fix Review Items: same replacement on the REVISE round commit instruction

`agents/reviewer.md`:
- §What You Own: replace `review_status:` and `integration_status:` ownership with: "Reviewer owns `status:` transitions `implemented → revise` and `implemented → approved`."
- §Verdict: replace "set `review_status: approved`" with "set `status: approved`", same for `revise`
- §Pre-Commit Self-Check: update the checklist item

**Workflow skills:**

`skills/implementation-workflow/SKILL.md`:
- §Step 2 (Execute Tasks): replace "status: implemented and review_status: implemented" with "status: implemented"
- §Step 2 reviewer dispatch: replace "review_status: approved" with "status: approved"
- §Step 3 (Verify Pipeline): remove `## Workflow Status` checkbox references

`skills/integration-workflow/SKILL.md`:
- Replace all `integration_status` references with `status` (§Integrate step, §Refactor loop, reviewer dispatch instructions, implementer fix instructions)
- Update the integration reviewer's field ownership to use `status` instead of `integration_status`

`skills/agent-orchestration/SKILL.md`:
- §Review Status Reference table: update to reference `status:` instead of `review_status:`
- §Completion gate: "task is complete when its `status` is `approved`"

`skills/planning-workflow/SKILL.md`:
- §Primary tracker: update field reference
- §Status clear instructions: now just reset `status` instead of clearing `review_status` and `integration_status` separately

**Using-superRA references:**

`skills/using-superRA/references/direct-mode-implementer.md`: same changes as implementer.md
`skills/using-superRA/references/direct-mode-reviewer.md`: same changes as reviewer.md
`skills/using-superRA/references/main-agent.md`: update frontmatter reading instructions, remove `## Workflow Status` references

**Other skill references:**

`skills/writing/references/planning.md`: update review_status references
`skills/writing/references/long-form-review.md`: update review protocol references

## Results
