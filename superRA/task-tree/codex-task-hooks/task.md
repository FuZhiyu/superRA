---
title: "Codex Task Hooks and Decision-Reminder Deprecation"
status: approved
depends_on: []
tags:
  - hooks
  - codex
  - task-tree
created: 2026-06-01
---

## Objective

Bring superRA's task-related hook behavior into a coherent Codex-compatible state while honoring the researcher decision to drop the user-decision log reminder and the `updated` frontmatter field. The durable hook contracts are:

1. Deprecate and remove the active `ask-user-question-logger` reminder from supported hook surfaces. The task-file record remains the durable decision mechanism; the hook should no longer be installed, advertised, or tested as active behavior.
2. Add Codex task-tree hook parity for `superRA/**/task.md` edits and structural `superRA/` shell mutations (formerly `.plan/**/task.md` — the root was renamed to `superRA/`). Current official Codex hook documentation states that `PostToolUse` supports `Bash`, `apply_patch`, and `Edit|Write` matcher aliases for `apply_patch`; use that surface to run the existing task reconcile path after Codex edits.
3. Remove `updated` from the task frontmatter schema, generated task templates, mutation scripts, dashboard summary, docs, tests, and this worktree's `superRA/` files. Git history is the source of truth for last modification time.
4. Update active docs and tests so they describe the supported hook set accurately: Codex should list autoload, merge-guard, codex-plan-stop, and the task-tree `PostToolUse` hooks; it should not list or imply the user-decision reminder.
5. Keep Codex task-hook no-feedback paths parseable: successful or ignored Codex `PostToolUse` invocations should emit `{}` while feedback paths still emit `additionalContext`, and Claude-compatible no-feedback paths should remain silent.

Scope boundary: do not redesign status rollup semantics, dashboard UI beyond removing `updated` display, or superRA decision logging protocol. This is hook packaging, hook input compatibility, task frontmatter cleanup, active documentation, and focused regression coverage.

### Conventions

Repository guidance walk, 2026-06-01: root `CLAUDE.md` governs superRA internals. Treat skill, hook, agent, harness adapter, and internal-doc edits as skill creation; load `skill-creator` before editing any `skills/*/SKILL.md`; keep instructions DRY and necessary; isolate Codex-specific behavior in harness adapters or hook manifests; leave generated Codex agent artifacts alone unless canonical `agents/*.md` changes.

Root `README.md` is user-facing and should describe the installed hook set without internal implementation detail. `docs/README.codex.md` owns Codex installation and verification notes. `skills/task-tree/SKILL.md` is the user-facing task-tree skill surface; `skills/task-tree/references/internals.md` owns task hook architecture details. Historical records under `docs/plans/` can remain historical unless they are used by active compatibility checks.

Official Codex hook reference consulted during planning: `https://developers.openai.com/codex/hooks`. Relevant current facts: plugin-bundled hooks can be loaded from `.codex-plugin/plugin.json`; `PostToolUse` supports `Bash`, `apply_patch`, and matcher aliases `Edit|Write` for `apply_patch`; `PostToolUse` input reports `tool_name: "apply_patch"` for file edits and carries edit content in `tool_input.command`; `PostToolUse` can return JSON `hookSpecificOutput.additionalContext` for model-visible feedback.

Date-field policy: `updated` is dropped because it duplicates git history and creates noisy metadata churn. Keep `created` for now unless the implementer finds it causes comparable churn or ambiguity; its main value is a stable human-facing task inception date, especially before the first commit or after task moves.

## Results

Codex task hooks are now coherent with the current supported hook set:
the decision-reminder hook is removed from active packaging, Codex
installs task-tree `PostToolUse` reconciliation hooks for documented edit
and shell paths, `updated` frontmatter is removed from task metadata, Codex
no-feedback task-hook paths emit parseable `{}` output, and active docs/tests
describe the supported Codex hooks without advertising inactive
decision-reminder behavior.

Validation across the child tasks covered hook manifests, Codex-shaped hook
payloads, task-tree tests, task metadata cleanup, and targeted
compatibility checks. The optional live Codex CLI smoke test remains opt-in
because it requires logged-in Codex auth and spends model turns.

The `posttooluse-empty-json` follow-up folded into this durable task in June
2026. `task_hook.py` now supports `SUPERRA_TASK_HOOK_EMPTY_JSON`, Codex
manifest task-hook commands export it and print `{}` when no plugin root is
available, and regression coverage verifies parseable empty JSON for Codex
Edit/Write, Bash, empty-stdin, and `apply_patch` no-feedback paths while
preserving `additionalContext` feedback behavior. The shim-level last resort
(emit `{}` when the inner hook produced no stdout and
`SUPERRA_TASK_HOOK_EMPTY_JSON` is set) lives in `render_hook_shim()` in
[wrapper_resolver.py](../../../skills/task-tree/scripts/wrapper_resolver.py);
the committed [hooks/task-hook](../../../hooks/task-hook) is regenerated from it
and `test_committed_hook_shim_matches_generator` guards the match.

**Final diff self-check:** `git diff 9ca25479f7cb588aec3d758f0bb27d66e4c8aded..HEAD`;
surviving hunks are limited to the approved hook-packaging scope:
removing the active decision-reminder hook and manifest entries, adding
Codex task-tree `PostToolUse` manifest wiring, adapting `task_hook.py`
and regression tests for Codex `apply_patch`/`Bash` payloads, removing
`updated` metadata behavior from task-tree code/tests/docs, refreshing
active README/Codex/task-tree hook documentation, updating compatibility
tests, adding Codex parseable empty-JSON no-feedback handling, and recording approved task/sync/protect/review status in the
codex-task-hooks task tree. Suspicious hunks are justified as follows:
`skills/task-tree/SKILL.md` and `skills/task-tree/references/internals.md`
only state the Codex-specific direct-edit/shell-hook boundary needed by
task 04 and pass the DRY/Necessity gate; `hooks/hooks*.json` and deleted
`hooks/ask-user-question-logger` implement tasks 01/02's active hook-set
changes; `tests/hooks/*` and `tests/check-harness-compatibility.sh` protect
the installed hook contract; `superRA/task.md` and this subtree's task
files are workflow evidence for sync, protection, review, and approved
results. No unrelated cleanup, broad reformatting, generated-agent changes,
or exporter/share/dashboard implementation hunks survive in the governing
diff.
