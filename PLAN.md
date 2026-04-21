# PLAN — superRA Autoload Hooks

## Objective

Add three hooks that keep the superRA skill-load state coherent without requiring the user or the agent to remember it manually:

1. **`autoload-superra`** (`UserPromptSubmit`) — soft reminder that detects "superRA" (and case/spacing variants) in the user's message and, if `superRA:using-superRA` has not been invoked this session, injects a system-reminder telling Claude to load it before responding.
2. **`ensure-using-superra`** (`PreToolUse` / `Skill`) — hard enforcement: when Claude invokes any `superRA:*-workflow` skill and `superRA:using-superRA` is NOT yet loaded, block the `Skill` call with a `permissionDecision: deny` and a reason directing Claude to load `using-superRA` first and then retry.
3. **`ensure-agent-orchestration`** (`PreToolUse` / `Skill`) — mirror of hook 2 for `superRA:agent-orchestration`. When any `superRA:*-workflow` skill is invoked without `agent-orchestration` loaded, block the `Skill` call with the same pattern.

Together: a user writing "let's do some superRA work" gets the soft reminder; any attempt to invoke a workflow skill without the companion skills loaded gets hard-intercepted and auto-corrected via deny-and-retry.

## Methodology

### Hook 1 — `autoload-superra` (UserPromptSubmit, soft)

