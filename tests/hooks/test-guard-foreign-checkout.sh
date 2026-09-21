#!/usr/bin/env bash
# Reproduction and regression tests for the cross-checkout isolation gate.
#
# Part 1 replays the 2026-08-02 escape in disposable repos: a session whose cwd
# is one checkout writes `## Results` into a *different* checkout's task tree and
# commits that checkout's in-flight diff. It asserts that the pre-existing gates
# and the PostToolUse reconcile hook all accept it silently — the escape had no
# guard, which is why it was only noticed in `git log`.
#
# Part 2 asserts the new gate stops both mutations — `ask`, so a researcher who
# set up cross-checkout work on purpose can approve — through every form that
# reaches a foreign directory. Part 3 asserts it stays out of the way of the work
# superRA actually does: a session's own task tree, sibling worktrees of its own
# repository, non-task files, and git in a foreign repo that is not a task-tree
# checkout.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
GUARD="$REPO_ROOT/hooks/guard-foreign-checkout"
APPROVAL_GUARD="$REPO_ROOT/hooks/guard-task-approval"
TASK_HOOK="$REPO_ROOT/skills/task-tree/scripts/task_hook.py"
TMPROOT=$(mktemp -d)
trap 'rm -rf "$TMPROOT"' EXIT INT TERM

GIT="git -c user.name=test -c user.email=test@example.com -c commit.gpgsign=false -c init.defaultBranch=main"

failures=0

make_task() {
  # make_task <dir> <title> <status>
  mkdir -p "$1"
  printf '%s\n' '---' "title: $2" "status: $3" 'depends_on: []' '---' '' \
    '## Objective' '' 'Do the thing.' '' '## Results' '' '(empty)' >"$1/task.md"
}

make_checkout() {
  # make_checkout <path> <task-slug>
  local root="$1" slug="$2"
  mkdir -p "$root"
  make_task "$root/superRA/$slug" "$slug" not-started
  (cd "$root" && $GIT init -q . && $GIT add -A && $GIT commit -qm "seed") >/dev/null
}

run_hook() {
  # run_hook <hook-path> <cwd> <tool_name> <tool_input-json>
  python3 -c '
import json, sys
print(json.dumps({
    "cwd": sys.argv[1],
    "hook_event_name": "PreToolUse",
    "tool_name": sys.argv[2],
    "tool_input": json.loads(sys.argv[3]),
}))
' "$2" "$3" "$4" | bash "$1"
}

edit_payload() {
  # edit_payload <file> <old> <new>
  python3 -c '
import json, sys
print(json.dumps({"file_path": sys.argv[1], "old_string": sys.argv[2], "new_string": sys.argv[3]}))
' "$1" "$2" "$3"
}

bash_payload() {
  python3 -c 'import json,sys; print(json.dumps({"command": sys.argv[1]}))' "$1"
}

expect() {
  # expect <name> <allow|ask|deny> <hook output>
  local name="$1" expected="$2" output="$3" actual="allow"
  if printf '%s' "$output" | grep -q '"permissionDecision":"ask"'; then
    actual="ask"
  elif printf '%s' "$output" | grep -q '"permissionDecision":"deny"'; then
    actual="deny"
  fi
  if [ "$actual" = "$expected" ] && printf '%s' "$output" | python3 -m json.tool >/dev/null 2>&1; then
    printf 'PASS  %s\n' "$name"
  else
    printf 'FAIL  %s (expected %s, got %s: %s)\n' "$name" "$expected" "$actual" "$output"
    failures=$((failures + 1))
  fi
}

assert() {
  # assert <name> <condition-exit-status-as-command...>
  local name="$1"; shift
  if "$@"; then
    printf 'PASS  %s\n' "$name"
  else
    printf 'FAIL  %s\n' "$name"
    failures=$((failures + 1))
  fi
}

session="$TMPROOT/session"      # the checkout the session was pointed at
victim="$TMPROOT/victim"        # the checkout it must not reach
plain="$TMPROOT/plain"          # a foreign repo with no task tree

make_checkout "$session" own-task
make_checkout "$victim" escaped-task
mkdir -p "$plain" && (cd "$plain" && $GIT init -q . && echo seed >file.txt && $GIT add -A && $GIT commit -qm seed) >/dev/null

victim_task="$victim/superRA/escaped-task/task.md"
# The victim checkout carries another agent's in-flight, uncommitted diff.
echo "work in progress" >"$victim/in-flight.txt"

# ---- Part 1: the escape, with the guard removed from the picture ------------

out=$(run_hook "$APPROVAL_GUARD" "$session" Edit "$(edit_payload "$victim_task" '(empty)' 'Escaped results: 105 passed.')")
expect 'reproduction: the approval gate does not see a foreign-checkout write' allow "$out"

python3 - "$victim_task" <<'PY'
import sys
from pathlib import Path
path = Path(sys.argv[1])
path.write_text(path.read_text().replace("(empty)", "Escaped results: 105 passed."))
PY

