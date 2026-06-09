---
title: "Cross-Reference Sweep and Verification"
status: not-started
depends_on: 
  - 01-reference-ownership
  - 03-dispatch-bundles
  - 04-planning-review
  - 05-consolidation-integration

tags: []
created: 2026-06-09
---

## Objective

Run the cross-reference, generated-artifact, and verification sweep after the redesign lands.

### Required Checks

- Sweep active source docs for stale references to `skills/task-system/references/planning.md`; update them to the new superplan tree-design reference or the renamed task-file contract reference as appropriate.
- Update inventory and ownership surfaces: `AGENTS.md`, `CLAUDE.md` if present as the contributor alias, `README.md`, `skills/CATEGORIES.md`, `skills/using-superRA/SKILL.md` inventory rows if needed, and deprecated handoff-doc stubs if they still point at active references.
- Update task-system diagnostics/docstrings such as `task_check.py` placement references if they cite the moved policy.
- Regenerate Codex/direct-mode artifacts when canonical role specs changed, and run the generator in check mode afterward.
- Run targeted tests for any code/docstring changes in task-system scripts, plus text or grep checks that prove stale active references are gone.
- Preserve historical task records unless an active instruction path loads them; record any intentionally retained historical citations in `## Results`.

### Validation

- `rg "task-system/references/planning.md" skills agents README.md AGENTS.md CLAUDE.md` has no active stale hits, or every remaining hit is explicitly justified as historical.
- Generated artifacts are in sync when role specs changed.
- Task-system checks still pass after any diagnostic or filename updates.

## Results
