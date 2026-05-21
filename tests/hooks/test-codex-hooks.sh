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

case_request_user_input_logger() {
  local name="decision logger accepts request_user_input"
  local input out context
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"PostToolUse","tool_name":"request_user_input","tool_input":{},"tool_response":{}}))')
  out=$(run_hook ask-user-question-logger "$input")
  assert_json "$name" "$out" || return
  context=$(printf '%s' "$out" | json_get 'print(d.get("hookSpecificOutput", {}).get("additionalContext", d.get("additionalContext", "")))')
  if printf '%s' "$context" | grep -Fq 'User decision'; then
    record_pass "$name"
  else
    record_fail "$name" "missing decision-log reminder: $context"
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
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"Stop","permission_mode":"plan","last_assistant_message":"<proposed_plan>plan</proposed_plan>"}))')
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

case_plan_stop_silent_nonplan() {
  local name="codex plan Stop silent outside plan mode"
  local input out
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"Stop","permission_mode":"default","last_assistant_message":"<proposed_plan>plan</proposed_plan>"}))')
  out=$(run_hook codex-plan-stop "$input")
  assert_json "$name" "$out" || return
  if [ "$out" = "{}" ]; then
    record_pass "$name"
  else
    record_fail "$name" "expected {}, got $out"
  fi
}

case_plan_stop_silent_without_plan() {
  local name="codex plan Stop silent without proposed_plan"
  local input out
  input=$(python3 -c 'import json; print(json.dumps({"session_id":"s","transcript_path":"","cwd":".","hook_event_name":"Stop","permission_mode":"plan","last_assistant_message":"ordinary message"}))')
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
case_request_user_input_logger
case_request_user_input_silent_other_tool
case_plan_stop_reminder
case_plan_stop_silent_nonplan
case_plan_stop_silent_without_plan

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi
exit 0
