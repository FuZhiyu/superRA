---
title: "Sweep PLAN.md/RESULTS.md references across skills"
status: implemented
review_status: implemented
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

### Scope

Swept all operational PLAN.md/RESULTS.md references and all `## Decisions` / `User Decisions Log` references across skill files, references, and supporting code. Additionally fixed the `sync_codex_agents.py` generator to handle code-fenced `##` headings and updated its pattern-matching strings to track the current `agents/implementer.md` wording.

### Files Modified

**PLAN.md/RESULTS.md sweep (40 files):**

- [`skills/using-superRA/SKILL.md`](skills/using-superRA/SKILL.md) — `PLAN.md` / `RESULTS.md` in §Runtime Workflow Map and `User Decisions Log format` in §Handoff Docs
- [`skills/econ-data-analysis/SKILL.md`](skills/econ-data-analysis/SKILL.md) — 4 operational refs (expectations comparison, implementation standards, documentation/handoff)
- [`skills/econ-data-analysis/references/planning.md`](skills/econ-data-analysis/references/planning.md) — 4 refs (Data Inventory gate, red flags)
- [`skills/econ-data-analysis/references/integrate-drift-tests.md`](skills/econ-data-analysis/references/integrate-drift-tests.md) — 4 refs (key results identification, audit trail)
- [`skills/econ-data-analysis/references/integration.md`](skills/econ-data-analysis/references/integration.md) — 1 ref (document-code consistency limitation flagging)
- [`skills/theory-modeling/SKILL.md`](skills/theory-modeling/SKILL.md) — 14 refs across all four gates and documentation/handoff (ledger artifacts, notation conventions, slot templates, common rationalizations)
- [`skills/theory-modeling/CLAUDE.md`](skills/theory-modeling/CLAUDE.md) — 1 ref (per-task ledger contributor note)
- [`skills/theory-modeling/references/planning.md`](skills/theory-modeling/references/planning.md) — 4 refs (model inventory gate, notation conventions, red flags)
- [`skills/theory-modeling/references/integration.md`](skills/theory-modeling/references/integration.md) — 7 refs (placeholder symbols, inline definition, notation pre-flight, document-code consistency, ledger survival, notation conventions table)
- [`skills/theory-modeling/references/integrate-drift-tests.md`](skills/theory-modeling/references/integrate-drift-tests.md) — 3 refs (key results identification, tolerance justification)
- [`skills/writing/SKILL.md`](skills/writing/SKILL.md) — 2 refs (project conventions lifecycle, workflow coupling)
- [`skills/writing/CLAUDE.md`](skills/writing/CLAUDE.md) — 1 ref (project conventions surface)
- [`skills/writing/references/planning.md`](skills/writing/references/planning.md) — full rewrite (header template, retrofit path, review-only marker)
- [`skills/writing/references/long-form-review.md`](skills/writing/references/long-form-review.md) — full rewrite (task tree retrofit, workflow status, review-time indices)
- [`skills/writing/references/draft.md`](skills/writing/references/draft.md) — 1 ref (workflow coupling)
- [`skills/writing/references/polish.md`](skills/writing/references/polish.md) — 2 refs (review-findings input shapes)
- [`skills/writing/references/structure.md`](skills/writing/references/structure.md) — 1 ref (handoff documentation)
- [`skills/writing/references/integration.md`](skills/writing/references/integration.md) — 2 refs (outline stability, scope respected)
- [`skills/semantic-merge/SKILL.md`](skills/semantic-merge/SKILL.md) — 7 refs (description, intent investigation, escalation, logging, coherence checklist, handoff docs)
- [`skills/semantic-merge/references/workflow-sync-author.md`](skills/semantic-merge/references/workflow-sync-author.md) — 5 refs (inputs, process, sync map format, task-local impact)
- [`skills/semantic-merge/references/workflow-sync-reviewer.md`](skills/semantic-merge/references/workflow-sync-reviewer.md) — 4 refs (inputs, process, verdict)
- [`skills/semantic-merge/references/standalone-merge.md`](skills/semantic-merge/references/standalone-merge.md) — 3 refs (inputs, process, merge record)
- [`skills/report-in-markdown/SKILL.md`](skills/report-in-markdown/SKILL.md) — 4 refs (description, body, load map, references)
- [`skills/report-in-markdown/references/baseline-io.md`](skills/report-in-markdown/references/baseline-io.md) — 3 refs (load condition, filename, git_dirty note)
- [`skills/report-in-markdown/references/rich-content.md`](skills/report-in-markdown/references/rich-content.md) — 2 refs (attachment directory cases)
- [`skills/report-in-markdown/references/final-form.md`](skills/report-in-markdown/references/final-form.md) — 3 operational refs (task-path indexing, exception, methodology)
- [`skills/refactor-and-integrate/SKILL.md`](skills/refactor-and-integrate/SKILL.md) — 2 refs (sync impact context, final diff self-check)
- [`skills/agent-orchestration/references/agent-teams.md`](skills/agent-orchestration/references/agent-teams.md) — 6 refs (task graph, dispatch, session handoff, checkpointing)

