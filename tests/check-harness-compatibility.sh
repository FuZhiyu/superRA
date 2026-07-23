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
assert plugin["hooks"] == "./hooks/hooks-codex.json", plugin["hooks"]
assert "skills" in plugin["interface"]["capabilities"], plugin["interface"]["capabilities"]
assert "hooks" in plugin["interface"]["capabilities"], plugin["interface"]["capabilities"]
assert entry["name"] == plugin["name"], (entry["name"], plugin["name"])
assert entry["source"]["source"] == "url", entry["source"]
assert entry["source"]["url"] == "https://github.com/FuZhiyu/superRA.git", entry["source"]["url"]
assert entry["source"]["ref"] == "main", entry["source"]["ref"]

hooks = json.loads(Path("hooks/hooks-codex.json").read_text(encoding="utf-8"))
events = hooks["hooks"]
assert "UserPromptSubmit" in events, "Codex hooks must include UserPromptSubmit"
assert "PreToolUse" in events, "Codex hooks must include PreToolUse"
assert "PostToolUse" in events, "Codex hooks must include PostToolUse task-hook reconcile coverage"
assert "Stop" in events, "Codex hooks must include Stop"
assert any("merge-guard" in h["command"] for group in events["PreToolUse"] for h in group["hooks"]), "Codex PreToolUse must wire merge-guard"
post_tool_groups = events["PostToolUse"]
post_tool_matchers = {group.get("matcher", "") for group in post_tool_groups}
assert "Edit|Write" in post_tool_matchers, "Codex PostToolUse must wire task-hook for edit/apply_patch paths"
assert "Bash" in post_tool_matchers, "Codex PostToolUse must wire task-hook for structural Bash paths"
assert all(
    any("run-hook.cmd" in h["command"] and "task-hook" in h["command"] for h in group["hooks"])
    for group in post_tool_groups
), "Codex PostToolUse groups must run the stable task-hook wrapper"
assert any("codex-plan-stop" in h["command"] for group in events["Stop"] for h in group["hooks"]), "Codex Stop must wire codex-plan-stop"
PY

section "Codex adapter references"
test -f skills/using-superra/references/codex-instructions.md
test "$(readlink AGENTS.md)" = "CLAUDE.md"
test "$(readlink AGENT.md)" = "CLAUDE.md"

section "Codex agent generation"
python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check

section "Codex skill packaging invariants"
ruby - <<'RUBY'
require "yaml"

# (i) Every skills/*/SKILL.md frontmatter parses as real YAML and description
# ≤ 1024 chars (Agent Skills spec: https://agentskills.io/specification).
errors = []
Dir.glob("skills/*/SKILL.md").sort.each do |skill_md|
  text = File.read(skill_md, encoding: "utf-8")
  unless text.start_with?("---\n")
    errors << "#{skill_md}: missing leading '---' frontmatter fence"
    next
  end

  parts = text.split(/^---\s*$\n?/, 3)
  if parts.length < 3
    errors << "#{skill_md}: missing closing '---' frontmatter fence"
    next
  end

  frontmatter = parts[1]
  begin
    fields = YAML.safe_load(frontmatter) || {}
  rescue Psych::SyntaxError => e
    errors << "#{skill_md}: invalid YAML: #{e.message.sub(/\A\(<unknown>\):\s*/, "")}"
    next
  end

  unless fields.is_a?(Hash)
    errors << "#{skill_md}: frontmatter must parse to a mapping"
    next
  end

  name = fields["name"].to_s
  desc = fields["description"].to_s
  errors << "#{skill_md}: frontmatter missing 'name'" if name.empty?
  errors << "#{skill_md}: frontmatter missing 'description'" if desc.empty?
  if desc.length > 1024
    errors << "#{skill_md}: description length #{desc.length} > 1024 (Agent Skills spec limit)"
  end
end

abort(errors.join("\n")) unless errors.empty?
RUBY

test -f skills/theory-modeling/SKILL.md
test -f skills/theory-modeling/references/planning.md
test -f skills/theory-modeling/references/integrate-drift-tests.md
test -f skills/theory-modeling/references/integration.md

python3 - <<'PY'
from pathlib import Path

# (ii) Every real skill under skills/ has a corresponding .agents/skills/ symlink.
skills_root = Path("skills")
agents_root = Path(".agents/skills")
canonical = {p.parent.name for p in skills_root.glob("*/SKILL.md")}
exposed = {p.name for p in agents_root.iterdir() if p.is_symlink() or p.is_dir()}
missing = canonical - exposed
if missing:
    raise SystemExit(f".agents/skills/ missing symlinks for: {sorted(missing)}")
PY

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
