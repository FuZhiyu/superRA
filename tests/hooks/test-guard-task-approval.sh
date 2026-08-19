#!/usr/bin/env bash
# Regression tests for the approved-task blocking-review gate.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK="$REPO_ROOT/hooks/guard-task-approval"
TMPROOT=$(mktemp -d)
trap 'rm -rf "$TMPROOT"' EXIT INT TERM

project="$TMPROOT/project"
task="$project/superRA/alpha/task.md"
mkdir -p "$(dirname "$task")"

write_task() {
  local task_status="$1"
  local finding="$2"
  printf '%s\n' '---' 'title: Alpha' "status: $task_status" 'depends_on: []' '---' '' \
    '## Objective' '' 'Test.' '' '## Review Notes' '' "$finding" >"$task"
}

run_hook() {
  local tool_name="$1"
  local tool_input="$2"
  python3 -c '
import json, sys
print(json.dumps({
    "cwd": sys.argv[1],
    "hook_event_name": "PreToolUse",
    "tool_name": sys.argv[2],
    "tool_input": json.loads(sys.argv[3]),
}))
' "$project" "$tool_name" "$tool_input" | bash "$HOOK"
}

expect() {
  local name="$1"
  local expected="$2"
  local output="$3"
  local actual="allow"
  if printf '%s' "$output" | grep -q '"permissionDecision":"deny"'; then
    actual="deny"
  fi
  if [ "$actual" = "$expected" ] && printf '%s' "$output" | python3 -m json.tool >/dev/null 2>&1; then
    printf 'PASS  %s\n' "$name"
  else
    printf 'FAIL  %s (expected %s, got %s: %s)\n' "$name" "$expected" "$actual" "$output"
    return 1
  fi
}

write_task revise '> [BLOCKING] Fix it.'
out=$(run_hook Edit "$(python3 -c 'import json,sys; print(json.dumps({"file_path":sys.argv[1],"old_string":"status: revise","new_string":"status: approved"}))' "$task")")
expect 'Edit blocks approval with blocking review item' deny "$out"

write_task revise '> [ADVISORY] Consider it.'
out=$(run_hook Edit "$(python3 -c 'import json,sys; print(json.dumps({"file_path":sys.argv[1],"old_string":"status: revise","new_string":"status: approved"}))' "$task")")
expect 'Edit permits approval with advisory review item' allow "$out"

write_task revise '> [BLOCKING] Fix it.'
content=$(sed 's/status: revise/status: approved/; /\[BLOCKING\]/d' "$task")
out=$(run_hook Write "$(python3 -c 'import json,sys; print(json.dumps({"file_path":sys.argv[1],"content":sys.argv[2]}))' "$task" "$content")")
expect 'Write permits approval after removing blocker' allow "$out"

write_task revise '> [BLOCKING] Fix it.'
patch=$(printf '%s\n' '*** Begin Patch' '*** Update File: superRA/alpha/task.md' '@@' '-status: revise' '+status: approved' '*** End Patch')
out=$(run_hook apply_patch "$(python3 -c 'import json,sys; print(json.dumps({"command":sys.argv[1]}))' "$patch")")
expect 'apply_patch blocks approval with retained blocker' deny "$out"

write_task revise '> [BLOCKING] Fix it.'
patch=$(printf '%s\n' '*** Begin Patch' '*** Update File: superRA/alpha/task.md' '@@' '-status: revise' '+status: approved' '@@' ' ## Review Notes' ' ' '-> [BLOCKING] Fix it.' '*** End Patch')
out=$(run_hook apply_patch "$(python3 -c 'import json,sys; print(json.dumps({"command":sys.argv[1]}))' "$patch")")
expect 'apply_patch permits atomic cleanup and approval' allow "$out"

write_task approved '> [ADVISORY] Consider it.'
out=$(run_hook Edit "$(python3 -c 'import json,sys; print(json.dumps({"file_path":sys.argv[1],"old_string":"Test.","new_string":"Test more."}))' "$task")")
expect 'Unrelated edit to approved advisory task passes' allow "$out"

write_task approved '> [ADVISORY] Consider it.'
patch=$(printf '%s\n' '*** Begin Patch' '*** Update File: superRA/alpha/task.md' '@@' ' ## Objective' ' ' '-Test.' '+Apply the [BLOCKING] checklist.' '*** End Patch')
out=$(run_hook apply_patch "$(python3 -c 'import json,sys; print(json.dumps({"command":sys.argv[1]}))' "$patch")")
expect 'Blocking vocabulary outside Review Notes passes' allow "$out"

# A hunk context line may be the empty string (no leading space); the parser
# must treat it as context, not drop it and fail open.
write_task revise '> [BLOCKING] Fix it.'
patch=$(printf '%s\n' '*** Begin Patch' '*** Update File: superRA/alpha/task.md' '@@' '-status: revise' '+status: approved' '@@' ' ## Review Notes' '' ' > [BLOCKING] Fix it.' '*** End Patch')
out=$(run_hook apply_patch "$(python3 -c 'import json,sys; print(json.dumps({"command":sys.argv[1]}))' "$patch")")
expect 'Blank-context hunk blocks approval' deny "$out"

