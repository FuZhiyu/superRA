#!/usr/bin/env bash
# Deterministic tests for hooks/agent-model-guard.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK="$REPO_ROOT/hooks/agent-model-guard"
pass=0
fail=0

run_case() {
  local name="$1"
  local expected="$2"
  local input="$3"
  local out got

  out=$(env -i PATH="$PATH" HOME="$HOME" bash "$HOOK" <<<"$input")
  if ! printf '%s' "$out" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null; then
    printf 'FAIL  %s (invalid JSON: %s)\n' "$name" "$out"
    fail=$((fail + 1))
    return
  fi

  if printf '%s' "$out" | grep -q '"permissionDecision":"deny"'; then
    got=deny
  elif [ "$out" = "{}" ]; then
    got=allow
  else
    got=unexpected
  fi

  if [ "$got" = "$expected" ]; then
    printf 'PASS  %s\n' "$name"
    pass=$((pass + 1))
  else
    printf 'FAIL  %s (expected %s, got %s: %s)\n' "$name" "$expected" "$got" "$out"
    fail=$((fail + 1))
  fi
}

payload() {
  python3 -c 'import json,sys; print(json.dumps({"hook_event_name":"PreToolUse","tool_name":sys.argv[1],"tool_input":json.loads(sys.argv[2])}))' "$1" "$2"
}

run_case "Claude missing model" deny "$(payload Agent '{"subagent_type":"general-purpose"}')"
run_case "Claude empty model" deny "$(payload Agent '{"subagent_type":"general-purpose","model":"  "}')"
run_case "Claude inherited model" deny "$(payload Agent '{"subagent_type":"general-purpose","model":"inherit"}')"
run_case "Claude omitted generic type" deny "$(payload Agent '{"model":"inherit"}')"
run_case "Claude concrete model" allow "$(payload Agent '{"subagent_type":"general-purpose","model":"sonnet"}')"
run_case "Claude named agent" allow "$(payload Agent '{"subagent_type":"superRA:implementer"}')"

run_case "Codex missing both controls" deny "$(payload spawn_agent '{"agent_type":"default"}')"
run_case "Codex missing model" deny "$(payload spawn_agent '{"agent_type":"default","reasoning_effort":"medium"}')"
run_case "Codex missing reasoning" deny "$(payload spawn_agent '{"agent_type":"default","model":"gpt-5.6"}')"
run_case "Codex empty controls" deny "$(payload spawn_agent '{"agent_type":"default","model":" ","reasoning_effort":""}')"
run_case "Codex omitted generic type" deny "$(payload spawn_agent '{"message":"probe"}')"
run_case "Codex explicit controls" allow "$(payload spawn_agent '{"agent_type":"default","model":"gpt-5.6","reasoning_effort":"medium"}')"
run_case "Codex named agent" allow "$(payload spawn_agent '{"agent_type":"superra_reviewer"}')"

run_case "Unrelated tool" allow "$(payload Bash '{"command":"true"}')"
run_case "Malformed JSON fails open" allow '{not-json'
run_case "Non-object input fails open" allow '[]'
run_case "Non-object tool input fails open" allow '{"tool_name":"Agent","tool_input":null}'

printf '\nPassed: %s    Failed: %s\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
