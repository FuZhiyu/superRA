---
title: "PostToolUse Reminder When a Producer Changes Without Its Step"
status: approved
depends_on: [01-section-contract]
---

## Objective

Extend the task hook so an edit to a maintained producer that leaves the graph untouched gets a non-blocking reminder in the same turn.

- **Trigger:** the changed file is a dep or script of a registered step, or a script under the task root that no step registers. A step's out and a task file never trigger. Which files changed comes from the tool-agnostic detector in [edit-detection](../../task-tree/edit-detection/task.md), which also retired `code_roots`.
- **Suppression:** one reminder per file per session, recorded as a marker in the runner's gitignored state directory keyed on the `session_id` the Claude Code payload carries; a harness whose payload has no session id (verify Codex's) keys the marker on a one-hour window per file instead. Editing a `## Reproduction` section clears the markers for the files that section's steps name.
- **Message:** names the file, the owning step(s) if any, and the duty: update the step's deps/outs or register a new step, then run `superra repro status`.
- **Parity:** the Claude hook and the Codex hook manifest emit the same reminder; both remain fail-open when the tree has no reproduction config.
- **Validation criteria:** hook fixture tests for edit-under-code-root, edit-of-registered-dep, second edit of the same file in one session (silent), edit after the section was updated (reminder again), task-file edit (silent), and no-config (silent); existing hook tests stay green.

## Details

- The hook entry is [task_hook.py](../../../skills/task-tree/scripts/task_hook.py) via `hooks/task-hook`; Codex wiring lives in `hooks/hooks-codex.json`. Reuse the graph model from [01-section-contract](../01-section-contract/task.md) for the dep lookup.

## Results

[task_hook.py](../../../skills/task-tree/scripts/task_hook.py) gains a reproduction reminder, run by `_process_paths` over every changed file whichever tool wrote it. It fires when the file is a dep/script of a registered `## Reproduction` step or an unregistered script under the task root, reusing [`_repro.build_graph`](../../../skills/task-tree/scripts/_repro.py) for the dep lookup. `task.md` is excluded before any lookup.

### Session identifier: verified, not assumed

- **Claude Code**'s PostToolUse payload carries `session_id` and `transcript_path` at the top level.
- **Codex CLI** (0.152.1, installed locally) also carries `session_id` in its native hook wire format — confirmed from the binary's embedded JSON-schema strings (`session_id`, `turn_id`, `agent_type`, `transcript_path`, `hook_event_name`, `model`, ... all listed together as one payload's fields). This contradicts the task's premise that Codex might lack one; Codex only grew a native hook system recently.

