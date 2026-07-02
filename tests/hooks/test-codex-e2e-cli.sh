#!/usr/bin/env bash
# Optional Codex CLI smoke test for hook runtime wiring.
#
# This is intentionally not part of default test runs: it requires a logged-in
# Codex CLI and spends model turns. It installs hooks matching
# hooks/hooks-codex.json through a temporary Codex profile using the in-tree
# superRA scripts, then checks Codex JSONL and filesystem state for hook effects.
#
# Run from repo root:
#   bash tests/hooks/test-codex-e2e-cli.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

if ! command -v codex >/dev/null 2>&1; then
  echo "FAIL: codex CLI not on PATH" >&2
  exit 2
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "FAIL: python3 not on PATH" >&2
  exit 2
fi

TMPROOT=$(mktemp -d)
CODEX_PROFILE_NAME="superra-e2e-hooks-$$"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
CODEX_PROFILE_FILE="$CODEX_HOME_DIR/${CODEX_PROFILE_NAME}.config.toml"
cleanup() {
  local rc=$?
  [ -n "${CODEX_PROFILE_FILE:-}" ] && [ -f "$CODEX_PROFILE_FILE" ] && rm -f "$CODEX_PROFILE_FILE"
  if [ "${KEEP_TMPROOT:-0}" = 1 ] && [ $rc -ne 0 ]; then
    echo "keeping temp root for failed Codex E2E run: $TMPROOT" >&2
  elif [ -n "${TMPROOT:-}" ] && [ -d "$TMPROOT" ]; then
    rm -rf "$TMPROOT"
  fi
  exit $rc
}
trap cleanup EXIT INT TERM

write_minimal_task_md() {
  local path="$1"
  local title="$2"
  local status="$3"
  mkdir -p "$(dirname "$path")"
  cat >"$path" <<EOF
---
title: $title
status: $status
depends_on: []
tags: []
created: 2026-06-17
---

## Objective

Runtime task-hook fixture.

## Results

(empty)
EOF
}

mkdir -p "$CODEX_HOME_DIR"
python3 - "$REPO_ROOT" "$CODEX_PROFILE_FILE" <<'PY'
import sys
repo, out = sys.argv[1], sys.argv[2]
def cmd(name, empty_json=False):
    prefix = "export SUPERRA_TASK_HOOK_EMPTY_JSON=1; " if empty_json else ""
    return f'{prefix}env PLUGIN_ROOT="{repo}" CLAUDE_PLUGIN_ROOT="{repo}" /bin/sh "{repo}/hooks/run-hook.cmd" {name}'

def toml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'

with open(out, "w", encoding="utf-8") as f:
    f.write("[[hooks.UserPromptSubmit]]\n")
    f.write("[[hooks.UserPromptSubmit.hooks]]\n")
    f.write('type = "command"\n')
    f.write(f"command = {toml_string(cmd('autoload-superra'))}\n\n")
    f.write("[[hooks.PreToolUse]]\n")
    f.write('matcher = "Bash"\n')
    f.write("[[hooks.PreToolUse.hooks]]\n")
    f.write('type = "command"\n')
    f.write(f"command = {toml_string(cmd('merge-guard'))}\n\n")
    f.write("[[hooks.PostToolUse]]\n")
    f.write('matcher = "Edit|Write"\n')
    f.write("[[hooks.PostToolUse.hooks]]\n")
    f.write('type = "command"\n')
    f.write(f"command = {toml_string(cmd('task-hook', empty_json=True))}\n\n")
    f.write("[[hooks.PostToolUse]]\n")
    f.write('matcher = "Bash"\n')
    f.write("[[hooks.PostToolUse.hooks]]\n")
    f.write('type = "command"\n')
    f.write(f"command = {toml_string(cmd('task-hook', empty_json=True))}\n\n")
    f.write("[[hooks.Stop]]\n")
    f.write("[[hooks.Stop.hooks]]\n")
    f.write('type = "command"\n')
    f.write(f"command = {toml_string(cmd('codex-plan-stop'))}\n")
PY

OUT="$TMPROOT/codex.jsonl"
PROMPT='superRA hook smoke test. Reply with exactly ok.'

