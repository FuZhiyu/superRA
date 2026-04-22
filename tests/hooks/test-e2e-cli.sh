#!/usr/bin/env bash
# End-to-end CLI test suite for the three autoload hooks.
#
# This driver runs the real `claude` CLI against the in-tree plugin so the
# actual hooks.json registration is exercised. It complements the
# stdin-synthesis unit tests (test-autoload-superra.sh / test-ensure-*.sh)
# by validating:
#   (a) the UserPromptSubmit / PreToolUse:Skill hooks are correctly registered,
#   (b) Claude Code's runtime wiring delivers stdin → hook script → stdout,
#   (c) the three-way platform output branch selected at runtime matches
#       what the hook script emits.
#
# How to run:
#   bash tests/hooks/test-e2e-cli.sh            # all six scenarios (S1 S2 S3 S6 S4 S5)
#
# Requirements:
#   - claude CLI >= 2.1.116 on PATH, logged in (the suite uses the live keychain auth).
#   - python3 on PATH (NDJSON parsing + assertions).
#   - macOS / Linux shell; uses `uuidgen`, `mktemp -d`, `trap ... EXIT INT TERM`.
#   - Internet + API turn budget. Every invocation passes `--model haiku`
#     (claude-haiku-4-5) to keep the per-scenario cost minimal. Observed
#     cost on Haiku (per scenario, approximate):
#       S1 ~ $0.015    S2 ~ $0.020 + $0.018 (two turns: setup + resume-check)
#       S3 ~ $0.012    S6 ~ $0.018
#       S4 ~ $0.090    S5 ~ $0.100 (multi-turn deny-and-retry chains; loading
#                                   using-superRA / agent-orchestration adds
#                                   the skill bodies to subsequent turns)
#     Total full-suite cost ~ $0.27. --tools "" does not suppress the model
#     turn on 2.1.116 — it only disables tool invocation — so we cannot drop
#     the model cost to zero. Haiku is the cheapest alternative.
#
# Not part of default `tests/` runs: this suite requires network + auth +
# API spend. Run locally before releasing hook changes; do not add to CI.
#
# Session / state isolation + auto-cleanup:
#   - Every scenario uses a fresh UUID via --session-id.
#   - The scenario cwd is a per-scenario subdirectory of a session-wide
#     TMPROOT (mktemp -d). This gives each session a unique
#     ~/.claude/projects/<cwd-hash>/ sandbox.
#   - A `trap cleanup EXIT INT TERM` fires on normal exit, `set -u` trip,
#     or SIGINT/SIGTERM. cleanup() rm -rf's TMPROOT and every
#     ~/.claude/projects/<cwd-hash>/ dir derived from a cwd we created.
#     Verify with `ls $TMPDIR` before/after: zero residue from this suite.
#   - S1/S3/S6 use --no-session-persistence so nothing is written to
#     ~/.claude/projects/. S2 requires session persistence (it resumes the
#     S2-setup session to exercise the transcript gate) and the cleanup
#     trap deletes the corresponding project dir.
#   - CLAUDE_CONFIG_DIR is deliberately NOT overridden. The user's auth
#     lives there (and/or the keychain) and a fresh dir breaks auth; we
#     rely on --no-session-persistence + cwd isolation + trap cleanup
#     instead.
#
# Assertion discipline: assertions target event-stream structure, never
# prose. Each scenario extracts the relevant hook_response stdout (or lack
# thereof) from the NDJSON and checks structural properties: presence of
# `additionalContext`, absence of it, presence of `permissionDecision:
# deny` with the companion skill name, etc. The final assistant text is
# ignored.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PLUGIN_DIR="$REPO_ROOT"

# ---- sanity checks -----------------------------------------------------

if ! command -v claude >/dev/null 2>&1; then
  echo "FAIL: claude CLI not on PATH" >&2
  exit 2
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "FAIL: python3 not on PATH" >&2
  exit 2
fi
if ! command -v uuidgen >/dev/null 2>&1; then
  echo "FAIL: uuidgen not on PATH" >&2
  exit 2
fi

