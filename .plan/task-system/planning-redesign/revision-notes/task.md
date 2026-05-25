---
title: "Replace ## Decisions with ## Revision Notes"
status: not-started
review_status: ~
integration_status: ~
depends_on: 
  - skill-rewrite

tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Implement the `## Revision Notes` mechanism across the task system, agent specs, and orchestration — replacing the `## Decisions` log and `User Decisions Log` protocol.

### What Changes

**Core concept:** Tasks track latest state only. When a task is updated (scope change, methodology pivot), the objective is rewritten to be fully self-sufficient. A temporary `## Revision Notes` section carries the delta signal (what changed, how significant) for the next agent. Revision notes follow the same cleanup lifecycle as review notes — cleaned out when the task is re-implemented and approved.

**Drop `## Decisions` section and User Decisions Log.** Methodology decisions are folded into task objectives directly. The commit message records what changed and why. No separate log section.

### Files to Update

**`skills/task-system/references/planning.md`:**
- Remove §User Decisions Log section entirely
- Update §Root task.md Anatomy: drop `## Decisions` from required sections, add `## Revision Notes` with lifecycle description
- Update §Field-by-Field Notes: replace `## Decisions` references with `## Revision Notes`
- Update §Stale Content Checklist if it references Decisions

**`skills/task-system/SKILL.md`:**
- Update body sections table: replace `## Decisions` row with `## Revision Notes` (purpose: temporary delta signal for plan changes, cleaned on approval)
- Update the task file format example to show `## Revision Notes` instead of `## Decisions`

**`agents/implementer.md`:**
- Update §Editing Etiquette / ownership: implementer no longer writes to `## Decisions`; may add `## Revision Notes` when updating a task objective (rewriting it fully, adding the delta note)
- Remove any "log in ## Decisions" instructions

**`agents/reviewer.md`:**
- Update ownership: reviewer does not edit `## Revision Notes` (same as current `## Decisions` — read-only for reviewers)

**`skills/agent-orchestration/SKILL.md`:**
- Update §Orchestrator Duties and §Handling Reviewer Feedback: replace "log in ## Decisions" with the new mechanism (rewrite objective + add revision note)
- Update escalation protocol: after `AskUserQuestion`, fold the decision into the objective text, optionally add a revision note if the change is non-obvious

**`skills/using-superRA/references/main-agent.md`:** Handled by sibling task `main-agent-update` (which is already rewriting that file). Not in scope here.

### Verification
- `grep -rn '## Decisions' skills/ agents/` should return no operational references (only historical/migration context)
- `grep -rn 'User Decisions Log' skills/ agents/` should return zero results
- Task file format in SKILL.md and references should show `## Revision Notes` with correct lifecycle description

## Results

