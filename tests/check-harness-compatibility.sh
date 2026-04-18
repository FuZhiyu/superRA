#!/usr/bin/env bash
# Verify that superRA's shared skill surface remains compatible with both
# Claude Code and Codex packaging/runtime expectations.

set -euo pipefail

cd "$(dirname "$0")/.."

section() {
  printf '\n== %s ==\n' "$1"
}

warn() {
  printf 'WARN %s\n' "$1"
}

section "Claude plugin metadata"
python3 - <<'PY'
import json
from pathlib import Path

plugin = json.loads(Path(".claude-plugin/plugin.json").read_text(encoding="utf-8"))
market = json.loads(Path(".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
entry = market["plugins"][0]

assert plugin["name"] == "superRA", plugin["name"]
assert entry["name"] == plugin["name"], (entry["name"], plugin["name"])
assert entry["version"] == plugin["version"], (entry["version"], plugin["version"])
assert entry["source"] == "./", entry["source"]
PY

section "Codex plugin metadata"
python3 - <<'PY'
import json
from pathlib import Path

plugin = json.loads(Path(".codex-plugin/plugin.json").read_text(encoding="utf-8"))
market = json.loads(Path(".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
entry = market["plugins"][0]

assert plugin["name"] == "superra", plugin["name"]
assert plugin["skills"] == "./skills/", plugin["skills"]
assert "skills" in plugin["interface"]["capabilities"], plugin["interface"]["capabilities"]
assert entry["name"] == plugin["name"], (entry["name"], plugin["name"])
assert entry["source"]["source"] == "local", entry["source"]
assert entry["source"]["path"] == "./", entry["source"]["path"]
PY

section "Shared harness adapters"
test -f skills/using-superRA/references/claude-tools.md
test -f skills/using-superRA/references/codex-tools.md
test "$(readlink AGENTS.md)" = "CLAUDE.md"
test "$(readlink AGENT.md)" = "CLAUDE.md"

section "Codex agent generation"
python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check

section "Shared structural invariants"
bash tests/structural-invariants.sh

section "Optional local CLIs"
if command -v claude >/dev/null 2>&1; then
  claude --version 2>/dev/null
else
  warn "claude CLI not found; skipped local Claude Code executable check"
fi

if command -v codex >/dev/null 2>&1; then
  codex --version 2>/dev/null
else
  warn "codex CLI not found; skipped local Codex executable check"
fi
