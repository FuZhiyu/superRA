---
title: "Task-Path Argument Resolution — Tolerate Redundant Root Prefix"
status: implemented
depends_on: []
tags:
  - task-tree
  - cli
  - ergonomics
created: 2026-06-07
---

## Objective

Fix a CLI quirk that silently strands agents: `task read` (and every other verb) takes a task path **relative to the task root** (e.g. `task-tree/planning-redesign`), but an agent that has the full path in hand naturally passes the `superRA/`-prefixed form, which resolves to a nonexistent `superRA/superRA/...` and fails with an error written only to **stderr** — so a stdout-capturing caller sees nothing and no usable diagnostic.

### Context (root cause)

`_task_io.py:resolve_path` joins `plan_root / task_path` and only guards against `../` escapes via `is_relative_to`; a redundant leading `superRA/` segment stays inside the root, so the path doubles to `superRA/superRA/...` and the not-found error (`task.md not found at .../superRA/superRA/...`) goes to stderr with exit 1. Every verb (`read`, `update`, `result add`, `status`, `dep`) routes through `resolve_path` / `resolve_plan_root_arg`, so all share the failure. Separately, no agent-facing doc states the canonical path form — every mention is a bare `<path>` placeholder, and the adjacent `git add superRA/<task-path>/task.md` line (correct for `git add`, a real filesystem path) reinforces the wrong prefix for `task read`.

### Scope

**1. CLI behavior — `skills/task-tree/scripts/_task_io.py` `resolve_path`.** When the first segment of `task_path` equals the plan-root basename (`superRA`, or legacy `.plan`), strip it before joining; otherwise, on not-found, emit a targeted hint that paths are task-root-relative and the `superRA/` prefix should be dropped. Fixing it in `resolve_path` repairs the quirk across all verbs at once. Keep the non-zero exit; the ask is the prefix tolerance + an actionable message, not changing exit semantics.

**2. Instruction — `skills/using-superRA/SKILL.md` §Task Interface.** State once, in the owning file, that `<path>` is **relative to the task root and omits the `superRA/` prefix** (e.g. `task-tree/planning-redesign`, not `superRA/task-tree/planning-redesign`). Do not restate it in the role specs, `agent-orchestration`, or `main-agent.md` — they use the bare placeholder and inherit this rule per the CLAUDE.md DRY gate (point/trust, do not paraphrase).

**3. Tests — `skills/task-tree/scripts/test_task_tree.py`.** Add regression coverage: prefixed path resolves correctly (or fails with the targeted hint), plan-root-relative path works, nonexistent path still exits 1.

### Constraints

- Keep the fix local and explicit in `resolve_path`; do not broaden into a general path-sanitization framework (same discipline as the `path-containment` sibling task).
- Preserve the `../`-escape rejection that `path-containment` and `resolve_path` already enforce — prefix tolerance must not open a traversal hole.

### Validation

- The prefixed form (`task read superRA/task-tree/planning-redesign`) now resolves to the right task **or** fails with a message naming the redundant prefix — not a cryptic doubled-path error.
- The plan-root-relative form continues to work; `../` escapes are still rejected.
- New tests fail on current code and pass after the fix; existing tests still pass.
- §Task Interface states the canonical path form exactly once; no duplicate statements added elsewhere.

## Results

The redundant-root-prefix quirk is fixed once in the shared resolver, covered by regression tests, and documented in the owning skill.

