#!/usr/bin/env bash
# Text-regression checks for skills/mistral-pdf-to-markdown/.
# This skill was migrated into superRA as the canonical home for the PDF->md
# conversion step behind zotero-paper-reader. The guards below lock in the
# harness-neutral invocation (no Claude-only ${CLAUDE_SKILL_DIR}) and confirm
# the PEP 723 script came over intact.
#
# Run from the repo root: bash tests/test-mistral-skill-text.sh

set -euo pipefail

cd "$(dirname "$0")/.."

SKILL_DIR="skills/mistral-pdf-to-markdown"

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
# Harness-neutral invocation                                                   #
# --------------------------------------------------------------------------- #

# Claude-only env var: undefined under Codex/superRA, where it expands to
# /scripts/... and the command fails before the converter runs. Must stay
# absent in favor of the <skill-dir> placeholder.
assert_absent "no CLAUDE_SKILL_DIR (Claude-only path)"     "CLAUDE_SKILL_DIR"

assert_present_in \
  "SKILL.md uses <skill-dir> placeholder" \
  "$SKILL_DIR/SKILL.md" \
  '<skill-dir>/scripts/convert_pdf_to_markdown.py'

assert_present_in \
  "reference.md uses <skill-dir> placeholder" \
  "$SKILL_DIR/references/reference.md" \
  '<skill-dir>/scripts'

# --------------------------------------------------------------------------- #
# PEP 723 invocation form                                                      #
# --------------------------------------------------------------------------- #

# The converter declares its deps inline (PEP 723), so it MUST be run with
# `uv run --script`, which installs them. `uv run python <script>` and bare
# `python <script>` both IGNORE PEP 723 deps and fail with ModuleNotFoundError
# on a fresh machine — the exact conversion dead-end the in-repo vendoring
# closes. Lock the documented invocation to the working form.
assert_absent "no 'uv run python <skill-dir>' (ignores PEP 723 deps)"        "uv run python <skill-dir>"
assert_absent "no bare 'python <skill-dir>/scripts' (ignores PEP 723 deps)"  "python <skill-dir>/scripts"
assert_absent "no 'uv,run,python' subprocess list (ignores PEP 723 deps)"    '"uv", "run", "python"'

assert_present_in \
  "SKILL.md runs converter via 'uv run --script' (PEP 723)" \
  "$SKILL_DIR/SKILL.md" \
  'uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py'

# --------------------------------------------------------------------------- #
# Script integrity                                                             #
# --------------------------------------------------------------------------- #

# The converter must arrive as a self-contained PEP 723 script with its OCR
# dependency declared inline.
assert_present_in \
  "converter declares mistralai dependency (PEP 723)" \
  "$SKILL_DIR/scripts/convert_pdf_to_markdown.py" \
  '"mistralai"'

# Secret hygiene: the API key is resolved at runtime, never hardcoded.
assert_present_in \
  "SKILL.md warns never to commit API keys" \
  "$SKILL_DIR/SKILL.md" \
  'Never commit API keys'

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi
exit 0
