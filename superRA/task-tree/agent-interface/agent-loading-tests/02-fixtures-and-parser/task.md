---
title: "Build Fixtures And Transcript Parser"
status: not-started
depends_on:
  - 01-load-contract-audit
tags: []
created: 2026-06-19
---

## Objective

Build the reusable, deterministic infrastructure for instruction-following tests: tiny mock task trees, sentinel files, and transcript parsers/assertions that can be used by both Claude and Codex live scripts.

The primary fixture should be a bundled disposable superRA task tree, not isolated one-behavior probes. One dispatch should be able to exercise several required behaviors at once by asking the agent to work on a task bundle and emit one evidence JSON artifact. The mock task should be intentionally superficial: its only substantive action is to gather required sentinel values from realistic superRA surfaces and write them into the artifact.

The fixture layer should include `tests/fixtures/task-trees/bundle-two-tasks/` with:

- Root, parent, and target task sentinel strings proving `superra task read` surfaced ancestor and target context.
- A sibling dependency with a status/title sentinel and a separate `## Results` sentinel proving dependency results are not inherited unless explicitly read.
- An unresolved comment sentinel proving task-read comment surfacing.
- At least one required external marker file whose content is not present in the prompt and must be read before the agent can produce the expected evidence artifact.
- Two related leaf tasks or one task plus one dependency so a single dispatch can require multiple `superra task read` calls and demonstrate ordering before any write.
- Distinct sentinel groups for task-read context, explicit marker-file read, dependency metadata, dependency result exclusion, and output artifact content.
- A promptable task objective that is fast but realistic: inspect assigned task context, read listed marker files, and write `loading-evidence.json`; no code edits besides that artifact and no test-suite execution.

The parser/assertion layer should support:

- Claude stream JSON from `claude -p --include-hook-events --output-format=stream-json --verbose`.
- Codex JSONL from `codex exec --json`.
- Structural checks for required file/tool events, especially `superra task read <path>`, before any write/edit/file-change event.
- Artifact checks for sentinel values emitted by the agent into a small JSON file.
- Bundled assertions that report all missing behaviors from one run, rather than failing after the first missing sentinel.

## Planner Guidance

Keep parser tests CI-safe by feeding committed sample transcripts or synthetic JSON events for the bundled scenario. The parser should expose clear failure messages that name the missing requirement and the expected path/command.

Avoid transcript-shape assumptions beyond what existing harness scripts already depend on; share recursive string/event search helpers where possible. Keep fixture setup local and cheap: copy or generate only a handful of files into a temporary workspace.

## Results
