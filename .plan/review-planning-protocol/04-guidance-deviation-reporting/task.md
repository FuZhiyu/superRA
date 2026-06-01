---
title: "Guidance Deviation Reporting"
status: implemented
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Require implementers to list any material deviation from `## Planner Guidance` in their task's `## Results`, explaining what guidance they did not follow, what they did instead, and why the alternative still satisfies `## Objective`. Reviewers should not fail a task merely for deviating from advisory guidance, but should flag unexplained material deviations as an evidence gap.

## Planner Guidance

Likely owner files are agents/implementer.md, agents/reviewer.md, and the task-system Results-section description. Regenerate Codex/direct-mode agent artifacts after changing role specs.

## Results

### Key Findings

- Updated the implementer role so material `## Planner Guidance` deviations must be recorded in `## Results` with the skipped guidance, chosen route, and objective-fit rationale ([../../../agents/implementer.md](../../../agents/implementer.md)).
- Updated the reviewer role so deviation itself is not a failure, but an unexplained material deviation is a MAJOR evidence gap ([../../../agents/reviewer.md](../../../agents/reviewer.md)).
- Updated task-system anatomy and planning reference so `## Results` is the owner surface for material guidance-deviation rationale ([../../../skills/task-system/SKILL.md](../../../skills/task-system/SKILL.md), [../../../skills/task-system/references/planning.md](../../../skills/task-system/references/planning.md)).
- Regenerated Codex named-agent files and direct-mode role references from the canonical role specs.

### Guidance Deviations

- None. The implementation used the planner-suggested owner files and regenerated generated artifacts.
