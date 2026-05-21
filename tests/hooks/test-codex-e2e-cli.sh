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

mkdir -p "$TMPROOT/.codex"
python3 - "$REPO_ROOT" "$TMPROOT/.codex/hooks.json" <<'PY'
import json, sys
repo, out = sys.argv[1], sys.argv[2]
def cmd(name):
    return f'env PLUGIN_ROOT="{repo}" CLAUDE_PLUGIN_ROOT="{repo}" "{repo}/hooks/run-hook.cmd" {name}'
hooks = {
    "hooks": {
        "UserPromptSubmit": [
            {"hooks": [{"type": "command", "command": cmd("autoload-superra")}]}
        ],
        "PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": cmd("merge-guard")}]}
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