hook_out=$(python3 -c '
import json, sys
print(json.dumps({"tool_name": "Edit", "tool_input": {"file_path": sys.argv[1]}, "tool_response": {}}))
' "$victim_task" | (cd "$session" && python3 "$TASK_HOOK") 2>&1)
assert 'reproduction: the PostToolUse reconcile hook accepts the foreign tree silently' \
  test -z "$(printf '%s' "$hook_out" | grep -i 'foreign\|checkout' || true)"

(cd "$victim" && $GIT add -A && $GIT commit -qm "implement(escaped-task): DONE") >/dev/null
assert 'reproduction: the escape commits the victim checkout in-flight diff' \
  bash -c "cd '$victim' && git show --stat --name-only HEAD | grep -q in-flight.txt"

# Reset the victim to a clean, pre-escape state for the guard assertions.
(cd "$victim" && $GIT reset -q --hard HEAD~1 && $GIT clean -qfd) >/dev/null
echo "work in progress" >"$victim/in-flight.txt"

# ---- Part 2: the guard stops both halves of the escape ----------------------

out=$(run_hook "$GUARD" "$session" Edit "$(edit_payload "$victim_task" '(empty)' 'Escaped results.')")
expect 'asks on an Edit of a foreign checkout task.md' ask "$out"

out=$(run_hook "$GUARD" "$session" Write "$(python3 -c 'import json,sys; print(json.dumps({"file_path": sys.argv[1], "content": "x"}))' "$victim_task")")
expect 'asks on a Write of a foreign checkout task.md' ask "$out"

out=$(run_hook "$GUARD" "$session" Write "$(python3 -c 'import json,sys; print(json.dumps({"file_path": sys.argv[1], "content": "x"}))' "$victim/superRA/new-task/task.md")")
expect 'asks on a Write creating a task.md in a foreign checkout' ask "$out"

# Every form that points a shell or git at the foreign checkout.
out=$(run_hook "$GUARD" "$session" Bash "$(bash_payload "cd $victim && git add -A && git commit -m 'implement(x): DONE'")")
expect 'asks on a git commit redirected by cd' ask "$out"

out=$(run_hook "$GUARD" "$session" Bash "$(bash_payload "(cd $victim && git commit -am wip)")")
expect 'asks on a git commit inside a subshell' ask "$out"

out=$(run_hook "$GUARD" "$session" Bash "$(bash_payload "{ cd $victim && git commit -am wip; }")")
expect 'asks on a git commit inside a brace group' ask "$out"

out=$(run_hook "$GUARD" "$session" Bash "$(bash_payload "bash -c \"cd $victim && git commit -am wip\"")")
expect 'asks on a git commit inside a bash -c payload' ask "$out"

out=$(run_hook "$GUARD" "$session" Bash "$(bash_payload "git -C $victim commit -am wip")")
expect 'asks on git -C into a foreign task-tree checkout' ask "$out"

out=$(run_hook "$GUARD" "$session" Bash "$(bash_payload "git --git-dir=$victim/.git --work-tree=$victim commit -am wip")")
expect 'asks on git --git-dir/--work-tree into a foreign task-tree checkout' ask "$out"

out=$(run_hook "$GUARD" "$TMPROOT/nowhere" Edit "$(edit_payload "$victim_task" '(empty)' 'x')")
expect 'asks on a foreign task.md write from a session with no repository' ask "$out"

# A `cd` earlier in the session can move the payload cwd into the foreign
# checkout; CLAUDE_PROJECT_DIR is the anchor that cannot drift.
out=$(CLAUDE_PROJECT_DIR="$session" run_hook "$GUARD" "$victim" Edit "$(edit_payload "$victim_task" '(empty)' 'x')")
expect 'asks on a foreign task.md write when the payload cwd has drifted' ask "$out"

assert 'the victim checkout keeps its in-flight diff uncommitted' \
  bash -c "cd '$victim' && git status --porcelain | grep -q in-flight.txt"

# ---- Part 3: the guard stays out of the way --------------------------------

out=$(run_hook "$GUARD" "$session" Edit "$(edit_payload "$session/superRA/own-task/task.md" '(empty)' 'Real results.')")
expect 'permits an Edit of the session own task tree' allow "$out"

worktree="$TMPROOT/worktrees/parallel"
(cd "$session" && $GIT worktree add -q -b parallel "$worktree") >/dev/null 2>&1
out=$(run_hook "$GUARD" "$session" Edit "$(edit_payload "$worktree/superRA/own-task/task.md" '(empty)' 'Worktree results.')")
expect 'permits an Edit in a sibling worktree of the session repository' allow "$out"

out=$(run_hook "$GUARD" "$session" Bash "$(bash_payload "cd $worktree && git add -A && git commit -m 'implement(x): DONE'")")
expect 'permits a commit in a sibling worktree of the session repository' allow "$out"

out=$(run_hook "$GUARD" "$session" Bash "$(bash_payload "(cd $worktree && git commit -am wip)")")
expect 'permits a subshell commit in a sibling worktree' allow "$out"

out=$(run_hook "$GUARD" "$session" Write "$(python3 -c 'import json,sys; print(json.dumps({"file_path": sys.argv[1], "content": "x"}))' "$victim/notes.md")")
expect 'permits a non-task file write outside the session checkout' allow "$out"

out=$(run_hook "$GUARD" "$session" Bash "$(bash_payload "cd $plain && git commit -am wip")")
expect 'permits git in a foreign repository that is not a task-tree checkout' allow "$out"

out=$(run_hook "$GUARD" "$session" Bash "$(bash_payload "bash -c \"cd $plain && git commit -am wip\"")")
expect 'permits a bash -c commit in a foreign repository with no task tree' allow "$out"

out=$(run_hook "$GUARD" "$session" Bash "$(bash_payload "cd $victim && git status && git log --oneline -3")")
expect 'permits read-only git in a foreign task-tree checkout' allow "$out"

out=$(run_hook "$GUARD" "$session" Bash "$(bash_payload "cd $victim && ls superRA")")
expect 'permits a non-git command in a foreign checkout' allow "$out"

if [ "$failures" -eq 0 ]; then
  printf '\nAll checks passed.\n'
  exit 0
fi
printf '\n%s check(s) failed.\n' "$failures"
exit 1
