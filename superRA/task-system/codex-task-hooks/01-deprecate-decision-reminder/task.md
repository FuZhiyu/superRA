---
title: "Deprecate user-decision reminder hook"
status: not-started
depends_on: []
tags: [hooks, deprecation]
script: ""
input: [hooks/hooks.json, hooks/hooks-cursor.json, hooks/ask-user-question-logger, README.md, docs/README.codex.md, tests/hooks/test-codex-hooks.sh]
output: [hooks/hooks.json, hooks/hooks-cursor.json, README.md, docs/README.codex.md, tests/hooks/test-codex-hooks.sh]
created: 2026-06-01
---

## Objective

Remove `ask-user-question-logger` as an active superRA hook. The researcher has decided to drop the user-decision reminder rather than preserve it as a Claude-only or future Codex hook.

Implementation should remove the hook from active manifests (`hooks/hooks.json` and `hooks/hooks-cursor.json`) and remove or retire the hook script so new installs do not expose it. Update active docs that list installed hooks so they no longer advertise the reminder or mention future `request_user_input` support. Update focused hook tests by deleting the `request_user_input`/decision-logger cases rather than preserving a manual-only compatibility contract.

Preserve the underlying workflow rule that material decisions are folded into task objectives before action; this task removes the reminder mechanism, not the durable task-file protocol. Historical archived planning/results docs may keep old mentions as historical record unless an active test greps them as runtime behavior.

Validation: JSON-validate hook manifests, run the focused hook tests after their expected strings are updated, and grep active runtime/docs surfaces for `ask-user-question-logger` and `request_user_input` to confirm only intentional historical or adapter-tool references remain.

## Results
