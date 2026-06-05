#!/usr/bin/env bash
# Credential-free behavior checks for the zotero-paper-reader tool script.
# Exercises CLI parsing, version reporting, access-mode detection, clean error
# paths, and the no-secret-leak invariant without contacting a real library.
# Run from the repo root: bash tests/test-zotero-tool.sh

set -euo pipefail

cd "$(dirname "$0")/.."

SCRIPT="skills/zotero-paper-reader/scripts/zotero_tool.py"
SCRIPT_ABS="$(pwd)/$SCRIPT"
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
for cmd in health libraries search item children collections tags fulltext doiindex pdf; do
  assert_stdout_contains "help lists '$cmd'" "$cmd"
done

# 2. Health reports the pinned pyzotero version and structured mode info.
#    The exit code depends on the real environment: 0 when a local Zotero API
#    is actually running on this machine, 1 when no access mode is available.
#    Branch so the check is deterministic either way.
unset ZOTERO_LIBRARY_ID ZOTERO_API_KEY ZOTERO_LIBRARY_TYPE
run_tool health
assert_stdout_contains "health reports pyzotero version" '"pyzotero_version": "1.13.0"'
assert_stdout_contains "health reports active_mode field" '"active_mode"'
if printf '%s' "$TOOL_OUT" | rg -q --fixed-strings '"local_api_available": true'; then
  assert_rc "health exits 0 when local API is available" 0
else
  assert_rc "health exits non-zero with no access mode" 1
fi

# 3. Clean error (not a stack trace) when no mode is available. Force --mode web
#    with no credentials so the no-access path is deterministic even when a local
#    Zotero API is running on the test machine.
run_tool search "anything" --mode web
assert_rc "web search without creds exits 1" 1
[ -n "$TOOL_ERR" ] && grep -q '^error:' <<<"$TOOL_ERR" \
  && record_pass "search emits a clean 'error:' line" \
  || record_fail "search emits a clean 'error:' line"

# 4. Full-text search reaches the same access-mode resolution as plain search
#    (it is NOT web-only — the local API serves qmode=everything, verified live
#    in task 05). With --mode web and no credentials it errors naming the Web
#    API requirement. The local full-text path needs a live library and is
#    covered by task 05's smoke test, not this credential-free suite.
run_tool search "anything" --fulltext --mode web
assert_rc "web fulltext without creds exits 1" 1
grep -q 'Web API' <<<"$TOOL_ERR" \
  && record_pass "web fulltext error names Web API requirement" \
  || record_fail "web fulltext error names Web API requirement"

# 4b. An invalid --library spec is rejected deterministically (parse_library
#     raises before any access attempt — no local API or credentials needed).
run_tool search "anything" --library notanid
assert_rc "invalid --library exits 1" 1
grep -q 'invalid --library' <<<"$TOOL_ERR" \
  && record_pass "invalid --library names the problem" \
  || record_fail "invalid --library names the problem"

# 5. No-secret-leak invariant: a forced web call with fake creds must error
#    without echoing the API key anywhere in stdout or stderr.
SECRET="ZT_TEST_SECRET_DO_NOT_LEAK"
ZOTERO_LIBRARY_ID=99999 ZOTERO_API_KEY="$SECRET" ZOTERO_LIBRARY_TYPE=user \
  run_tool search "anything" --mode web
assert_combined_absent "API key never appears in output" "$SECRET"

# 6. Notes/.env parsing: with env vars unset, load_env_file must pick up a
#    project-local Notes/.env (resolved from cwd). Uses fake non-secret values;
#    the .env-sourced key must still never leak.
ENV_TMP="$(mktemp -d)"
mkdir -p "$ENV_TMP/Notes"
DOTENV_SECRET="ZT_DOTENV_SECRET_DO_NOT_LEAK"
cat >"$ENV_TMP/Notes/.env" <<EOF
ZOTERO_LIBRARY_ID=4242424
ZOTERO_API_KEY=$DOTENV_SECRET
ZOTERO_LIBRARY_TYPE=user
EOF
DOTENV_OUT="$(cd "$ENV_TMP" && uv run --quiet --script "$SCRIPT_ABS" health 2>/tmp/zt_dotenv_err)" || true
DOTENV_ERR="$(cat /tmp/zt_dotenv_err)"
printf '%s' "$DOTENV_OUT" | rg -q --fixed-strings -- '"ZOTERO_LIBRARY_ID": true' \
  && record_pass "Notes/.env library_id is read" \
  || record_fail "Notes/.env library_id is read"
printf '%s' "$DOTENV_OUT" | rg -q --fixed-strings -- '"ZOTERO_API_KEY": true' \
  && record_pass "Notes/.env api_key is read" \
  || record_fail "Notes/.env api_key is read"
if printf '%s%s' "$DOTENV_OUT" "$DOTENV_ERR" | rg -q --fixed-strings -- "$DOTENV_SECRET"; then
  record_fail ".env API key never appears in output"
else
  record_pass ".env API key never appears in output"
fi
rm -rf "$ENV_TMP"

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi
exit 0
