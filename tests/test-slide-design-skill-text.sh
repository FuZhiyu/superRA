#!/usr/bin/env bash
# Text guards for the slide-design skill's harness-neutral bundled paths.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DIR="$ROOT/skills/slide-design"

PASSED=0
FAILED=0

assert_contains() {
  local label="$1"
  local file="$2"
  local pattern="$3"
  if grep -Fq "$pattern" "$file"; then
    printf 'PASS  %s\n' "$label"
    PASSED=$((PASSED + 1))
  else
    printf 'FAIL  %s\n' "$label"
    printf '      missing pattern: %s\n' "$pattern"
    FAILED=$((FAILED + 1))
  fi
}

assert_absent() {
  local label="$1"
  local file="$2"
  local pattern="$3"
  if grep -Fq "$pattern" "$file"; then
    printf 'FAIL  %s\n' "$label"
    printf '      forbidden pattern: %s\n' "$pattern"
    FAILED=$((FAILED + 1))
  else
    printf 'PASS  %s\n' "$label"
    PASSED=$((PASSED + 1))
  fi
}

assert_contains "SKILL.md defines <skill-dir>" "$SKILL_DIR/SKILL.md" '<skill-dir>'
assert_contains "SKILL.md uses checker via uv --script" "$SKILL_DIR/SKILL.md" 'uv run --script <skill-dir>/scripts/check_slide_layout.py'
assert_contains "SKILL.md uses template via <skill-dir>" "$SKILL_DIR/SKILL.md" '<skill-dir>/assets/beamer-starter-template.tex'
assert_contains "layout reference uses checker via <skill-dir>" "$SKILL_DIR/references/layout-checks.md" 'uv run --script <skill-dir>/scripts/check_slide_layout.py'
assert_contains "techniques reference uses checker via <skill-dir>" "$SKILL_DIR/references/beamer-techniques.md" 'uv run --script <skill-dir>/scripts/check_slide_layout.py'
assert_contains "overlays reference uses template via <skill-dir>" "$SKILL_DIR/references/beamer-overlays.md" '<skill-dir>/assets/beamer-starter-template.tex'
assert_absent "no bare checker script path in slide skill docs" "$SKILL_DIR/SKILL.md" 'use `scripts/check_slide_layout.py`'
assert_absent "no bare checker command in layout reference" "$SKILL_DIR/references/layout-checks.md" 'uv run --script scripts/check_slide_layout.py'

printf '\nPassed: %d    Failed: %d\n' "$PASSED" "$FAILED"
if [ "$FAILED" -gt 0 ]; then
  exit 1
fi