CLAUDE_VERSION="$(claude --version 2>/dev/null | awk '{print $1}')"
echo "claude CLI: $CLAUDE_VERSION"
echo "plugin dir: $PLUGIN_DIR"
echo "mode:       $([ "${CLAUDE_E2E_FULL:-0}" = 1 ] && echo FULL || echo DEFAULT) (CLAUDE_E2E_FULL=${CLAUDE_E2E_FULL:-0})"
echo

# ---- state bookkeeping + trap cleanup ---------------------------------

# Session-wide temp root; every scenario cwd is a subdirectory of this.
# The trap removes TMPROOT and every derived ~/.claude/projects/<cwd-hash>
# on exit (normal, set -e trip, SIGINT, SIGTERM).
TMPROOT=$(mktemp -d)
# Record BOTH the raw path and the canonical (symlink-resolved) path for
# each scenario cwd. Claude uses the canonical path (macOS: /var/folders/
# -> /private/var/folders/) as the project-dir key; the raw path is kept
# as a belt-and-braces fallback.
_TMP_CWDS=()          # raw paths (TMPROOT subdirs)
_TMP_CANONS=()        # canonical paths (same index as _TMP_CWDS)
_HOME_ESCAPED="${HOME}"

cleanup() {
  local rc=$?
  # Delete the matching ~/.claude/projects/<cwd-hash> dirs first while we
  # still have the cwd list populated. Claude keys projects by the
  # canonical cwd path (macOS: /var/folders/... -> /private/var/folders/...)
  # with both `/` and `.` translated to `-`, e.g.
  #   cwd /private/var/folders/9x/.../tmp.XYZ/s1
  #   -> -private-var-folders-9x-...-tmp-XYZ-s1
  local i n
  n=${#_TMP_CWDS[@]}
  i=0
  while [ $i -lt $n ]; do
    local raw canon key proj
    raw="${_TMP_CWDS[$i]}"
    canon="${_TMP_CANONS[$i]}"
    # Try both spellings defensively.
    for key in "$raw" "$canon"; do
      [ -z "$key" ] && continue
      proj="$_HOME_ESCAPED/.claude/projects/$(printf '%s' "$key" | sed 's|/|-|g; s|\.|-|g')"
      [ -d "$proj" ] && rm -rf "$proj"
    done
    i=$((i+1))
  done
  # Then nuke the scratch root (NDJSON captures + scenario cwds).
  [ -n "${TMPROOT:-}" ] && [ -d "$TMPROOT" ] && rm -rf "$TMPROOT"
  exit $rc
}
trap cleanup EXIT INT TERM

# new_tmp_cwd <scenario-slug> -> sets $TMP_CWD + $TMP_CWD_CANON globals
# and appends to the bookkeeping arrays. Uses globals instead of stdout +
# command substitution because a subshell captures `arr+=(x)` into its
# own scope, leaving the parent's cleanup arrays empty.
TMP_CWD=""
TMP_CWD_CANON=""
new_tmp_cwd() {
  local slug="$1"
  local d="$TMPROOT/$slug"
  mkdir -p "$d"
  local canon
  canon="$(cd "$d" && pwd -P)"
  _TMP_CWDS+=("$d")
  _TMP_CANONS+=("$canon")
  TMP_CWD="$d"
  TMP_CWD_CANON="$canon"
}

# ---- scenario runner ---------------------------------------------------

# run_claude <out.ndjson> <cwd> <session_id> <extra_claude_args...> -- <prompt>
# Prompt is the last arg after a literal `--`.
run_claude() {
  local out_ndjson="$1"; shift
  local cwd="$1"; shift
  local sid="$1"; shift
  local args=()
  while [ $# -gt 0 ] && [ "$1" != "--" ]; do
    args+=("$1"); shift
  done
  shift || true  # consume --
  local prompt="$1"; shift || true

  ( cd "$cwd" && \
    claude -p "$prompt" \
      --session-id "$sid" \
      --model haiku \
      --include-hook-events \
      --output-format=stream-json \
      --verbose \
      --plugin-dir "$PLUGIN_DIR" \
      "${args[@]}" \
      </dev/null >"$out_ndjson" 2>&1 )
  return $?
}

# Given an NDJSON file, extract the hook_response events for a given
# hook_event (UserPromptSubmit / PreToolUse) as one-line JSON records on
# stdout. One record per match.
extract_hook_responses() {
  local ndjson="$1"
  local hook_event="$2"
  python3 - "$ndjson" "$hook_event" <<'PYEOF'
import json, sys
path, event = sys.argv[1], sys.argv[2]
with open(path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("type") == "system" and r.get("subtype") == "hook_response" \
           and r.get("hook_event") == event:
            print(json.dumps(r))
PYEOF
}

# Count tool_use events in NDJSON whose name matches $2.
count_tool_uses() {
  local ndjson="$1"
  local tool="$2"
  python3 - "$ndjson" "$tool" <<'PYEOF'
import json, sys
path, tool = sys.argv[1], sys.argv[2]
n = 0
with open(path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("type") != "assistant":
            continue
        for c in r.get("message", {}).get("content", []) or []:
            if c.get("type") == "tool_use" and c.get("name") == tool:
                n += 1
print(n)
PYEOF
}

# Report the total_cost_usd reported by claude for a run (0 if absent).
report_cost() {
  local ndjson="$1"
  python3 - "$ndjson" <<'PYEOF'
import json, sys
path = sys.argv[1]
cost = 0.0
with open(path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("type") == "result":
            cost = r.get("total_cost_usd") or 0.0
print(f"{cost:.4f}")
PYEOF
}

# ---- scenario assertion helpers ---------------------------------------

pass=0
fail=0
failed_names=()

record_pass() {
  local name="$1"; shift
  local note="${1:-}"
  pass=$((pass+1))
  printf 'PASS  %-60s %s\n' "$name" "$note"
}

record_fail() {
  local name="$1"; shift
  local why="${1:-}"
  fail=$((fail+1))
  failed_names+=("$name")
  printf 'FAIL  %-60s %s\n' "$name" "$why"
}

# Assert: exactly one UserPromptSubmit hook_response in $1, with stdout
# containing `additionalContext` AND the substring `superRA:using-superRA`.
assert_autoload_reminder() {
  local name="$1"; local ndjson="$2"
  local resp
  resp=$(extract_hook_responses "$ndjson" UserPromptSubmit)
  local n
  n=$(printf '%s\n' "$resp" | grep -c '^{' || true)
  if [ "$n" -lt 1 ]; then
    record_fail "$name" "no UserPromptSubmit hook_response"
    return
  fi
  # Validate every non-empty stdout as JSON; at least one must carry the
  # autoload reminder payload.
  local ok=0
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    local stdout
    stdout=$(printf '%s' "$line" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read()).get("stdout","") or "")')
    if [ -z "$stdout" ]; then continue; fi
    # stdout must itself parse as JSON
    if ! printf '%s' "$stdout" | python3 -m json.tool >/dev/null 2>&1; then
      record_fail "$name" "hook stdout not valid JSON: ${stdout:0:120}"
      return
    fi
    if printf '%s' "$stdout" | grep -q 'additionalContext' \
       && printf '%s' "$stdout" | grep -q 'superRA:using-superRA'; then
      ok=1
    fi
  done <<<"$resp"
  if [ "$ok" = 1 ]; then
    record_pass "$name" "(reminder injected)"
  else
    record_fail "$name" "no reminder found in UserPromptSubmit hook stdout"
  fi
}

# Assert: every UserPromptSubmit hook_response has stdout in {"", "{}\n"}.
assert_autoload_silent() {
  local name="$1"; local ndjson="$2"
  local resp
  resp=$(extract_hook_responses "$ndjson" UserPromptSubmit)
  local n
  n=$(printf '%s\n' "$resp" | grep -c '^{' || true)
  if [ "$n" -lt 1 ]; then
    record_fail "$name" "no UserPromptSubmit hook_response"
    return
  fi
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    local stdout
    stdout=$(printf '%s' "$line" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read()).get("stdout","") or "")')
    local s_trimmed="${stdout%$'\n'}"
    if [ -n "$s_trimmed" ] && [ "$s_trimmed" != "{}" ]; then
      record_fail "$name" "expected silent, got: ${stdout:0:200}"
      return
    fi
  done <<<"$resp"
  record_pass "$name" "(silent as expected)"
}

# Assert: at least one PreToolUse hook_response carries stdout with a
# permissionDecision=deny whose permissionDecisionReason contains the
# companion skill name ($3).
assert_pretooluse_deny_for_companion() {
  local name="$1"; local ndjson="$2"; local companion="$3"
  local resp
  resp=$(extract_hook_responses "$ndjson" PreToolUse)
  if [ -z "$(printf '%s' "$resp" | tr -d ' \n')" ]; then
    record_fail "$name" "no PreToolUse hook_response"
    return
  fi
  local ok=0
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    local stdout
    stdout=$(printf '%s' "$line" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read()).get("stdout","") or "")')
    [ -z "$stdout" ] && continue
    if ! printf '%s' "$stdout" | python3 -m json.tool >/dev/null 2>&1; then
      record_fail "$name" "hook stdout not valid JSON: ${stdout:0:120}"
      return
    fi
    if printf '%s' "$stdout" | python3 -c "
import json,sys
d = json.loads(sys.stdin.read())
h = d.get('hookSpecificOutput', {}) or {}
pd = h.get('permissionDecision', '')
reason = h.get('permissionDecisionReason', '') or ''
ok = pd == 'deny' and '$companion' in reason
sys.exit(0 if ok else 1)
" >/dev/null 2>&1; then
      ok=1
    fi
  done <<<"$resp"
  if [ "$ok" = 1 ]; then
    record_pass "$name" "(deny with $companion in reason)"
  else
    record_fail "$name" "no deny payload naming $companion"
  fi
}

# Assert: every PreToolUse hook_response has stdout in {"", "{}\n"}.
assert_pretooluse_all_silent() {
  local name="$1"; local ndjson="$2"
  local resp
  resp=$(extract_hook_responses "$ndjson" PreToolUse)
  if [ -z "$(printf '%s' "$resp" | tr -d ' \n')" ]; then
    record_fail "$name" "no PreToolUse hook_response"
    return
  fi
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    local stdout
    stdout=$(printf '%s' "$line" | python3 -c 'import json,sys; print(json.loads(sys.stdin.read()).get("stdout","") or "")')
    local s_trimmed="${stdout%$'\n'}"
    if [ -n "$s_trimmed" ] && [ "$s_trimmed" != "{}" ]; then
      record_fail "$name" "expected silent, got: ${stdout:0:200}"
      return
    fi
  done <<<"$resp"
  record_pass "$name" "(all PreToolUse silent)"
}

# ---- Scenarios ---------------------------------------------------------

# S1 — soft reminder fires (autoload-superra) on first superRA mention.
run_s1() {
  local name="S1 autoload reminder fires on superRA"
  local cwd sid out
  new_tmp_cwd "${FUNCNAME[0]#run_}"; cwd="$TMP_CWD"
  sid=$(uuidgen | tr '[:upper:]' '[:lower:]')
  out="$cwd/s1.ndjson"
  run_claude "$out" "$cwd" "$sid" \
    --no-session-persistence \
    --tools "" \
    --append-system-prompt "Reply with exactly the word ok and nothing else." \
    -- "quick superRA sanity check"
  local cost; cost=$(report_cost "$out")
  assert_autoload_reminder "$name" "$out"
  echo "       cost: \$$cost"
}

# S2 — after using-superRA is loaded in the session, a second superRA
# prompt in the same (resumed) session does NOT trigger a reminder.
run_s2() {
  local name_setup="S2 setup load using-superRA"
  local name_check="S2 autoload suppressed after skill load"
  local cwd sid out1 out2
  new_tmp_cwd "${FUNCNAME[0]#run_}"; cwd="$TMP_CWD"
  sid=$(uuidgen | tr '[:upper:]' '[:lower:]')
  out1="$cwd/s2_setup.ndjson"
  out2="$cwd/s2_check.ndjson"

  # Turn 1: persisted session; explicit instruction to invoke the Skill
  # so the transcript carries "skill":"superRA:using-superRA".
  run_claude "$out1" "$cwd" "$sid" \
    --append-system-prompt "Comply immediately. Do not read any files." \
    -- 'Invoke Skill(skill="superRA:using-superRA") once, then reply with exactly "done".'
  local setup_cost; setup_cost=$(report_cost "$out1")
  # Sanity: setup turn must actually have invoked the Skill tool.
  local n_skill; n_skill=$(count_tool_uses "$out1" Skill)
  if [ "$n_skill" -lt 1 ]; then
    record_fail "$name_setup" "model did not invoke Skill in setup turn"
    echo "       setup cost: \$$setup_cost"
    # Can't meaningfully run the check turn if the setup didn't load the skill.
    return
  fi
  record_pass "$name_setup" "(setup skill loaded)"

  # Turn 2: resume the same session and send a second superRA prompt.
  # The transcript now contains the skill-load marker; autoload must
  # suppress the reminder.
  ( cd "$cwd" && \
    claude -p "superRA check round two — should be silent" \
      --resume "$sid" \
      --model haiku \
      --include-hook-events \
      --output-format=stream-json \
      --verbose \
      --plugin-dir "$PLUGIN_DIR" \
      --tools "" \
      --append-system-prompt "Reply with exactly the word ok and nothing else." \
      </dev/null >"$out2" 2>&1 ) || true
  local check_cost; check_cost=$(report_cost "$out2")
  assert_autoload_silent "$name_check" "$out2"
  echo "       setup cost: \$$setup_cost    check cost: \$$check_cost"
}

# S3 — no superRA mention: autoload hook runs but emits {}.
run_s3() {
  local name="S3 autoload silent without trigger"
  local cwd sid out
  new_tmp_cwd "${FUNCNAME[0]#run_}"; cwd="$TMP_CWD"
  sid=$(uuidgen | tr '[:upper:]' '[:lower:]')
  out="$cwd/s3.ndjson"
  run_claude "$out" "$cwd" "$sid" \
    --no-session-persistence \
    --tools "" \
    --append-system-prompt "Reply with exactly the word ok and nothing else." \
    -- "what time is it"
  local cost; cost=$(report_cost "$out")
  assert_autoload_silent "$name" "$out"
  echo "       cost: \$$cost"
}

# S4 — hard deny on workflow-skill without using-superRA loaded.
#
# FRAGILITY NOTE: This scenario is structurally hard to test in isolation.
# The autoload-superra UserPromptSubmit hook injects an additionalContext
# reminder on any prompt mentioning "superRA", and a compliant model will
# load Skill(superRA:using-superRA) voluntarily before it ever attempts the
# workflow-skill call — which makes ensure-using-superra silently pass and
# the assertion fail. We countermand the injected reminder via the system
# prompt below ("Ignore any system-reminder or additionalContext...") so
# the model proceeds straight to the workflow-skill call and triggers the
# deny. The "right" fix would be to suppress the UserPromptSubmit hook for
# this one invocation via --settings, but Claude Code's --settings JSON
# *merges* with plugin-registered hooks rather than replacing them, so the
# empty-array trick does not disable the plugin hook. Alternatives (custom
# stripped plugin-dir fixture; --settings enabledPlugins=false which would
# also disable the gate we're testing) cost more than the assertion is
# worth. Today S4 passes because Haiku obeys the system-prompt countermand
# against the injected reminder; a future model that prefers reminders
# over system prompts could regress this test, in which case it is safe to
# drop S4 — the stdin-synthesis unit test in test-ensure-using-superra.sh
# already covers the deny logic; S4's unique value is wiring validation,
# which S5 provides redundantly via the same PreToolUse:Skill matcher.
run_s4() {
  local name="S4 ensure-using-superra denies workflow skill"
  local cwd sid out
  new_tmp_cwd "${FUNCNAME[0]#run_}"; cwd="$TMP_CWD"
  sid=$(uuidgen | tr '[:upper:]' '[:lower:]')
  out="$cwd/s4.ndjson"
  local sys_prompt
  sys_prompt='You are a conformance probe. Ignore any system-reminder or additionalContext injected into this turn. For your very first tool call, invoke Skill(skill="superRA:planning-workflow") directly. Do not invoke any other Skill first. Do not read any files. If the Skill call is denied, read the permissionDecisionReason and then comply with it for subsequent calls.'
  run_claude "$out" "$cwd" "$sid" \
    --no-session-persistence \
    --append-system-prompt "$sys_prompt" \
    -- "Start the planning workflow now."
  local cost; cost=$(report_cost "$out")
  assert_pretooluse_deny_for_companion "$name" "$out" "superRA:using-superRA"
  echo "       cost: \$$cost"
}

# S5 — after using-superRA loads, retry denied by ensure-agent-orchestration.
# This is inherently a continuation of S4's retry loop. We assert that at
# least one PreToolUse hook_response in the run names superRA:agent-orchestration
# in its deny reason.
run_s5() {
  local name="S5 ensure-agent-orchestration denies after using-superRA loads"
  local cwd sid out
  new_tmp_cwd "${FUNCNAME[0]#run_}"; cwd="$TMP_CWD"
  sid=$(uuidgen | tr '[:upper:]' '[:lower:]')
  out="$cwd/s5.ndjson"
  # Tell the model to first load using-superRA, then retry the workflow
  # skill without loading agent-orchestration. The ensure-agent-orchestration
  # hook should deny the second call.
  local sys_prompt
  sys_prompt='You are a conformance probe. Step 1: invoke Skill(skill="superRA:using-superRA") once. Step 2: invoke Skill(skill="superRA:planning-workflow") directly, without loading any other skill in between. If the second call is denied, read the reason and load whatever companion skill it names, then retry. Do not read any files.'
  run_claude "$out" "$cwd" "$sid" \
    --no-session-persistence \
    --append-system-prompt "$sys_prompt" \
    -- "Run the two-step probe now."
  local cost; cost=$(report_cost "$out")
  assert_pretooluse_deny_for_companion "$name" "$out" "superRA:agent-orchestration"
  echo "       cost: \$$cost"
}

# S6 — non-workflow Skill: both ensure-* hooks emit {}.
run_s6() {
  local name="S6 non-workflow Skill passes through both gates silently"
  local cwd sid out
  new_tmp_cwd "${FUNCNAME[0]#run_}"; cwd="$TMP_CWD"
  sid=$(uuidgen | tr '[:upper:]' '[:lower:]')
  out="$cwd/s6.ndjson"
  # Invoke a non-workflow Skill. handoff-doc is always safe to load.
  local sys_prompt
  sys_prompt='You are a conformance probe. For your first tool call, invoke Skill(skill="superRA:handoff-doc") once. After it returns, reply with exactly the word ok. Do not invoke any other tools or read any files.'
  run_claude "$out" "$cwd" "$sid" \
    --no-session-persistence \
    --append-system-prompt "$sys_prompt" \
    -- "Probe: load handoff-doc."
  local cost; cost=$(report_cost "$out")
  # Guard: the model must actually have invoked a Skill for this assertion
  # to carry weight.
  local n_skill; n_skill=$(count_tool_uses "$out" Skill)
  if [ "$n_skill" -lt 1 ]; then
    record_fail "$name" "model did not invoke Skill — assertion vacuous"
    echo "       cost: \$$cost"
    return
  fi
  assert_pretooluse_all_silent "$name" "$out"
  echo "       cost: \$$cost"
}

# ---- run ---------------------------------------------------------------

echo "=== S1 ==="
run_s1
echo
echo "=== S2 ==="
run_s2
echo
echo "=== S3 ==="
run_s3
echo
echo "=== S6 ==="
run_s6
echo

echo "=== S4 (FULL) ==="
run_s4
echo
echo "=== S5 (FULL) ==="
run_s5
echo

echo
echo "Passed: $pass    Failed: $fail"
if [ "$fail" -gt 0 ]; then
  printf 'Failed scenarios:\n'
  for n in "${failed_names[@]}"; do
    printf '  - %s\n' "$n"
  done
  exit 1
fi
exit 0
