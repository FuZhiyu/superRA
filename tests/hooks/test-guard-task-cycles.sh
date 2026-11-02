#!/usr/bin/env bash
# Regression tests for the task-level cycle gate.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOOK="$REPO_ROOT/hooks/guard-task-cycles"
TMPROOT=$(mktemp -d)
trap 'rm -rf "$TMPROOT"' EXIT INT TERM

project="$TMPROOT/project"
failures=0

write_task() {
  local name="$1" task_status="$2" depends="$3" steps="$4"
  mkdir -p "$project/superRA/$name"
  {
    printf '%s\n' '---' "title: $name" "status: $task_status" "depends_on: $depends" '---' '' \
      '## Objective' '' 'Test.' '' '## Reproduction' '' '```yaml' 'steps:'
    printf '%s\n' "$steps"
    printf '%s\n' '```'
  } >"$project/superRA/$name/task.md"
}

step() { printf '  - name: %s\n    cmd: "true"\n    deps: [%s]\n    outs: [%s]' "$1" "$2" "$3"; }

a1=$(step a1 '' a1.txt)
a2=$(step a2 b1.txt a2.txt)
a3=$(step a3 b1.txt a3.txt)
b1=$(step b1 a1.txt b1.txt)

reset_one_way() {
  rm -rf "$project"
  write_task a not-started '[]' "$a1"
  write_task b not-started '[]' "$b1"
}

