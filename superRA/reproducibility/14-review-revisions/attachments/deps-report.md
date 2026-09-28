# Design review: effective task dependencies and reproduction hooks

Branch `skills/reproducibility` at 7d5fa992. The scratch fixtures (`s1`–`s9`, `h1`–`h3`) were session-local and are not retained. [V] means I ran it. [I] means I inferred it from the code.

## What works as specified [V]
- **Edge kinds and cycle handling.** Inferred-only, logical-only and duplicate-origin edges render as `inferred`, `logical`, and `inferred, logical`. `dep remove d a` prints "Inferred dependency remains." Grouping and mixed-source cycles produce witnesses with the file or declaration. Frontier and `repro build --dry-run` refuse to run.
- **Moves and logical edges.** A move that would create a cycle is refused with a clean `git status`, so nothing is written. A logical-only dependency does not pull the producer into `repro build c` (s9).
- **Failed variable resolution.** A bad `${VAR}` shell makes the frontier exit 1 instead of showing tasks as ready.

## Major

**M1. Any error anywhere freezes planning, not just the frontier.** [V s4, s4b]
- **Cause:** `compose(complete=resolve_vars and not any(error))` (_repro.py:1244) runs, then `dependencies.findings` is overwritten with every reproduction finding (:1247). After that, `valid` is false whenever any reproduction error exists.
- **Cause:** `preflight` → `require_valid` (_task_snapshot.py:9-20) rejects the proposed tree even when the error already existed before the edit.
- **Result:** with one unset env var (`DATA: {env: …}`), `task frontier`, `task create c`, `task move b b2` and `task dep add` all fail. Only non-archive `update` still works. On a Dropbox-synced tree used across three machines, an env var that exists only on one machine locks the task tree on the other two.
- **Fix:** have preflight reject only errors the edit introduces (compare error sets before and after). Scope `valid` to dependency-affecting errors. Report the frontier as degraded for the affected tasks only.

**M2. Parent-owned steps are kept as separate nodes only at their own task's level.** [V s8, s8b; _task_dependencies.py:185-192]
- **Cause:** at the grandparent level, `project()` merges the parent's own steps into `task:P`.
- **Over-blocking:** P's `report` step reads `q.txt` from sibling Q. That blocks P's unrelated child `P/c`, which has no steps.
- **False cycle:** a common setup is `paper` (owns a `tables` step) → `robustness` → `paper/estimate`. It is rejected as `paper→robustness→paper` even though the step graph has no cycle, and the whole frontier then dies.
- **Why it matters:** the design forbids merging parent-owned steps into one virtual prerequisite that fabricates a cycle. That rule holds only one level deep.
- **Fix:** keep the parent's own steps as separate nodes at every level, or only lift the producer and consumer steps that are actually involved. An edge whose consumer is a parent-owned step should block only that step.

**M3. Readiness uses two different rules.** [V s2b, s3a, s7, live repo]
- **The two rules:** a prerequisite from another branch is satisfied by *status*. `a` is `implemented` with its output never built, and `b` is still ready. A parent→child prerequisite is satisfied only when the step is *fresh*.
- **In-progress work drops off:** editing `setup.sh` removes the in-progress `P/c` from the frontier and puts `P [own work: setup]` in its place.
- **Inconsistent "own work":** own-work lists stale steps for approved *parents* but never for approved *leaves*. In a fully approved tree (s7) only the root's own step shows. In this repo, `task frontier` lists only `scalable-navigation`'s two stale checks. The stale or missing `dag-design`, `02-agent-signals` and `edit-detection` steps (all approved leaves) are invisible.
- **Why it matters:** this is where "file edges govern replay" leaks into development gating.
- **Fix:** gate development by status everywhere. Report stale or missing steps through `repro status` or a separate "rerun" list, not the frontier.

**M4. Adding a subtask silently un-approves the parent and blocks downstream work.** [V s6]
- **Example:** `task create data/extra-check` on an approved `data` task rewrites `data/task.md` to `status: not-started`.
- **Effect:** the in-progress `analysis` task leaves the frontier because it is "blocked by task:data (not-started)", even though `panel.txt` is unchanged.
- **Why it matters:** this follows the specified status roll-up, but combined with inferred edges it is the biggest surprise for researchers. Deciding readiness from the producing step, not the rolled-up status, would avoid it.

