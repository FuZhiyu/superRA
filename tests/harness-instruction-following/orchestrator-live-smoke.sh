#!/usr/bin/env bash
# Opt-in live smoke for superimplement orchestrator dispatch behavior.
#
# Drives the main agent through `superimplement` on the smallest realistic mock
# frontier (the seeded bundle-two-tasks fixture) and asserts structural evidence
# that it followed the documented dispatch path — implementer subagent dispatch
# for the frontier, then a reviewer subagent dispatch — instead of silently
# implementing inline.
#
# Manual-only. Gated behind RUN_LIVE_HARNESS=1; a bare invocation in CI is a
# documented no-op. Requires a logged-in CLI and a model turn budget. Pick the
# harness with HARNESS=claude (default) or HARNESS=codex.
#
#   RUN_LIVE_HARNESS=1 bash tests/harness-instruction-following/orchestrator-live-smoke.sh
#   RUN_LIVE_HARNESS=1 HARNESS=codex bash tests/harness-instruction-following/orchestrator-live-smoke.sh
#
# Model: CLAUDE_MODEL (default haiku) for Claude; CODEX_MODEL (no canonical
# cheapest model in this repo) for Codex.
#
# --include-hook-events (audited): a real, documented `claude -p` flag (confirmed
# in CLI 2.1.183 `--help`: "Include all hook lifecycle events in the output
# stream"). It surfaces hook lifecycle events (e.g. the UserPromptSubmit
# autoloads) into the stream — not a no-op — but does not make filesystem
# PreToolUse hooks fire under `claude -p`. Kept for debugging visibility; this
# smoke keys off Task/Agent dispatch tool events, not the hook events.
#
# Harness-evidence limitation: dispatch evidence is structural, never prose
# claims. Claude exposes subagent dispatch as Task/Agent tool events carrying a
# subagent_type; Codex exposes it as spawn_agent(agent_type="superra_implementer"
# / "superra_reviewer"). The shared check_orchestrator_dispatches keys off those
# event shapes. If a harness cannot expose subagent dispatch events at all, the
# evaluator records the documented direct-mode fallback (the agent naming direct
# mode plus a reviewer dispatch) and the smoke passes-with-skip rather than
# failing on invisible behavior. A main agent that silently implements inline
# with neither dispatch events nor a documented fallback fails the smoke.

set -uo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=tests/harness-instruction-following/live_smoke_lib.sh
source "$LIB_DIR/live_smoke_lib.sh"

require_live_gate RUN_LIVE_HARNESS
require_cmd python3

HARNESS="${HARNESS:-claude}"
echo "harness:    $HARNESS"

TMPROOT="$(mktemp -d)"
CODEX_PROFILE_FILE=""
cleanup() {
  local rc=$?
  [ -n "${CODEX_PROFILE_FILE:-}" ] && [ -f "$CODEX_PROFILE_FILE" ] && rm -f "$CODEX_PROFILE_FILE"
  if [ "${KEEP_TMPROOT:-0}" = 1 ] && [ $rc -ne 0 ]; then
    echo "keeping temp root for failed orchestrator smoke: $TMPROOT" >&2
  elif [ -n "${TMPROOT:-}" ] && [ -d "$TMPROOT" ]; then
    rm -rf "$TMPROOT"
  fi
  exit $rc
}
trap cleanup EXIT INT TERM

WORKSPACE="$TMPROOT/ws"
mkdir -p "$WORKSPACE"
seed_workspace "$WORKSPACE"

OUT="$TMPROOT/orchestrator.transcript"
PROMPT="$(orchestrator_prompt)"

if [ "$HARNESS" = claude ]; then
  require_cmd claude
  CLAUDE_MODEL="${CLAUDE_MODEL:-haiku}"
  echo "claude CLI: $(claude --version 2>/dev/null | awk '{print $1}')"
  echo "model:      $CLAUDE_MODEL"
  echo
  SID="$(uuidgen 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo "smoke-$$")"
  ( cd "$WORKSPACE" && \
    claude -p "$PROMPT" \
      --session-id "$SID" \
      --model "$CLAUDE_MODEL" \
      --include-hook-events \
      --output-format=stream-json \
      --verbose \
      --plugin-dir "$REPO_ROOT" \
      --no-session-persistence \
      --permission-mode acceptEdits \
      </dev/null >"$OUT" 2>&1 )
  rc=$?
