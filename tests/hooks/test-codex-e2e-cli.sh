#!/usr/bin/env bash
# Optional Codex CLI smoke test for hook runtime wiring.
#
# This is intentionally not part of default test runs: it requires a logged-in
# Codex CLI and spends model turns. It installs project-local hooks matching
# hooks/hooks-codex.json in a temp repo using the in-tree superRA scripts, then
# checks Codex JSONL for hook responses.
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
cleanup() {
  local rc=$?
  [ -n "${TMPROOT:-}" ] && [ -d "$TMPROOT" ] && rm -rf "$TMPROOT"
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

mkdir -p "$TMPROOT/.codex"
python3 - "$REPO_ROOT" "$TMPROOT/.codex/hooks.json" <<'PY'
import json, sys
repo, out = sys.argv[1], sys.argv[2]
def cmd(name, empty_json=False):
    prefix = "export SUPERRA_TASK_HOOK_EMPTY_JSON=1; " if empty_json else ""
    return f'{prefix}env PLUGIN_ROOT="{repo}" CLAUDE_PLUGIN_ROOT="{repo}" "{repo}/hooks/run-hook.cmd" {name}'
hooks = {
    "hooks": {
        "UserPromptSubmit": [
            {"hooks": [{"type": "command", "command": cmd("autoload-superra")}]}
        ],
        "PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": cmd("merge-guard")}]}
        ],
        "PostToolUse": [
            {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": cmd("task-hook", empty_json=True)}]},
            {"matcher": "Bash", "hooks": [{"type": "command", "command": cmd("task-hook", empty_json=True)}]},
        ],
        "Stop": [
            {"hooks": [{"type": "command", "command": cmd("codex-plan-stop")}]}
        ],
    }
}
with open(out, "w", encoding="utf-8") as f:
    json.dump(hooks, f, indent=2)
    f.write("\n")
PY

OUT="$TMPROOT/codex.jsonl"
PROMPT='superRA hook smoke test. First run this exact shell command: git merge main. If it fails, do not fix it. Then reply with exactly ok.'

(cd "$TMPROOT" && codex exec \
  --json \
  --ephemeral \
  --skip-git-repo-check \
  --dangerously-bypass-hook-trust \
  --ask-for-approval never \
  --sandbox workspace-write \
  "$PROMPT" >"$OUT" 2>&1)
rc=$?
if [ $rc -ne 0 ]; then
  echo "FAIL: codex exec exited $rc" >&2
  tail -n 80 "$OUT" >&2
  exit 1
fi

python3 - "$OUT" <<'PY'
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
    "merge-guard reminder": "superRA:semantic-merge" in all_text,
    "Stop hook observed": "Stop" in all_text,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("missing hook evidence: " + ", ".join(failed))
print("PASS Codex hook smoke evidence present")
PY

mkdir -p "$TMPROOT/superRA/01-child"
write_minimal_task_md "$TMPROOT/superRA/task.md" "Codex Hook Root" "not-started"
write_minimal_task_md "$TMPROOT/superRA/01-child/task.md" "Codex Hook Child" "not-started"

TASK_OUT="$TMPROOT/codex-task-hook.jsonl"
TASK_PROMPT='Edit only superRA/01-child/task.md. Use the file edit/apply-patch tool, not a shell command, to change the frontmatter line `status: not-started` to `status: approved`. Do not edit any other file. Then reply with exactly ok.'

(cd "$TMPROOT" && codex exec \
  --json \
  --ephemeral \
  --skip-git-repo-check \
  --dangerously-bypass-hook-trust \
  --ask-for-approval never \
  --sandbox workspace-write \
  "$TASK_PROMPT" >"$TASK_OUT" 2>&1)
rc=$?
if [ $rc -ne 0 ]; then
  echo "FAIL: codex exec task-hook run exited $rc" >&2
  tail -n 80 "$TASK_OUT" >&2
  exit 1
fi

python3 - "$TASK_OUT" "$TMPROOT/superRA/task.md" "$TMPROOT/superRA/01-child/task.md" <<'PY'
import json, sys
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

def dicts(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from dicts(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from dicts(v)

def status(path):
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip()
    return ""

edit_tools = ("apply_patch", "Edit", "Write")
event_text = [(event, list(strings(event))) for event in events]
has_post_tool_hook = any(
    any("PostToolUse" in s for s in values)
    for _event, values in event_text
)
has_task_edit_event = any(
    any("superRA/01-child/task.md" in s for s in strings(d))
    and (
        any(str(d.get(k, "")) in edit_tools for k in ("tool_name", "tool", "name"))
        or (
            "tool" in str(d.get("type", "")).lower()
            and any(name in s for s in strings(d) for name in edit_tools)
        )
    )
    for event in events
    for d in dicts(event)
)

checks = {
    "PostToolUse hook event": has_post_tool_hook,
    "task edit event": has_task_edit_event,
    "child task approved": status(child_md) == "approved",
    "root status propagated": status(root_md) == "approved",
    "dashboard not generated": not (Path(root_md).parent / "dashboard.html").exists(),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("missing task-hook evidence: " + ", ".join(failed))
print("PASS Codex task-hook PostToolUse evidence present")
PY