**M5. The edit hook misses some producer edits.** [V h1]
- **Detection itself is sound:** Bash heredoc and `sed` edits are caught by a content baseline, not by parsing the command (_edit_detect.py). A heredoc edit to `Code/build.py` fired correctly.
- **Miss 1: `${VAR}` dependencies.** Both `sed` and Edit on `${CODE}/est.jl` are silent, even when `CODE: Code` is a plain literal. `resolve_vars=False` skips all variables. `_repro_watched_files` drops `${` paths (task_hook.py:872), and `_repro_owning_steps` cannot match them. The docstring claim that such a dependency "cannot name a real producer file" is wrong.
- **Miss 2: directory dependencies.** A Bash edit inside dependency directory `Code/lib` is silent; the Edit tool catches it. `is_file()` filters the watch list (:875).
- **Miss 3: the first hooked call.** The first Bash/Edit/Write call of a session only seeds the baseline, so an edit in that call is missed.
- **Miss 4: new scripts outside `superRA/`.** A new `Code/new_producer.py` is silent. The "register a new step" reminder only covers scripts inside the task root.
- **Fix:** resolve literal and `env:` variables in the hook (no subprocess needed). Walk directory dependencies with a size limit. Seed the baseline at UserPromptSubmit or SessionStart.

## Minor
- **`task tree --json` always reports incomplete.** It emits `effective_depends_on: null, dependencies_complete: false`, even on a valid tree with no config (s1), because `resolve_vars=False` forces `complete=False` (task_query.py:271, _repro.py:1245). [V]
- **Hook noise on task files.** Every `task.md` edit repeats tree-wide dependency warnings (for example "archived prerequisite 'G2'") and the communicate reminder, whatever task was edited (task_hook.py:538-540). [V h3]
- **Archiving can be used to skip readiness.** Archiving producer G2 immediately puts consumer `m` on the frontier while its input is missing. `repro build m --dry-run` then prints a failure *and* "Nothing to execute: every selected step is fresh". [V s5]
- **Messages don't explain edge kinds.** Human-readable `task read` lists effective dependencies without their kind or file. `dep remove b a` on an inferred-only edge says "a is not in depends_on" without explaining that the edge is inferred. [V]
- **Hook cost is acceptable.** About 40 ms per no-op Bash call (python), 57 ms through the shim, and 160–200 ms when a `task.md` edit triggers reconcile on the 99-task tree. [V]

## Single-sourcing (Q3)
- **Shared:** read, frontier, dag, check, preflight and the dashboard all use `build_graph`, then `compose`. [I]
- **Not shared, point 1:** the hook and `tree --json` build a different snapshot with variables left unresolved.
- **Not shared, point 2:** readiness state comes from `own_step_states` for the frontier. `task read` additionally runs `compute_status` over all steps. The dashboard computes no readiness at all.
- **Parallel implementations still exist:** `_task_io.compute_frontier` / `_collect_frontier` (only tests call them), `_task_validate.detect_cycles` / `validate_dependencies` (only `dependencies=True`, which nothing calls), `task_query.print_frontier` (unused), and the dashboard's fallback to authored `depends_on` (plan_dashboard.py:1000-1004).

## Q1 verdict
The split is coherent for replay: logical edges never become file inputs. For development it breaks down in three places: freshness gating on parent→child edges (M3), parent-owned steps merged at outer levels (M2), and status roll-up on inferred edges (M4).

## Simplify
1. **Frontier:** one readiness rule based on status. Take own-work out of the frontier.
2. **Hierarchy:** keep parent-owned steps as separate nodes at every level (fixes M2's over-blocking and false cycles).
3. **Validity:** preflight compares error sets before and after the edit. `valid` covers dependency errors only.
4. **Dead code:** delete the legacy frontier, cycle-detection and fallback-edge paths listed above.
5. **Hook:** resolve non-shell variables and seed the baseline at session start. Keep "once per file" but also clear the marker after a successful build.
