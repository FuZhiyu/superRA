---
title: "Add migration preparation instructions to task-tree"
status: implemented
depends_on: []
tags: []
created: 2026-05-25
---

## Objective

Add agent-facing instructions for preparing non-conforming PLAN.md files for migration. The `plan_migrate.py` script expects strict formatting — `### Task N: Title` headings, `## Task N: Title` in RESULTS.md, bold metadata fields (`**Depends on:**`, `**Script:**`, etc.), checkbox syntax `- [x]`/`- [ ]` for status inference. Real PLAN.md files often diverge: unnumbered tasks, different heading levels, free-form prose, missing metadata fields, non-standard checkboxes.

### Deliverables

Two additions (concise, agent-reads-at-migration-time style):

1. **`skills/task-tree/SKILL.md`** — add a "Preparing a PLAN.md for migration" subsection adjacent to the existing "Migrate from PLAN.md + RESULTS.md" section. Cover:
   - What the script expects (exact heading patterns, metadata field formats, status-inference rules from `_compute_status_from_steps` and `_extract_field`)
   - How to assess script-compatibility (run a quick check: does `grep -c '^### Task [0-9]' PLAN.md` match the expected task count?)
   - Normalization checklist for common deviations (renumber tasks to `### Task N:` format, fix heading levels, add missing metadata fields with defaults, standardize checkboxes)
   - When manual migration is simpler than normalization (e.g. ≤3 tasks, heavily free-form structure)
   - Brief manual migration procedure for that case (create `.plan/` dirs, write `task.md` files directly using `task_create.py` or by hand)

2. **`skills/task-tree/references/internals.md`** — add a parallel section under the existing "Migration: `plan_migrate.py`" heading, covering the same content with slightly more detail on the parser expectations (the regex patterns, field extraction logic).

## Results

Added migration preparation instructions to two files, sourced directly from `plan_migrate.py` parser logic:

1. [skills/task-tree/references/internals.md §Preparing a legacy PLAN.md for migration](../../../../skills/task-tree/references/internals.md) — `### Preparing a legacy PLAN.md for migration` subsection added (line numbers have drifted; see current file). Covers: quick compatibility check (`grep` command), what the script expects (heading patterns, metadata fields, status inference, dependency format, file lists), normalization checklist (5 items), and manual migration fallback for small/free-form files. Note: the SKILL.md subsection from original implementation moved into internals.md by a later consolidation.

2. [skills/task-tree/references/internals.md §Parser Expectations and Preparation](../../../../skills/task-tree/references/internals.md) — `### Parser Expectations and Preparation` section under the migration heading. Documents all regex patterns (`TASK_BLOCK_RE`, `RESULTS_SECTION_RE`, `FIELD_RE`), field extraction table, status inference cascade, dependency resolution, slugification rules, and normalization-vs-manual decision guidance.

### Decisions

- Kept the migration-prep content checklist-oriented (agent reads at migration time); internals.md goes deeper on parser details per the dispatch guidance.
- Did not modify `superplan/SKILL.md` — Entry Assessment already routes to `task-tree` §Migration, and the new subsection is adjacent to that anchor.

## Review Notes

1. **[MAJOR]** Broken Results links: `[SKILL.md:212-245](skills/task-tree/SKILL.md#L212)` and `[internals.md:111-158](skills/task-tree/references/internals.md#L111)` are task-dir-relative and have never resolved from this file; the cited line ranges have also drifted in the live files. Fix: [../../../../skills/task-tree/SKILL.md](../../../../skills/task-tree/SKILL.md) / [../../../../skills/task-tree/references/internals.md](../../../../skills/task-tree/references/internals.md) and re-verify anchors.
   → implemented: updated Results with correct relative paths and section anchors; removed stale line number anchors ([migration-prep/task.md](task.md))

