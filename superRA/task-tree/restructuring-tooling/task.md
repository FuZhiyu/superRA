---
title: "Safe Restructuring Tooling — Dep-Rewire Hook + Placement Detector"
status: approved
depends_on: []
tags:
  - task-tree
  - cli
  - consolidation
  - placement
created: 2026-06-07
---

## Objective

Give the placement and consolidation rules a safe, repeatable *execution* substrate so the structural moves consolidation performs are dependency-safe — `depends_on` auto-handled where the fix is lossless, clearly surfaced where it needs a human decision — and so pre-existing structural debt (narrow-root, misplacement) is detectable. Today consolidation relies on raw `mv`/`rm`, and the PostToolUse hook auto-fixes only status rollups and the dashboard — it leaves `depends_on` edges broken with a warning and never renumbers prefixes.

This is the tooling half of the placement/consolidation redesign whose rules are codified in `task-tree/planning-redesign/placement-and-update-lifecycle`. That dependency is **logical and cross-tree**, so it is not expressible as a sibling `depends_on` edge under the current sibling-only model — implement after those rules are settled so the detector encodes them. (This very limitation — that a dependency between tasks in different subtrees cannot be declared — is part of the motivation for the rewire work below.)

### Scope

**1. Lossless `depends_on` rewire in the hook (YAML metadata only).** Extend `skills/task-tree/scripts/task_hook.py` (and a shared helper in `_task_io.py`) so that after a mutating Bash op the hook auto-cascades the **lossless** cases, consistent with the status-rollup it already auto-writes:

- **Same-parent rename** (`mv superRA/a/x superRA/a/y`): cascade every sibling `depends_on: x` → `y`. This is the cross-parent-refusing `task_rename.py` cascade, applied to raw `mv` by detecting the old→new slug mapping from the parsed Bash command.
- **Delete** of a depended-on task: leave the dangling edge as a *warning*, do not silently drop it. Dropping a real dependency changes execution ordering and is closer to content loss than mechanical YAML maintenance — surface it for a human/agent decision.
- **Cross-parent move and merge**: cannot be auto-rewired (a cross-tree edge is inexpressible in the sibling-only model) — warn, do not guess. These are handled deliberately by the consolidation prose procedure; **merge in particular stays manual** so the human controls how nuance from the combined tasks is integrated. No `task merge` command. (Cross-parent moves are handled by the shipped `task move` command, which the `cli-scripts` subtree provides as the canonical path-change mechanism; the prohibition here is on a `task merge` command only.)

Boundary: auto-mutate YAML metadata (`depends_on`, mirroring status), never task *content* (objectives, results). Do not auto-renumber display prefixes.

**Document the behavior for agents (so the change is not surprising).** Wherever the hook's existing auto-behaviors are described to agents — the agent-facing §Task Interface / commit-hygiene surface in `using-superRA`, and `task-tree` SKILL — state that a rename auto-cascades sibling `depends_on`, so an agent that renames a task expects the hook to re-point its dependents rather than being surprised by a silent edit. A silent auto-mutation the agent does not anticipate is the exact failure this guards against.

**2. Advisory placement/structure `task check` category.** Add a category to `skills/task-tree/scripts/task_check.py` (current categories: status, dependency, rollup) that emits **advisory** findings (warn, never auto-fix) for the structural smells that the placement ladder forbids:

- a root carrying `script` / `input` / `output` frontmatter (a leaf masquerading as the project);
- a single-child root (a wrapper around one narrow task);
- a root-level leaf sitting beside root-level branches (a narrow feature hoisted to root);
- substantial concern overlap between a task and another subtree (misplacement / duplicate candidate), to the extent detectable from objective/output fields.

These encode the positive root-task definition and the misplacement detection described in the placement task. Findings are surfaced, not auto-corrected, per the "hooks warn, not auto-mutate" principle.

### Constraints

- No new `Stage:` value — this is CLI/hook tooling, not a workflow stage.
- Reuse the existing `task_rename.py` cascade logic for the rename case rather than duplicating it; the shared rewire helper lives in `_task_io.py`.
- Add regression tests in `skills/task-tree/scripts/test_task_tree.py` for: same-parent-rename cascade via raw `mv`, delete-leaves-warning, cross-parent-move-warns, and each new `task check` advisory.
- Apply the CLAUDE.md DRY/Necessity gate line by line; keep changes local and explicit (the `path-containment` task is the precedent for a small, contained CLI hardening).