**1. CLI behavior — prefix stripping in [`_task_io.py`](../../../../skills/task-tree/scripts/_task_io.py#L535) + uniform forwarding in [`cli.py`](../../../../skills/task-tree/scripts/cli.py#L87).** The prefix tolerance is now a shared `strip_root_prefix(plan_root, task_path)` helper that drops a leading segment when it equals **both** the plan-root basename (`plan_root.name`) **and** a known task-root dirname (`superRA` or legacy `.plan`); `resolve_path` calls it before joining, so `superRA/task-tree/planning-redesign` resolves to the same directory as `task-tree/planning-redesign` instead of doubling to `superRA/superRA/...`.

The read-side verbs (`read`, `comment`, `move`, `rename`) route through `resolve_path` and were already prefix-tolerant. The mutation verbs (`update`, `result add`, `dep`, `status cascade`, `create`) delegate to mutator functions that joined `plan_root / task_path` **naively**. Those mutators now call `resolve_path` / `strip_root_prefix` themselves (single enforcement point — see the `unified-command-surface` sibling), so a prefixed path resolves correctly and a `../` escape is rejected regardless of entry surface (packaged CLI **or** direct script). The mutation CLI handlers also call the mutator functions directly rather than re-serializing argv, so there is no longer a second parser to keep prefix-tolerant. The fix now applies across the whole mutation command surface, not just the resolver unit.

The fix is deliberately narrow per the `path-containment` sibling discipline: only the first segment, only when it matches the actual root basename — a real task slug that happens to be named `superRA` under a differently-named root is **not** stripped (covered by `test_prefix_only_stripped_when_it_matches_root_basename`). The `../`-escape rejection via `is_relative_to` is preserved unchanged, so prefix tolerance opens no traversal hole. `resolve_path` stays a pure path operation — existence remains each verb's own check (which already exits 1 with a not-found message), so the prefix tolerance never invents a directory.

I did not add a separate per-verb "redundant prefix" hint message. Stripping the prefix in the resolver makes the prefixed form resolve to the correct task, which satisfies the primary arm of the validation ("resolves to the right task **or** fails with a message naming the redundant prefix") directly and across all verbs, without touching every verb's error path or risking the broader path-sanitization framework the constraints prohibit.

**2. Instruction — [using-superRA SKILL.md §Task Interface](../../../../skills/using-superRA/SKILL.md#L44).** The §Task Interface **Read** line now states once that every `<path>` argument is relative to the task root and omits the `superRA/` prefix, with a concrete example. No duplicate was added to role specs, `agent-orchestration`, or `main-agent.md` — they keep the bare `<path>` placeholder and inherit this rule per the CLAUDE.md DRY gate. The `_task_io.py` docstring and `cli.py` argparse `--help` text describe the resolver/CLI at the point they are loaded (code help, not agent-facing doc prose) and are not duplicate statements of the instruction.

**3. Tests.** Resolver-unit coverage in [`TestResolvePath`](../../../../skills/task-tree/scripts/test_task_tree.py#L228) (plan-root-relative resolves; redundant prefix stripped; legacy `.plan` stripped; prefix stripped only when it matches the root basename; nonexistent path resolves but does not exist; `../` still raises `escapes plan root`). New [`TestStripRootPrefix`](../../../../skills/task-tree/scripts/test_task_tree.py#L276) covers the extracted helper directly. New [`TestCliPrefixTolerantMutations`](../../../../skills/task-tree/scripts/test_task_tree.py#L292) is the end-to-end regression the CRITICAL asked for: it drives `cli.main` for every mutation verb (`update`, `result add`, `dep add`, `status cascade`, `create`, `move`) with the `superRA/`-prefixed form and asserts the on-disk effect landed on the right task. Without the routing fix these five (move excepted) fail with the exact doubled-path stderr error.

**Verification:**
- Full suite: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts` -> **631 passed, 2 skipped**.
- Red-green on the routing bug: with the mutation handlers temporarily reverted to forward raw `args.path` (and the mutators' own `resolve_path` not yet added), the five mutation cases of `TestCliPrefixTolerantMutations` fail with `…/superRA/superRA/…` doubled-path errors (`move` passes — `task_rename` already calls `resolve_path`); with the fix in place all pass.
- Real CLI in this worktree: `uv run --script skills/task-tree/scripts/cli.py task update superRA/task-tree/cli-scripts/path-arg-resolution --add-tag …` now exits 0 and writes the correct task.md (previously a stderr-only doubled-path error); reverted with `--remove-tag`.

## Review Notes

> 1. [CRITICAL] The headline Results claim ([task.md:41](task.md#L41)) — "every verb (`read`, `update`, `result add`, `status`, `dep`, `comment`) routes through `resolve_path`, the fix applies across the whole command surface at once" — is false; the defect this task was opened to fix is still live on every mutation verb. [`cli.py` `_checked_task_root_args`](../../../../skills/task-tree/scripts/cli.py#L77) calls `resolve_path` for validation only, discards the stripped result, and forwards the raw prefixed path to [`task_update.py:84`](../../../../skills/task-tree/scripts/task_update.py#L84), [`task_link.py:57`](../../../../skills/task-tree/scripts/task_link.py#L57), and [`task_add_result.py:52`](../../../../skills/task-tree/scripts/task_add_result.py#L52), which join `plan_root / task_path` naively. Reproduced on a scratch tree: `task update superRA/<path>`, `result add superRA/<path>`, `dep add superRA/<path>`, and `status cascade superRA/<path>` all exit 1 with the exact doubled-path stderr error (`Error: task not found: …/superRA/superRA/…`) and no prefix hint, failing both arms of this task's Validation; `task create superRA/<path>` fails with `parent directory does not exist: …/superRA/superRA`. Only `read`/`comment`/`move`/`rename` are prefix-tolerant. The regression tests ([`TestResolvePath`](../../../../skills/task-tree/scripts/test_task_tree.py#L228)) exercise the `resolve_path` unit only, so they cannot detect this. Fix: forward the stripped task-root-relative path from `_checked_task_root_args` to the delegated scripts (or move the `resolve_path` call into the mutators themselves), and add one end-to-end prefixed `task update` regression test.
>    → implemented: extracted `strip_root_prefix` ([`_task_io.py:535`](../../../../skills/task-tree/scripts/_task_io.py#L535)); moved `resolve_path` containment + prefix tolerance into the mutator functions `update_task`/`add_result`/`link_task`/`create_task` (single enforcement point regardless of entry surface) and switched the CLI mutation handlers to call those functions directly ([cli.py:240](../../../../skills/task-tree/scripts/cli.py#L240)) instead of forwarding argv; added end-to-end [`TestCliPrefixTolerantMutations`](../../../../skills/task-tree/scripts/test_task_tree.py#L292) driving `cli.main` for every mutation verb (red-green confirmed); rewrote the false headline claim ([task.md:41](task.md#L41)).
