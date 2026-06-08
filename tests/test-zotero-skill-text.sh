#!/usr/bin/env bash
# Text-regression checks for skills/zotero-paper-reader/.
# Blocks MCP regressions (mcp__zotero / mcp_zotero) and stale setup
# instructions (old hardcoded paths, uv run --project, get_zotero_pdf.py).
# Also asserts positive invariants: every uv invocation uses --script, and
# all command examples use the harness-neutral <skill-dir> placeholder.
#
# Run from the repo root: bash tests/test-zotero-skill-text.sh

set -euo pipefail

cd "$(dirname "$0")/.."

SKILL_DIR="skills/zotero-paper-reader"

pass=0
fail=0
failed_names=()

record_pass() { printf 'PASS  %s\n' "$1"; pass=$((pass + 1)); }
record_fail() { printf 'FAIL  %s\n' "$1"; fail=$((fail + 1)); failed_names+=("$1"); }

# assert_absent: pattern must not appear anywhere under SKILL_DIR.
assert_absent() {
  local name="$1" pattern="$2"
  if rg -rl --fixed-strings -- "$pattern" "$SKILL_DIR" >/dev/null 2>&1; then
    printf '      pattern present (must be absent): %s\n' "$pattern"
    record_fail "$name"
  else
    record_pass "$name"
  fi
}

# assert_present_in: pattern must appear in the given file.
assert_present_in() {
  local name="$1" file="$2" pattern="$3"
  if rg -q --fixed-strings -- "$pattern" "$file" 2>/dev/null; then
    record_pass "$name"
  else
    printf '      pattern absent in %s: %s\n' "$file" "$pattern"
    record_fail "$name"
  fi
}

# --------------------------------------------------------------------------- #
# MCP regression guards                                                        #
# --------------------------------------------------------------------------- #

assert_absent "no mcp__zotero reference"          "mcp__zotero"
assert_absent "no mcp_zotero reference"           "mcp_zotero"
# Guard against any instruction that tells the agent to call an MCP tool for
# Zotero (e.g. "call mcp" / "use mcp" in a Zotero-specific context).
# We check for the literal token in a tool-call context, not every prose
# occurrence of the acronym (the architecture discussion in access-modes.md
# is fine; a tool-call instruction is not).
assert_absent "no call_mcp_zotero instruction"    "call_mcp"
assert_absent "no use_mcp_tool instruction"       "use_mcp_tool"

# --------------------------------------------------------------------------- #
# Stale setup-instruction guards                                               #
# --------------------------------------------------------------------------- #

# Old hardcoded install path.
assert_absent "no .claude/skills/mistral hardcoded path"   ".claude/skills/mistral"
assert_absent "no .claude/skills/ hardcoded path"          ".claude/skills/"

# Claude-only env var: undefined under Codex/superRA, where it expands to
# /scripts/zotero_tool.py and every command fails before pyzotero runs. The
# install-location-independent invocation uses the <skill-dir> placeholder.
assert_absent "no CLAUDE_SKILL_DIR (Claude-only path)"     "CLAUDE_SKILL_DIR"

# Legacy script name replaced by zotero_tool.py.
assert_absent "no get_zotero_pdf.py reference"             "get_zotero_pdf.py"

# PEP 723 inline-script runner must be --script, never --project.
assert_absent "no uv run --project invocation"             "uv run --project"

# The old Zotero MCP server package name.
assert_absent "no zotero-mcp-server reference"             "zotero-mcp-server"
assert_absent "no zotero_mcp reference"                    "zotero_mcp"

# --------------------------------------------------------------------------- #
# Positive invariants                                                          #
# --------------------------------------------------------------------------- #

# SKILL.md must tell agents to use the harness-neutral <skill-dir> placeholder
# so the path is install-location and harness independent.
assert_present_in \
  "SKILL.md uses <skill-dir> placeholder" \
  "$SKILL_DIR/SKILL.md" \
  '<skill-dir>/scripts/zotero_tool.py'

# paper-reading.md must show the full uv run --script form with <skill-dir>.
assert_present_in \
  "paper-reading.md uses uv run --script with <skill-dir>" \
  "$SKILL_DIR/references/paper-reading.md" \
  'uv run --script <skill-dir>/scripts/zotero_tool.py'

# access-modes.md must document the local API probe behavior (connector port
# vs. /api path distinction — key for the 403 edge case).
assert_present_in \
  "access-modes.md documents 403 local-API-not-enabled edge case" \
  "$SKILL_DIR/references/access-modes.md" \
  '403'

# The script's PEP 723 metadata must pin pyzotero 1.13.0 exactly.
assert_present_in \
  "script pins pyzotero==1.13.0" \
  "$SKILL_DIR/scripts/zotero_tool.py" \
  '"pyzotero==1.13.0"'

# SKILL.md must reference pyzotero (the new approach), not the old MCP server.
assert_present_in \
  "SKILL.md mentions pyzotero" \
  "$SKILL_DIR/SKILL.md" \
  'pyzotero'

# --------------------------------------------------------------------------- #
# BibTeX / citation surface (tasks 07-09)                                      #
# --------------------------------------------------------------------------- #

# SKILL.md must surface the three new commands in its routing body so they are
# discoverable without loading the reference.
for cmd in bibtex cite bibliography; do
  assert_present_in \
    "SKILL.md surfaces the '$cmd' command" \
    "$SKILL_DIR/SKILL.md" \
    "$cmd"
done

# SKILL.md must state the key model (BBT keys by default) and point at the
# depth reference rather than inlining it.
assert_present_in \
  "SKILL.md names the Better BibTeX key model" \
  "$SKILL_DIR/SKILL.md" \
  'Better BibTeX'
assert_present_in \
  "SKILL.md routes to the bibtex-citations reference" \
  "$SKILL_DIR/SKILL.md" \
  'references/bibtex-citations.md'

# The depth reference must exist and document the three commands.
BIBREF="$SKILL_DIR/references/bibtex-citations.md"
for cmd in bibtex cite bibliography; do
  assert_present_in \
    "bibtex-citations.md documents the '$cmd' command" \
    "$BIBREF" \
    "$cmd"
done

# The reference must explain the BBT-default / built-in-fallback key model and
# the key-mismatch warning, plus the master-.bib sync semantics.
assert_present_in \
  "bibtex-citations.md documents the BBT-default key model" \
  "$BIBREF" \
  'Better BibTeX'
assert_present_in \
  "bibtex-citations.md documents the built-in fallback" \
  "$BIBREF" \
  'fallback'
assert_present_in \
  "bibtex-citations.md documents the bbt_fallback flag" \
  "$BIBREF" \
  'bbt_fallback'
assert_present_in \
  "bibtex-citations.md documents the master-.bib sync" \
  "$BIBREF" \
  'master'
assert_present_in \
  "bibtex-citations.md documents dedup by citekey" \
  "$BIBREF" \
  'citekey'

# Stale-claim guard: no surface may claim BBT is reachable over the Web API or
# pyzotero (BBT is local-only — a contradiction would mislead web-mode users).
assert_absent "no claim that BBT works over the Web API" "Better BibTeX over the Web API"
assert_absent "no claim that pyzotero exposes Better BibTeX" "pyzotero exposes Better BibTeX"

# Inventory consistency: the skill must NOT be described as Manifest-loaded on
# any surface (it is a standalone Utility skill).
assert_absent "SKILL.md does not claim Manifest loading" "loaded by the Skill-Load Manifest"

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi
exit 0
