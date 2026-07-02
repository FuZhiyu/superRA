#!/usr/bin/env bash
# Opt-in Codex always-loaded skill canary smoke (task 10).
#
# Codex has no skill autoload, so the always-loaded skills (`superRA:using-superra`
# and `superRA:report-in-markdown`) reach context only if the agent follows the
# role-spec body-load instruction. This smoke drives a real Codex agent through
# the `always-loaded-canary` fixture and asserts each always-loaded skill emitted
# its skill-unique canary (report-in-markdown: runs its own `check_markdown.py`;
# using-superra: the `superra task read` wrapper convention), in a command or the
# output artifact — producible only if the skill body loaded.
#
# Manual-only. Gated behind RUN_LIVE_HARNESS=1; a bare invocation in CI is a
# documented no-op. Requires a logged-in `codex` CLI and a model turn budget.
#
#   RUN_LIVE_HARNESS=1 bash tests/harness-instruction-following/always-loaded-codex-smoke.sh
#
# Model: uses CODEX_MODEL when set (passed via `--model`); no override = Codex CLI
# default. The Claude always-loaded canary is the introspection probe in
# always_loaded_live.py (run via that module's __main__), not this script —
# Claude autoloads, so it needs the discriminating canary, not a body-load proxy.

set -uo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=tests/harness-instruction-following/live_smoke_lib.sh
source "$LIB_DIR/live_smoke_lib.sh"

require_live_gate RUN_LIVE_HARNESS
require_cmd codex
require_cmd python3

FIXTURE="$REPO_ROOT/tests/fixtures/task-trees/always-loaded-canary"

echo "codex CLI: $(codex --version 2>/dev/null)"
echo "model:     ${CODEX_MODEL:-<codex default>}"
echo

TMPROOT="$(mktemp -d)"
CODEX_PROFILE_NAME="superra-always-loaded-smoke-$$"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
CODEX_PROFILE_FILE="$CODEX_HOME_DIR/${CODEX_PROFILE_NAME}.config.toml"
cleanup() {
  local rc=$?
  [ -n "${CODEX_PROFILE_FILE:-}" ] && [ -f "$CODEX_PROFILE_FILE" ] && rm -f "$CODEX_PROFILE_FILE"
  if [ "${KEEP_TMPROOT:-0}" = 1 ] && [ $rc -ne 0 ]; then
    echo "keeping temp root for failed always-loaded Codex smoke: $TMPROOT" >&2
  elif [ -n "${TMPROOT:-}" ] && [ -d "$TMPROOT" ]; then
    rm -rf "$TMPROOT"
  fi
  exit $rc
}
trap cleanup EXIT INT TERM

# Temporary Codex profile installing the superRA autoload + task hooks, matching
# the loading smoke's profile so the role-spec body-load path is exercised.
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
cp -R "$FIXTURE/superRA" "$WORKSPACE/superRA"
cat >"$WORKSPACE/superRA/superra" <<EOF
#!/usr/bin/env bash
exec python3 "$REPO_ROOT/skills/task-tree/scripts/cli.py" "\$@"
EOF
chmod +x "$WORKSPACE/superRA/superra"

OUT="$TMPROOT/codex.jsonl"
PROMPT="You are an implementer assigned the superRA task always-loaded-task in this workspace. Run \`./superRA/superra task read always-loaded-task\` and follow its objective exactly, loading the skills your role spec tells you to load before acting. Do only what that task says; do not edit source code, install anything, or run a test suite."

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

python3 "$LIB_DIR/check_always_loaded_smoke.py" \
  --transcript "$OUT" \
  --artifact "$WORKSPACE/always-loaded-evidence.json"
