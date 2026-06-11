---
title: "Cross-Reference Sweep and Verification"
status: approved
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

- Sweep active source docs for stale references to `skills/task-tree/references/planning.md`; update them to the new superplan tree-design reference or the renamed task-file contract reference as appropriate.
- Update inventory and ownership surfaces: `AGENTS.md`, `CLAUDE.md` if present as the contributor alias, `README.md`, `skills/CATEGORIES.md`, `skills/using-superRA/SKILL.md` inventory rows if needed, and deprecated handoff-doc stubs if they still point at active references.
- Update task-tree diagnostics/docstrings such as `task_check.py` placement references if they cite the moved policy.
- Regenerate Codex/direct-mode artifacts when canonical role specs changed, and run the generator in check mode afterward.
- Run targeted tests for any code/docstring changes in task-tree scripts, plus text or grep checks that prove stale active references are gone.
- Preserve historical task records unless an active instruction path loads them; record any intentionally retained historical citations in `## Results`.

### Validation

- `rg "task-tree/references/planning.md" skills agents README.md AGENTS.md CLAUDE.md` has no active stale hits, or every remaining hit is explicitly justified as historical.
- Generated artifacts are in sync when role specs changed.
- Task-system checks still pass after any diagnostic or filename updates.

## Results

### Cross-Reference Sweep

- Active source/docs grep is clean: `rg -n "task-tree/references/planning\.md|skills/task-tree/references/planning\.md|references/planning\.md\)" skills agents README.md AGENTS.md CLAUDE.md .codex -g '!skills/task-tree/scripts/vendor/**'` returned no matches.
- The old task-tree planning reference is gone from the active reference directory: [task-file-contract.md](../../../../../skills/task-tree/references/task-file-contract.md) and [task-tree-design.md](../../../../../skills/superplan/references/task-tree-design.md) are the live owners, and `test -e skills/task-tree/references/planning.md` exited 1.
- Ownership and inventory surfaces already point at the split owners: [AGENTS.md](../../../../../CLAUDE.md#L88), [CLAUDE.md](../../../../../CLAUDE.md#L88), [README.md](../../../../../README.md#L97), [CATEGORIES.md](../../../../../skills/CATEGORIES.md#L45), [task-tree/SKILL.md](../../../../../skills/task-tree/SKILL.md#L75), and [handoff-doc/SKILL.md](../../../../../skills/handoff-doc/SKILL.md#L11).
- The task-tree diagnostic placement reference already points at the superplan tree-design owner: [task_check.py](../../../../../skills/task-tree/scripts/task_check.py#L224).

### Generated Artifacts and Tests

- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` confirmed `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`, `skills/using-superRA/references/direct-mode-implementer.md`, and `skills/using-superRA/references/direct-mode-reviewer.md` are in sync with [implementer.md](../../../../../agents/implementer.md) and [reviewer.md](../../../../../agents/reviewer.md).
- `uv run --with pytest --with pyyaml python -m pytest skills/task-tree/scripts/test_task_tree.py -q -k task_check` passed: 4 tests passed, 321 deselected.
- No generated artifacts, active skill files, role specs, or task-tree scripts required edits in this final sweep.

### Historical Records Retained

- `rg -n "task-tree/references/planning\.md|skills/task-tree/references/planning\.md" . -g '!skills/task-tree/scripts/vendor/**' -g '!.git/**'` still returns hits under `superRA/` task records. I intentionally retained those task-record citations as historical provenance, including prior tasks that implemented the old file and this task's own objective naming the obsolete path as the sweep target. They are not active source instruction paths.
- The pre-existing unrelated deletion of `skills/task-tree/.gitignore` was ignored as instructed: it was not restored, edited, staged, or committed.
