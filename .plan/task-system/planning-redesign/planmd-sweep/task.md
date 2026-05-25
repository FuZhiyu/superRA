---
title: "Sweep PLAN.md/RESULTS.md references across skills"
status: not-started
review_status: ~
integration_status: ~
depends_on: 
  - main-agent-update
  - revision-notes

tags: []
created: 2026-05-24
updated: 2026-05-24
---

## Objective

Update all remaining operational references to PLAN.md/RESULTS.md across skill files and references. After this task, `grep -rn 'PLAN\.md' skills/` should return only migration/historical references (in `task-system` and `CATEGORIES.md`), not operational references.

### Files and Changes

**`skills/using-superRA/SKILL.md`** (1 line)
- Line 22: "creates or revises `PLAN.md` / `RESULTS.md`" → "creates or revises the `.plan/` task tree"

**`skills/econ-data-analysis/SKILL.md`** (4 lines)
- Line 120: "`PLAN.md` expectations comparison" → "task objective expectations comparison"
- Line 145: "what `PLAN.md` specifies" → "what the task objective specifies"
- Line 152: "`RESULTS.md` updated in place" → "task `## Results` updated in place"
- Line 154: "embedded in `RESULTS.md`" → "embedded in task `## Results`"

**`skills/econ-data-analysis/references/planning.md`** (4 lines)
- Line 10: "live in `PLAN.md` as sections" → "live in root `.plan/task.md` as sections"
- Line 16: "becomes the Data Inventory section of `PLAN.md`" → "becomes the `## Data Inventory` section of root `.plan/task.md`"
- Line 60: "becomes part of `PLAN.md`" → "becomes part of root `.plan/task.md`"
- Line 67: "written into `PLAN.md`" → "written into root `.plan/task.md`"

**`skills/econ-data-analysis/references/integrate-drift-tests.md`** (4 lines)
- Line 5: "pull candidate invariants out of `RESULTS.md`" → "pull candidate invariants out of task `## Results` sections"
- Line 21: "Identifying Key Results from `RESULTS.md`" → "Identifying Key Results from Task Results"
- Line 23: "read `RESULTS.md` and extract candidates" → "read task `## Results` sections and extract candidates"
- Line 32: "PLAN.md / RESULTS.md" → "task files"

**`skills/econ-data-analysis/references/integration.md`** (1 line)
- Line 14: "flag unreconciled inconsistencies in `RESULTS.md` §Limitations" → "flag unreconciled inconsistencies in the task's `## Results` §Limitations"

**`skills/theory-modeling/references/planning.md`** (4 lines)
- Line 9: "becomes the Model Inventory / Assumption Map section of `PLAN.md`" → "becomes the `## Model Inventory / Assumption Map` section of root `.plan/task.md`"
- Line 31: "Write it into `PLAN.md` as a dedicated header section" → "Write it into root `.plan/task.md` as a dedicated header section"
- Line 84: "written into `PLAN.md`" → "written into root `.plan/task.md`"
- Line 87: "written into `PLAN.md`" → (same)

**`skills/writing/references/planning.md`** — throughout, update PLAN.md → root `.plan/task.md`, RESULTS.md → task `## Results`. The PLAN-only long-form review retrofit path simplifies naturally: review findings go in each task's `## Review Notes` section.

### Direct-Mode References (generated files)
`skills/using-superRA/references/direct-mode-implementer.md` and `direct-mode-reviewer.md` are generated from `agents/implementer.md` and `agents/reviewer.md` via `sync_codex_agents.py`. Since the canonical agent specs are already .plan/-native, regeneration should produce .plan/-native direct-mode refs. Verify by running the generator and checking output.

### Verification
Run `grep -rn 'PLAN\.md\|RESULTS\.md' skills/ --include='*.md'` and confirm remaining matches are only in:
- `task-system/` (migration tool references — correct)
- `CATEGORIES.md` or inventory descriptions (historical — correct)
- Any "migration from PLAN.md" documentation (correct)

## Results

