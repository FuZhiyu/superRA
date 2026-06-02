---
title: "Reconcile docs and compatibility tests"
status: approved
depends_on:
  - 01-deprecate-decision-reminder
  - 02-enable-codex-task-hook
  - 03-drop-updated-frontmatter
tags: [docs, tests, codex]
script: ""
input: [README.md, docs/README.codex.md, skills/task-system/SKILL.md, skills/task-system/references/internals.md, tests/check-harness-compatibility.sh, tests/hooks/test-codex-hooks.sh, tests/hooks/test-codex-e2e-cli.sh]
output: [README.md, docs/README.codex.md, skills/task-system/SKILL.md, skills/task-system/references/internals.md, tests/check-harness-compatibility.sh, tests/hooks/test-codex-hooks.sh, tests/hooks/test-codex-e2e-cli.sh]
created: 2026-06-01
---

## Objective

Make active documentation and compatibility checks match the new supported behavior after the deprecation, Codex task-hook, and `updated` frontmatter cleanup tasks land.

Update the README hook table, Codex README, task-system skill docs, and task-system internals reference so they state:

- the user-decision reminder is deprecated/removed from active hook packaging;
- Codex installs task-system `PostToolUse` hooks for supported edit and shell paths;
- Codex shell interception remains incomplete where the official docs say it is incomplete, so the hook is a best-effort reconcile rather than a complete enforcement boundary;
- direct task edits are safe in Codex only through the supported `apply_patch`/`Bash` paths covered by tests.

Update `tests/check-harness-compatibility.sh` so it requires Codex `PostToolUse` task-hook wiring instead of asserting that Codex has no `PostToolUse`. Update `tests/hooks/test-codex-hooks.sh` stale expected strings from `PLAN.md + RESULTS.md` to `.plan/ task tree` and remove the decision-logger cases. Update the optional Codex CLI smoke test only if the installed hook set it asserts has changed materially.

If this task edits `skills/task-system/SKILL.md`, load `skill-creator` first and apply the root `CLAUDE.md` DRY and Necessity tests line by line. Generated Codex named-agent artifacts are not affected unless canonical `agents/*.md` changes; do not regenerate them for this task.

Validation: run `python3 -m json.tool hooks/hooks-codex.json`, `bash tests/hooks/test-codex-hooks.sh`, `uv run pytest skills/task-system/scripts/test_task_system.py`, and the Codex/Codex-agnostic portions of `bash tests/check-harness-compatibility.sh` after accounting for any unrelated pre-existing failures.

## Results

### Key Findings
- Active docs now list Codex task-system `PostToolUse` support and describe it as best-effort reconcile coverage rather than a complete shell-enforcement boundary ([README.md](../../../../README.md), [docs/README.codex.md](../../../../docs/README.codex.md)).
- Task-system docs now distinguish Codex direct task edits through `apply_patch` from structural task-tree shell commands through `Bash`, and the internals reference points to both Claude and Codex hook manifests ([skills/task-system/SKILL.md](../../../../skills/task-system/SKILL.md), [skills/task-system/references/internals.md](../../../../skills/task-system/references/internals.md)).
- Compatibility coverage now requires Codex `PostToolUse` task-hook wiring, exercises the manifest task-hook command, updates the stale `.plan/ task tree` Stop-hook fixture wording, and mirrors the new `PostToolUse` hook set in the optional Codex CLI smoke harness ([tests/check-harness-compatibility.sh](../../../../tests/check-harness-compatibility.sh), [tests/hooks/test-codex-hooks.sh](../../../../tests/hooks/test-codex-hooks.sh), [tests/hooks/test-codex-e2e-cli.sh](../../../../tests/hooks/test-codex-e2e-cli.sh)).

### Validation
- `python3 -m json.tool hooks/hooks-codex.json` passed.
- `bash tests/hooks/test-codex-hooks.sh` passed: 14 passed, 0 failed.
- `uv run pytest skills/task-system/scripts/test_task_system.py` passed: 232 passed.
- `bash tests/check-harness-compatibility.sh` passed the Claude plugin metadata, Codex plugin metadata, and shared harness adapter sections, including the new Codex `PostToolUse` assertions. It then failed in the unrelated sync-integration contract with six pre-existing failures in files outside this task write set: `skills/superintegrate/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`, `agents/reviewer.md`, and `skills/superplan/SKILL.md`.

### Notes
- Loaded `skill-creator` before editing [skills/task-system/SKILL.md](../../../../skills/task-system/SKILL.md) and kept the added skill text to the task-hook behavior difference needed by this task.
- Did not regenerate Codex named-agent artifacts because no canonical `agents/*.md` files changed.
- Did not run `tests/hooks/test-codex-e2e-cli.sh`; it is an optional logged-in Codex smoke test that spends model turns. The script was updated to mirror the current installed hook set.
