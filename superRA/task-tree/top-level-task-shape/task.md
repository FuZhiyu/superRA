---
title: "Unprivilege Top-Level Tasks; Make Umbrella task.md Optional"
status: approved
depends_on:  []
---

## Objective

Redefine the canonical superRA/ task shape so top-level tasks (direct children of superRA/) are the default, unprivileged unit: no umbrella superRA/task.md is required, and a top-level task carries no scope requirement (it may be a narrow leaf or a broad branch, same as any nested task). When an umbrella task.md exists, it is an ordinary task like any other, used only when a shared Objective/Context genuinely spans every top-level task (Context Distillation's lowest-ancestor rule applies to it too). Propagate this shape and the resulting terminology change ("top-level task", not "root-level task") through every skill, workflow entry-gate, and doc that assumed a required umbrella, and drop the task_check.py placement smells that treated top-level position as requiring broad scope.

## Results

### Key Findings

- Added `## Tree Shape` to `task-tree/references/task-file-contract.md`: top-level task dirs are the default; umbrella `superRA/task.md` is optional and, when present, ordinary. "Top-level task" is positional only, no scope privilege.
- Dropped the two `task_check.py` placement smells that encoded the old privilege (single-child-root wrapper, leaf-beside-branch) — they only made sense if top-level position implied required scope. Removed the now-empty `check_placement`, the `placement` check category (`task_check.py`, `cli.py`, `commands.md`), and `is_forest` threading that existed only to feed it. Forest detection itself (`_task_io.py`, `_worktree_discovery.py`, dashboard) is untouched.
- Fixed workflow entry-gates that hard-required the umbrella file instead of checking for a valid tree: `superimplement/SKILL.md` Step 0b (`[ -f superRA/task.md ]` → checks for umbrella-or-top-level-task-dirs), `using-superra/references/main-agent.md` (dropped the "umbrella missing → enter superplan" trigger, generalized to tree-missing).
- Reworded "root-level task" → "top-level task" and dropped scope-implying language ("workstream") at every prose site: `superplan/SKILL.md` (placement default, handoff test, user-review note), `superplan/references/task-tree-design.md` (descent algorithm now starts from the top-level task set rather than "root's children"; anti-pattern reworded), root `CLAUDE.md`/`AGENTS.md`/`AGENT.md` terminology section, `docs/site/05-workflows/01-plan/task.md`.
- `theory-modeling`/`superimplement`: "root task.md's Notation Conventions table" → "the canonical Notation Conventions table" (umbrella when one exists, else the nearest shared ancestor) — same shape rule, no special case, in `theory-modeling/SKILL.md`, `theory-modeling/CLAUDE.md`, `theory-modeling/references/integration.md`.

### Notes

- Full `task-tree` script suite passes: 689 passed (`uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`). Removed/adjusted tests that existed only to dodge the deleted placement smells (`test_task_tree.py`).
- Pre-existing, unrelated line-number anchor drift found but not fixed: `theory-modeling/references/integration.md`'s `[skills/superimplement/SKILL.md:135]` link was already stale before this task (points at a numbered completion-menu option, not the promotion paragraph it cites) and drifted one further line from the Step 0b edit above. Out of scope for this task.
- Fix round: adopted "the governing ancestor task" as the one phrase for "wherever shared context for this scope lives," replacing the umbrella/fallback elaboration this task had introduced at several sites (`theory-modeling/SKILL.md:66`, plus the reviewer's five findings) — the split is fully owned by `task-tree/references/task-file-contract.md` §Tree Shape, so consuming skills point at "the governing ancestor task" without re-deriving which structural form it takes.
- Own re-sweep beyond the reviewer's five findings surfaced two more sites with the same "top/root `superRA/task.md`" phrasing the original grep missed (backtick-adjacent path, not the literal string "root task.md"): `econ-data-analysis/references/planning.md:10` and `writing/SKILL.md:38` + `writing/references/planning.md:13`. Fixed with the same "governing ancestor task" wording.
- Full `task-tree` script suite re-run after the fix round (no code touched this round, prose only): still 689 passed.