**`## Decisions` / `User Decisions Log` sweep:**

- [`skills/implementation-workflow/SKILL.md`](skills/implementation-workflow/SKILL.md) — 3 refs replaced with "fold into task objective" pattern
- [`skills/integration-workflow/SKILL.md`](skills/integration-workflow/SKILL.md) — 6 refs replaced with "fold into task objective" or "record in root task.md"
- [`skills/semantic-merge/SKILL.md`](skills/semantic-merge/SKILL.md) — 2 refs replaced with "fold into task objective"
- [`skills/result-protection/references/drift-test-quality.md`](skills/result-protection/references/drift-test-quality.md) — 1 ref replaced
- [`skills/handoff-doc/SKILL.md`](skills/handoff-doc/SKILL.md) — 1 ref updated (deprecated skill redirect)

**Code and data model updates:**

- [`skills/task-system/scripts/_task_io.py`](skills/task-system/scripts/_task_io.py) — added `revision_notes` field to `Task` dataclass, kept `decisions` as legacy
- [`skills/task-system/scripts/task_query.py`](skills/task-system/scripts/task_query.py) — added `revision_notes` to JSON output
- [`skills/task-system/references/internals.md`](skills/task-system/references/internals.md) — updated data model docs with `revision_notes` field, marked `decisions` as legacy
- [`skills/task-system/scripts/test_task_system.py`](skills/task-system/scripts/test_task_system.py) — added `revision_notes` to JSON key test and body-sections parse test

**Generator fix and regeneration:**

- [`skills/codex-superra-setup/scripts/sync_codex_agents.py`](skills/codex-superra-setup/scripts/sync_codex_agents.py) — fixed `split_top_level_sections` to skip `##` headings inside code fences; updated `source_opener` and `direct_opener` pattern strings to match current `agents/implementer.md` wording
- [`skills/using-superRA/references/direct-mode-implementer.md`](skills/using-superRA/references/direct-mode-implementer.md) — regenerated (clean of PLAN.md/RESULTS.md)
- [`skills/using-superRA/references/direct-mode-reviewer.md`](skills/using-superRA/references/direct-mode-reviewer.md) — regenerated (clean of PLAN.md/RESULTS.md and `## Decisions`)
- [`.codex/agents/superra_implementer.toml`](.codex/agents/superra_implementer.toml) — regenerated
- [`.codex/agents/superra_reviewer.toml`](.codex/agents/superra_reviewer.toml) — regenerated

**Contract test update:**

- [`tests/test-sync-integration-contract.sh`](tests/test-sync-integration-contract.sh) — updated PLAN-only retrofit marker pattern to match new `(review-only; no ## Results)` wording

### Verification

`grep -rn 'PLAN\.md\|RESULTS\.md' skills/ --include='*.md'` remaining matches are only:
- `task-system/` — migration tool references (correct)
- `CATEGORIES.md` — inventory description (correct)
- `using-superRA/SKILL.md:63` — skill inventory mentioning migration feature (correct)
- `main-agent.md:19` — backward-compatibility migration offer (correct)
- `planning-workflow/SKILL.md:32` — legacy PLAN.md detection (correct)
- `report-in-markdown/references/final-form.md` — literal `RESULTS.md` output file artifact (correct)
- `report-in-markdown/references/baseline-io.md` — literal `RESULTS.md` filename (correct)

`grep -rn '## Decisions\|User Decisions Log' skills/ agents/ --include='*.md'` returns only `internals.md:30` (data model field comment marked `(legacy)`).

All 92 task-system tests pass. `sync_codex_agents.py --check` passes. Contract tests show 48 passed / 6 failed (all 6 pre-existing).