# Hunks may arrive out of order; each must match from position 0.
write_task revise '> [BLOCKING] Fix it.'
patch=$(printf '%s\n' '*** Begin Patch' '*** Update File: superRA/alpha/task.md' '@@' '-Test.' '+Tested.' '@@' '-status: revise' '+status: approved' '*** End Patch')
out=$(run_hook apply_patch "$(python3 -c 'import json,sys; print(json.dumps({"command":sys.argv[1]}))' "$patch")")
expect 'Out-of-order hunks block approval' deny "$out"

# A `Move to:` header must not reset the parser and drop the hunks.
write_task revise '> [BLOCKING] Fix it.'
patch=$(printf '%s\n' '*** Begin Patch' '*** Update File: superRA/alpha/task.md' '*** Move to: superRA/beta/task.md' '@@' '-status: revise' '+status: approved' '*** End Patch')
out=$(run_hook apply_patch "$(python3 -c 'import json,sys; print(json.dumps({"command":sys.argv[1]}))' "$patch")")
expect 'Move-to patch blocks approval' deny "$out"

# Fail closed: an unreconstructable patch that adds `status: approved` onto a
# file with blocking review notes is denied, not waved through.
write_task revise '> [BLOCKING] Fix it.'
patch=$(printf '%s\n' '*** Begin Patch' '*** Update File: superRA/alpha/task.md' '@@' '-status: no-such-line' '+status: approved' '*** End Patch')
out=$(run_hook apply_patch "$(python3 -c 'import json,sys; print(json.dumps({"command":sys.argv[1]}))' "$patch")")
expect 'Unreconstructable approval patch fails closed' deny "$out"

write_task revise '> [ADVISORY] Consider it.'
patch=$(printf '%s\n' '*** Begin Patch' '*** Update File: superRA/alpha/task.md' '@@' '-status: no-such-line' '+status: approved' '*** End Patch')
out=$(run_hook apply_patch "$(python3 -c 'import json,sys; print(json.dumps({"command":sys.argv[1]}))' "$patch")")
expect 'Unreconstructable patch without blocking notes passes' allow "$out"

# Bash in-place mutations are never reconstructable: conservative deny when the
# command sets `status: approved` and the file retains a blocker.
write_task revise '> [BLOCKING] Fix it.'
out=$(run_hook Bash "$(python3 -c 'import json,sys; print(json.dumps({"command":"sed -i \"\" \"s/status: revise/status: approved/\" " + sys.argv[1]}))' "$task")")
expect 'Bash sed in-place approval flip is denied' deny "$out"

write_task revise '> [BLOCKING] Fix it.'
out=$(run_hook Bash "$(python3 -c 'import json,sys; print(json.dumps({"command":"printf \"status: approved\" > " + sys.argv[1]}))' "$task")")
expect 'Bash redirect approval flip is denied' deny "$out"

write_task revise '> [BLOCKING] Fix it.'
out=$(run_hook Bash "$(python3 -c 'import json,sys; print(json.dumps({"command":"perl -pi -e \"s/status: revise/status: approved/\" " + sys.argv[1]}))' "$task")")
expect 'Bash perl clustered -pi approval flip is denied' deny "$out"

write_task revise '> [ADVISORY] Consider it.'
out=$(run_hook Bash "$(python3 -c 'import json,sys; print(json.dumps({"command":"sed -i \"\" \"s/status: revise/status: approved/\" " + sys.argv[1]}))' "$task")")
expect 'Bash approval flip without blocking notes passes' allow "$out"

write_task revise '> [BLOCKING] Fix it.'
out=$(run_hook Bash "$(python3 -c 'import json,sys; print(json.dumps({"command":"sed -i \"\" \"s/Test./Tested./\" " + sys.argv[1]}))' "$task")")
expect 'Bash mutation without approval flip passes' allow "$out"

codex_command=$(python3 - "$REPO_ROOT/hooks/hooks-codex.json" <<'PY'
import json, sys
groups = json.load(open(sys.argv[1]))["hooks"]["PreToolUse"]
for group in groups:
    for hook in group.get("hooks", []):
        if "guard-task-approval" in hook.get("command", ""):
            print(hook["command"])
            raise SystemExit
raise SystemExit("guard-task-approval command missing")
PY
)
write_task revise '> [BLOCKING] Fix it.'
patch=$(printf '%s\n' '*** Begin Patch' '*** Update File: superRA/alpha/task.md' '@@' '-status: revise' '+status: approved' '*** End Patch')
payload=$(python3 -c 'import json,sys; print(json.dumps({"cwd":sys.argv[1],"hook_event_name":"PreToolUse","tool_name":"apply_patch","tool_input":{"command":sys.argv[2]}}))' "$project" "$patch")
out=$(cd "$project" && PLUGIN_ROOT="$REPO_ROOT" /bin/sh -c "$codex_command" <<EOF
$payload
EOF
)
expect 'Codex manifest executes the approval gate' deny "$out"

python3 - "$REPO_ROOT" <<'PY'
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
for name, matcher in (("hooks.json", "Edit|Write|Bash"), ("hooks-codex.json", "Edit|Write|Bash|apply_patch")):
    groups = json.loads((root / "hooks" / name).read_text())["hooks"]["PreToolUse"]
    assert any(
        group.get("matcher") == matcher
        and any("guard-task-approval" in hook.get("command", "") for hook in group.get("hooks", []))
        for group in groups
    ), name
cursor = json.loads((root / "hooks/hooks-cursor.json").read_text())
assert any("guard-task-approval" in hook["command"] for hook in cursor["hooks"]["preToolUse"])
PY
printf 'PASS  hook registries cover Claude, Codex, and Cursor\n'
