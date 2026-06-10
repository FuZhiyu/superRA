---
title: "Add migration preparation instructions to task-tree"
status: approved
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

1. **[SKILL.md:212-245](skills/task-tree/SKILL.md#L212)** — `#### Preparing a PLAN.md for migration` subsection added adjacent to the existing migration command. Covers: quick compatibility check (`grep` command), what the script expects (heading patterns, metadata fields, status inference, dependency format, file lists), normalization checklist (5 items), and manual migration fallback for small/free-form files.

2. **[internals.md:111-158](skills/task-tree/references/internals.md#L111)** — `### Parser Expectations and Preparation` section added under the existing migration heading. Documents all regex patterns (`TASK_BLOCK_RE`, `RESULTS_SECTION_RE`, `FIELD_RE`), field extraction table, status inference cascade (review_status override then checkbox counting with exact match semantics), dependency resolution with silent-drop behavior, header extraction, slugification rules, and normalization-vs-manual decision guidance.

### Decisions

- Kept SKILL.md section concise and checklist-oriented (agent reads at migration time); internals.md goes deeper on parser details per the dispatch guidance.
- Did not modify `planning-workflow/SKILL.md` — Phase 0 already routes to `task-tree` §Migration, and the new subsection is adjacent to that anchor.

