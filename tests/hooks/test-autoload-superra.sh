#!/usr/bin/env bash
# Regression tests for hooks/autoload-superra.
# Run from the repo root: bash tests/hooks/test-autoload-superra.sh

set -uo pipefail

HOOK="$(cd "$(dirname "$0")/../.." && pwd)/hooks/autoload-superra"
if [ ! -x "$HOOK" ]; then
  echo "FAIL: hook not found or not executable at $HOOK" >&2
  exit 2
fi

pass=0
fail=0
failed_names=()

# run_case <name> <expect-reminder|expect-silent> <prompt> [transcript_content]
run_case() {
  local name="$1"
  local expect="$2"
  local prompt="$3"
  local transcript_content="${4:-}"

  local transcript_path=""
  if [ -n "$transcript_content" ]; then
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
    "hook_event_name": "UserPromptSubmit",
    "prompt": sys.argv[2],
}))
' "$transcript_path" "$prompt")

  # Run the hook in an env stripped of harness env vars so we exercise
  # the fallback output branch deterministically.
  local out
  out=$(env -i PATH="$PATH" HOME="$HOME" bash "$HOOK" <<<"$input")
  local rc=$?

  [ -n "$transcript_path" ] && rm -f "$transcript_path"

  local got
  if [ $rc -ne 0 ]; then
    got="ERROR (rc=$rc)"
  elif echo "$out" | grep -q 'additionalContext'; then
    got="reminder"
  elif [ "$out" = "{}" ]; then
    got="silent"
  else
    got="UNKNOWN: $out"
  fi

  if { [ "$expect" = "expect-reminder" ] && [ "$got" = "reminder" ]; } \
     || { [ "$expect" = "expect-silent" ] && [ "$got" = "silent" ]; }; then
    printf 'PASS  %-50s (got %s)\n' "$name" "$got"
    pass=$((pass + 1))
  else
    printf 'FAIL  %-50s (expected %s, got %s)\n' "$name" "$expect" "$got"
    failed_names+=("$name")
    fail=$((fail + 1))
  fi
}

# V1: no superRA mention -> silent
run_case "V1 no-mention" expect-silent "let's refactor the data loader"

# V2: variant spellings -> reminder
run_case "V2a superRA"      expect-reminder "let's use superRA here"
run_case "V2b super RA"     expect-reminder "run super RA on this"
run_case "V2c super-ra"     expect-reminder "kick off super-ra workflow"
run_case "V2d Super_RA"     expect-reminder "Super_RA time"
run_case "V2e superra lc"   expect-reminder "superra please"
run_case "V2f mid-sentence" expect-reminder "ok, superRA, go"

# V3: word boundary -> silent (no false positive)
run_case "V3 superrapid" expect-silent "this is superrapid output"
run_case "V3 superrant"  expect-silent "no superrant behavior here"

# V4: already loaded (transcript shows a Skill invocation) -> silent
loaded_transcript='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"superRA:using-superRA"}}]}}'
run_case "V4 already-loaded" expect-silent "superRA again, what now?" "$loaded_transcript"

# V4b: transcript mentions a different superRA skill -> still remind
other_skill='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"superRA:planning-workflow"}}]}}'
run_case "V4b other-superRA-skill" expect-reminder "superRA hello" "$other_skill"

# V5: transcript_path empty -> reminder (fail-open)
run_case "V5 empty-transcript-path" expect-reminder "superRA now"

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi
exit 0
