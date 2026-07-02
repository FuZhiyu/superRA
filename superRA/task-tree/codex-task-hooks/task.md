---
title: "Codex Task Hooks and Decision-Reminder Deprecation"
status: approved
depends_on: []
---

## Objective

Bring superRA's task-related hook behavior into a coherent Codex-compatible state while honoring the researcher decision to drop the user-decision log reminder and the `updated` frontmatter field. The durable hook contracts are:

1. Deprecate and remove the active `ask-user-question-logger` reminder from supported hook surfaces. The task-file record remains the durable decision mechanism; the hook is no longer installed, advertised, or tested as active behavior.
2. Add Codex task-tree hook parity for `superRA/**/task.md` edits and structural `superRA/` shell mutations, using the `PostToolUse` surface (`Bash`, `apply_patch`, and the `Edit|Write` matcher aliases for `apply_patch`) to run the existing task reconcile path after Codex edits.
3. Remove `updated` from the task frontmatter schema, generated task templates, mutation scripts, dashboard summary, docs, and tests. Git history is the source of truth for last modification time.
4. Keep active docs and tests describing the supported hook set accurately: Codex lists autoload, merge-guard, codex-plan-stop, and the task-tree `PostToolUse` hooks, and does not list or imply the user-decision reminder.
5. Keep Codex task-hook no-feedback paths parseable: successful or ignored Codex `PostToolUse` invocations emit `{}` while feedback paths still emit `additionalContext`, and Claude-compatible no-feedback paths remain silent.

Scope boundary: hook packaging, hook input compatibility, task frontmatter cleanup, active documentation, and focused regression coverage — not status rollup semantics, dashboard UI beyond removing `updated` display, or the decision-logging protocol.

## Results

Codex task hooks are coherent with the current supported hook set: the decision-reminder hook is removed from active packaging; Codex installs task-tree `PostToolUse` reconciliation hooks for the documented edit and shell paths; `updated` frontmatter is removed from task metadata; Codex no-feedback task-hook paths emit parseable `{}` output; and active docs/tests describe the supported Codex hooks without advertising inactive decision-reminder behavior. The optional live Codex CLI smoke test remains opt-in (it needs logged-in Codex auth and spends model turns).

The `posttooluse-empty-json` follow-up folded into this task. `task_hook.py` supports `SUPERRA_TASK_HOOK_EMPTY_JSON`; the Codex manifest task-hook commands export it and print `{}` when no plugin root is available; and regression coverage verifies parseable empty JSON for Codex Edit/Write, Bash, empty-stdin, and `apply_patch` no-feedback paths while preserving `additionalContext` feedback. The shim-level last resort (emit `{}` when the inner hook produced no stdout and `SUPERRA_TASK_HOOK_EMPTY_JSON` is set) lives in `render_hook_shim()` in `skills/task-tree/scripts/wrapper_resolver.py`; the committed `hooks/task-hook` is regenerated from it and `test_committed_hook_shim_matches_generator` guards the match.

The Codex-specific direct-edit/shell-hook boundary is stated in `skills/task-tree/SKILL.md` and `skills/task-tree/references/internals.md`; the active hook manifests (`hooks/hooks*.json`, with `hooks/ask-user-question-logger` deleted) and the harness-compatibility tests (`tests/hooks/*`, `tests/check-harness-compatibility.sh`) protect the installed hook contract.
