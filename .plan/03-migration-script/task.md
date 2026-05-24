---
title: "Migration Script"
status: implemented
review_status: implemented
integration_status: ~
depends_on:
  - 01-core-data-layer-task-iopy
tags: []
script: skills/task-system/scripts/plan_migrate.py
created: 2026-05-23
updated: 2026-05-23
---

## Objective
- **Step 1: Parse PLAN.md** — extract header (everything before `### Task 1:`), extract task blocks via `TASK_BLOCK_RE = r"^###\s+Task\s+(\d+):\s+(.+?)$"`. Per block: extract `**Depends on:**`, `**Review status:**`, `**Integration status:**`, `**Script:**`, `**Input:**`, `**Output:**` via field-specific regexes.

- **Step 2: Parse RESULTS.md** — extract per-task results via `RESULTS_SECTION_RE = r"^##\s+Task\s+(\d+):\s+(.+?)$"`. Skip stubs (`Not started`).

- **Step 3: Generate tree** — slugify titles (`re.sub` chain → lowercase, strip non-word, hyphenate). Map `Task N` numbers to `NN-slug/` directories. Convert `Task N` depends-on references to slug names. Infer status from checkbox states and review status. Build `task.md` with frontmatter + Steps + Results body sections.

- **Step 4: Write root task.md** — header content → root `.plan/task.md` with `title: "Project Plan"` frontmatter.

---

## Results

**Status:** Completed (Task 3 approved 2026-05-23)

### Key Findings
- 307-line script parsing PLAN.md task blocks via regex `r"^###\s+Task\s+(\d+):\s+(.+?)$"`
- Correctly extracts: depends_on (maps `Task N` references to slugs), review/integration status (normalizes to lowercase enum), script/input/output (backtick-delimited file lists), step checkboxes
- Status inference from checkbox states: all checked + no review → implemented; partial checked → in-progress; review APPROVED → approved
- `slugify()` produces clean directory names (lowercase, strip non-word, hyphenate, max 60 chars)
- RESULTS.md sections merged into corresponding task.md `## Results` via task number matching; stubs (`Not started`) skipped

---

