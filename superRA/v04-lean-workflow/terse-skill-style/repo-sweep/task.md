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

