---
title: "Repo Sweep: Restyle Remaining Skill Prose to the Terse Style"
status: in-progress
depends_on: []
---

## Objective

Every instruction file under skills/ matches the terse style at implement-task / review-task density. Behavior-preserving restyle only: protocol content, gates, and ordering constraints survive verbatim in meaning. Done so far: implement-task and using-superra (2e1fbdaa), review-task (f525b63e), superintegrate mature-consolidate.md (35832fe7), using-superra task-companion-files.md (f46265a5). Remaining: workflow skills, stage references, domain and utility skills.

## Planner Guidance

Per file: apply the CLAUDE.md DRY/Necessity gate first (delete lines that fail), then compress to the style (CLAUDE.md §Skill Prose Style). The daea6ae3 failure mode is the check: if the word count barely moves, the pass cut connectives, not clauses.

## Results

Spec test (main agent applying the fresh [CLAUDE.md §Skill Prose Style](../../../../CLAUDE.md)): [superplan/SKILL.md](../../../../skills/superplan/SKILL.md) 1047 → 756 words (−28%), [references/decomposition.md](../../../../skills/superplan/references/decomposition.md) 708 → 539 (−24%). Protocol preserved — all phase gates, tier table, dispatch template, and self-review items survive; the harness contract tests pass (15/15). One consolidation: decomposition's duplicate dependency-edge check merged into Self-Review item 8.
