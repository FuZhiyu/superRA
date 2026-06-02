---
title: "Codex Task Hooks and Decision-Reminder Deprecation"
status: in-progress
depends_on: []
tags: [hooks, codex, task-system]
created: 2026-06-01
---

## Objective

Bring superRA's task-related hook behavior into a coherent Codex-compatible state while honoring the researcher decision to drop the user-decision log reminder and the `updated` frontmatter field. The work has three independent implementation branches plus a final reconciliation pass:

1. Deprecate and remove the active `ask-user-question-logger` reminder from supported hook surfaces. The task-file record remains the durable decision mechanism; the hook should no longer be installed, advertised, or tested as active behavior.
2. Add Codex task-system hook parity for `.plan/**/task.md` edits and structural `.plan/` shell mutations. Current official Codex hook documentation states that `PostToolUse` supports `Bash`, `apply_patch`, and `Edit|Write` matcher aliases for `apply_patch`; use that surface to run the existing task reconcile path after Codex edits.
3. Remove `updated` from the task frontmatter schema, generated task templates, mutation scripts, dashboard summary, docs, tests, and this worktree's `.plan/` files. Git history is the source of truth for last modification time.
4. Update active docs and tests so they describe the supported hook set accurately: Codex should list autoload, merge-guard, codex-plan-stop, and the task-system `PostToolUse` hooks; it should not list or imply the user-decision reminder.

Scope boundary: do not redesign status rollup semantics, dashboard UI beyond removing `updated` display, or superRA decision logging protocol. This is hook packaging, hook input compatibility, task frontmatter cleanup, active documentation, and focused regression coverage.

## Conventions

Repository guidance walk, 2026-06-01: root `CLAUDE.md` governs superRA internals. Treat skill, hook, agent, harness adapter, and internal-doc edits as skill creation; load `skill-creator` before editing any `skills/*/SKILL.md`; keep instructions DRY and necessary; isolate Codex-specific behavior in harness adapters or hook manifests; leave generated Codex agent artifacts alone unless canonical `agents/*.md` changes.

Root `README.md` is user-facing and should describe the installed hook set without internal implementation detail. `docs/README.codex.md` owns Codex installation and verification notes. `skills/task-system/SKILL.md` is the user-facing task-system skill surface; `skills/task-system/references/internals.md` owns task hook architecture details. Historical records under `docs/plans/` can remain historical unless they are used by active compatibility checks.

Official Codex hook reference consulted during planning: `https://developers.openai.com/codex/hooks`. Relevant current facts: plugin-bundled hooks can be loaded from `.codex-plugin/plugin.json`; `PostToolUse` supports `Bash`, `apply_patch`, and matcher aliases `Edit|Write` for `apply_patch`; `PostToolUse` input reports `tool_name: "apply_patch"` for file edits and carries edit content in `tool_input.command`; `PostToolUse` can return JSON `hookSpecificOutput.additionalContext` for model-visible feedback.

Date-field policy: `updated` is dropped because it duplicates git history and creates noisy metadata churn. Keep `created` for now unless the implementer finds it causes comparable churn or ambiguity; its main value is a stable human-facing task inception date, especially before the first commit or after task moves.

## Results
