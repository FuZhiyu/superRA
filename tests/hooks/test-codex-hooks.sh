#!/usr/bin/env bash
# Regression tests for Codex-shaped superRA hook payloads.
# Run from repo root: bash tests/hooks/test-codex-hooks.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK_DIR="$REPO_ROOT/hooks"
TMPROOT=$(mktemp -d)
cleanup() {
  rm -rf "$TMPROOT"
}
trap cleanup EXIT INT TERM
SPARSE_BIN="$TMPROOT/bin"
mkdir -p "$SPARSE_BIN"
ln -s /bin/cat "$SPARSE_BIN/cat"
ln -s "$(command -v grep)" "$SPARSE_BIN/grep"
ln -s "$(command -v python3)" "$SPARSE_BIN/python3"

pass=0
fail=0
failed_names=()

record_pass() {
  printf 'PASS  %s\n' "$1"
  pass=$((pass + 1))
}

record_fail() {
  printf 'FAIL  %s (%s)\n' "$1" "$2"
  failed_names+=("$1")
  fail=$((fail + 1))
}

json_get() {
  python3 -c 'import json,sys; d=json.load(sys.stdin); exec(sys.argv[1])' "$1"
}

run_hook() {
  local hook="$1"
  local input="$2"
  env -i PATH="$PATH" HOME="$HOME" PLUGIN_ROOT="$REPO_ROOT" CLAUDE_PLUGIN_ROOT="$REPO_ROOT" bash "$HOOK_DIR/$hook" <<<"$input"
}

codex_manifest_command() {
  local hook="$1"
  python3 - "$REPO_ROOT/hooks/hooks-codex.json" "$hook" <<'PY'
import json, sys

path, hook_name = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as f:
    data = json.load(f)
for groups in data["hooks"].values():
    for group in groups:
        for hook in group.get("hooks", []):
            command = hook.get("command", "")
            if hook_name in command:
                print(command)
                raise SystemExit(0)
raise SystemExit(f"hook command not found for {hook_name}")
PY
}

run_codex_manifest_hook() {
  local hook="$1"
  local input="$2"
  local root_mode="${3:-plugin}"
  local command
  command=$(codex_manifest_command "$hook")
  case "$root_mode" in
    plugin)
      env -i PATH="$SPARSE_BIN" PLUGIN_ROOT="$REPO_ROOT" CLAUDE_PLUGIN_ROOT="$REPO_ROOT" /bin/sh -c "$command" <<<"$input"
      ;;
    claude)
      env -i PATH="$SPARSE_BIN" CLAUDE_PLUGIN_ROOT="$REPO_ROOT" /bin/sh -c "$command" <<<"$input"
      ;;
    *)
      echo "unknown root mode: $root_mode" >&2
      return 1
      ;;
  esac
}

run_codex_manifest_hook_no_root() {
  local hook="$1"
  local input="$2"
  local command
  command=$(codex_manifest_command "$hook")
  env -i PATH="$SPARSE_BIN" /bin/sh -c "$command" <<<"$input"
}

assert_json() {
  local name="$1"
  local out="$2"
  if ! printf '%s' "$out" | python3 -c 'import json,sys; json.loads(sys.stdin.read())' 2>/dev/null; then
    record_fail "$name" "invalid JSON: $out"
    return 1
  fi
  return 0
}

case_autoload_codex_wording() {
  local name="autoload emits Codex-native skill wording"
  local input out context
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"UserPromptSubmit","prompt":"use superRA here"}))')
  out=$(run_hook autoload-superra "$input")
  assert_json "$name" "$out" || return
  context=$(printf '%s' "$out" | json_get 'print(d.get("hookSpecificOutput", {}).get("additionalContext", d.get("additionalContext", "")))')
  if printf '%s' "$context" | grep -Fq 'superRA:using-superra' \
     && ! printf '%s' "$context" | grep -Fq 'Skill(skill='; then
    record_pass "$name"
  else
    record_fail "$name" "unexpected context: $context"
  fi
}

