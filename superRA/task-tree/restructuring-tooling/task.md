---
title: "Safe Restructuring Tooling — Dep-Rewire Hook"
status: approved
depends_on: []
---

## Objective

Give the placement and consolidation rules a safe, repeatable *execution* substrate so the structural moves consolidation performs are dependency-safe — `depends_on` auto-handled where the fix is lossless, clearly surfaced where it needs a human decision.

**Lossless `depends_on` rewire in the hook (YAML metadata only).** After a mutating Bash op, the PostToolUse hook auto-cascades the lossless case, consistent with the status rollup it already auto-writes:

- **Same-parent rename** (`mv superRA/a/x superRA/a/y`): cascade every sibling `depends_on: x` → `y`. This is the cross-parent-refusing `task_rename.py` cascade, applied to raw `mv` by detecting the old→new slug mapping from the parsed Bash command.
- **Delete** of a depended-on task: leave the dangling edge as a *warning*, never silently drop it — dropping a real dependency changes execution ordering and is closer to content loss than mechanical YAML maintenance.
- **Cross-parent move and merge**: cannot be auto-rewired (a cross-tree edge is inexpressible in the sibling-only model) — warn, do not guess. Cross-parent moves use the shipped `task move` command; merge stays manual (no `task merge` command) so the human controls how nuance from the combined tasks integrates.

Boundary: auto-mutate YAML metadata (`depends_on`, mirroring status), never task *content*. Do not auto-renumber display prefixes.

Wherever the hook's existing auto-behaviors are described to agents (the §Task Interface surface in `using-superra`, and `task-tree` SKILL), state that a rename auto-cascades sibling `depends_on`, so an agent that renames a task expects the hook to re-point its dependents rather than being surprised by a silent edit.

### Constraints

- No new `Stage:` value — this is CLI/hook tooling, not a workflow stage.
- Reuse the existing `task_rename.py` cascade logic rather than duplicating it; the shared rewire helper lives in `_task_io.py`.
- Add regression tests in `skills/task-tree/scripts/test_task_tree.py` for same-parent-rename cascade via raw `mv`, delete-leaves-warning, and cross-parent-move-warns.

## Results

The dep-rewire hook is the durable capability this task owns. (An advisory `task check --category placement` detector originally landed here too, but it was later removed with the top-level-task privilege it encoded — see the parent [task-tree/task.md](../task.md) `## Results`; it is not a current capability.) All edits are local CLI/hook changes plus agent-facing docs of the new hook behavior; the full suite passes.

### What landed

- **Shared lossless rewire helper — `_task_io.cascade_depends_on_rename`.** Re-points every sibling `depends_on: old_slug` → `new_slug` within the parent that holds both slugs, rewriting only `depends_on` YAML metadata, never task content. `task_rename.py` delegates its cascade to this helper (the existence checks + same-parent guard stay in the CLI). To keep rename + cascade atomic, the CLI parse-validates every sibling `task.md` *before* the directory rename, so a malformed sibling aborts with the directory still in place rather than half-applying the cascade.
- **Hook auto-cascade on same-parent rename — `task_hook.py`.** `_detect_same_parent_rename` classifies a raw `mv` / `git mv` as a rename only when it is a two-operand move, no flags, same parent, differing final slug, both inside a task root, with the destination holding a `task.md`. On a match the shared helper runs *before* the reconcile pass, so `validate_plan` sees the rewired edges and emits no spurious dangling-dependency warning, and the rewire is surfaced in hook feedback. The rename-vs-move-into-dir disambiguation reads post-move filesystem state: when `dst/<src basename>/task.md` exists (a move into an existing dir), the classifier returns None (warn-only re-parent). Trailing-slash `mv x y/`, flagged `mv`, more-than-two operands, cross-parent moves, and deletes all fall through to the existing warn-only path.
- **Scoped to the lossless case only.** Cross-parent move, delete of a depended-on task, and merge are left as dangling-dependency warnings, never silently rewired.
- **Agent-facing docs** of the new hook behavior, placed where the hook's existing auto-behaviors are already surfaced: `using-superra/SKILL.md §Task Interface` (the same line that documents the status cascade now also states the same-parent-rename `depends_on` re-point), the `task-tree/SKILL.md` move/rename line, `references/commands.md §Rename / move a task`, and the implementation-facing `references/internals.md §Hook Architecture`.

Regression tests in `skills/task-tree/scripts/test_task_tree.py` cover the same-parent-rename cascade (raw `mv` and `git mv`), cross-parent-move-warns, delete-warns-no-silent-drop, flagged-`mv`-does-not-cascade, `mv`-into-existing-task-dir-does-not-cascade, and rename-aborts-before-mutation-on-malformed-sibling (validate-then-rename atomicity), all red-green verified against the pre-change code.
