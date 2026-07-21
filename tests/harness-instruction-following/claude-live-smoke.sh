#!/usr/bin/env bash
# Opt-in Claude live smoke for agent-loading instruction-following.
#
# Drives the bundled `bundle-two-tasks` fixture through the cheapest Claude
# agent path and asserts structural evidence that the agent ran both
# `superra task read` calls and read all three marker files BEFORE writing the
# evidence artifact, then compares the artifact to the committed expected shape.
#
# Manual-only. Gated behind RUN_LIVE_HARNESS=1; a bare invocation in CI is a
# documented no-op. Requires a logged-in `claude` CLI and an API turn budget.
#
#   RUN_LIVE_HARNESS=1 bash tests/harness-instruction-following/claude-live-smoke.sh
#
# Model: defaults to CLAUDE_MODEL=haiku (cheapest). Override with CLAUDE_MODEL.
#
# --include-hook-events (audited): a real, documented `claude -p` flag (confirmed
# in CLI 2.1.183 `--help`: "Include all hook lifecycle events in the output
# stream (only works with --output-format=stream-json)"). It is NOT a no-op — it
# surfaces hook lifecycle events (e.g. the UserPromptSubmit autoload hooks) into
# the stream. It does NOT make filesystem PreToolUse hooks fire under `claude -p`
# (issue #40506), so it does not give skill-load-by-name evidence here; that comes
# from the in-process SDK harness (sdk_load_harness.py). Kept because it is
# harmless and exposes the autoloads for debugging; this smoke does not assert on
# the extra events.
#
# Harness-evidence limitation: Claude's stream-json exposes Bash and Read tool
# events but does NOT emit a structural event for `Skill(...)` skill loading in
# a way the shared parser can tie to the manifest by name here. Rather than
# assert something vacuous, this smoke asserts the strongest available
# observables — task-read command events and marker Read events ordered before
# the artifact write, plus an artifact whose sentinel values can only be
# produced after reading the required context. Structured manifest mappings and
# role frontmatter are covered statically by the CI-safe contract tests; the
# orchestrator dispatch smoke covers subagent dispatch evidence separately.

set -uo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=tests/harness-instruction-following/live_smoke_lib.sh
source "$LIB_DIR/live_smoke_lib.sh"

require_live_gate RUN_LIVE_HARNESS
require_cmd claude
require_cmd python3

CLAUDE_MODEL="${CLAUDE_MODEL:-haiku}"
echo "claude CLI: $(claude --version 2>/dev/null | awk '{print $1}')"
echo "model:      $CLAUDE_MODEL"
echo "plugin dir: $REPO_ROOT"
echo

TMPROOT="$(mktemp -d)"
cleanup() {
  local rc=$?
  if [ "${KEEP_TMPROOT:-0}" = 1 ] && [ $rc -ne 0 ]; then
    echo "keeping temp root for failed Claude live smoke: $TMPROOT" >&2
  elif [ -n "${TMPROOT:-}" ] && [ -d "$TMPROOT" ]; then
    rm -rf "$TMPROOT"
  fi
  exit $rc
}
trap cleanup EXIT INT TERM

WORKSPACE="$TMPROOT/ws"
mkdir -p "$WORKSPACE"
seed_workspace "$WORKSPACE"

OUT="$TMPROOT/claude.ndjson"
SID="$(uuidgen 2>/dev/null | tr '[:upper:]' '[:lower:]' || echo "smoke-$$")"
PROMPT="$(smoke_task_prompt)"

( cd "$WORKSPACE" && \
  claude -p "$PROMPT" \
    --session-id "$SID" \
    --model "$CLAUDE_MODEL" \
    --include-hook-events \
    --output-format=stream-json \
    --verbose \
    --plugin-dir "$REPO_ROOT" \
    --no-session-persistence \
    --allowedTools Bash,Read,Write \
    --permission-mode acceptEdits \
    </dev/null >"$OUT" 2>&1 )
rc=$?
if [ $rc -ne 0 ]; then
  echo "FAIL: claude exec exited $rc" >&2
  tail -n 60 "$OUT" >&2
  exit 1
fi

# Cost/model metadata (recorded, never asserted).
python3 - "$OUT" <<'PY'
import json, sys
cost = 0.0
with open(sys.argv[1], encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("type") == "result":
            cost = r.get("total_cost_usd") or 0.0
print(f"cost: ${cost:.4f}")
PY

python3 "$LIB_DIR/check_loading_smoke.py" \
  --harness claude \
  --transcript "$OUT" \
  --artifact "$WORKSPACE/loading-evidence.json" \
  --expected "$(expected_artifact_path)"