case_merge_guard_codex_bash() {
  local name="merge-guard handles Codex Bash payload"
  local input out context
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git merge main"}}))')
  out=$(run_hook merge-guard "$input")
  assert_json "$name" "$out" || return
  context=$(printf '%s' "$out" | json_get 'print(d.get("hookSpecificOutput", {}).get("additionalContext", d.get("additionalContext", "")))')
  if printf '%s' "$context" | grep -Fq 'superRA:semantic-merge'; then
    record_pass "$name"
  else
    record_fail "$name" "missing semantic-merge reminder: $context"
  fi
}

case_codex_manifest_sparse_path() {
  local name="Codex manifest command works with sparse PATH"
  local input out context
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git merge main"}}))')
  out=$(run_codex_manifest_hook merge-guard "$input" plugin)
  assert_json "$name" "$out" || return
  context=$(printf '%s' "$out" | json_get 'print(d.get("hookSpecificOutput", {}).get("additionalContext", d.get("additionalContext", "")))')
  if printf '%s' "$context" | grep -Fq 'superRA:semantic-merge'; then
    record_pass "$name"
  else
    record_fail "$name" "missing semantic-merge reminder: $context"
  fi
}

case_codex_manifest_claude_root_fallback() {
  local name="Codex manifest command accepts CLAUDE_PLUGIN_ROOT fallback"
  local input out context
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"git merge main"}}))')
  out=$(run_codex_manifest_hook merge-guard "$input" claude)
  assert_json "$name" "$out" || return
  context=$(printf '%s' "$out" | json_get 'print(d.get("hookSpecificOutput", {}).get("additionalContext", d.get("additionalContext", "")))')
  if printf '%s' "$context" | grep -Fq 'superRA:semantic-merge'; then
    record_pass "$name"
  else
    record_fail "$name" "missing semantic-merge reminder: $context"
  fi
}

case_codex_manifest_plan_stop_execution() {
  local name="Codex manifest command executes plan Stop hook"
  local input out reason
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"Stop","permission_mode":"plan","last_assistant_message":"# Proposed Plan\n\n## Summary\n\nDo the work."}))')
  out=$(run_codex_manifest_hook codex-plan-stop "$input" plugin)
  assert_json "$name" "$out" || return
  reason=$(printf '%s' "$out" | json_get 'print(d.get("reason", ""))')
  if printf '%s' "$reason" | grep -Fq 'PLAN.md + RESULTS.md'; then
    record_pass "$name"
  else
    record_fail "$name" "missing Stop reminder through manifest command: $out"
  fi
}

case_request_user_input_logger() {
  local name="decision logger accepts request_user_input"
  local input out context
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"PostToolUse","tool_name":"request_user_input","tool_input":{},"tool_response":{}}))')
  out=$(run_hook ask-user-question-logger "$input")
  assert_json "$name" "$out" || return
  context=$(printf '%s' "$out" | json_get 'print(d.get("hookSpecificOutput", {}).get("additionalContext", d.get("additionalContext", "")))')
  if printf '%s' "$context" | grep -Fq 'consider recording it in PLAN.md'; then
    record_pass "$name"
  else
    record_fail "$name" "missing decision-log reminder: $context"
  fi
}

case_codex_manifest_missing_root_fails_open() {
  local name="Codex manifest command fails open without plugin root"
  local input out
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"UserPromptSubmit","prompt":"use superRA here"}))')
  out=$(run_codex_manifest_hook_no_root autoload-superra "$input")
  assert_json "$name" "$out" || return
  if [ "$out" = "{}" ]; then
    record_pass "$name"
  else
    record_fail "$name" "expected {}, got $out"
  fi
}

case_request_user_input_silent_other_tool() {
  local name="decision logger silent on unrelated tool"
  local input out
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"PostToolUse","tool_name":"Bash","tool_input":{},"tool_response":{}}))')
  out=$(run_hook ask-user-question-logger "$input")
  assert_json "$name" "$out" || return
  if [ "$out" = "{}" ]; then
    record_pass "$name"
  else
    record_fail "$name" "expected {}, got $out"
  fi
}

