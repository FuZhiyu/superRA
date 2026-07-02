#!/usr/bin/env bash
# Opt-in Codex live smoke for agent-loading instruction-following.
#
# Runs the same bundled `bundle-two-tasks` mock task used by the Claude smoke
# through the cheapest configurable Codex path, then asserts structural evidence
# that the agent ran both `superra task read` calls and read all three marker
# files BEFORE writing the evidence artifact, and compares the artifact to the
# committed expected shape.
#
# Manual-only. Gated behind RUN_LIVE_HARNESS=1; a bare invocation in CI is a
# documented no-op. Requires a logged-in `codex` CLI and a model turn budget.
#
#   RUN_LIVE_HARNESS=1 bash tests/harness-instruction-following/codex-live-smoke.sh
#
# Model: uses CODEX_MODEL when set (passed via `--model`). This repo does not
# currently prescribe a canonical cheapest Codex model; with no override the
# script uses the Codex CLI default.
#
# Harness-evidence limitation: Codex JSONL exposes command_execution and
# file_change items. Task reads surface as command_execution events running
# `superra task read <path>`; marker reads surface either as a read command or a
# file_change-free read item. The shared parser keys task-read detection off the
# command string and marker reads off read-tool / read-command events, which is
# the strongest available observable. Codex JSONL does not emit a structural
# skill-load event tied to the manifest by name, so manifest/role-surface load
# expectations stay covered by the CI-safe contract tests, and subagent dispatch
# is covered by the orchestrator smoke. This smoke isolates all Codex-specific
# profile/hook setup in the temporary profile below.

set -uo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=tests/harness-instruction-following/live_smoke_lib.sh
source "$LIB_DIR/live_smoke_lib.sh"

require_live_gate RUN_LIVE_HARNESS
require_cmd codex
require_cmd python3

echo "codex CLI: $(codex --version 2>/dev/null)"
echo "model:     ${CODEX_MODEL:-<codex default>}"
echo

TMPROOT="$(mktemp -d)"
CODEX_PROFILE_NAME="superra-live-smoke-$$"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
CODEX_PROFILE_FILE="$CODEX_HOME_DIR/${CODEX_PROFILE_NAME}.config.toml"
cleanup() {
  local rc=$?
  [ -n "${CODEX_PROFILE_FILE:-}" ] && [ -f "$CODEX_PROFILE_FILE" ] && rm -f "$CODEX_PROFILE_FILE"
  if [ "${KEEP_TMPROOT:-0}" = 1 ] && [ $rc -ne 0 ]; then
    echo "keeping temp root for failed Codex live smoke: $TMPROOT" >&2
  elif [ -n "${TMPROOT:-}" ] && [ -d "$TMPROOT" ]; then
    rm -rf "$TMPROOT"
  fi
  exit $rc
}
trap cleanup EXIT INT TERM

# Temporary Codex profile installing the superRA hooks (autoload + task-hook),
# matching hooks/hooks-codex.json against the in-tree scripts. Isolated to this
# script per the Codex-specific-setup constraint.
mkdir -p "$CODEX_HOME_DIR"
python3 - "$REPO_ROOT" "$CODEX_PROFILE_FILE" <<'PY'
import sys
repo, out = sys.argv[1], sys.argv[2]

def cmd(name, empty_json=False):
    prefix = "export SUPERRA_TASK_HOOK_EMPTY_JSON=1; " if empty_json else ""
    return (
        f'{prefix}env PLUGIN_ROOT="{repo}" CLAUDE_PLUGIN_ROOT="{repo}" '
        f'/bin/sh "{repo}/hooks/run-hook.cmd" {name}'
    )

def toml_string(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'

with open(out, "w", encoding="utf-8") as f:
    f.write("[[hooks.UserPromptSubmit]]\n")
    f.write("[[hooks.UserPromptSubmit.hooks]]\n")
    f.write('type = "command"\n')
    f.write(f"command = {toml_string(cmd('autoload-superra'))}\n\n")
    f.write("[[hooks.PostToolUse]]\n")
    f.write('matcher = "Edit|Write"\n')
    f.write("[[hooks.PostToolUse.hooks]]\n")
    f.write('type = "command"\n')
    f.write(f"command = {toml_string(cmd('task-hook', empty_json=True))}\n")
PY

WORKSPACE="$TMPROOT/ws"
mkdir -p "$WORKSPACE"
seed_workspace "$WORKSPACE"

OUT="$TMPROOT/codex.jsonl"
PROMPT="$(smoke_task_prompt)"

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
if [ $rc -ne 0 ]; then
  echo "FAIL: codex exec exited $rc" >&2
  tail -n 80 "$OUT" >&2
  exit 1
fi

python3 "$LIB_DIR/check_loading_smoke.py" \
  --harness codex \
  --transcript "$OUT" \
  --artifact "$WORKSPACE/loading-evidence.json" \
  --expected "$(expected_artifact_path)"
