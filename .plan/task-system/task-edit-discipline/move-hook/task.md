---
title: "Bash-triggered task-tree revalidation (manual move support)"
status: approved
depends_on: []
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Generalize the existing PostToolUse hook so that an out-of-band structural change to a `.plan/` task tree made through the shell — primarily `mv` (re-parent / reorder a task directory), and the same risk class `rm`, `rmdir`, `cp`, `mkdir`, `git mv` — triggers the same reconcile the hook already runs after an `Edit`/`Write` on a `task.md`: validate the tree, propagate parent status, rebuild the dashboard. The point is to let agents and humans reorganize the tree with a plain `mv` and have the tree stay validated-or-flagged automatically, removing the need to run `task_rename.py` purely to keep the tree consistent.

### Why PostToolUse, not PreToolUse

The work is a reaction to a completed move — the resulting tree must exist before it can be validated, status propagated, or the dashboard rebuilt. This is the same role the hook already plays for `Edit`/`Write`. PreToolUse is for gating (allow/deny before the action, like `merge-guard`); we are not blocking `mv`. So the new behavior attaches to the existing best-effort, never-blocking, always-exit-0 PostToolUse path.

### 1. `skills/task-system/scripts/task_hook.py` — add a Bash branch

Currently the hook acts only on `Edit`/`Write` of a `task.md` and finds the plan root from `tool_input.file_path`. Add handling for `tool_name == "Bash"`:

- Read `tool_input.command` (a string). Bash gives no structured "file moved" event, so do NOT attempt to parse `mv` source/destination precisely — that parsing is fragile across `git mv`, `mv -t`, variable expansion, and `&&` chains.
- Gate to avoid firing on read-only `.plan` commands (the many `task_query.py` / `task_read.py` / `grep .plan` / `.plan/serve` invocations): act only when the command both references `.plan` and contains a filesystem-mutating verb (`mv`, `rm`, `rmdir`, `cp`, `mkdir`, `git mv`). A read-only command that merely mentions `.plan` must early-exit.
- On a gated match, locate the affected plan root(s) and run the existing reconcile: `validate_plan` (warnings to stderr, same `[task-hook]` prefix), `propagate_parent_status`, `generate_dashboard` — each best-effort in its own try/except, never fatal, always exit 0. Reuse the existing helper functions; do not duplicate their logic.
- Plan-root discovery for the Bash case: prefer extracting any `.plan`-containing path token from the command, resolving it, and walking up via `_find_plan_root` to the tree it belongs to (handles a move whose paths are explicit). Fall back to the `.plan/` under the process working directory when no resolvable token is found. De-duplicate so each distinct plan root is reconciled once.

**Explicitly do NOT auto-cascade `depends_on`.** A post-hoc hook sees only the after-state and cannot know the old slug, so it cannot safely rewrite sibling `depends_on` the way `task_rename.py` does (and cannot distinguish a rename from a re-parent or a delete). The correct behavior is to let `validate_plan` surface the now-dangling dependency as a warning; re-wiring stays an explicit human/agent action (`task_link.py` or a direct edit). Auto-rewriting references here would be a correctness hazard.

### 2. `hooks/hooks.json` — wire the Bash matcher

Add a PostToolUse entry with `"matcher": "Bash"` invoking the same `python3 "${CLAUDE_PLUGIN_ROOT}/skills/task-system/scripts/task_hook.py"` command as the existing `Edit|Write` entry. Keep the existing `Edit|Write` entry unchanged. (The merge-guard PreToolUse Bash hook is unrelated and stays as is.)

### 3. Tests — extend `skills/task-system/scripts/test_task_system.py`

Extend `TestTaskHook` (existing helper runs `task_hook.main()` with a JSON payload via stdin). Add cases:
- A Bash `mv` of a task directory within a temp `.plan/` triggers revalidation/propagation/dashboard rebuild (assert the dashboard is regenerated and/or status rolled up).
- A Bash `mv` that re-parents a task across a sibling boundary so a `depends_on` becomes dangling produces a validation warning on stderr (assert the dangling-dep warning appears) — and confirms the hook does NOT rewrite the dependency.
- A read-only `.plan` Bash command (e.g. a `task_query.py` invocation or `grep .plan`) early-exits with no reconcile side effects.
- The hook always exits 0, including when the command references no plan tree.

## Validation

