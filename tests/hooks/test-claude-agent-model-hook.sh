#!/usr/bin/env bash
# Claude manifest wiring tests for the generic-agent model guard.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MANIFEST="$REPO_ROOT/hooks/hooks.json"

command=$(python3 - "$MANIFEST" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as f:
    hooks = json.load(f)["hooks"]["PreToolUse"]
matches = [
    hook["command"]
    for group in hooks
    if group.get("matcher") == "Agent"
    for hook in group.get("hooks", [])
    if "agent-model-guard" in hook.get("command", "")
]
if len(matches) != 1:
    raise SystemExit(f"expected one PreToolUse(Agent) model guard, found {len(matches)}")
print(matches[0])
PY
) || exit 1

run_manifest_hook() {
  env -i PATH="$PATH" HOME="$HOME" CLAUDE_PLUGIN_ROOT="$REPO_ROOT" /bin/sh -c "$command" <<<"$1"
}

payload() {
  python3 -c 'import json,sys; print(json.dumps({"hook_event_name":"PreToolUse","tool_name":"Agent","tool_input":json.loads(sys.argv[1])}))' "$1"
}

denied=$(run_manifest_hook "$(payload '{"subagent_type":"general-purpose","prompt":"probe"}')")
allowed=$(run_manifest_hook "$(payload '{"subagent_type":"general-purpose","model":"haiku","prompt":"probe"}')")
named=$(run_manifest_hook "$(payload '{"subagent_type":"superRA:implementer","prompt":"probe"}')")

python3 - "$denied" "$allowed" "$named" <<'PY'
import json
import sys

denied, allowed, named = map(json.loads, sys.argv[1:])
assert denied["hookSpecificOutput"]["permissionDecision"] == "deny", denied
assert allowed == {}, allowed
assert named == {}, named
print("PASS Claude PreToolUse(Agent) manifest wiring")
PY