### Validation

- New tests fail on current code and pass after the change.
- Existing task-tree tests continue to pass.
- A same-parent `mv` of a depended-on task leaves no broken `depends_on`; a delete leaves a visible warning, not a silent drop.
- `task check` flags a deliberately narrow-root / single-child-root fixture as advisory and exits without auto-mutating.

## Planner Guidance

Likely splits at implementation into (a) hook + `_task_io` rewire helper and (b) the `task check` placement category — leave the split to the implement pass. The hook rewire (1) is the load-bearing piece; the detector (2) is what lets a future consolidation pass *find* the debt the placement ladder is meant to prevent. Sequence after the placement/consolidation rules are settled so the detector matches the codified definitions.

## Results

Both halves landed: the lossless `depends_on` auto-rewire in the PostToolUse hook (same-parent rename only) and the advisory `task check --category placement` detector. All edits are local CLI/hook changes plus the agent-facing docs of the new hook behavior; no new `Stage:` value, no `task merge` command (cross-parent moves use the shipped `task move` command). The full suite passes (631 tests at the time of the revise round).

### What landed

**1. Shared lossless rewire helper — [`_task_io.cascade_depends_on_rename`](../../../skills/task-tree/scripts/_task_io.py).** Re-points every sibling `depends_on: old_slug` → `new_slug` within the parent that holds both slugs, rewriting only `depends_on` YAML metadata, never task content. [`task_rename.py`](../../../skills/task-tree/scripts/task_rename.py) now delegates its cascade to this helper instead of duplicating the loop (the existence checks + same-parent guard stay in the CLI), satisfying the "reuse, do not duplicate" constraint. To keep rename + cascade atomic, the CLI parse-validates every sibling `task.md` *before* `from_dir.rename(...)`, so a malformed sibling aborts with the directory still in place rather than half-applying the cascade — restoring the pre-refactor validate-then-rename ordering.

**2. Hook auto-cascade on same-parent rename — [`task_hook.py`](../../../skills/task-tree/scripts/task_hook.py).** New `_detect_same_parent_rename` classifies a raw `mv` / `git mv` from the Bash command text as a rename only when it is a two-operand move, no flags, same parent, differing final slug, both inside a task root, with the destination holding a `task.md`. On a match `_handle_bash` calls the shared helper **before** the reconcile pass, so `validate_plan` sees the rewired edges and emits no spurious dangling-dependency warning, and the rewire is surfaced in the hook feedback so the silent edit is expected by the agent. Slugs are resolved from the command text (the source no longer exists post-move), but the rename-vs-move-into-dir disambiguation reads **post-move filesystem state**: a clean rename never leaves `dst/<src basename>/task.md` behind, whereas a move-into-an-existing-dir lands the source there — so when `(dst_abs / src_abs.name / "task.md").exists()` the classifier returns None (warn-only re-parent). This corrects an earlier mistaken claim that the two cases were indistinguishable by stat: they are, the earlier reasoning just checked the wrong path (`dst` itself, which always exists post-move, rather than `dst/<src basename>`). A bare `mv x existing-task` where `existing-task` is a pre-existing sibling task (real result `existing-task/x`) is the case the prior guard corrupted — it now correctly falls through to warn-only. Trailing-slash `mv x y/` (the explicit move-into-dir spelling), flagged `mv`, >2 operands, cross-parent moves, and deletes also fall through to the existing warn-only path.

**Scoped to the lossless case only.** Cross-parent move (cross-tree edge inexpressible in the sibling-only model), delete of a depended-on task (dropping a real edge changes execution ordering — closer to content loss than YAML upkeep), and merge (human controls nuance integration — no command) are left as dangling-dependency **warnings**, never silently rewired. This preserves the pre-existing `test_bash_mv_dangling_dep_warns_and_does_not_rewrite` behavior for re-parents.

