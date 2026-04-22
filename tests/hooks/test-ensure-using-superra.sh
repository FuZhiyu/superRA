#!/usr/bin/env bash
# Regression tests for hooks/ensure-using-superra.
# Run from the repo root: bash tests/hooks/test-ensure-using-superra.sh

set -uo pipefail

HOOK_NAME="ensure-using-superra"
COMPANION="superRA:using-superRA"

HOOK="$(cd "$(dirname "$0")/../.." && pwd)/hooks/$HOOK_NAME"
if [ ! -x "$HOOK" ]; then
  echo "FAIL: hook not found or not executable at $HOOK" >&2
  exit 2
fi

pass=0
fail=0
failed_names=()

# run_case <name> <expect-deny|expect-silent> <tool_name> <skill> [transcript_content]
#
# When transcript_content is empty, transcript_path is set to "" in the
# hook input (fail-open path). When provided, a tempfile is created and
# its path is passed in.
run_case() {
  local name="$1"
  local expect="$2"
  local tool_name="$3"
  local skill="$4"
  local transcript_content="${5:-}"
  local transcript_mode="${6:-file}"  # file | empty | nonexistent

  local transcript_path=""
  if [ "$transcript_mode" = "nonexistent" ]; then
    transcript_path="/tmp/does-not-exist-$$-$RANDOM"
  elif [ -n "$transcript_content" ]; then
    transcript_path=$(mktemp)
    printf '%s\n' "$transcript_content" >"$transcript_path"
  fi

  # Build the hook input JSON safely via python.
  local input
  input=$(python3 -c '
import json, sys
print(json.dumps({
    "session_id": "test",
    "transcript_path": sys.argv[1],
    "cwd": ".",
    "hook_event_name": "PreToolUse",
    "tool_name": sys.argv[2],
    "tool_input": {"skill": sys.argv[3]} if sys.argv[3] else {},
}))
' "$transcript_path" "$tool_name" "$skill")

  # Run the hook in an env stripped of harness env vars so we exercise
  # the fallback output branch deterministically.
  local out
  out=$(env -i PATH="$PATH" HOME="$HOME" bash "$HOOK" <<<"$input")
  local rc=$?

  [ "$transcript_mode" = "file" ] && [ -n "$transcript_path" ] && rm -f "$transcript_path"

  local got
  if [ $rc -ne 0 ]; then
    got="ERROR (rc=$rc)"
  elif echo "$out" | grep -q '"permissionDecision":"deny"'; then
    got="deny"
  elif [ "$out" = "{}" ]; then
    got="silent"
  else
    got="UNKNOWN: $out"
  fi

  # JSON-validity assertion: every non-empty hook payload must parse as
  # JSON. Without this, a malformed deny payload with an unescaped `"` in
  # the reason slips past a plain grep check even though the harness
  # would drop it.
  local json_ok=1
  if [ "$got" != "ERROR (rc=$rc)" ] && [ -n "$out" ]; then
    if ! echo "$out" | python3 -c 'import json,sys; json.loads(sys.stdin.read())' 2>/dev/null; then
      json_ok=0
    fi
  fi

  if [ $json_ok -eq 0 ]; then
    printf 'FAIL  %-50s (invalid JSON payload: %s)\n' "$name" "$out"
    failed_names+=("$name")
    fail=$((fail + 1))
    return
  fi

  # For deny cases, also assert the reason names the companion skill and
  # round-trips through json.loads intact (V6 family).
  if [ "$got" = "deny" ]; then
    local reason
    reason=$(echo "$out" | python3 -c '
import json, sys
d = json.loads(sys.stdin.read())
print(d.get("hookSpecificOutput", {}).get("permissionDecisionReason", ""))
')
    if ! echo "$reason" | grep -Fq "$COMPANION"; then
      printf 'FAIL  %-50s (deny reason missing companion %s: %s)\n' "$name" "$COMPANION" "$reason"
      failed_names+=("$name")
      fail=$((fail + 1))
      return
    fi
  fi

  if { [ "$expect" = "expect-deny" ]    && [ "$got" = "deny" ]; } \
  || { [ "$expect" = "expect-silent" ]  && [ "$got" = "silent" ]; }; then
    printf 'PASS  %-50s (got %s)\n' "$name" "$got"
    pass=$((pass + 1))
  else
    printf 'FAIL  %-50s (expected %s, got %s)\n' "$name" "$expect" "$got"
    failed_names+=("$name")
    fail=$((fail + 1))
  fi
}

loaded_transcript='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"superRA:using-superRA"}}]}}'
other_transcript='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"superRA:agent-orchestration"}}]}}'

# V1: non-Skill tool -> silent
run_case "V1 non-Skill Bash"             expect-silent "Bash"  ""
run_case "V1 non-Skill Read"             expect-silent "Read"  ""

# V2: Skill tool, non-workflow skill -> silent
run_case "V2 Skill handoff-doc"          expect-silent "Skill" "superRA:handoff-doc"
run_case "V2 Skill using-superRA itself" expect-silent "Skill" "superRA:using-superRA"
run_case "V2 Skill agent-orchestration"  expect-silent "Skill" "superRA:agent-orchestration"
run_case "V2 Skill empty"                expect-silent "Skill" ""

# V3: workflow skill, companion NOT loaded -> deny
#
# Transcript present but only mentions other-companion (agent-orchestration) —
# this hook must still deny because it specifically guards using-superRA.
run_case "V3a planning-workflow no-transcript"   expect-deny   "Skill" "superRA:planning-workflow"       "$other_transcript"
run_case "V3b implementation-workflow not-loaded" expect-deny  "Skill" "superRA:implementation-workflow" "$other_transcript"
run_case "V3c integration-workflow not-loaded"    expect-deny  "Skill" "superRA:integration-workflow"    "$other_transcript"

# V4: workflow skill, companion loaded -> silent
run_case "V4a planning-workflow loaded"          expect-silent "Skill" "superRA:planning-workflow"       "$loaded_transcript"
run_case "V4b implementation-workflow loaded"    expect-silent "Skill" "superRA:implementation-workflow" "$loaded_transcript"
run_case "V4c integration-workflow loaded"       expect-silent "Skill" "superRA:integration-workflow"    "$loaded_transcript"

# V4d: transcript contains the skill reference buried among other text
# with whitespace around the colon — tolerant regex must still match.
tolerant_transcript='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{ "skill" : "superRA:using-superRA" }}]}}'
run_case "V4d tolerant-whitespace"       expect-silent "Skill" "superRA:planning-workflow" "$tolerant_transcript"

# V5: fail-open on missing transcript
run_case "V5a transcript empty-string"   expect-silent "Skill" "superRA:planning-workflow" "" "empty"
run_case "V5b transcript nonexistent"    expect-silent "Skill" "superRA:planning-workflow" "" "nonexistent"

# V6: deny payload has valid JSON with round-tripping reason. The reason
# contains embedded double quotes (Skill(skill="...")) so this implicitly
# exercises the json.dumps escape path.
run_case "V6 deny-reason round-trip"     expect-deny   "Skill" "superRA:planning-workflow" "$other_transcript"

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi
exit 0