case_plan_stop_reminder() {
  local name="codex plan Stop emits materialization reminder"
  local input out decision reason
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"Stop","permission_mode":"plan","last_assistant_message":"# Proposed Plan\n\n## Summary\n\nDo the work."}))')
  out=$(run_hook codex-plan-stop "$input")
  assert_json "$name" "$out" || return
  decision=$(printf '%s' "$out" | json_get 'print(d.get("decision", ""))')
  reason=$(printf '%s' "$out" | json_get 'print(d.get("reason", ""))')
  if [ "$decision" = "block" ] && printf '%s' "$reason" | grep -Fq 'PLAN.md + RESULTS.md'; then
    record_pass "$name"
  else
    record_fail "$name" "missing Stop continuation decision/reason: $out"
  fi
}

case_plan_stop_accepts_proposed_plan_tag() {
  local name="codex plan Stop accepts proposed_plan tag"
  local input out
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"Stop","permission_mode":"plan","last_assistant_message":"<proposed_plan>plan</proposed_plan>"}))')
  out=$(run_hook codex-plan-stop "$input")
  assert_json "$name" "$out" || return
  if printf '%s' "$out" | grep -Fq 'PLAN.md + RESULTS.md'; then
    record_pass "$name"
  else
    record_fail "$name" "missing proposed_plan reminder: $out"
  fi
}

case_plan_stop_silent_for_quoted_tag_outside_plan_mode() {
  local name="codex plan Stop silent for quoted tag outside plan mode"
  local input out
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"Stop","permission_mode":"default","last_assistant_message":"The literal <proposed_plan> marker appears in this review."}))')
  out=$(run_hook codex-plan-stop "$input")
  assert_json "$name" "$out" || return
  if [ "$out" = "{}" ]; then
    record_pass "$name"
  else
    record_fail "$name" "expected {}, got $out"
  fi
}

case_plan_stop_silent_when_already_continued() {
  local name="codex plan Stop silent during Stop-hook continuation"
  local input out
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"Stop","permission_mode":"plan","stop_hook_active":True,"last_assistant_message":"# Proposed Plan"}))')
  out=$(run_hook codex-plan-stop "$input")
  assert_json "$name" "$out" || return
  if [ "$out" = "{}" ]; then
    record_pass "$name"
  else
    record_fail "$name" "expected {}, got $out"
  fi
}

case_plan_stop_silent_without_plan() {
  local name="codex plan Stop silent outside plan mode without proposed_plan"
  local input out
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"Stop","permission_mode":"default","last_assistant_message":"ordinary message"}))')
  out=$(run_hook codex-plan-stop "$input")
  assert_json "$name" "$out" || return
  if [ "$out" = "{}" ]; then
    record_pass "$name"
  else
    record_fail "$name" "expected {}, got $out"
  fi
}

case_plan_stop_silent_for_non_plan_output_in_plan_mode() {
  local name="codex plan Stop silent for non-plan output in plan mode"
  local input out
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"Stop","permission_mode":"plan","last_assistant_message":"Verdict: APPROVE\n\nNo critical findings. PLAN.md was not changed."}))')
  out=$(run_hook codex-plan-stop "$input")
  assert_json "$name" "$out" || return
  if [ "$out" = "{}" ]; then
    record_pass "$name"
  else
    record_fail "$name" "expected {}, got $out"
  fi
}

case_plan_stop_silent_for_negated_proposed_plan_phrase() {
  local name="codex plan Stop silent for negated proposed-plan phrase"
  local input out
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"Stop","permission_mode":"plan","last_assistant_message":"This is not a proposed plan; it is a code review verdict."}))')
  out=$(run_hook codex-plan-stop "$input")
  assert_json "$name" "$out" || return
  if [ "$out" = "{}" ]; then
    record_pass "$name"
  else
    record_fail "$name" "expected {}, got $out"
  fi
}

case_autoload_codex_wording
case_merge_guard_codex_bash
case_codex_manifest_sparse_path
case_codex_manifest_claude_root_fallback
case_codex_manifest_plan_stop_execution
case_codex_manifest_missing_root_fails_open
case_request_user_input_logger
case_request_user_input_silent_other_tool
case_plan_stop_reminder
case_plan_stop_accepts_proposed_plan_tag
case_plan_stop_silent_for_quoted_tag_outside_plan_mode
case_plan_stop_silent_when_already_continued
case_plan_stop_silent_without_plan
case_plan_stop_silent_for_non_plan_output_in_plan_mode
case_plan_stop_silent_for_negated_proposed_plan_phrase

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi
exit 0