elif [ "$HARNESS" = codex ]; then
  require_cmd codex
  echo "codex CLI: $(codex --version 2>/dev/null)"
  echo "model:     ${CODEX_MODEL:-<codex default>}"
  echo
  CODEX_PROFILE_NAME="superra-orchestrator-smoke-$$"
  CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
  CODEX_PROFILE_FILE="$CODEX_HOME_DIR/${CODEX_PROFILE_NAME}.config.toml"
  mkdir -p "$CODEX_HOME_DIR"
  # Codex JSONL hides spawn_agent, so dispatch is observed out-of-band via a
  # SubagentStart hook (matcher = agent type) that appends each dispatched agent
  # type to this log. This supersedes JSONL-based dispatch detection for the
  # codex orchestrator path; the claude path still keys off Task/Agent events.
  SUBAGENT_LOG="$TMPROOT/codex-dispatch.log"
  : >"$SUBAGENT_LOG"
  python3 - "$REPO_ROOT" "$CODEX_PROFILE_FILE" "$LIB_DIR/subagent_start_hook.py" "$SUBAGENT_LOG" <<'PY'
import sys
repo, out, hook_script, subagent_log = sys.argv[1:5]

def cmd(name):
    return (
        f'env PLUGIN_ROOT="{repo}" CLAUDE_PLUGIN_ROOT="{repo}" '
        f'/bin/sh "{repo}/hooks/run-hook.cmd" {name}'
    )

def subagent_cmd():
    # Run the SubagentStart hook directly (it is a PEP 723-free stdlib script),
    # passing the dispatch-log path via env. The payload arrives on stdin.
    return f'env SUPERRA_SUBAGENT_LOG="{subagent_log}" python3 "{hook_script}"'

def toml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'

with open(out, "w", encoding="utf-8") as f:
    f.write("[[hooks.UserPromptSubmit]]\n")
    f.write("[[hooks.UserPromptSubmit.hooks]]\n")
    f.write('type = "command"\n')
    f.write(f"command = {toml_string(cmd('autoload-superra'))}\n\n")
    # One SubagentStart hook per agent type (matcher = agent type). The hook
    # disambiguates by the agent-type payload field, not session_id.
    for agent_type in ("superra_implementer", "superra_reviewer"):
        f.write("[[hooks.SubagentStart]]\n")
        f.write(f'matcher = "{agent_type}"\n')
        f.write("[[hooks.SubagentStart.hooks]]\n")
        f.write('type = "command"\n')
        f.write(f"command = {toml_string(subagent_cmd())}\n\n")
PY
  MODEL_ARGS=()
  if [ -n "${CODEX_MODEL:-}" ]; then
    MODEL_ARGS=(--model "$CODEX_MODEL")
  fi
  codex --profile "$CODEX_PROFILE_NAME" \
    --dangerously-bypass-hook-trust \
    --ask-for-approval never \
    --sandbox workspace-write \
    "${MODEL_ARGS[@]+"${MODEL_ARGS[@]}"}" \
    exec \
    --json \
    --ephemeral \
    --skip-git-repo-check \
    -C "$WORKSPACE" \
    "$PROMPT" >"$OUT" 2>&1
  rc=$?
else
  echo "FAIL: unknown HARNESS=$HARNESS (use claude or codex)" >&2
  exit 2
fi

if [ $rc -ne 0 ]; then
  echo "FAIL: $HARNESS exec exited $rc" >&2
  tail -n 80 "$OUT" >&2
  exit 1
fi

CHECK_ARGS=(--harness "$HARNESS" --transcript "$OUT")
if [ "$HARNESS" = codex ]; then
  CHECK_ARGS+=(--dispatch-log "$SUBAGENT_LOG")
fi
python3 "$LIB_DIR/check_orchestrator_smoke.py" "${CHECK_ARGS[@]}"
