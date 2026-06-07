---
title: "Task-Path Argument Resolution — Tolerate Redundant Root Prefix"
status: approved
depends_on: []
tags: [task-system, cli, ergonomics]
created: 2026-06-07
---

## Objective

Fix a CLI quirk that silently strands agents: `task read` (and every other verb) takes a task path **relative to the task root** (e.g. `task-system/planning-redesign`), but an agent that has the full path in hand naturally passes the `superRA/`-prefixed form, which resolves to a nonexistent `superRA/superRA/...` and fails with an error written only to **stderr** — so a stdout-capturing caller sees nothing and no usable diagnostic.

### Context (root cause)

`_task_io.py:resolve_path` joins `plan_root / task_path` and only guards against `../` escapes via `is_relative_to`; a redundant leading `superRA/` segment stays inside the root, so the path doubles to `superRA/superRA/...` and the not-found error (`task.md not found at .../superRA/superRA/...`) goes to stderr with exit 1. Every verb (`read`, `update`, `result add`, `status`, `dep`) routes through `resolve_path` / `resolve_plan_root_arg`, so all share the failure. Separately, no agent-facing doc states the canonical path form — every mention is a bare `<path>` placeholder, and the adjacent `git add superRA/<task-path>/task.md` line (correct for `git add`, a real filesystem path) reinforces the wrong prefix for `task read`.

### Scope

**1. CLI behavior — `skills/task-system/scripts/_task_io.py` `resolve_path`.** When the first segment of `task_path` equals the plan-root basename (`superRA`, or legacy `.plan`), strip it before joining; otherwise, on not-found, emit a targeted hint that paths are task-root-relative and the `superRA/` prefix should be dropped. Fixing it in `resolve_path` repairs the quirk across all verbs at once. Keep the non-zero exit; the ask is the prefix tolerance + an actionable message, not changing exit semantics.

**2. Instruction — `skills/using-superRA/SKILL.md` §Task Interface.** State once, in the owning file, that `<path>` is **relative to the task root and omits the `superRA/` prefix** (e.g. `task-system/planning-redesign`, not `superRA/task-system/planning-redesign`). Do not restate it in the role specs, `agent-orchestration`, or `main-agent.md` — they use the bare placeholder and inherit this rule per the CLAUDE.md DRY gate (point/trust, do not paraphrase).

**3. Tests — `skills/task-system/scripts/test_task_system.py`.** Add regression coverage: prefixed path resolves correctly (or fails with the targeted hint), plan-root-relative path works, nonexistent path still exits 1.

### Constraints

- Keep the fix local and explicit in `resolve_path`; do not broaden into a general path-sanitization framework (same discipline as the `path-containment` sibling task).
- Preserve the `../`-escape rejection that `path-containment` and `resolve_path` already enforce — prefix tolerance must not open a traversal hole.

### Validation

- The prefixed form (`task read superRA/task-system/planning-redesign`) now resolves to the right task **or** fails with a message naming the redundant prefix — not a cryptic doubled-path error.
- The plan-root-relative form continues to work; `../` escapes are still rejected.
- New tests fail on current code and pass after the fix; existing tests still pass.
- §Task Interface states the canonical path form exactly once; no duplicate statements added elsewhere.

## Results

The redundant-root-prefix quirk is fixed once in the shared resolver, covered by regression tests, and documented in the owning skill.

**1. CLI behavior — [`_task_io.py` `resolve_path`](../../../../skills/task-system/scripts/_task_io.py#L451).** `resolve_path` now strips a leading path segment when it equals **both** the plan-root basename (`plan_root.name`) **and** a known task-root dirname (`superRA` or legacy `.plan`) before joining. So `superRA/task-system/planning-redesign` resolves to the same directory as `task-system/planning-redesign` instead of doubling to `superRA/superRA/...`. Because every verb (`read`, `update`, `result add`, `status`, `dep`, `comment`) routes through `resolve_path`, the fix applies across the whole command surface at once.

The fix is deliberately narrow per the `path-containment` sibling discipline: only the first segment, only when it matches the actual root basename — a real task slug that happens to be named `superRA` under a differently-named root is **not** stripped (covered by `test_prefix_only_stripped_when_it_matches_root_basename`). The `../`-escape rejection via `is_relative_to` is preserved unchanged, so prefix tolerance opens no traversal hole. `resolve_path` stays a pure path operation — existence remains each verb's own check (which already exits 1 with a not-found message), so the prefix tolerance never invents a directory.

I did not add a separate per-verb "redundant prefix" hint message. Stripping the prefix in the resolver makes the prefixed form resolve to the correct task, which satisfies the primary arm of the validation ("resolves to the right task **or** fails with a message naming the redundant prefix") directly and across all verbs, without touching every verb's error path or risking the broader path-sanitization framework the constraints prohibit.

**2. Instruction — [using-superRA SKILL.md §Task Interface](../../../../skills/using-superRA/SKILL.md#L45).** The §Task Interface **Read** line now states once that every `<path>` argument is relative to the task root and omits the `superRA/` prefix, with a concrete example. No duplicate was added to role specs, `agent-orchestration`, or `main-agent.md` — they keep the bare `<path>` placeholder and inherit this rule per the CLAUDE.md DRY gate. The `_task_io.py` docstring and `cli.py` argparse `--help` text describe the resolver/CLI at the point they are loaded (code help, not agent-facing doc prose) and are not duplicate statements of the instruction.

**3. Tests — [`test_task_system.py` `TestResolvePath`](../../../../skills/task-system/scripts/test_task_system.py#L222).** Six regression tests: plan-root-relative path resolves; redundant root prefix is stripped (red-green confirmed — fails on pre-fix code with the exact `superRA/superRA/01-first` doubled path, passes after); legacy `.plan` prefix is stripped; prefix is stripped only when it matches the root basename; a nonexistent path resolves to a path that does not exist (no invented directory); `../` traversal still raises `escapes plan root`.

**Verification:**
- `~/.venv/bin/python -m pytest skills/task-system/scripts/test_task_system.py` -> **291 passed**.
- Red-green: with `_task_io.py` stashed, `test_redundant_root_prefix_is_stripped` fails with the doubled-path `AssertionError`; with the fix, it passes.
- Real CLI: `uv run --project skills/task-system superra task read superRA/task-system/cli-scripts/path-arg-resolution --no-ancestors` now exits 0 and prints this task (previously a stderr-only doubled-path error).
