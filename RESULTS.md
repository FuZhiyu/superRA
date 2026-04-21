# RESULTS — superRA Autoload Hook

## Task 1: Write the autoload-superra hook script

**Status:** IMPLEMENTED

Created `hooks/autoload-superra` (extensionless bash, `chmod +x`) and `tests/hooks/test-autoload-superra.sh`. The hook:

- Parses stdin UserPromptSubmit JSON via python3, extracting `prompt` and `transcript_path` as tab-separated so `IFS=$'\t' read` splits cleanly even when the prompt contains spaces.
- Fast-path `grep -iqE '(^|[^[:alnum:]])super[-_ ]?ra([^[:alnum:]]|$)'` on the prompt. No match → `{}`.
- Transcript gate: `grep -iEq '"skill"[[:space:]]*:[[:space:]]*"superRA:using-superRA"' "$transcript_path"` — case-insensitive, whitespace-tolerant around the colon so minor format drift does not produce duplicate reminders. Match → `{}`. Fails-open when transcript_path is missing or empty (V5).
- JSON-escapes the reminder text through `python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'` before splicing into the payload, so inner `"` / `\` in the reminder cannot invalidate the JSON. The three-way platform branch (`CURSOR_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` / fallback) matches `merge-guard`, `ask-user-question-logger`, and `exit-plan-mode` while emitting the already-quoted JSON string.

Regression suite (`tests/hooks/test-autoload-superra.sh`, 16 vectors — V6 family added per review finding 3; every non-empty payload asserted via `python3 -m json.tool` per finding 2):

```
PASS  V1 no-mention                                      (got silent)
PASS  V2a superRA                                        (got reminder)
PASS  V2b super RA                                       (got reminder)
PASS  V2c super-ra                                       (got reminder)
PASS  V2d Super_RA                                       (got reminder)
PASS  V2e superra lc                                     (got reminder)
PASS  V2f mid-sentence                                   (got reminder)
PASS  V3 superrapid                                      (got silent)
PASS  V3 superrant                                       (got silent)
PASS  V4 already-loaded                                  (got silent)
PASS  V4b other-superRA-skill                            (got reminder)
PASS  V5 empty-transcript-path                           (got reminder)
PASS  V6a embedded-dquote                                (got reminder)
PASS  V6b embedded-bslash                                (got reminder)
PASS  V6c multiline-prompt                               (got reminder)
PASS  V6d non-ascii                                      (got reminder)

Passed: 16    Failed: 0
```

The V4b vector ("transcript shows `superRA:planning-workflow` loaded but not `using-superRA`") deliberately triggers the reminder — the transcript gate is specifically about the master skill. V6a–d cover JSON-special and non-ASCII prompts; the hook does not embed the prompt into its output, but the vectors fence against a future regression that would.

## Task 2: Register the hook in hooks.json and hooks-cursor.json

**Status:** IMPLEMENTED

Added `UserPromptSubmit` array to `hooks/hooks.json` (Claude Code) routing through `run-hook.cmd autoload-superra`, and a `userPromptSubmit` entry to `hooks/hooks-cursor.json` (Cursor) invoking `./hooks/autoload-superra` directly. Both JSONs validate via `python3 -m json.tool`. No `matcher` field on the Claude Code registration — `UserPromptSubmit` does not scope by tool name.

## Task 3: Write the two PreToolUse workflow-skill gate hooks + tests

**Status:** IMPLEMENTED

Created two extensionless bash hooks at `hooks/ensure-using-superra` and `hooks/ensure-agent-orchestration` (both `chmod +x`), plus one test driver per hook at `tests/hooks/test-ensure-using-superra.sh` and `tests/hooks/test-ensure-agent-orchestration.sh`. The two hooks share an identical skeleton, differing only in the `COMPANION` variable and the companion-specific grep pattern:

- Parse `tool_name`, `tool_input.skill`, and `transcript_path` from the PreToolUse JSON via a single python3 call emitting tab-separated fields; consume with `IFS=$'\t' read -r`.
- Fast-path silent `{}` when `tool_name != "Skill"` or when the skill is not one of `{superRA:planning-workflow, superRA:implementation-workflow, superRA:integration-workflow}`.
- Fail-open silent `{}` when `transcript_path` is empty, unset, or points to a non-regular file.
- Companion check: `grep -iEq '"skill"[[:space:]]*:[[:space:]]*"superRA:<companion>"'` (case-insensitive, whitespace-tolerant around the colon — matches the tolerance already proven in `autoload-superra`). Present → silent `{}`. Absent → deny branch.
- Deny branch: build the reason string (naming the companion and instructing Claude to load it then retry the original call), JSON-escape it through `python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'`, splice into `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":<escaped>}}`. The escape step is load-bearing — without it, the embedded `Skill(skill="…")` double-quotes in the reason would break the JSON. This is the CRITICAL fix carried over from Task 1's first-round review (commit 554be0c).
- Three-way platform output branch (`CURSOR_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` / fallback). For deny decisions the payload shape is the same across all three branches because the harnesses agree on `hookSpecificOutput` for PreToolUse denials; the branch is retained for shape parity with the other hooks.

