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
python3 - <<'PY'
import re
from pathlib import Path
text = Path("skills/using-superRA/SKILL.md").read_text(encoding="utf-8")
m = re.search(r"^name:\s*(\S+)\s*$", text, re.MULTILINE)
assert m and m.group(1) == "using-superra", f"using-superRA SKILL.md name must be lowercase 'using-superra', got {m and m.group(1)!r}"
PY

section "Codex agent generation"
python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check

section "Codex skill packaging invariants"
python3 - <<'PY'
import re
from pathlib import Path

# (i) Every skills/*/SKILL.md frontmatter parses and description ≤ 500 chars.
skills_root = Path("skills")
errors = []
for skill_md in sorted(skills_root.glob("*/SKILL.md")):
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{skill_md}: missing leading '---' frontmatter fence")
        continue
    end = text.find("\n---", 4)
    if end == -1:
        errors.append(f"{skill_md}: missing closing '---' frontmatter fence")
        continue
    fm = text[4:end]
    # Tolerant parse: collect simple key: value pairs and folded-block 'description: >'.
    fields = {}
    lines = fm.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", "|", ">-", "|-"):
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i] == ""):
                block.append(lines[i].strip())
                i += 1
            fields[key] = " ".join(s for s in block if s)
            continue
        fields[key] = val
        i += 1
    name = fields.get("name", "")
    desc = fields.get("description", "")
    if not name:
        errors.append(f"{skill_md}: frontmatter missing 'name'")
    if not desc:
        errors.append(f"{skill_md}: frontmatter missing 'description'")
    if len(desc) > 500:
        errors.append(f"{skill_md}: description length {len(desc)} > 500 (Codex limit)")

# (ii) Every skill under skills/ has a corresponding .agents/skills/ symlink.
agents_root = Path(".agents/skills")
canonical = {p.name for p in skills_root.iterdir() if p.is_dir()}
exposed = {p.name for p in agents_root.iterdir() if p.is_symlink() or p.is_dir()}
missing = canonical - exposed
if missing:
    errors.append(f".agents/skills/ missing symlinks for: {sorted(missing)}")

if errors:
    raise SystemExit("\n".join(errors))
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
