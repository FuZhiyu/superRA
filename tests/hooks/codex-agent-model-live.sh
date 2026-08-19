#!/usr/bin/env bash
# Opt-in Codex CLI smoke for generic-agent model enforcement.

set -uo pipefail

if [ "${RUN_LIVE_HARNESS:-0}" != 1 ]; then
  echo "RUN_LIVE_HARNESS=1 is required" >&2
  exit 2
fi

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMPROOT=$(mktemp -d)
PROFILE_NAME="superra-agent-model-$$"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
PROFILE_FILE="$CODEX_HOME_DIR/${PROFILE_NAME}.config.toml"
CAPTURE_LOG="$TMPROOT/pretooluse.jsonl"
START_LOG="$TMPROOT/subagent-start.log"
OUT="$TMPROOT/codex.jsonl"

cleanup() {
  local rc=$?
  [ -f "$PROFILE_FILE" ] && rm -f "$PROFILE_FILE"
  if [ "${KEEP_TMPROOT:-0}" = 1 ] && [ $rc -ne 0 ]; then
    echo "keeping failed Codex model-hook run at $TMPROOT" >&2
  else
    rm -rf "$TMPROOT"
  fi
  exit $rc
}
trap cleanup EXIT INT TERM

mkdir -p "$CODEX_HOME_DIR"
python3 - "$REPO_ROOT" "$PROFILE_FILE" "$CAPTURE_LOG" "$START_LOG" <<'PY'
import sys

repo, profile, capture, starts = sys.argv[1:]

def quoted(value):
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'

capture_cmd = f'env AGENT_MODEL_CAPTURE_LOG={quoted(capture)} python3 {quoted(repo + "/tests/hooks/codex-agent-model-capture.py")}'
start_cmd = f'env SUPERRA_SUBAGENT_LOG={quoted(starts)} python3 {quoted(repo + "/tests/harness-instruction-following/subagent_start_hook.py")}'
with open(profile, "w", encoding="utf-8") as f:
    f.write("[[hooks.PreToolUse]]\nmatcher = \"Agent\"\n")
    f.write("[[hooks.PreToolUse.hooks]]\ntype = \"command\"\n")
    f.write("command = " + quoted(capture_cmd) + "\n\n")
    f.write("[[hooks.SubagentStart]]\nmatcher = \"default\"\n")
    f.write("[[hooks.SubagentStart.hooks]]\ntype = \"command\"\n")
    f.write("command = " + quoted(start_cmd) + "\n")
PY

PROMPT='Call spawn_agent to ask it to reply ready. On the first call, set fork_turns=none and omit agent_type, model, and reasoning_effort. After the hook denies it, retry with fork_turns=none, agent_type=default, model=gpt-5.6-luna, and reasoning_effort=low. Wait for the agent and make no file changes.'

codex --profile "$PROFILE_NAME" \
  --dangerously-bypass-hook-trust \
  --ask-for-approval never \
  --sandbox workspace-write \
  exec --json --ephemeral -C "$REPO_ROOT" "$PROMPT" >"$OUT" 2>&1
rc=$?
if [ $rc -ne 0 ]; then
  tail -n 80 "$OUT" >&2
  exit $rc
fi

python3 - "$CAPTURE_LOG" "$START_LOG" <<'PY'
import json
from pathlib import Path
import sys

capture_path = Path(sys.argv[1])
start_path = Path(sys.argv[2])
payloads = [json.loads(line) for line in capture_path.read_text(encoding="utf-8").splitlines() if line.strip()] if capture_path.exists() else []
inputs = [p.get("tool_input", {}) for p in payloads if p.get("tool_name") == "spawn_agent"]
generic = [i for i in inputs if i.get("agent_type") in (None, "", "default")]
denied = [i for i in generic if not str(i.get("model", "")).strip() or not str(i.get("reasoning_effort", "")).strip()]
allowed = [i for i in generic if str(i.get("model", "")).strip() and str(i.get("reasoning_effort", "")).strip()]
starts = [line for line in start_path.read_text(encoding="utf-8").splitlines() if line.strip()] if start_path.exists() else []
if not payloads and len(starts) == 1:
    print("LIMITATION Codex did not route spawn_agent through PreToolUse(Agent); SubagentStart still fired")
    print(json.dumps({"start": starts[0], "pretooluse_payloads": 0}, sort_keys=True))
    raise SystemExit(3)
if not denied or not allowed or len(starts) != 1:
    raise SystemExit(f"missing live evidence: denied={denied!r} allowed={allowed!r} starts={starts!r}")
top_model = next(p.get("model") for p in payloads if p.get("tool_name") == "spawn_agent")
print(f"PASS Codex live model guard: denied={len(denied)} allowed={len(allowed)} starts={len(starts)} top_model={top_model}")
print(json.dumps({"denied": denied[0], "allowed": allowed[-1], "start": starts[-1], "top_level_model": top_model}, sort_keys=True))
PY
