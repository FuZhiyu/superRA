---
title: "Build Fixtures And Transcript Parser"
status: revise
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
- Structural checks for orchestrator events in a `superimplement` scenario, such as Claude role-agent dispatch or Codex `spawn_agent(agent_type="superra_implementer")` / `spawn_agent(agent_type="superra_reviewer")`, with documented skip/fallback handling when a harness cannot expose subagent events.
- Artifact checks for sentinel values emitted by the agent into a small JSON file.
- Bundled assertions that report all missing behaviors from one run, rather than failing after the first missing sentinel.

## Planner Guidance

Keep parser tests CI-safe by feeding committed sample transcripts or synthetic JSON events for the bundled scenario. The parser should expose clear failure messages that name the missing requirement and the expected path/command.

Avoid transcript-shape assumptions beyond what existing harness scripts already depend on; share recursive string/event search helpers where possible. Keep fixture setup local and cheap: copy or generate only a handful of files into a temporary workspace.

## Results

Implemented the deterministic harness-instruction infrastructure without adding live model runners.

### Key Findings

- Added the bundled disposable task tree fixture at [tests/fixtures/task-trees/bundle-two-tasks/README.md](../../../../../tests/fixtures/task-trees/bundle-two-tasks/README.md). It includes root, parent, primary-target, and secondary-target context sentinels; an approved sibling dependency with title/status metadata and an excluded `## Results` sentinel; a JSON `comments.yaml` unresolved comment sentinel; marker files; and [expected/loading-evidence.expected.json](../../../../../tests/fixtures/task-trees/bundle-two-tasks/expected/loading-evidence.expected.json).
- Added reusable transcript parsing and assertion helpers in [transcript_assertions.py](../../../../../tests/harness-instruction-following/transcript_assertions.py). The helpers parse Claude stream JSON and Codex JSONL, preserve event order, check required task/file reads before writes, check orchestrator dispatch or documented fallback evidence, and compare expected artifact scalar values while collecting all missing evidence in one report.
- Added CI-safe parser and fixture tests in [test_transcript_assertions.py](../../../../../tests/harness-instruction-following/test_transcript_assertions.py) and [test_bundle_fixture.py](../../../../../tests/harness-instruction-following/test_bundle_fixture.py). The tests use committed synthetic transcript samples and local `task_read.py`; no live Claude/Codex calls are run.

### Verification

- `uv run --with pytest python -m pytest tests/harness-instruction-following` — 9 passed.

## Review Notes

1. [MAJOR] The task-read assertion accepts prose as structural evidence. [check_task_reads_before_write](../../../../../tests/harness-instruction-following/transcript_assertions.py#L201-L215) delegates to [check_event_before_write](../../../../../tests/harness-instruction-following/transcript_assertions.py#L179-L198), which only requires an event haystack containing `"superra task read"` and the path. An assistant message like "I will run superra task read agent-loading-bundle/02-primary-loading-task" before a write satisfies the check even though no tool/command event occurred. This violates the objective's requirement for structural file/tool evidence. Require a shell/tool event whose command actually invokes `superra task read <path>`, and add a negative test where assistant narration alone must fail.

2. [MAJOR] The default ordering check ignores writes to files other than `loading-evidence.json`. [check_task_reads_before_write](../../../../../tests/harness-instruction-following/transcript_assertions.py#L201-L215) and [check_file_reads_before_write](../../../../../tests/harness-instruction-following/transcript_assertions.py#L218-L230) both pass `write_path="loading-evidence.json"` into [first_write_index](../../../../../tests/harness-instruction-following/transcript_assertions.py#L289-L299), so a transcript can edit source code or another artifact before any required task/marker read and still pass as long as the required reads precede the final evidence artifact write. The objective asks for required reads before any write/edit/file-change event and the fixture forbids code edits. Make the default boundary the first write event of any path, or add a separate no-extra-writes assertion that fails on earlier non-artifact writes.

3. [MAJOR] Orchestrator dispatch evidence can also pass on assistant prose. [check_orchestrator_dispatches](../../../../../tests/harness-instruction-following/transcript_assertions.py#L233-L265) searches every event for `superra_implementer` and `superra_reviewer`, without verifying a Claude role-agent dispatch, a Codex `spawn_agent` tool call, or an explicit documented fallback event. A plain assistant message saying it should dispatch both roles is recorded as "orchestrator dispatch events observed." Tighten this to recognized dispatch tool/event shapes, keep fallback evidence distinct, and add a negative prose-only test.
