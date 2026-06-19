---
title: "Build Fixtures And Transcript Parser"
status: approved
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
- Added reusable transcript parsing and assertion helpers in [transcript_assertions.py](../../../../../tests/harness-instruction-following/transcript_assertions.py). The helpers parse Claude stream JSON and Codex JSONL, preserve event order, require `superra task read <path>` evidence from structural command/tool events, require task and marker reads before the first write event by default, check Claude `Agent` role dispatch or Codex `spawn_agent` dispatch separately from documented fallback evidence, and compare expected artifact scalar values while collecting all missing evidence in one report.
- Added CI-safe parser and fixture tests in [test_transcript_assertions.py](../../../../../tests/harness-instruction-following/test_transcript_assertions.py) and [test_bundle_fixture.py](../../../../../tests/harness-instruction-following/test_bundle_fixture.py). The tests use committed synthetic transcript samples and local `task_read.py`; no live Claude/Codex calls are run. Negative tests now cover prose-only task-read narration, pre-read writes to non-artifact files, and prose-only orchestrator dispatch narration.

### Real-Harness Robustness Fixes (from live smoke runs)

Driving real `codex exec --json` output through the parser during the live smokes (03/04/07) surfaced two ways the committed synthetic samples did not represent real harness output. Both are fixed in `transcript_assertions.py` with regression tests:

- **Non-JSON banner lines.** Real codex prints `Reading additional input from stdin...` before the JSONL stream begins. `parse_json_events` now skips lines not shaped like a JSON object/array, but still raises on a `{`/`[`-shaped line that fails to parse, so a genuinely corrupt event stream is not silently dropped (`test_parser_skips_non_json_banner_lines`, `test_parser_still_raises_on_corrupt_json_event`).
- **Quote-/wrapper-terminated task-read commands.** Real codex wraps the command as `zsh -lc './superRA/superra task read <path>'`, so the task path is reached through the wrapper path and terminated by a closing quote rather than whitespace. `_command_runs_task_read`'s trailing boundary now accepts a quote, not just whitespace/EOL/operator (`test_task_read_detected_in_wrapped_quoted_command`).

### Verification

- `uv run --with pytest python -m pytest tests/harness-instruction-following` — 27 passed.