- **Event:** `UserPromptSubmit` — fires once per user message, stdin `{session_id, transcript_path, cwd, hook_event_name, prompt}`.
- **Trigger:** case-insensitive match of `super[-_ ]?ra` with non-alphanumeric boundaries in `prompt`. Matches `superRA`, `super RA`, `super-ra`, `Super_RA`, `superra`; rejects `superrapid`.
- **Session-state detection:** regex-grep the JSONL `transcript_path` for `"skill"[[:space:]]*:[[:space:]]*"superRA:using-superRA"` (case-insensitive, whitespace-tolerant). Present → suppress; absent → emit.
- **Output:** on match + not-yet-loaded, emit `hookSpecificOutput.additionalContext` (matches `merge-guard` / `exit-plan-mode` convention). Never block the turn. **JSON string escaping:** the reminder text is passed through `python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'` before splicing into the payload, so any inner `"` or `\` in the reminder does not invalidate the JSON. (This is the CRITICAL fix from Task 1's first-round review.)
- **Cross-harness parity:** three-way platform branch (`CURSOR_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` / fallback).

### Hooks 2 & 3 — `ensure-using-superra` / `ensure-agent-orchestration` (PreToolUse, hard)

Both are PreToolUse hooks matched on tool name `Skill` and share the same skeleton:

- **Event:** `PreToolUse`, `matcher: "Skill"`. Stdin `{session_id, transcript_path, cwd, hook_event_name, tool_name, tool_input}`.
- **Trigger:** `tool_input.skill` is one of `superRA:planning-workflow`, `superRA:implementation-workflow`, `superRA:integration-workflow`. Any other `Skill` invocation — emit `{}`.
- **Companion-skill check:** grep `transcript_path` for the companion's `"skill":"superRA:<companion>"` pattern (same tolerant regex as hook 1). Present → emit `{}`. Absent → emit a deny:
  ```json
  {"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"<instruction>"}}
  ```
  The `permissionDecisionReason` tells Claude exactly what to do: load `superRA:<companion>` first, then retry the original workflow-skill invocation.
- **Companion per hook:** hook 2 guards `superRA:using-superRA`; hook 3 guards `superRA:agent-orchestration`.
- **Ordering:** both hooks run in parallel on the same PreToolUse event. If both companions are missing on the same call, both hooks deny; Claude loads them one at a time across two retries; the third retry of the original workflow-skill Skill call passes through both hooks silently.
- **Fail-open:** transcript_path missing / unreadable → emit `{}` (do not block). A misconfigured transcript must not wedge the workflow.

### Testing

A shell test driver per hook feeds synthetic JSON stdin and asserts the output's (a) JSON validity via `python3 -m json.tool` on every non-empty payload, and (b) presence/absence of the expected field (`additionalContext` for hook 1, `permissionDecision: deny` for hooks 2/3). Vectors cover the happy path, the loaded-already suppression, the trigger-boundary cases, JSON-special characters in the input, and the fail-open branch.

## Output

- `hooks/autoload-superra`, `hooks/ensure-using-superra`, `hooks/ensure-agent-orchestration` — three extensionless bash hook scripts.
- `hooks/hooks.json` — `UserPromptSubmit` entry for hook 1; two `PreToolUse` entries (matcher `Skill`) for hooks 2 and 3.
- `hooks/hooks-cursor.json` — mirrors above.
- `tests/hooks/test-autoload-superra.sh`, `tests/hooks/test-ensure-using-superra.sh`, `tests/hooks/test-ensure-agent-orchestration.sh` — one test driver per hook, each asserting JSON validity of every non-empty payload.

## Expected Result

- A fresh session where the user says "let's do some superRA work" → hook 1 injects reminder → Claude loads `using-superRA`. A follow-up `superRA` message in the same session produces no duplicate reminder.
- An agent that calls `Skill(superRA:planning-workflow)` without loading `using-superRA` → hook 2 denies the Skill call with a reason → agent calls `Skill(superRA:using-superRA)` → retries the workflow-skill call → succeeds (hook 3 may then intercept for `agent-orchestration`; same pattern repeats).
- A `Skill` call for a non-workflow skill, or with both companions already loaded, passes through all three hooks silently.

## Pipeline

Not applicable — this is plugin tooling, not an analysis pipeline.

## Workflow Status

- [x] Plan approved
- [ ] Implementation complete
- [ ] Review passed
- [ ] Integration complete

## Project Conventions

**Walk date:** 2026-04-20

### `CLAUDE.md` (repo root, `superRA` contributor guidelines)
Contributor-facing entry point. Modifying superRA itself is treated as skill-creation work; hooks are plugin code and follow the same "one problem per commit, test on at least one harness before claiming done" discipline. Design principles are load-bearing: workflow principles (implementer–reviewer pair, handoff docs as auditable record, fast-early-strict-before-merge, autonomous-with-human-in-loop), DRY / one-source-of-truth, and positive-instruction skill design. Edits to `skills/*/SKILL.md` require loading `skill-creator`; this task touches `hooks/` only, so `skill-creator` is not required.

### `~/.claude/CLAUDE.md` (user global preferences)
User is a finance academic, Julia-first, dictation-heavy. Prefers concise, accurate responses.

### `hooks/` conventions (inferred from existing hook files — no dedicated README)
Hooks are **extensionless bash scripts** at `hooks/<name>` (so Windows auto-detection doesn't prepend `bash` to `.sh`). A polyglot `hooks/run-hook.cmd` wrapper dispatches to the named script on both platforms. Every hook `set -euo pipefail`, reads JSON from stdin, and emits JSON to stdout. The output-format branch — `CURSOR_PLUGIN_ROOT` → `{"additional_context":"..."}`, `CLAUDE_PLUGIN_ROOT` (non-Copilot) → `{"hookSpecificOutput":{"hookEventName":"<event>","additionalContext":"..."}}`, else `{"additionalContext":"..."}` — is copied verbatim across `merge-guard`, `ask-user-question-logger`, and `exit-plan-mode`. Hooks are advisory: they inject reminders, they do NOT block (`does NOT block — the discipline system handles enforcement` is the repeated docstring). Registration lives in `hooks/hooks.json` (Claude Code) and `hooks/hooks-cursor.json` (Cursor); both must be updated together.

## Decisions

> **User decision (2026-04-20):** Scope expanded from one hook to three. Add two PreToolUse/Skill hooks alongside the existing `autoload-superra` UserPromptSubmit hook: `ensure-using-superra` (hard-intercepts any `Skill(superRA:*-workflow)` call when `using-superRA` is not yet loaded) and `ensure-agent-orchestration` (same pattern for `agent-orchestration`). Each hook lives in its own file rather than one combined hook. The interception mechanism is `permissionDecision: deny` with a reason directing Claude to load the missing companion skill and retry.
>
> **Question asked:** Should the new workflow-skill autoload be one combined hook or two separate hooks, and should it intercept (PreToolUse) or remind after (PostToolUse)?
>
> **Rationale:** User wants hard enforcement — soft reminders are acceptable for the user-prompt case where the agent still has discretion, but once a workflow skill is actually being invoked, the companion skills must be loaded. Two files keep each hook's concern single-purpose; PreToolUse deny-and-retry is the only primitive the harness exposes for hard enforcement. Affects: Task 3 added (write hooks 2 & 3), Task 4 reframed to register all new hooks, old Task 3 (live verification) renumbered to Task 5 and expanded to cover all three hooks.

---

## Task 1: Write the autoload-superra hook script

**Depends on:** *(none)*

**Objective:** Produce a tested, extensionless bash script at `hooks/autoload-superra` that implements the detection + transcript-gate logic described in Methodology, with the three-way platform output branch used by every other hook in the repo.

**Input:** stdin JSON `{prompt, transcript_path, ...}` from the `UserPromptSubmit` event.

**Output:**
- `hooks/autoload-superra` (executable, `chmod +x`).
- `tests/hooks/test-autoload-superra.sh` covering the vectors below.

**Methodology:**
1. Script body:
   - `set -euo pipefail`
   - Read stdin → `input`.
   - Extract `prompt` and `transcript_path` via `python3 -c 'import sys,json; ...'` (same pattern as `merge-guard`).
   - Fast-path `grep -iqE '(^|[^[:alnum:]])super[-_ ]?ra([^[:alnum:]]|$)'` on the prompt. No match → emit `{}`.
   - Transcript gate: if `$transcript_path` exists and `grep -Fq '"skill":"superRA:using-superRA"' "$transcript_path"`, emit `{}`.
   - Build the reminder context (text: instruct Claude to invoke `Skill(skill="superRA:using-superRA")` before its response, because the user has invoked a superRA workflow term).
   - Emit via the three-way platform branch (Cursor / Claude Code / fallback), event name `UserPromptSubmit`.
2. Test vectors (in `tests/hooks/test-autoload-superra.sh`, each asserted with a `grep -q` or equivalent on the hook's stdout):
   - **V1 — no superRA mention:** `prompt="let's refactor the data loader"` → `{}`.
   - **V2 — variant spellings:** `"superRA"`, `"super RA"`, `"super-ra"`, `"Super_RA"`, `"superra"` each → output contains `additionalContext` with the reminder.
   - **V3 — word boundary:** `"this is superrapid"` → `{}` (no false positive).
   - **V4 — already loaded:** prompt matches, but `transcript_path` points to a file containing `"skill":"superRA:using-superRA"` → `{}`.
   - **V5 — missing transcript file:** prompt matches, `transcript_path` empty or points to nonexistent file → reminder is emitted (fail-open to the useful side).

**Steps:**
- [x] Implement `hooks/autoload-superra` with header comment + test vectors listed as a regression table.
- [x] `chmod +x hooks/autoload-superra`.
- [x] Implement `tests/hooks/test-autoload-superra.sh` driving 12 vectors (the V1–V5 families in the Methodology table expanded for each spelling variant); the script prints `PASS`/`FAIL` per vector and exits non-zero if any fail.
- [x] Run `bash tests/hooks/test-autoload-superra.sh`; record the output in RESULTS.md Task 1. All 12 vectors pass.
- [x] Commit as `hooks: add autoload-superra UserPromptSubmit hook + tests`.

**Review status:** APPROVED


---

## Task 2: Register the hook in hooks.json and hooks-cursor.json

**Depends on:** 1

**Objective:** Wire `autoload-superra` into both hook configs so Claude Code and Cursor invoke it on every `UserPromptSubmit`.

**Input:** `hooks/hooks.json`, `hooks/hooks-cursor.json`, the new script from Task 1.

**Output:** Both JSONs updated; no other hooks perturbed.

**Methodology:**
- In `hooks/hooks.json`, add a `UserPromptSubmit` array sibling to `PreToolUse`/`PostToolUse`:
  ```json
  "UserPromptSubmit": [
    {
      "hooks": [
        { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" autoload-superra", "async": false }
      ]
    }
  ]
  ```
  (No `matcher` key — `UserPromptSubmit` does not take a tool-name matcher.)
- In `hooks/hooks-cursor.json`, add a `userPromptSubmit` array mirroring the existing style: `{ "command": "./hooks/autoload-superra" }`.

**Steps:**
- [x] Edit `hooks/hooks.json`; validate JSON (`python3 -m json.tool < hooks/hooks.json`).
- [x] Edit `hooks/hooks-cursor.json`; validate JSON.
- [x] Commit as `hooks: register autoload-superra for UserPromptSubmit`.

**Review status:** APPROVED

---

## Task 3: Write the two PreToolUse workflow-skill gate hooks + tests

**Depends on:** *(none — Task 2 only established the hooks.json pattern, which is already in-tree)*

**Objective:** Produce two tested extensionless bash scripts at `hooks/ensure-using-superra` and `hooks/ensure-agent-orchestration` that implement the hard-enforcement `PreToolUse` / `Skill` gate described in Methodology, and a regression test driver per hook.

**Input:** stdin JSON `{tool_name, tool_input, transcript_path, ...}` from the `PreToolUse` event.

**Output:**
- `hooks/ensure-using-superra` (executable).
- `hooks/ensure-agent-orchestration` (executable).
- `tests/hooks/test-ensure-using-superra.sh` and `tests/hooks/test-ensure-agent-orchestration.sh`.

**Methodology:**

1. Shared script skeleton (both hooks differ only in the companion skill name):
   - `set -euo pipefail`.
   - Read stdin → parse `tool_name`, `tool_input.skill`, `transcript_path` via a single `python3 -c '...'` call emitting tab-separated fields; consume with `IFS=$'\t' read -r`.
   - Fast path: if `tool_name != "Skill"` or `tool_input.skill` is not in the allow-list `{superRA:planning-workflow, superRA:implementation-workflow, superRA:integration-workflow}`, emit `{}`.
   - Companion check: if `transcript_path` is empty, unset, or not a regular file → emit `{}` (fail-open). Otherwise grep `"skill"[[:space:]]*:[[:space:]]*"superRA:<companion>"` (case-insensitive). Present → emit `{}`.
   - Deny branch: emit `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"<instruction>"}}`. **Escape `<instruction>` through `python3 json.dumps` before splicing**, so any inner `"` or `\` in the reason cannot break the payload. The instruction names the exact companion skill and tells Claude to load it then retry the original workflow-skill call.
   - Three-way platform branch for the output shape, matching the other hooks.
2. Test vectors (per hook; assertions include a `python3 -m json.tool` validity check on every non-empty payload):
   - **V1 — non-Skill tool:** `tool_name="Bash"` → `{}`.
   - **V2 — Skill, non-workflow:** `tool_input.skill="superRA:handoff-doc"` → `{}`.
   - **V3 — workflow skill, companion missing:** each of the three workflow skills, transcript empty → deny payload with the companion name in the reason.
   - **V4 — workflow skill, companion present:** transcript contains the companion's `"skill":"..."` tool_use line → `{}`.
   - **V5 — fail-open:** `transcript_path=""` or points to a nonexistent file → `{}` regardless of trigger match (the hook must never wedge a session on a missing transcript).
   - **V6 — deny reason contains no unescaped metacharacters:** the emitted JSON parses via `python3 -m json.tool` and the `permissionDecisionReason` round-trips intact.

**Steps:**
- [ ] Dispatch implementer subagent to author both scripts and both test drivers as one bundle (same skeleton, per `superRA:agent-orchestration` §Workload Balancing Tier 2).
- [ ] Implementer runs both test scripts, records `PASS`/`FAIL` per vector in RESULTS.md Task 3.
- [ ] Implementer commits as `hooks: add ensure-using-superra + ensure-agent-orchestration PreToolUse gates`.
- [ ] Reviewer subagent runs a comprehensive pass per `agents/reviewer.md`; iterate to APPROVE.

**Review status:**

---

## Task 4: Register the two new hooks in hooks.json and hooks-cursor.json

**Depends on:** 3

**Objective:** Wire `ensure-using-superra` and `ensure-agent-orchestration` into both hook configs so every `Skill` tool invocation passes through the gates.

**Input:** `hooks/hooks.json`, `hooks/hooks-cursor.json`, the new scripts from Task 3.

**Output:** Both JSONs updated with two new `PreToolUse` entries (Claude Code) and two new `preToolUse` entries (Cursor), both scoped to `matcher: "Skill"`. No other hooks perturbed.

**Methodology:**
- In `hooks/hooks.json`, append to the existing `PreToolUse` array two additional entries with `matcher: "Skill"`:
  ```json
  { "matcher": "Skill",
    "hooks": [ { "type": "command",
                 "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" ensure-using-superra",
                 "async": false } ] }
  ```
  (and a sibling entry for `ensure-agent-orchestration`).
- In `hooks/hooks-cursor.json`, append two entries to `preToolUse` mirroring the existing `./hooks/<name>` style.
- Validate both JSONs with `python3 -m json.tool`.

**Steps:**
- [ ] Dispatch implementer subagent (Tier 1 — trivial JSON edit; orchestrator may handle inline at its discretion, but default is subagent per workflow).
- [ ] Implementer validates both JSONs and commits as `hooks: register ensure-using-superra and ensure-agent-orchestration PreToolUse gates`.
- [ ] Reviewer pass confirms no regressions to existing hook registrations.

**Review status:**

---

## Task 5: End-to-end verification in a fresh session

**Depends on:** 4

**Objective:** Confirm all three hooks fire as designed in a real Claude Code session — soft reminder on first superRA mention; hard deny-and-retry when a workflow skill is invoked without companions loaded; silent pass-through otherwise.

**Input:** All three hooks registered in both configs.

**Output:** Transcript excerpts pasted into RESULTS.md Task 5 showing (a) soft-reminder fire on first-mention, (b) suppression on second mention, (c) hard deny-and-retry when the user asks the agent to invoke `Skill(superRA:planning-workflow)` in a fresh session, (d) control prompt with no trigger.

**Methodology:**
1. User opens a fresh Claude Code session in this worktree.
2. **Probe A (soft):** User sends `"quick superRA sanity check — what phase am I in?"`. Expected: hook 1 injects reminder; Claude invokes `Skill(superRA:using-superRA)`; response proceeds.
3. **Probe B (suppression):** User sends another superRA-containing prompt. Expected: no new reminder.
4. **Probe C (hard gate):** User opens a *different* fresh session and asks the agent to load the planning workflow directly without first loading `using-superRA` (phrased so the agent does not invoke `using-superRA` on its own). Expected: `Skill(superRA:planning-workflow)` is denied by hook 2; agent loads `using-superRA`, retries; hook 3 may then deny pending `agent-orchestration`; agent loads it; third retry of the workflow-skill call passes.
5. **Probe D (control):** A non-superRA prompt → no hook output.
6. User pastes outcomes; orchestrator records in RESULTS.md and marks APPROVED or files issues.

**Steps:**
- [ ] Orchestrator announces the verification protocol to the user.
- [ ] User runs the four probes above in two fresh sessions (Probes A/B/D in session 1; Probe C in session 2).
- [ ] Orchestrator records outcomes in RESULTS.md Task 5.
- [ ] Commit as `hooks: verify all three autoload hooks end-to-end`.

**Review status:**
