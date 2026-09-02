---
title: "PostToolUse Reminder When a Producer Changes Without Its Step"
status: implemented
depends_on: [01-section-contract]
---

## Objective

Extend the task hook so an edit to a maintained producer that leaves the graph untouched gets a non-blocking reminder in the same turn.

- **Trigger:** the edited or written file is a dep or script of a registered step, or lies under a configured `code_roots` directory. Task files never trigger.
- **Suppression:** one reminder per file per session, recorded as a marker in the runner's gitignored state directory keyed on the `session_id` the Claude Code payload carries; a harness whose payload has no session id (verify Codex's) keys the marker on a one-hour window per file instead. Editing a `## Reproduction` section clears the markers for the files that section's steps name.
- **Message:** names the file, the owning step(s) if any, and the duty: update the step's deps/outs or register a new step, then run `superra repro status`.
- **Parity:** the Claude hook and the Codex hook manifest emit the same reminder; both remain fail-open when the tree has no reproduction config.
- **Validation criteria:** hook fixture tests for edit-under-code-root, edit-of-registered-dep, second edit of the same file in one session (silent), edit after the section was updated (reminder again), task-file edit (silent), and no-config (silent); existing hook tests stay green.

## Details

- The hook entry is [task_hook.py](../../../skills/task-tree/scripts/task_hook.py) via `hooks/task-hook`; Codex wiring lives in `hooks/hooks-codex.json`. Reuse the graph model from [01-section-contract](../01-section-contract/task.md) for the dep lookup.

## Results

[task_hook.py](../../../skills/task-tree/scripts/task_hook.py) gains a reproduction reminder, wired into `_handle_edit_write` and `_handle_apply_patch` (not `_handle_bash`, which carries no single edited file). It fires when the edited file is a dep/script of a registered `## Reproduction` step or lies under a configured `code_roots` directory, reusing [`_repro.build_graph`](../../../skills/task-tree/scripts/_repro.py) for the dep lookup. `task.md` is excluded before any lookup.

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

`build_graph()` on this repo's real 83-task tree (no reproduction config anywhere) takes ~31ms measured directly — acceptable for a non-blocking hook that now runs on every edit, not only markdown-under-task-root ones. A tree with no config anywhere (`graph.steps == [] and graph.config.code_roots == []`) short-circuits before any per-file matching or marker I/O.

### Validation

6 tests added to `TestTaskHook` in [test_task_tree.py](../../../skills/task-tree/scripts/test_task_tree.py), covering the objective's list exactly: edit-under-code-root, edit-of-registered-dep, same-session silence, reminder-again-after-section-edit, task-file silence, no-config silence. Full suite: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts -q` — 915 passed (909 baseline + 6 new). Also exercised end-to-end through the real committed `hooks/task-hook` shell shim and through the `hooks-codex.json` manifest's `task-hook` command against a scratch project with a real `code_roots` config, confirming Claude/Codex parity on the actual wiring, not only the Python entry point.

Pre-existing and unrelated: `tests/hooks/test-codex-hooks.sh`'s "Codex manifest command executes task PostToolUse hook" case fails on `main` before this change too (asserts a Communicate-reminder string that commit `447f0ef1` already updated in the pytest suite but not in this shell test). Not touched here — one concern per commit.

Docs: [internals.md](../../../skills/task-tree/references/internals.md) §Hook Architecture gets a "Reproduction reminder" paragraph and the `task_hook.py` Script Inventory row is updated.