`uv run` / `python3` the task-system test suite green (all existing `TestTaskHook` and plan tests still pass plus the new cases). Manually: in a scratch `.plan/`, `mv` a leaf task to a new parent and confirm the dashboard rebuilds and a dangling-dep warning prints if the move crossed a dependency edge.

## Out of scope

Codex and Cursor hook variants (`hooks/hooks-codex.json`, `hooks/hooks-cursor.json`) do not wire `task_hook.py` for `Edit`/`Write` at all today, so there is no Bash-parity change to make there; bringing those harnesses to task-validation parity is a separate, larger effort and is not part of this task. Note this asymmetry in the implementation results so it is not mistaken for an omission.

## Results

Implemented the Bash branch, wired the matcher, and added four tests. Full task-system suite green: **147 passed** (`python -m pytest test_task_system.py`), including the 4 new `TestTaskHook` Bash cases. Manual scratch-`.plan/` move confirmed: dangling-dep warning prints, parent status rolls up, `depends_on` left intact, exit 0.

### `task_hook.py`

`main()` now dispatches on `tool_name`: `Bash` → [`_handle_bash`](../../../../skills/task-system/scripts/task_hook.py#L137), `Edit`/`Write` → [`_handle_edit_write`](../../../../skills/task-system/scripts/task_hook.py#L185). The shared three-step reconcile (validate → propagate → rebuild dashboard, each in its own best-effort try/except, always exit 0) was extracted into [`_reconcile`](../../../../skills/task-system/scripts/task_hook.py#L37) so both branches call one source of truth — the `Edit`/`Write` behavior is unchanged.

Bash gating ([`_handle_bash`](../../../../skills/task-system/scripts/task_hook.py#L137)): act only when the command both contains `.plan` **and** matches a filesystem-mutating verb (`mv`, `git mv`, `rm`, `rmdir`, `cp`, `mkdir`) via `_MUTATING_RE`. A read-only command that merely mentions `.plan` (`task_query.py`, `grep .plan`, `.plan/serve`) fails the verb test and early-exits. No attempt is made to parse `mv` source/destination semantics.

**Plan-root discovery deviation from the objective.** The objective suggested resolving a `.plan` token and "walking up via `_find_plan_root`". `_find_plan_root` requires every directory on the walk to exist (it calls `.exists()`), but after a move the source path is gone and a destination may not yet be materialized in the form the token names. So instead [`_find_plan_root_for_token`](../../../../skills/task-system/scripts/task_hook.py#L112) splits the token on its first `.plan` path segment and returns the directory up to and including it — existence-independent, which is the correct behavior for post-hoc move tokens. Tokens are extracted with `_PLAN_TOKEN_RE`, resolved against `cwd`, and de-duplicated by resolved path so each distinct plan root reconciles once. When no resolvable token is found, it falls back to `cwd/.plan`.

**Whole-tree status propagation.** `propagate_parent_status` only recomputes the ancestor chain of one given `task_path`, but a structural move can change several branches at once and the hook does not know the precise post-move location. [`_propagate_whole_tree`](../../../../skills/task-system/scripts/task_hook.py#L77) walks the tree, collects every leaf path, and calls `propagate_parent_status` for each — covering all intermediate parents. The `Edit`/`Write` path still uses the single-chain call since it knows its exact `task_path`.

**No `depends_on` auto-cascade.** The hook never rewrites sibling `depends_on`. A move that strands a dependency surfaces as a `validate_plan` warning on stderr (`[task-hook]` prefix); re-wiring stays an explicit human/agent action. Verified by `test_bash_mv_dangling_dep_warns_and_does_not_rewrite`.

### `hooks.json`

Added a second `PostToolUse` entry with `"matcher": "Bash"` invoking the same `task_hook.py` command. The existing `Edit|Write` entry and the unrelated `merge-guard` PreToolUse Bash hook are unchanged.

### Tests

Added to `TestTaskHook`: `test_bash_mv_triggers_rebuild_and_propagation` (dashboard regenerated + parent rolls up to approved), `test_bash_mv_dangling_dep_warns_and_does_not_rewrite`, `test_bash_readonly_plan_command_no_side_effects`, `test_bash_command_without_plan_exits_zero`.

### Out-of-scope asymmetry confirmed

`hooks/hooks-codex.json` and `hooks/hooks-cursor.json` do not wire `task_hook.py` for `Edit`/`Write` today, so there is no Bash-parity entry to add there. This is the documented asymmetry, not an omission.