codex --profile "$CODEX_PROFILE_NAME" \
  --dangerously-bypass-hook-trust \
  --ask-for-approval never \
  --sandbox workspace-write \
  exec \
  --json \
  --ephemeral \
  --skip-git-repo-check \
  -C "$TMPROOT" \
  "$PROMPT" >"$OUT" 2>&1
rc=$?
if [ $rc -ne 0 ]; then
  echo "FAIL: codex exec exited $rc" >&2
  tail -n 80 "$OUT" >&2
  exit 1
fi

if ! python3 - "$OUT" <<'PY'
import json, sys
path = sys.argv[1]
events = []
with open(path, encoding="utf-8") as f:
    for line in f:
        try:
            events.append(json.loads(line))
        except Exception:
            continue

def strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v)

all_text = "\n".join(s for event in events for s in strings(event))
checks = {
    "UserPromptSubmit reminder": "superRA:using-superra" in all_text,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("missing hook evidence: " + ", ".join(failed))
print("PASS Codex UserPromptSubmit hook evidence present")
PY
then
  exit 1
fi

mkdir -p "$TMPROOT/superRA/01-child"
write_minimal_task_md "$TMPROOT/superRA/task.md" "Codex Hook Root" "not-started"
write_minimal_task_md "$TMPROOT/superRA/01-child/task.md" "Codex Hook Child" "not-started"

TASK_OUT="$TMPROOT/codex-task-hook.jsonl"
TASK_PROMPT='Edit only superRA/01-child/task.md. Use the file edit/apply-patch tool, not a shell command, to change the frontmatter line `status: not-started` to `status: approved`. Do not edit any other file. Then reply with exactly ok.'

codex --profile "$CODEX_PROFILE_NAME" \
  --dangerously-bypass-hook-trust \
  --ask-for-approval never \
  --sandbox workspace-write \
  exec \
  --json \
  --ephemeral \
  --skip-git-repo-check \
  -C "$TMPROOT" \
  "$TASK_PROMPT" >"$TASK_OUT" 2>&1
rc=$?
if [ $rc -ne 0 ]; then
  echo "FAIL: codex exec task-hook run exited $rc" >&2
  tail -n 80 "$TASK_OUT" >&2
  exit 1
fi

if ! python3 - "$TASK_OUT" "$TMPROOT/superRA/task.md" "$TMPROOT/superRA/01-child/task.md" <<'PY'
import json, re, sys
from pathlib import Path

jsonl, root_md, child_md = sys.argv[1:]
events = []
with open(jsonl, encoding="utf-8") as f:
    for line in f:
        try:
            events.append(json.loads(line))
        except Exception:
            continue

def strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v)

def status(path):
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip()
    return ""

cwd = Path(root_md).parent.parent.resolve()

def task_rel(path_text):
    path = Path(path_text)
    if path.is_absolute():
        try:
            path = path.resolve().relative_to(cwd)
        except ValueError:
            return None
    rel = path.as_posix()
    if rel == "superRA/task.md":
        return rel
    if rel.startswith("superRA/") and rel.endswith("/task.md"):
        return rel
    return None

mutating_task_paths = []
has_child_file_change = False
shell_task_edits = []
for event in events:
    item = event.get("item") if isinstance(event, dict) else None
    if not isinstance(item, dict):
        continue
    if item.get("type") == "file_change":
        for change in item.get("changes", []) or []:
            rel = task_rel(str(change.get("path", "")))
            if rel is None:
                continue
            mutating_task_paths.append(rel)
            if rel == "superRA/01-child/task.md":
                has_child_file_change = True
    if item.get("type") == "command_execution":
        command = str(item.get("command", ""))
        if re.search(r"superRA/(?:[^\s`'\"),;]+/)?task\.md", command):
            shell_task_edits.append(command)
unique_mutating_task_paths = sorted(set(mutating_task_paths))

checks = {
    "child file_change event": has_child_file_change,
    "only child task edit event": unique_mutating_task_paths == ["superRA/01-child/task.md"],
    "no shell task edits": not shell_task_edits,
    "child task approved": status(child_md) == "approved",
    "root status propagated": status(root_md) == "approved",
    "dashboard not generated": not (Path(root_md).parent / "dashboard.html").exists(),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("missing task-hook evidence: " + ", ".join(failed))
print("PASS Codex task-hook PostToolUse evidence present")
PY
then
  exit 1
fi
