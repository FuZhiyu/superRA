---
title: "Refactor figure attachments to task-local storage"
status: approved
depends_on:  []
tags: []
created: 2026-05-27
updated: 2026-05-27
---

## Objective

Migrate the figure attachment convention from a shared root-level `results_attachments/` directory to task-local `attachments/` directories next to each task's `task.md`. This fixes three problems: (1) embed paths don't render in task previews or the dashboard because they are root-relative, not task-relative; (2) figures leak outside `.plan/` into the project root; (3) moving a task breaks its figure references. The new convention: figures go in `attachments/` next to the task file, embedded as `attachments/fig.png`. The dashboard already resolves task-relative paths correctly (base.html line 663 computes pathPrefix from taskPath).

### Files to change

**Authoritative instruction files (7):**

1. `skills/task-system/references/planning.md` §Figure Embedding (lines 192–200) + example in results template (line 174) — rewrite to task-local `attachments/`
2. `skills/report-in-markdown/references/rich-content.md` §caller-parameter table (lines 9–15) + §Materialize figures (line 25) + §Embed example (line 48) — update Stage 1 convention from `results_attachments/` to task-local `attachments/`, fix embed example to use `ATTACH_DIR` placeholder or show context-specific examples
3. `skills/report-in-markdown/references/final-form.md` §Commit 3 (lines 37–47) — collect from task-specific `.plan/*/attachments/` directories instead of root `results_attachments/`
4. `skills/econ-data-analysis/SKILL.md` line 154 — update `[BLOCKING]` checklist from `results_attachments/` to task-local `attachments/`
5. `skills/implementation-workflow/SKILL.md` line 119 — update Step 3 verification gate
6. `agents/implementer.md` line 143 — update pre-commit checklist
7. `skills/using-superRA/references/direct-mode-implementer.md` line 138 — update pre-commit checklist

**Generated files (regenerate after source changes):**
- `.codex/agents/superra_implementer.toml` line 149

**Historical docs (`docs/plans/`):** leave as-is — they describe past work accurately.

### Design decisions

- **Task-local over unified `.plan/attachments/`:** self-contained tasks survive moves; no depth-counting for relative paths.
- **Embed syntax:** `attachments/fig.png` (relative to task.md). No `./` prefix needed.
- **Maturation (Stage 2):** Commit 3 in `final-form.md` collects from all `.plan/*/attachments/` into `${RESULTS_DIR}/attachments/`. RESULTS.md at root references figures via full task path (`.plan/task-path/attachments/fig.png`) before maturation rewrites them.
- **Dashboard:** no code changes needed — `pathPrefix` logic already prepends `.plan/{taskPath}/` to relative image `src`.

## Results

All 7 authoritative instruction files updated. Generated Codex agent files regenerated via `sync_codex_agents.py`. Zero remaining `results_attachments/` references in active files (only in historical `docs/plans/` and this task's own description).

### Files changed

| File | Change |
|---|---|
| [planning.md](../../skills/task-system/references/planning.md) | §Figure Embedding + results template example → task-local `attachments/` |
| [rich-content.md](../../skills/report-in-markdown/references/rich-content.md) | Caller-parameter table, Stage 1 description, embed example → `ATTACH_DIR` placeholder |
| [final-form.md](../../skills/report-in-markdown/references/final-form.md) | Commit 3 → collect from `.plan/*/attachments/` |
| [SKILL.md (econ-data-analysis)](../../skills/econ-data-analysis/SKILL.md) | `[BLOCKING]` checklist → task-local `attachments/` |
| [SKILL.md (implementation-workflow)](../../skills/implementation-workflow/SKILL.md) | Step 3 gate → task-local `attachments/` |
| [implementer.md](../../agents/implementer.md) | Pre-commit checklist → `attachments/...` |
| [direct-mode-implementer.md](../../skills/using-superRA/references/direct-mode-implementer.md) | Pre-commit checklist → `attachments/...` |
| `.codex/agents/superra_implementer.toml` | Regenerated from source |

### Dashboard

No code changes needed. `base.html` line 663 already computes `pathPrefix = '.plan/' + taskPath + '/'` and prepends it to relative image `src` attributes (line 678), so task-local `attachments/fig.png` resolves correctly to `/files/.plan/task-path/attachments/fig.png`.

