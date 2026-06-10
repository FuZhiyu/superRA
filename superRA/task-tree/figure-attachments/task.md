---
title: "Refactor figure attachments to task-local storage"
status: approved
depends_on: []
tags: []
created: 2026-05-27
---

## Objective

Migrate the figure attachment convention from a shared root-level `results_attachments/` directory to task-local `attachments/` directories next to each task's `task.md`. This fixes three problems: (1) embed paths don't render in task previews or the dashboard because they are root-relative, not task-relative; (2) figures leak outside `.plan/` into the project root; (3) moving a task breaks its figure references. The new convention: figures go in `attachments/` next to the task file, embedded as `attachments/fig.png`. The dashboard already resolves task-relative paths correctly (base.html line 663 computes pathPrefix from taskPath).

### Files to change

**Authoritative instruction files (current):**

1. `skills/task-tree/references/task-file-contract.md` §Figure Embedding + §Results Shape example — rewrite to task-local `attachments/` (this content was in the now-removed `planning.md` when the work was done; it has since moved to `task-file-contract.md`)
2. `skills/report-in-markdown/references/rich-content.md` §caller-parameter table (lines 9–15) + §Materialize figures (line 25) + §Embed example (line 48) — update Stage 1 convention from `results_attachments/` to task-local `attachments/`, fix embed example to use `ATTACH_DIR` placeholder or show context-specific examples
3. `skills/econ-data-analysis/SKILL.md` line 154 — update `[BLOCKING]` checklist from `results_attachments/` to task-local `attachments/`
4. `skills/superimplement/SKILL.md` line 119 — update Step 3 verification gate
5. `agents/implementer.md` line 143 — update pre-commit checklist
6. `skills/using-superRA/references/direct-mode-implementer.md` line 138 — update pre-commit checklist

**Legacy authority removed by [task-tree/planning-redesign/planmd-sweep](../task-tree/planning-redesign/planmd-sweep/task.md):**
- `skills/report-in-markdown/references/final-form.md` formerly owned Stage 2 final-results relocation. Current Stage 2 task-result maturation lives in `skills/task-tree/references/task-file-contract.md` §Results Shape (the figure-embedding/results-shape content moved here from the removed `planning.md`); tree-design judgment lives in `skills/superplan/references/task-tree-design.md`; figure mechanics live in `skills/report-in-markdown/references/rich-content.md` §Figures.

**Generated files (regenerate after source changes):**
- `.codex/agents/superra_implementer.toml` line 149

**Historical docs (`docs/plans/`):** leave as-is — they describe past work accurately.

### Design decisions

- **Task-local over unified `.plan/attachments/`:** self-contained tasks survive moves; no depth-counting for relative paths.
- **Embed syntax:** `attachments/fig.png` (relative to task.md). No `./` prefix needed.
- **Maturation (Stage 2):** selected task `## Results` sections mature in place under `skills/task-tree/references/task-file-contract.md` §Results Shape. Task figures stay in task-local `attachments/` unless a caller explicitly chooses another directory per `skills/report-in-markdown/references/rich-content.md` §Figures.
- **Dashboard:** no code changes needed — `pathPrefix` logic already prepends `.plan/{taskPath}/` to relative image `src`.

## Results

Current attachment guidance is task-local: task results embed figures from `attachments/` next to each `task.md`, Stage 2 maturation keeps selected results in task files, and rich-content figure mechanics treat `attachments/` as a caller-supplied directory. Generated Codex agent files were regenerated via `sync_codex_agents.py`. Zero remaining active `results_attachments/` references outside legacy migration or historical records.

### Files changed

| File | Change |
|---|---|
| [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) | §Figure Embedding + §Results Shape example → task-local `attachments/` (content has since moved here from the removed `planning.md`) |
| [rich-content.md](../../../skills/report-in-markdown/references/rich-content.md) | Caller-parameter table, Stage 1 description, embed example → `ATTACH_DIR` placeholder |
| [SKILL.md (econ-data-analysis)](../../../skills/econ-data-analysis/SKILL.md) | `[BLOCKING]` checklist → task-local `attachments/` |
| [SKILL.md (superimplement)](../../../skills/superimplement/SKILL.md) | Step 3 gate → task-local `attachments/` |
| [implementer.md](../../../agents/implementer.md) | Pre-commit checklist → `attachments/...` |
| [direct-mode-implementer.md](../../../skills/using-superRA/references/direct-mode-implementer.md) | Pre-commit checklist → `attachments/...` |
| `.codex/agents/superra_implementer.toml` | Regenerated from source |

### Dashboard

The dashboard resolves task-local figure embeds without any change to this task's convention. In served mode, `renderMarkdown` rewrites a relative image `src` to `/files/<ROOT_PREFIX>/<taskPath>/<src>` ([base.html:1834](../../../skills/task-tree/scripts/templates/base.html#L1834)) — built from the resolved-root basis (`rootRel` + `taskDirRel`), so `attachments/fig.png` next to a `task.md` resolves to e.g. `/files/superRA/<task-path>/attachments/fig.png` and is served by the `/files/` route. (This paragraph originally claimed a `pathPrefix = '.plan/' + taskPath + '/'` variable required no change; the task root was since renamed `.plan/` → `superRA/` and the path basis was reworked to the resolved-root delink — that delink also briefly shipped a dangling `pathPrefix` reference, fixed under [02-file-link-consistency](../dashboard/live-server/path-basis-consistency/02-file-link-consistency/task.md). The current resolution is the `/files/<ROOT_PREFIX>/<taskPath>/<src>` form above, covered by `TestRenderMarkdownImageRewrite`.)

