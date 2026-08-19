#!/usr/bin/env bash
# Regression tests for the main-thread Markdown communication gate.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK="$REPO_ROOT/hooks/ensure-communicate"
TMPROOT=$(mktemp -d)
trap 'rm -rf "$TMPROOT"' EXIT INT TERM

project="$TMPROOT/project"
mkdir -p "$project/superRA/alpha"
printf '# Notes\n' >"$project/README.md"
printf 'plain\n' >"$project/notes.txt"
printf '%s\n' '---' 'title: Alpha' 'status: in-progress' '---' '' '## Objective' '' 'Test.' >"$project/superRA/alpha/task.md"

pass=0
fail=0

run_case() {
  local name="$1"
  local expect="$2"
  local tool_name="$3"
  local tool_input_json="$4"
  local transcript_content="${5:-}"
  local agent_id="${6:-}"
  local expected_reason="${7:-}"
  local transcript_path=""
  if [ "$transcript_content" = "__NONEXISTENT__" ]; then
    transcript_path="$TMPROOT/does-not-exist-$RANDOM.jsonl"
  elif [ -n "$transcript_content" ]; then
    transcript_path="$TMPROOT/transcript-$RANDOM.jsonl"
    printf '%s\n' "$transcript_content" >"$transcript_path"
  fi

  local input out got
  input=$(python3 -c '
import json, sys
print(json.dumps({
    "session_id": "session",
    "tool_use_id": sys.argv[1],
    "transcript_path": sys.argv[2],
    "cwd": sys.argv[3],
    "hook_event_name": "PreToolUse",
    "tool_name": sys.argv[4],
    "tool_input": json.loads(sys.argv[5]),
    **({"agent_id": sys.argv[6]} if sys.argv[6] else {}),
}))
' "tool-$RANDOM" "$transcript_path" "$project" "$tool_name" "$tool_input_json" "$agent_id")
  out=$(env SUPERRA_COMMUNICATE_STATE_DIR="$TMPROOT/state" bash "$HOOK" <<<"$input")

  if ! printf '%s' "$out" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null; then
    got="invalid-json"
  elif printf '%s' "$out" | grep -q '"permissionDecision":"deny"'; then
    got="deny"
  elif [ "$out" = "{}" ]; then
    got="silent"
  else
    got="unexpected"
  fi

  if [ "$got" = "$expect" ] && { [ -z "$expected_reason" ] || printf '%s' "$out" | grep -Fq "$expected_reason"; }; then
    printf 'PASS  %s\n' "$name"
    pass=$((pass + 1))
  else
    printf 'FAIL  %s (expected %s, got %s: %s)\n' "$name" "$expect" "$got" "$out"
    fail=$((fail + 1))
  fi
}

loaded='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"superRA:communicate"}}]}}'
codex_loaded='{"type":"function_call","name":"exec_command","arguments":{"cmd":"sed -n 1,220p skills/communicate/SKILL.md"}}'
task_read='{"type":"tool_use","name":"Bash","input":{"command":"./superRA/superra task read alpha"}}'
other='{"type":"assistant","message":{"content":[]}}'
mentioned='{"type":"user","message":{"content":"load superRA:communicate and run ./superRA/superra task read alpha"}}'

run_case "Edit Markdown requires Communicate" deny Edit "{\"file_path\":\"$project/README.md\"}" "$other"
run_case "Edit Markdown passes after Skill load" silent Edit "{\"file_path\":\"$project/README.md\"}" "$loaded"
run_case "Codex skill-file read counts as load" silent Edit "{\"file_path\":\"$project/README.md\"}" "$codex_loaded"
run_case "Edit non-Markdown is ignored" silent Edit "{\"file_path\":\"$project/notes.txt\"}" "$other"
run_case "Missing Edit target fails open" silent Edit '{}' "$other"
run_case "Missing transcript fails open" silent Edit "{\"file_path\":\"$project/README.md\"}"
run_case "Unreadable transcript fails open" silent Edit "{\"file_path\":\"$project/README.md\"}" __NONEXISTENT__
run_case "Malformed transcript fails open" silent Edit "{\"file_path\":\"$project/README.md\"}" 'not-json'
run_case "Subagent call is ignored" silent Edit "{\"file_path\":\"$project/README.md\"}" "$other" subagent-1

run_case "Task Markdown requires Communicate" deny Edit "{\"file_path\":\"$project/superRA/alpha/task.md\"}" "$task_read" "" 'load `superRA:communicate`'
run_case "Task Markdown passes with Communicate load" silent Edit "{\"file_path\":\"$project/superRA/alpha/task.md\"}" "$loaded"
run_case "Prose mention is not load evidence" deny Edit "{\"file_path\":\"$project/superRA/alpha/task.md\"}" "$mentioned"
run_case "Retry passes when evidence appears" silent Edit "{\"file_path\":\"$project/README.md\"}" "$loaded"

read_tool='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"skills/communicate/SKILL.md"}}]}}'
grep_tool='{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Grep","input":{"path":"skills/communicate/SKILL.md","pattern":"pyramid"}}]}}'
git_diff='{"type":"tool_use","name":"Bash","input":{"command":"git diff skills/communicate/SKILL.md"}}'
grep_cmd='{"type":"function_call","name":"exec_command","arguments":{"cmd":"grep -n pyramid skills/communicate/SKILL.md"}}'
run_case "Read-tool path counts as load" silent Edit "{\"file_path\":\"$project/README.md\"}" "$read_tool"
tail_read='{"type":"tool_use","name":"Bash","input":{"command":"tail -50 skills/communicate/SKILL.md"}}'
sed_cluster_read='{"type":"function_call","name":"exec_command","arguments":{"cmd":"sed -ne 1,50p skills/communicate/SKILL.md"}}'
run_case "tail read counts as load" silent Edit "{\"file_path\":\"$project/README.md\"}" "$tail_read"
run_case "sed clustered -n read counts as load" silent Edit "{\"file_path\":\"$project/README.md\"}" "$sed_cluster_read"
run_case "Grep-tool path is not load evidence" deny Edit "{\"file_path\":\"$project/README.md\"}" "$grep_tool"
run_case "git diff mention is not load evidence" deny Edit "{\"file_path\":\"$project/README.md\"}" "$git_diff"
run_case "grep command mention is not load evidence" deny Edit "{\"file_path\":\"$project/README.md\"}" "$grep_cmd"

agent_type_only=$(python3 -c '
import json, sys
print(json.dumps({
    "session_id": "session",
    "transcript_path": "",
    "cwd": sys.argv[1],
    "hook_event_name": "PreToolUse",
    "tool_name": "Edit",
    "tool_input": {"file_path": sys.argv[1] + "/README.md"},
    "agent_type": "general-purpose",
}))
' "$project")
out=$(bash "$HOOK" <<<"$agent_type_only")
if [ "$out" = "{}" ]; then
  printf 'PASS  agent_type-only subagent call is ignored\n'
  pass=$((pass + 1))
else
  printf 'FAIL  agent_type-only subagent call is ignored (got %s)\n' "$out"
  fail=$((fail + 1))
fi

patch_md=$(printf '%s\n' '*** Begin Patch' '*** Update File: README.md' '@@' '*** End Patch')
patch_txt=$(printf '%s\n' '*** Begin Patch' '*** Update File: notes.txt' '@@' '*** End Patch')
run_case "apply_patch Markdown is gated" deny apply_patch "$(python3 -c 'import json,sys; print(json.dumps({"command":sys.argv[1]}))' "$patch_md")" "$other"
run_case "apply_patch non-Markdown is ignored" silent apply_patch "$(python3 -c 'import json,sys; print(json.dumps({"command":sys.argv[1]}))' "$patch_txt")" "$other"
run_case "Malformed apply_patch fails open" silent apply_patch '{"command":"not a patch"}' "$other"

run_case "Bash redirection is gated" deny Bash '{"command":"printf text > README.md"}' "$other"
run_case "Bash append is gated" deny Bash '{"command":"echo text >> README.md"}' "$other"
run_case "Bash tee is gated" deny Bash '{"command":"printf text | tee README.md"}' "$other"
run_case "Bash sed in-place is gated" deny Bash '{"command":"sed -i s/a/b/ README.md"}' "$other"
run_case "Bash perl clustered in-place is gated" deny Bash '{"command":"perl -pi -e s/a/b/ README.md"}' "$other"
run_case "Bash touch is gated" deny Bash '{"command":"touch README.md"}' "$other"
run_case "Bash copy destination is gated" deny Bash '{"command":"cp notes.txt README.md"}' "$other"
run_case "Bash copy source is not mistaken for destination" silent Bash '{"command":"cp README.md notes.txt"}' "$other"
run_case "Unsupported Bash mutation fails open" silent Bash '{"command":"python3 rewrite.py README.md"}' "$other"
run_case "Read-only Bash mention is ignored" silent Bash '{"command":"rg heading README.md"}' "$other"

if python3 - "$REPO_ROOT" <<'PY'
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
claude = json.loads((root / "hooks/hooks.json").read_text(encoding="utf-8"))
codex = json.loads((root / "hooks/hooks-codex.json").read_text(encoding="utf-8"))
cursor = json.loads((root / "hooks/hooks-cursor.json").read_text(encoding="utf-8"))

def wired(groups, matcher):
    return any(
        group.get("matcher") == matcher
        and any("ensure-communicate" in hook.get("command", "") for hook in group.get("hooks", []))
        for group in groups
    )

assert wired(claude["hooks"]["PreToolUse"], "Edit|Write|Bash")
assert wired(codex["hooks"]["PreToolUse"], "Edit|Write|Bash|apply_patch")
assert any("ensure-communicate" in hook["command"] for hook in cursor["hooks"]["preToolUse"])
PY
then
  printf 'PASS  hook registries cover Claude, Codex, and Cursor\n'
  pass=$((pass + 1))
else
  printf 'FAIL  hook registries cover Claude, Codex, and Cursor\n'
  fail=$((fail + 1))
fi

printf '\nPassed: %d    Failed: %d\n' "$pass" "$fail"
if [ "$fail" -gt 0 ]; then
  exit 1
fi
