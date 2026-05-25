---
title: "Replace ## Decisions with ## Revision Notes"
status: approved
review_status: approved
integration_status: approved
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

### Files Modified

- [`skills/task-system/references/planning.md`](skills/task-system/references/planning.md) — Removed §User Decisions Log section entirely. Updated §Root task.md Anatomy: replaced `## Decisions` with `## Revision Notes` (with lifecycle description). Updated §Field-by-Field Notes: replaced `## Decisions` entry with `## Revision Notes` entry. Updated §Stale Content Checklist: replaced "Decisions section" reference with revision-note guidance.
- [`skills/task-system/SKILL.md`](skills/task-system/SKILL.md) — Updated body sections table: replaced `## Decisions` row with `## Revision Notes` (owner: planner/orchestrator, purpose: temporary delta signal). Updated §Ownership Model: removed `## Decisions` from implementer-owned sections list.
- [`agents/implementer.md`](agents/implementer.md) — Removed `## Decisions` from §What You Own body-sections list. Removed "record decisions in `## Decisions`" from §Update the Task and Commit.
- [`agents/reviewer.md`](agents/reviewer.md) — No changes needed; reviewer already has correct ownership model (only writes `## Review Notes`).
- [`skills/agent-orchestration/SKILL.md`](skills/agent-orchestration/SKILL.md) — Updated §Orchestrator Duties escalation: replaced "log in `## Decisions`" with "fold into objective + revision note". Updated §Handling Reviewer Feedback items 5 and limits: replaced all `## Decisions` / `§User Decisions Log` references with the new mechanism. Updated §Handling Implementer Status: replaced "log decision in `## Decisions`" with "fold into task objective".

### Verification

- `grep -rn '## Decisions' skills/task-system/ skills/agent-orchestration/ agents/` returns only `internals.md:30` (Python data model field comment — code-level, not operational instruction).
- `grep -rn 'User Decisions Log'` returns zero results across all five in-scope files.
- `## Revision Notes` appears with correct lifecycle description in `planning.md` (2 locations) and `SKILL.md` (1 location), and as the new mechanism in `agent-orchestration/SKILL.md` (3 locations).

### Out-of-Scope Residuals

- `skills/task-system/references/internals.md:30` — data model field `decisions: str # extracted from ## Decisions`. This is a code-level concern for whoever updates the Python scripts; not in this task's file list.
- `skills/using-superRA/SKILL.md:43` — parenthetical mention of "User Decisions Log format" in §Handoff Docs. Not in this task's file list. The sibling `main-agent-update` task or a follow-up should address this.
- Other files outside scope (implementation-workflow, integration-workflow, semantic-merge, result-protection, handoff-doc, direct-mode refs) still reference `## Decisions` and `§User Decisions Log`. These are not in this task's five-file scope.

