# PLAN — superRA Autoload Hook

## Objective

Add a `UserPromptSubmit` hook that detects "superRA" (and case/spacing variants) in the user's message and, if `superRA:using-superRA` has not already been loaded this session, injects a system-reminder instructing Claude to load it before responding. Goal: remove the need for the user or the agent to remember to load the master skill manually at the start of a superRA task.

## Methodology

- **Hook event:** `UserPromptSubmit` — fires once per user message, receives `{session_id, transcript_path, cwd, hook_event_name, prompt}` on stdin.
- **Trigger:** case-insensitive match of `super[-_ ]?ra` with non-alphanumeric boundaries in the `prompt` field. Matches `superRA`, `super RA`, `super-ra`, `Super_RA`, `superra`; rejects `superrapid`.
- **Session-state detection:** grep the JSONL `transcript_path` for a prior `Skill` tool invocation naming `superRA:using-superRA`. If present → suppress the reminder; if absent → emit it. Grep on the literal string `"skill":"superRA:using-superRA"` is sufficient — the transcript records tool calls as JSON, and a false positive (e.g., the user literally pasting that string in a prior turn) is harmless.
- **Output shape:** on match + not-yet-loaded, emit `hookSpecificOutput.additionalContext` (matches the existing `merge-guard` / `exit-plan-mode` convention). Otherwise emit `{}`. Never block the turn.
- **Cross-harness parity:** register in both `hooks/hooks.json` (Claude Code) and `hooks/hooks-cursor.json` (Cursor) like every other hook in the repo. Output branching in the script mirrors `merge-guard` (`CURSOR_PLUGIN_ROOT` / `CLAUDE_PLUGIN_ROOT` / fallback).
- **Testing:** small shell test driver that feeds synthetic JSON stdin through the hook and asserts the output. Covers: no-match prompt, match + no prior load, match + prior load (via fake transcript), word-boundary exclusion (`superrapid`), variant spellings.

## Output

- `hooks/autoload-superra` — extensionless bash hook script.
- `hooks/hooks.json` — adds `UserPromptSubmit` registration.
- `hooks/hooks-cursor.json` — adds `userPromptSubmit` registration.
- `tests/hooks/test-autoload-superra.sh` — shell test driver with the vectors above.

## Expected Result

A fresh Claude Code session where the user says "let's do some superRA work" causes the hook to inject a reminder; Claude loads `superRA:using-superRA`. A follow-up message also containing "superRA" produces no further reminder (the transcript gate suppresses it). Non-superRA messages are untouched; `superrapid` does not trigger.

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

*(none yet)*

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
- [ ] Implement `hooks/autoload-superra` with header comment + test vectors listed as a regression table.
- [ ] `chmod +x hooks/autoload-superra`.
- [ ] Implement `tests/hooks/test-autoload-superra.sh` driving all five vectors; the script prints `PASS`/`FAIL` per vector and exits non-zero if any fail.
- [ ] Run `bash tests/hooks/test-autoload-superra.sh`; record the output in RESULTS.md Task 1.
- [ ] Commit as `hooks: add autoload-superra UserPromptSubmit hook + tests`.

**Review status:**

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
- [ ] Edit `hooks/hooks.json`; validate JSON (`python3 -m json.tool < hooks/hooks.json`).
- [ ] Edit `hooks/hooks-cursor.json`; validate JSON.
- [ ] Commit as `hooks: register autoload-superra for UserPromptSubmit`.

**Review status:**

---

## Task 3: End-to-end verification in a fresh session

**Depends on:** 2

**Objective:** Confirm the hook fires as designed in a real Claude Code session — superRA mention → skill loads once; subsequent mentions → no duplicate reminder; non-superRA traffic → no reminder.

**Input:** The registered hook from Tasks 1–2.

**Output:** A short transcript excerpt pasted into RESULTS.md Task 3 showing (a) first-mention trigger, (b) second-mention suppression, (c) control prompt with no trigger. Because this requires a brand-new session (the current one has `using-superRA` already in its transcript), the user runs the verification and pastes results.

**Methodology:**
1. User opens a fresh Claude Code session in this worktree.
2. User sends: `"quick superRA sanity check — what phase am I in?"`. Expected: hook injects reminder; Claude invokes `Skill(superRA:using-superRA)`; response proceeds.
3. User sends another superRA-containing prompt in the same session. Expected: no new reminder injected (transcript gate).
4. User sends a control prompt (no superRA). Expected: no reminder.
5. User pastes outcomes; orchestrator records in RESULTS.md and marks APPROVED or files issues.

**Steps:**
- [ ] Orchestrator announces the verification protocol to the user.
- [ ] User runs the three probes above.
- [ ] Orchestrator records outcomes in RESULTS.md Task 3.
- [ ] Commit as `hooks: verify autoload-superra behavior end-to-end`.

**Review status:**
