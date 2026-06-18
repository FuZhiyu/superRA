---
title: "Deprecate user-decision reminder hook"
status: approved
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

Removed the decision-reminder hook from active installation surfaces: `hooks/hooks.json` no longer registers the `AskUserQuestion` `PostToolUse` hook, `hooks/hooks-cursor.json` no longer lists `./hooks/ask-user-question-logger`, and the obsolete `hooks/ask-user-question-logger` executable was deleted so new installs cannot expose it ([../../../../hooks/hooks.json](../../../../hooks/hooks.json), [../../../../hooks/hooks-cursor.json](../../../../hooks/hooks-cursor.json)).

Updated active hook documentation to stop advertising the reminder or future `request_user_input` support while leaving the durable task-file decision protocol intact ([../../../../README.md](../../../../README.md), [../../../../docs/README.codex.md](../../../../docs/README.codex.md)).

Updated the focused Codex hook tests by removing both `request_user_input`/decision-logger cases. While rerunning the suite, the remaining Codex plan-stop cases exposed stale `PLAN.md + RESULTS.md` expectations, so the same test file now expects the current `superRA/ task tree` reminder text emitted by `hooks/codex-plan-stop` ([../../../../tests/hooks/test-codex-hooks.sh](../../../../tests/hooks/test-codex-hooks.sh)).

Validation:

- `python3 -m json.tool hooks/hooks.json` — passed.
- `python3 -m json.tool hooks/hooks-cursor.json` — passed.
- `python3 -m json.tool hooks/hooks-codex.json` — passed.
- `bash tests/hooks/test-codex-hooks.sh` — passed, 13/13 cases.
- `rg -n "ask-user-question-logger|request_user_input" hooks README.md docs/README.codex.md tests/hooks/test-codex-hooks.sh skills/using-superra/references/codex-instructions.md` — only the intentional Codex adapter mapping remains in `skills/using-superra/references/codex-instructions.md`.