[`_repro_session_key`](../../../skills/task-tree/scripts/task_hook.py#L161) therefore reads `session_id` generically off the payload (both harnesses supply it today) and falls back to a rolling one-hour bucket only when a payload omits it — harness-agnostic rather than branching on `tool_name`.

### Plan-root resolution is file-path-based, not cwd-based

A producer file (e.g. `Code/build_panel.jl`) sits beside the task tree, not inside it, so the existing `_find_plan_root` (task tree among the file's *ancestors*) doesn't apply. [`_repro_plan_root_for_file`](../../../skills/task-tree/scripts/task_hook.py#L139) instead walks up from the edited file looking for a `superRA/`/`.plan/` *child* at each level, independent of process cwd. This also keeps the test suite isolated: a cwd-based fallback would have made every hook test that doesn't pass `cwd=` explicitly resolve against this dev repo's own real task tree, since pytest's default subprocess cwd is the repo root (verified this repo's real tree has no `## Reproduction` section yet, so that risk is latent, not currently tripped).

### State directory

Neither `superRA/config.yaml` nor `02-runner` exist yet, so there's no established runner state directory to key markers into. Chose `<project_root>/.superra-repro/hook-markers/<session-or-hour-key>/<sha256(resolved_path)[:32]>` — gitignored by convention, lazily created only when there's something to remind about. [02-runner](../02-runner/task.md)'s own "one gitignored state directory" should reuse `.superra-repro/` rather than mint a second one (noted in `internals.md`). This hook does not write a `.gitignore` entry itself; `02-runner`'s task text already assigns it that duty ("creates and adds to `.gitignore` on first run").

### Marker clearing

[`_clear_reproduction_markers_for_task`](../../../skills/task-tree/scripts/task_hook.py#L278) runs after every task.md reconcile, gated on a cheap `parse_body_sections` check so an ordinary task.md edit costs nothing extra. When the edited task currently declares `## Reproduction`, it rebuilds the graph and clears markers — across every session key, not only the current one — for that task's steps' resolved deps.

### Fail-open / performance

The first pass measured only the no-config case; REVISE fixed a real gap the reviewer found (see Review Notes item 1): `_reproduction_reminder` called `_repro.build_graph` with full `${VAR}` resolution *before* checking relevance, so any configured `shell:`/`env:` var spawned a subprocess (or environment lookup) on *every* Edit/Write/apply_patch beside a task tree, not only on producer-file edits, and `_handle_apply_patch` rebuilt the graph once per edited file even when several shared a `plan_root`.

Fix: [`_repro.build_graph`](../../../skills/task-tree/scripts/_repro.py) gained a `resolve_vars: bool = True` parameter (default preserves existing behavior for every other caller — `03-task-interface`, `task check`, the runner, and all of `test_repro.py`'s 82 tests pass unchanged). `resolve_vars=False` skips `resolve_variables()` entirely (an empty `variables` dict, so no `shell:` subprocess and no `env:` lookup ever runs) and, threaded into `_build_step` as `strict_vars`, no longer raises on an unresolved `${VAR}` — `interpolate()` already leaves the placeholder text in place for an unknown var, so a literal (non-`${VAR}`) dep/out/script resolves exactly as it would under full resolution, while a `${VAR}`-containing one keeps the placeholder and matches no real file. [`_reproduction_reminder`](../../../skills/task-tree/scripts/task_hook.py#L204) now always calls `build_graph(..., resolve_vars=False)`, and groups candidate files by `plan_root` first so a multi-file `apply_patch` builds each distinct project's graph exactly once, not once per file. `_clear_reproduction_markers_for_task` uses the same `resolve_vars=False` mode, for two reasons: it avoids a subprocess on a `## Reproduction`-section edit too, and it keeps the resolved paths it clears identical to the ones `_reproduction_reminder` ever sets (since a marker is only ever set for a literal-path match).

Practical cost of the carve-out: a dep, out, `cmd`, or `script` that references an unresolved `${VAR}` is invisible to this reminder. Per the contract, `${VAR}` interpolation is data/output routing (`${DATA}/…`, `${OUT}/…`), not the producer script/dep path itself, which is normally a literal repo-relative path (as in the contract's own example and both planned pilots) — so the reminder still catches the case it exists for.

Measured (in-process, `time.perf_counter`, averaged over runs) on a fixture matching the review's concern — a `config.yaml` with a `shell:`-typed var, an 11-task tree, and a step whose `.jl` dep transitively includes a helper via `include(joinpath(@__DIR__, …))`:

| Call | Cost |
|---|---|
| `build_graph(..., resolve_vars=True)` (old codepath, would run on every edit) | 8.45 ms |
| `build_graph(..., resolve_vars=False)` (new codepath) | 2.80 ms |
| `_reproduction_reminder` end-to-end (new, includes the Julia-closure match) | 3.12 ms |

The `shell:` var here is a cheap `echo` (~1ms); the fix's real value is that the new codepath's cost no longer has *any* subprocess term at all, so it does not scale with the number of `shell:` vars or their cost (the review measured ~12ms for one shell round-trip locally; TreasuryGIV's actual `${OUT}` routing shells out to a Julia script, plausibly costing far more per call). `build_graph()` on this repo's real 83-task tree (no reproduction config anywhere) still takes ~30ms — the tree walk itself, unaffected by `resolve_vars` and unavoidable to determine relevance at all. A tree with no config anywhere ([`has_reproduction`](../../../skills/task-tree/scripts/_repro_signals.py#L194): no step, no `## Reproduction` section, no `reproduction:` config value) short-circuits before any per-file matching or marker I/O.

### Validation

9 tests added to `TestTaskHook` in [test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py): the original 6 covering the objective's list (unregistered-companion-script, edit-of-registered-dep, same-session silence, reminder-again-after-section-edit, task-file silence, no-config silence), plus 3 REVISE regression tests — `test_reproduction_reminder_never_resolves_vars` (monkeypatches `_repro.resolve_variables` to record calls; asserts zero calls for both an irrelevant edit and a real producer edit under a configured `shell:` var), `test_reproduction_reminder_builds_graph_once_per_plan_root` (monkeypatches `_repro.build_graph` to count calls; asserts exactly one call for a two-file edit sharing a `plan_root`), and `test_reproduction_reminder_cost_with_shell_var_and_julia_closure` (times 5 in-process calls on the shell-var + Julia-closure fixture above, asserting the average stays under 200ms — tree-walk-bound, not subprocess-bound). Full suite: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts -q` — 918 passed (909 baseline + 9 new). Also exercised end-to-end through the real committed `hooks/task-hook` shell shim and through the `hooks-codex.json` manifest's `task-hook` command against a scratch project carrying a real reproduction config, confirming Claude/Codex parity on the actual wiring, not only the Python entry point.

Pre-existing and unrelated: `tests/hooks/test-codex-hooks.sh`'s "Codex manifest command executes task PostToolUse hook" case fails on `main` before this change too (asserts a Communicate-reminder string that commit `447f0ef1` already updated in the pytest suite but not in this shell test). Not touched here — one concern per commit.

Docs: [internals.md](../../../skills/task-tree/references/internals.md) §Hook Architecture gets a "Reproduction reminder" paragraph and the `task_hook.py` Script Inventory row is updated.

## Review Notes

Tier: quick. Focus: correctness.

1. **[ADVISORY, informational]** The `.superra-repro` naming coupling with `02-runner` (§State directory) is recorded only in `internals.md`, not in `02-runner/task.md` — a subagent dispatched to 02-runner isn't pointed there by the Skill-Load Manifest. This didn't drift in practice: 02-runner has since been implemented and independently landed on `.superra-repro/` too. No action needed now; a one-line cross-reference in `02-runner/task.md` would remove the reliance on both sides separately reading `internals.md`.