**3. Advisory placement category — [`task_check.py`](../../../skills/task-tree/scripts/task_check.py) `check_placement`.** New `--category placement` (wired in both [`task_check.py`](../../../skills/task-tree/scripts/task_check.py) and the packaged [`cli.py`](../../../skills/task-tree/scripts/cli.py)) emits `warning`-severity findings, never auto-fixes, for the four placement-ladder smells codified in [`planning.md` §Placing Work](../../../skills/task-tree/references/planning.md):
- root carrying `script` / `input` / `output` (a leaf masquerading as the project);
- single-child root (a wrapper around one narrow task);
- a root-level leaf sitting beside root-level branches (a narrow feature hoisted to root — an all-leaf flat plan is intentionally not flagged);
- identical declared `output` artifact owned by tasks in different top-level subtrees (split-concern / duplicate candidate). Generic basenames (`README.md`, `SKILL.md`, `task.md`, …) are excluded so a shared common filename is not a false split-concern signal — only a shared *specific* artifact fires.

**4. Agent-facing docs of the new hook behavior** (so a rename's silent dep re-point is expected, not surprising), placed where the hook's existing auto-behaviors are already surfaced:
- [`using-superRA/SKILL.md` §Task Interface](../../../skills/using-superRA/SKILL.md#L46) — the universal-interface surface every executing agent preloads: the same line that documents the status cascade now also states that a same-parent rename re-points siblings' `depends_on` edges (revise round; the scope item required this surface and it was previously missing).
- [`task-tree/SKILL.md`](../../../skills/task-tree/SKILL.md) move/rename line — same-parent rename auto-cascades; cross-parent move and delete strand for re-wiring.
- [`references/commands.md` §Rename / move a task](../../../skills/task-tree/references/commands.md) — full agent-facing statement of the cascade + the non-cascading cases.
- [`references/internals.md` §Hook Architecture](../../../skills/task-tree/references/internals.md) — implementation-facing description (helper, classifier, ordering-before-reconcile, the lossless-only boundary).

The placement category itself follows the precedent of the existing categories (status/dependency/rollup): discoverable via `--category` `--help` choices, not separately documented in prose — adding a new prose surface for it would exceed precedent.

### Tests (red-green verified)

Added to [`test_task_tree.py`](../../../skills/task-tree/scripts/test_task_tree.py): same-parent-rename cascade via raw `mv` and via `git mv`; cross-parent-move-does-not-cascade (warns); delete-of-depended-on-task-warns-no-silent-drop; flagged-`mv`-does-not-cascade; `mv`-into-existing-task-dir-does-not-cascade (the bare `mv x existing-task` re-parent the prior code corrupted — asserts no silent rewire of the dependent and a dangling-dependency warning); rename-aborts-before-mutation-on-malformed-sibling (validate-then-rename atomicity); and seven placement-category tests (root leaf-fields, single-child root, root-leaf-beside-branch, all-leaf-flat-root-clean, cross-subtree output overlap, generic-output-overlap-ignored, never-mutates). Stashing the source files and running the new tests shows them failing on old code (rename-cascade + all placement tests fail; the `mv`-into-existing-dir test corrupts the dependent on old code — `02-second` rewritten to `03-third`; the atomicity test renames then crashes mid-cascade on old code; the delete-warns and cross-parent-warns tests pass on old code, confirming those behaviors are *preserved* not newly added). Two pre-existing tests (`test_json_output_parseable`, `test_task_check_autodetects_legacy_plan_root`) used single-child-root fixtures that the new check legitimately flags; their fixtures gained a second child to restore their unrelated intent. `_write_task_md` gained optional `script`/`input`/`output` kwargs for the placement fixtures.

### Verification

- `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts` → **631 passed, 2 skipped** (at the revise round; was 305 for this task's original landing).
- `superra task check --category placement --root superRA` runs against the live tree and reports "All checks passed" (the depth-1 root check is exercised by the smell-3 test on a synthetic tree); advisory-only — no auto-mutation. An earlier run over-fired on shared `README.md` outputs, which drove the generic-basename exclusion.
- DRY/Necessity gate (skill-creator unavailable, per dispatch) applied line by line to the doc edits: the rename cascade is documented once per existing surface where the hook's auto-behaviors already live, each phrased to the surface's audience (agent-facing vs implementation-facing); no new doc file or category prose surface created.