# Guards the fixture itself: a step the parser rejects would make every case vacuous.
expect_steps() {
  local actual
  actual=$(PYTHONPATH="$REPO_ROOT/skills/task-tree/scripts" python3 -c '
import sys
from pathlib import Path
from _repro import build_graph
print(sorted(step.name for step in build_graph(Path(sys.argv[1]), resolve_vars=False).steps))
' "$project/superRA")
  if [ "$actual" = "$1" ]; then
    printf 'PASS  fixture registers %s\n' "$1"
  else
    printf 'FAIL  fixture registers %s, expected %s\n' "$actual" "$1"
    failures=$((failures + 1))
  fi
}

reset_looped() {
  rm -rf "$project"
  write_task a not-started '[]' "$a1
$a2"
  write_task b not-started '[]' "$b1"
}

payload() {
  python3 -c '
import json, sys
print(json.dumps({"cwd": sys.argv[1], "hook_event_name": "PreToolUse",
                  "tool_name": sys.argv[2], "tool_input": json.loads(sys.argv[3])}))
' "$project" "$1" "$2"
}

run_hook() { payload "$1" "$2" | bash "$HOOK"; }

edit_input() {
  python3 -c 'import json,sys; print(json.dumps({"file_path":sys.argv[1],"old_string":sys.argv[2],"new_string":sys.argv[3]}))' "$1" "$2" "$3"
}

expect() {
  local name="$1" expected="$2" output="$3" needle="${4:-}"
  local actual="allow"
  printf '%s' "$output" | grep -q '"permissionDecision":"deny"' && actual="deny"
  if [ "$actual" = "$expected" ] && printf '%s' "$output" | python3 -m json.tool >/dev/null 2>&1 \
    && { [ -z "$needle" ] || printf '%s' "$output" | grep -qF -- "$needle"; }; then
    printf 'PASS  %s\n' "$name"
  else
    printf 'FAIL  %s (expected %s, got %s: %s)\n' "$name" "$expected" "$actual" "$output"
    failures=$((failures + 1))
  fi
}

reset_one_way
expect_steps "['a1', 'b1']"
task="$project/superRA/a/task.md"
out=$(run_hook Edit "$(edit_input "$task" "$a1" "$a1
$a2")")
expect 'Edit adding a step that closes a loop is denied' deny "$out" 'task cycle at (root): b -> a -> b'
expect 'The denial marks the edge the edit adds' deny "$out" 'b -> a by b1.txt (new edge)'
expect 'The denial says how to restructure' deny "$out" 'make this boundary one-way'

reset_one_way
out=$(run_hook Edit "$(edit_input "$task" 'depends_on: []' 'depends_on: [b]')")
expect 'Edit adding a depends_on against the file flow is denied' deny "$out" 'task-level cycle'

reset_one_way
text=$(python3 -c 'import sys; print(open(sys.argv[1]).read().replace(sys.argv[2], sys.argv[2] + "\n" + sys.argv[3]))' "$task" "$a1" "$a2")
out=$(run_hook Write "$(python3 -c 'import json,sys; print(json.dumps({"file_path":sys.argv[1],"content":sys.argv[2]}))' "$task" "$text")")
expect 'Write that closes a loop is denied' deny "$out" 'task-level cycle'

reset_one_way
write_task a not-started '[]' "$a1
$(step a4 c.txt a4.txt)"
text=$(printf '%s\n' '---' 'title: c' 'status: not-started' 'depends_on: []' '---' '' '## Reproduction' '' '```yaml' 'steps:' "$(step c1 b1.txt c.txt)" '```')
out=$(run_hook Write "$(python3 -c 'import json,sys; print(json.dumps({"file_path":sys.argv[1],"content":sys.argv[2]}))' "$project/superRA/c/task.md" "$text")")
expect 'Write of a new task that closes a loop is denied' deny "$out" 'task-level cycle'

reset_one_way
write_task b archived '[]' "$b1"
write_task a not-started '[]' "$a1
$a2"
out=$(run_hook Edit "$(edit_input "$project/superRA/b/task.md" 'status: archived' 'status: not-started')")
expect 'Un-archiving a task that closes a loop is denied' deny "$out" 'task-level cycle'

reset_looped
expect_steps "['a1', 'a2', 'b1']"
out=$(run_hook Edit "$(edit_input "$task" "$a2" "$a2
$a3")")
expect 'Edit inside an existing loop passes' allow "$out"

reset_looped
out=$(run_hook Edit "$(edit_input "$task" 'Test.' 'Reworded.')")
expect 'Edit outside the graph inputs passes' allow "$out"

reset_looped
out=$(run_hook Edit "$(edit_input "$task" "$a1
$a2" "$a1")")
expect 'Edit that shrinks a loop passes' allow "$out"

reset_one_way
out=$(run_hook Edit "$(edit_input "$task" 'never in this file' 'x')")
expect 'Edit that cannot be reconstructed passes' allow "$out"

out=$(run_hook Edit "$(edit_input "$project/Code/task.md" 'x' 'y')")
expect 'A task.md outside a task root passes' allow "$out"

out=$(printf 'not json' | bash "$HOOK")
expect 'Malformed input passes' allow "$out"

reset_one_way
out=$(run_hook Edit "$(edit_input "$task" 'status: not-started' 'status: [unterminated')")
expect 'A status the parser rejects passes' allow "$out"

reset_one_way
git -C "$project" init -q
git_dir=$(git -C "$project" rev-parse --absolute-git-dir)
: >"$git_dir/MERGE_HEAD"
out=$(run_hook Edit "$(edit_input "$task" "$a1" "$a1
$a2")")
expect 'A merge in progress passes' allow "$out"
rm -f "$git_dir/MERGE_HEAD"

codex_command=$(python3 - "$REPO_ROOT/hooks/hooks-codex.json" <<'PY'
import json, sys
for group in json.load(open(sys.argv[1]))["hooks"]["PreToolUse"]:
    for hook in group.get("hooks", []):
        if "guard-task-cycles" in hook.get("command", ""):
            print(hook["command"])
            raise SystemExit
raise SystemExit("guard-task-cycles command missing")
PY
)
reset_one_way
added=$(printf '%s\n' "$a2" | sed 's/^/+/')
patch=$(printf '%s\n' '*** Begin Patch' '*** Update File: superRA/a/task.md' '@@' '     outs: [a1.txt]' "$added" '*** End Patch')
input=$(payload apply_patch "$(python3 -c 'import json,sys; print(json.dumps({"command":sys.argv[1]}))' "$patch")")
out=$(cd "$project" && PLUGIN_ROOT="$REPO_ROOT" /bin/sh -c "$codex_command" <<EOF
$input
EOF
)
expect 'Codex manifest denies an apply_patch that closes a loop' deny "$out" 'task-level cycle'

python3 - "$REPO_ROOT" <<'PY' || failures=$((failures + 1))
import json, sys
from pathlib import Path

root = Path(sys.argv[1])
for name, matcher in (("hooks.json", "Edit|Write"), ("hooks-codex.json", "Edit|Write|apply_patch")):
    groups = json.loads((root / "hooks" / name).read_text())["hooks"]["PreToolUse"]
    assert any(
        group.get("matcher") == matcher
        and any("guard-task-cycles" in hook.get("command", "") for hook in group.get("hooks", []))
        for group in groups
    ), name
PY
printf 'PASS  hook registries cover Claude and Codex\n'

exit "$failures"
