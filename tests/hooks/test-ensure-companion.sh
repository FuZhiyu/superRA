#!/usr/bin/env bash
# Regression tests for the merged companion-skill gate (ensure-companion).
# Covers the vectors formerly split across test-ensure-using-superra.sh and
# test-ensure-agent-orchestration.sh, plus the combined-deny case.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK="$REPO_ROOT/hooks/ensure-companion"

pass=0
fail=0
failed_names=()

# run_case NAME EXPECT TOOL_NAME SKILL [TRANSCRIPT_CONTENT] [TRANSCRIPT_MODE] [EXPECTED_REASON_SUBSTRINGS...]
run_case() {
  local name="$1"
  local expect="$2"
  local tool_name="$3"
  local skill="$4"
  local transcript_content="${5:-}"
  local transcript_mode="${6:-file}"  # file | empty | nonexistent
  shift 6 2>/dev/null || shift $#
  local expected_reasons=("$@")

  local transcript_path=""
  if [ "$transcript_mode" = "nonexistent" ]; then
    transcript_path="/tmp/does-not-exist-$$-$RANDOM"
  elif [ -n "$transcript_content" ]; then
    transcript_path=$(mktemp)
    printf '%s\n' "$transcript_content" >"$transcript_path"
  fi

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

  # Every non-empty hook payload must parse as JSON.
  if [ "$got" != "ERROR (rc=$rc)" ] && [ -n "$out" ]; then
    if ! echo "$out" | python3 -c 'import json,sys; json.loads(sys.stdin.read())' 2>/dev/null; then
      printf 'FAIL  %-50s (invalid JSON payload: %s)\n' "$name" "$out"
      failed_names+=("$name")
      fail=$((fail + 1))
      return
    fi
  fi

  # Deny reasons must name each expected companion and round-trip intact.
  if [ "$got" = "deny" ] && [ ${#expected_reasons[@]} -gt 0 ]; then
    local reason expected
    reason=$(echo "$out" | python3 -c '
import json, sys
d = json.loads(sys.stdin.read())
print(d.get("hookSpecificOutput", {}).get("permissionDecisionReason", ""))
')
    for expected in "${expected_reasons[@]}"; do
      if ! echo "$reason" | grep -Fq "$expected"; then
        printf 'FAIL  %-50s (deny reason missing %s: %s)\n' "$name" "$expected" "$reason"
        failed_names+=("$name")
        fail=$((fail + 1))
        return
      fi
    done
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

run_raw_silent_case() {
  local name="$1"
  local input="$2"
  local out
  out=$(env -i PATH="$PATH" HOME="$HOME" bash "$HOOK" <<<"$input")
  local rc=$?

  if [ $rc -eq 0 ] && [ "$out" = "{}" ]; then
    printf 'PASS  %-50s (got silent)\n' "$name"
    pass=$((pass + 1))
  else
    printf 'FAIL  %-50s (expected silent, got rc=%s output=%s)\n' "$name" "$rc" "$out"
    failed_names+=("$name")
    fail=$((fail + 1))
  fi
}

using_loaded='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"superRA:using-superra"}}]}}'
orch_loaded='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"superRA:agent-orchestration"}}]}}'
both_loaded="$using_loaded
$orch_loaded"
unrelated='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"superRA:communicate"}}]}}'

# V1: non-Skill tool -> silent
run_case "V1 non-Skill Bash"             expect-silent "Bash"  ""
run_case "V1 non-Skill Read"             expect-silent "Read"  ""

# V2: Skill tool, non-workflow skill -> silent
run_case "V2 Skill handoff-doc"          expect-silent "Skill" "superRA:handoff-doc"
run_case "V2 Skill using-superra itself" expect-silent "Skill" "superRA:using-superra"
run_case "V2 Skill agent-orchestration"  expect-silent "Skill" "superRA:agent-orchestration"
run_case "V2 Skill empty"                expect-silent "Skill" ""

# V3: superplan needs using-superra only
run_case "V3a superplan not-loaded"      expect-deny   "Skill" "superRA:superplan" "$unrelated" file "superRA:using-superra"
run_case "V3b superplan orch-only"       expect-deny   "Skill" "superRA:superplan" "$orch_loaded" file "superRA:using-superra"
run_case "V3c superplan loaded"          expect-silent "Skill" "superRA:superplan" "$using_loaded"

# V4: dispatching skills need both companions; deny lists every missing one
run_case "V4a superimplement neither"    expect-deny   "Skill" "superRA:superimplement" "$unrelated" file "superRA:using-superra" "superRA:agent-orchestration"
run_case "V4b superimplement using-only" expect-deny   "Skill" "superRA:superimplement" "$using_loaded" file "superRA:agent-orchestration"
run_case "V4c superimplement orch-only"  expect-deny   "Skill" "superRA:superimplement" "$orch_loaded" file "superRA:using-superra"
run_case "V4d superimplement both"       expect-silent "Skill" "superRA:superimplement" "$both_loaded"
run_case "V4e superintegrate neither"    expect-deny   "Skill" "superRA:superintegrate" "$unrelated" file "superRA:using-superra" "superRA:agent-orchestration"
run_case "V4f superintegrate both"       expect-silent "Skill" "superRA:superintegrate" "$both_loaded"

# V4g: tolerant match — whitespace around the colon in the transcript field.
tolerant='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{ "skill" : "superRA:using-superra" }}]}}'
run_case "V4g tolerant-whitespace"       expect-silent "Skill" "superRA:superplan" "$tolerant"

# V5: fail-open on missing transcript
run_case "V5a transcript empty-string"   expect-silent "Skill" "superRA:superplan" "" "empty"
run_case "V5b transcript nonexistent"    expect-silent "Skill" "superRA:superplan" "" "nonexistent"

# V6: deny reason round-trips embedded quotes through json escaping.
run_case "V6 deny-reason round-trip"     expect-deny   "Skill" "superRA:superplan" "$unrelated" file 'superRA:superplan'

# V7: valid JSON with the wrong top-level shape fails open.
run_raw_silent_case "V7 non-object JSON array" '[1,2,3]'
run_raw_silent_case "V7 non-object JSON null"  'null'

# Registry wiring: Claude + Cursor reference ensure-companion; Codex has no
# Skill interception so it must NOT wire the gate.
if python3 - "$REPO_ROOT" <<'PY'
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
claude = json.loads((root / "hooks/hooks.json").read_text(encoding="utf-8"))
codex = json.loads((root / "hooks/hooks-codex.json").read_text(encoding="utf-8"))
cursor = json.loads((root / "hooks/hooks-cursor.json").read_text(encoding="utf-8"))

claude_skill = [
    hook["command"]
    for group in claude["hooks"]["PreToolUse"]
    if group.get("matcher") == "Skill"
    for hook in group["hooks"]
]
assert any("ensure-companion" in cmd for cmd in claude_skill)
assert not any("ensure-using-superra" in cmd or "ensure-agent-orchestration" in cmd for cmd in claude_skill)

codex_cmds = [
    hook["command"]
    for groups in codex["hooks"].values()
    for group in groups
    for hook in group["hooks"]
]
assert not any("ensure-companion" in cmd or "ensure-using-superra" in cmd for cmd in codex_cmds)

cursor_cmds = [hook["command"] for hook in cursor["hooks"]["preToolUse"]]
assert any("ensure-companion" in cmd for cmd in cursor_cmds)
assert not any("ensure-using-superra" in cmd or "ensure-agent-orchestration" in cmd for cmd in cursor_cmds)
PY
then
  printf 'PASS  %-50s\n' "registry wiring (Claude, Codex, Cursor)"
  pass=$((pass + 1))
else
  printf 'FAIL  %-50s\n' "registry wiring (Claude, Codex, Cursor)"
  failed_names+=("registry wiring")
  fail=$((fail + 1))
fi

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi
exit 0
