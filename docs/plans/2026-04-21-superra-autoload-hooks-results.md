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

**Status:** SUPERSEDED by Task 6 — manual probe protocol replaced by `tests/hooks/test-e2e-cli.sh`.

## Task 6: Automate end-to-end verification via the claude CLI

**Status:** APPROVED — full suite (S1 S2 S3 S4 S5 S6) passes 7/7 by default; S4 documented as opportunistic per the 2026-04-21 user decision in PLAN.md §Decisions.

Delivered `tests/hooks/test-e2e-cli.sh`, a driver that runs the real `claude` CLI (2.1.116) with `--include-hook-events --output-format=stream-json` and asserts on the NDJSON event stream. Every invocation passes `--model haiku` (claude-haiku-4-5) to keep cost minimal, and uses `--plugin-dir $REPO_ROOT` so the in-tree `hooks.json` registration is the one under test.

### Event-stream shape discovered

Each hook invocation produces two NDJSON records:
- `{"type":"system","subtype":"hook_started","hook_name":"<event[:matcher]>","hook_event":"<event>",...}` — e.g. `hook_name="PreToolUse:Skill"`, `hook_name="UserPromptSubmit"`.
- `{"type":"system","subtype":"hook_response","hook_name":"<event[:matcher]>","stdout":"<hook-script-stdout>","exit_code":0,...}` — the hook script's stdout is carried verbatim inside the `stdout` field (with `\n` preserved and inner JSON escaped once).

**`hook_name` is the event name (plus `:matcher` for tool-matched hooks), NOT the hook script file name.** When two hooks are registered for the same `PreToolUse:Skill` event (as is the case here for `ensure-using-superra` and `ensure-agent-orchestration`), both fire in parallel and both produce separate `hook_started` / `hook_response` records with identical `hook_name`. They can only be distinguished by inspecting the `stdout` payload (one may emit `{}`, the other a deny JSON).

The driver therefore asserts on the *set* of `stdout` payloads per event rather than per-hook-script. For a silent pass-through we require every `PreToolUse:Skill` `hook_response` to have stdout in `{"", "{}\n"}`; for a deny we require at least one to contain the target companion's name in a `permissionDecisionReason`.

### Session / state isolation + auto-cleanup

- Every scenario uses a fresh UUID via `--session-id` and runs in a per-scenario temp cwd rooted at a session-wide `TMPROOT=$(mktemp -d)`.
- `trap cleanup EXIT INT TERM` removes `TMPROOT` (NDJSON captures + scenario cwds) and every matching `~/.claude/projects/<cwd-hash>/` dir.
- The project-dir key is derived from the canonical cwd (macOS `/var/folders/` → `/private/var/folders/`) with both `/` and `.` translated to `-`. The canonical path is recorded at cwd-creation time so the trap can still derive the key after the scratch dir has been removed.
- The canonical path is stored via module-level globals (`TMP_CWD`, `TMP_CWD_CANON`) instead of command-substitution return values, because `arr+=(x)` inside `$(...)` only mutates the subshell's array — the parent shell's cleanup arrays would otherwise be empty.
- **Pre/post `ls ~/.claude/projects/` diff confirms zero residue.**
- `CLAUDE_CONFIG_DIR` is deliberately NOT overridden: a fresh config dir breaks auth (the user's OAuth token is not there), so the suite uses `--no-session-persistence` + cwd isolation + trap cleanup instead. This deviates from the dispatch prescription of a scratch `CLAUDE_CONFIG_DIR`, but the prescription does not work in practice on this machine.

### Cost discipline

The dispatch proposed `--tools ""` + `--append-system-prompt` to make hook-only scenarios free of model turns. **This did not work on 2.1.116** — the model still takes one turn per `claude -p` invocation even with zero tools enabled; `--tools ""` only prevents tool *invocation*, not the turn itself. As fallback the driver passes `--model haiku` on every invocation. Observed cost: ~$0.01–$0.02 per hook-only scenario; ~$0.09–$0.10 each for S4/S5 (multi-turn deny-and-retry chains pull the full bodies of `using-superRA` and `agent-orchestration` into subsequent turns).

### Full-suite output

```
claude CLI: 2.1.116
plugin dir: /Users/zhiyufu/Dropbox/package_dev/superRA-dev
mode:       DEFAULT (CLAUDE_E2E_FULL=0)

=== S1 ===
PASS  S1 autoload reminder fires on superRA                        (reminder injected)
       cost: $0.0150

=== S2 ===
PASS  S2 setup load using-superRA                                  (setup skill loaded)
PASS  S2 autoload suppressed after skill load                      (silent as expected)
       setup cost: $0.0194    check cost: $0.0180

=== S3 ===
PASS  S3 autoload silent without trigger                           (silent as expected)
       cost: $0.0123

=== S6 ===
PASS  S6 non-workflow Skill passes through both gates silently     (all PreToolUse silent)
       cost: $0.0181

=== S4 (FULL) ===
PASS  S4 ensure-using-superra denies workflow skill                (deny with superRA:using-superRA in reason)
       cost: $0.0893

=== S5 (FULL) ===
PASS  S5 ensure-agent-orchestration denies after using-superRA loads (deny with superRA:agent-orchestration in reason)
       cost: $0.0988


Passed: 7    Failed: 0
```

Total cost: ~$0.27. Pre/post `~/.claude/projects/` diff empty (NO_LEAK). S4 and S5 are the dominant cost: each runs a multi-turn deny-and-retry sequence that loads `using-superRA` and (S5 only) `agent-orchestration`, both of which add their full skill bodies to every subsequent turn's input.

### S4 fragility (deferred design issue, accepted)

S4 is structurally hard to test in isolation because `autoload-superra` injects a `superRA:using-superRA` reminder into the user-prompt context, and a compliant model loads the companion before reaching the workflow-skill call — which makes `ensure-using-superra` silently pass and the assertion fail. The driver works around this by instructing the model in its system prompt to *ignore the injected reminder* and proceed straight to `Skill(superRA:planning-workflow)`. Haiku obeys, so S4 currently passes.

The cleaner fix would suppress the `UserPromptSubmit` hook for S4's invocation only, but Claude Code's `--settings` JSON merges array-shaped settings (including hooks) across scopes rather than overriding them, so the obvious `--settings '{"hooks":{"UserPromptSubmit":[]}}'` trick does not strip plugin-registered hooks. Per the 2026-04-21 user decision (PLAN.md §Decisions), the residual fragility is accepted: the deny *logic* is already covered by the stdin-synthesis unit test in `tests/hooks/test-ensure-using-superra.sh`, and S5 redundantly covers the `PreToolUse:Skill` *wiring* against the live CLI. If a future model regresses S4 by preferring injected reminders over its system prompt, the disposition path (delete S4) is documented inline in the test's S4 docstring.

### Run this locally

```bash
bash tests/hooks/test-e2e-cli.sh    # all six scenarios
```

Requires `claude` on PATH (logged in via keychain), `python3`, and `uuidgen`. Not part of default `tests/` runs.
