#!/usr/bin/env bash
# Credential-free behavior checks for the zotero-paper-reader tool script.
# Exercises CLI parsing, version reporting, access-mode detection, clean error
# paths, and the no-secret-leak invariant without contacting a real library.
# Run from the repo root: bash tests/test-zotero-tool.sh

set -euo pipefail

cd "$(dirname "$0")/.."

SCRIPT="skills/zotero-paper-reader/scripts/zotero_tool.py"
RUN=(uv run --quiet --script "$SCRIPT")

pass=0
fail=0
failed_names=()

record_pass() {
  printf 'PASS  %s\n' "$1"
  pass=$((pass + 1))
}

record_fail() {
  printf 'FAIL  %s\n' "$1"
  fail=$((fail + 1))
  failed_names+=("$1")
}

# Run the tool, capturing stdout, stderr, and exit code into globals.
run_tool() {
  TOOL_OUT="$("${RUN[@]}" "$@" 2>/tmp/zt_test_err)" && TOOL_RC=0 || TOOL_RC=$?
  TOOL_ERR="$(cat /tmp/zt_test_err)"
}

assert_rc() {
  local name="$1" want="$2"
  if [ "$TOOL_RC" = "$want" ]; then
    record_pass "$name"
  else
    printf '      want rc=%s got rc=%s\n' "$want" "$TOOL_RC"
    record_fail "$name"
  fi
}

assert_stdout_contains() {
  local name="$1" pattern="$2"
  if printf '%s' "$TOOL_OUT" | rg -q --fixed-strings -- "$pattern"; then
    record_pass "$name"
  else
    printf '      stdout missing: %s\n' "$pattern"
    record_fail "$name"
  fi
}

assert_combined_absent() {
  local name="$1" pattern="$2"
  if printf '%s%s' "$TOOL_OUT" "$TOOL_ERR" | rg -q --fixed-strings -- "$pattern"; then
    printf '      leaked pattern present: %s\n' "$pattern"
    record_fail "$name"
  else
    record_pass "$name"
  fi
}

# 1. Help works and lists every required subcommand.
run_tool --help
assert_rc "help exits 0" 0
for cmd in health search item children collections tags fulltext doiindex pdf; do
  assert_stdout_contains "help lists '$cmd'" "$cmd"
done

# 2. Health reports the pinned pyzotero version and structured mode info.
unset ZOTERO_LIBRARY_ID ZOTERO_API_KEY ZOTERO_LIBRARY_TYPE
run_tool health
assert_stdout_contains "health reports pyzotero version" '"pyzotero_version": "1.13.0"'
assert_stdout_contains "health reports active_mode field" '"active_mode"'
# No usable mode without local API or credentials.
assert_rc "health exits non-zero with no access mode" 1

# 3. Clean error (not a stack trace) when no mode is available.
run_tool search "anything"
assert_rc "search without access exits 1" 1
[ -n "$TOOL_ERR" ] && grep -q '^error:' <<<"$TOOL_ERR" \
  && record_pass "search emits a clean 'error:' line" \
  || record_fail "search emits a clean 'error:' line"

# 4. Full-text search states its Web API requirement when web is unconfigured.
run_tool search "anything" --fulltext
assert_rc "fulltext search without web creds exits 1" 1
grep -q 'Web API' <<<"$TOOL_ERR" \
  && record_pass "fulltext error names Web API requirement" \
  || record_fail "fulltext error names Web API requirement"

# 5. No-secret-leak invariant: a forced web call with fake creds must error
#    without echoing the API key anywhere in stdout or stderr.
SECRET="ZT_TEST_SECRET_DO_NOT_LEAK"
ZOTERO_LIBRARY_ID=99999 ZOTERO_API_KEY="$SECRET" ZOTERO_LIBRARY_TYPE=user \
  run_tool search "anything" --mode web
assert_combined_absent "API key never appears in output" "$SECRET"

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi
exit 0