The two test drivers each run 16 vectors covering all six families listed in Task 3 Methodology. Every non-empty payload is asserted via `python3 -c 'import json,sys; json.loads(sys.stdin.read())'`; every deny payload is additionally asserted to contain the companion skill name in its `permissionDecisionReason` (V6 round-trip). V4d adds a tolerant-whitespace fixture (`{ "skill" : "..." }`) to lock in the case-insensitive + whitespace-tolerant grep.

`bash tests/hooks/test-ensure-using-superra.sh`:

```
PASS  V1 non-Skill Bash                                  (got silent)
PASS  V1 non-Skill Read                                  (got silent)
PASS  V2 Skill handoff-doc                               (got silent)
PASS  V2 Skill using-superRA itself                      (got silent)
PASS  V2 Skill agent-orchestration                       (got silent)
PASS  V2 Skill empty                                     (got silent)
PASS  V3a planning-workflow no-transcript                (got deny)
PASS  V3b implementation-workflow not-loaded             (got deny)
PASS  V3c integration-workflow not-loaded                (got deny)
PASS  V4a planning-workflow loaded                       (got silent)
PASS  V4b implementation-workflow loaded                 (got silent)
PASS  V4c integration-workflow loaded                    (got silent)
PASS  V4d tolerant-whitespace                            (got silent)
PASS  V5a transcript empty-string                        (got silent)
PASS  V5b transcript nonexistent                         (got silent)
PASS  V6 deny-reason round-trip                          (got deny)

Passed: 16    Failed: 0
```

`bash tests/hooks/test-ensure-agent-orchestration.sh`:

```
PASS  V1 non-Skill Bash                                  (got silent)
PASS  V1 non-Skill Read                                  (got silent)
PASS  V2 Skill handoff-doc                               (got silent)
PASS  V2 Skill using-superRA                             (got silent)
PASS  V2 Skill agent-orchestration                       (got silent)
PASS  V2 Skill empty                                     (got silent)
PASS  V3a planning-workflow no-transcript                (got deny)
PASS  V3b implementation-workflow not-loaded             (got deny)
PASS  V3c integration-workflow not-loaded                (got deny)
PASS  V4a planning-workflow loaded                       (got silent)
PASS  V4b implementation-workflow loaded                 (got silent)
PASS  V4c integration-workflow loaded                    (got silent)
PASS  V4d tolerant-whitespace                            (got silent)
PASS  V5a transcript empty-string                        (got silent)
PASS  V5b transcript nonexistent                         (got silent)
PASS  V6 deny-reason round-trip                          (got deny)

Passed: 16    Failed: 0
```

V3 uses the *other* companion's transcript fixture — e.g. the `ensure-using-superra` V3 vectors pass a transcript that only shows `superRA:agent-orchestration` being loaded, and the hook correctly denies because it specifically guards `superRA:using-superRA`. This locks in that each hook's companion check is independent.

## Task 4: Register the two new hooks in hooks.json and hooks-cursor.json

**Status:** IMPLEMENTED

Appended two `"matcher": "Skill"` entries to the existing `PreToolUse` array in `hooks/hooks.json` — one for `ensure-using-superra`, one for `ensure-agent-orchestration` — each routed through `"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd"`. Appended two parallel entries (`./hooks/ensure-using-superra` and `./hooks/ensure-agent-orchestration`) to `preToolUse` in `hooks/hooks-cursor.json`. The existing `merge-guard` / Bash entry is untouched in both files, as are the `UserPromptSubmit` (autoload-superra) and `PostToolUse` blocks. Both hooks will run in parallel on every `PreToolUse:Skill` event; if both companions are missing, both deny — Claude loads them across two retries, then the third retry of the original workflow-skill call passes silently.

`python3 -m json.tool < hooks/hooks.json` and `python3 -m json.tool < hooks/hooks-cursor.json` both parse cleanly (stdout omitted, exit 0).

## Task 5: End-to-end verification in a fresh session

**Status:** Not started

## Task 6: Automate end-to-end verification via the claude CLI

**Status:** Not started
