#!/usr/bin/env bash
# Structural invariant tests for the superRA plugin itself.
# Intended to be run before any plugin-level refactor merge, or by CI.
#
# These are the plugin's analogue of drift tests: they verify that the
# shape of the plugin (skill registry, cross-references, hook config,
# workflow-principle ordering in CLAUDE.md, load-bearing invariants)
# still holds after a structural change.
#
# Exit 0 = all invariants pass. Exit >0 = one or more failures.
# Known pre-existing warnings (broken upstream refs in writing-skills)
# are reported as WARN, not FAIL, so CI stays green until they're
# addressed separately.

set -u
cd "$(dirname "$0")/.."

fail=0
warn=0

pass() { printf '\033[32mPASS\033[0m %s\n' "$1"; }
fail() { printf '\033[31mFAIL\033[0m %s\n' "$1"; fail=$((fail+1)); }
warn() { printf '\033[33mWARN\033[0m %s\n' "$1"; warn=$((warn+1)); }

# 1. AGENTS.md is a symlink to CLAUDE.md — the canonical way we keep them
# identical. A file copy would silently drift; enforce the symlink.
if [ "$(readlink AGENTS.md 2>/dev/null)" = "CLAUDE.md" ]; then
  pass "AGENTS.md is a symlink to CLAUDE.md"
else
  fail "AGENTS.md must be a symlink to CLAUDE.md"
fi

# 2. Every superRA:<name> invocation in the live plugin surface resolves to
# a real skill directory. Scope: skills/, agents/, hooks/, README.md,
# CLAUDE.md. Excludes RELEASE-NOTES.md (historical refs to removed skills
# are expected). Excludes agent subagent_types (superRA:implementer,
# superRA:reviewer — these are agent dispatch targets, not skills).
broken_live=0
for ref in $(grep -rohE 'superRA:[a-zA-Z-]+' skills/ agents/ hooks/ README.md CLAUDE.md 2>/dev/null | sort -u); do
  name=${ref#superRA:}
  [ "$name" = "implementer" ] && continue
  [ "$name" = "reviewer" ] && continue
  if [ ! -d "skills/$name" ]; then
    broken_live=$((broken_live+1))
    # Known pre-existing upstream refs → WARN, not FAIL
    if [ "$name" = "systematic-debugging" ] || [ "$name" = "test-driven-development" ]; then
      warn "superRA:$name — unresolved upstream ref in writing-skills (known)"
    else
      fail "superRA:$name — invocation does not resolve to a skills/ directory"
    fi
  fi
done
[ $broken_live -eq 0 ] && pass "all superRA: invocations in live surface resolve"

# 3. Iron Law and cross-cutting content preserved in econ-data-analysis
# main SKILL.md body. These are load-bearing and must not drift to
# references (per feedback_skill_file_thoroughness).
grep -q '^NO TRANSFORMATION WITHOUT PRIOR DESCRIPTION$' skills/econ-data-analysis/SKILL.md \
  && pass "Iron Law in econ-data-analysis main body" \
  || fail "Iron Law missing from econ-data-analysis main body"
for section in '## Describe' '## Analyze' '## Validate' '## Pitfalls' '## Red Flags'; do
  if grep -Fq "$section" skills/econ-data-analysis/SKILL.md; then
    pass "main body contains '$section'"
  else
    fail "main body missing '$section'"
  fi
done

# 3b. Validate section must carry a Sensitivity analysis sub-section — this
# is the first-class execution-phase discipline added in the DAV restructure.
if grep -Fq '### Sensitivity analysis' skills/econ-data-analysis/SKILL.md; then
  pass "Validate section contains Sensitivity analysis sub-section"
else
  fail "Validate section missing Sensitivity analysis sub-section"
fi

# 3c. No lingering DAD / describe-analyze-doc strings in the SKILL.md body.
if grep -qiE 'describe.analyze.doc|\bDAD\b' skills/econ-data-analysis/SKILL.md; then
  fail "SKILL.md still contains DAD / describe-analyze-doc references"
else
  pass "SKILL.md free of DAD / describe-analyze-doc references"
fi

# 4. planning-workflow is domain-agnostic (no data-specific strings).
forbidden=$(grep -ciE 'WRDS|Compustat|winsoriz|CRSP' skills/planning-workflow/SKILL.md || true)
if [ "$forbidden" -eq 0 ]; then
  pass "planning-workflow/SKILL.md has no data-analysis-specific strings"
else
  fail "planning-workflow/SKILL.md contains $forbidden data-specific strings"
fi

# 5. Stage-scoped references exist and are cross-linked from the load-map.
for f in skills/econ-data-analysis/references/planning.md \
         skills/econ-data-analysis/references/integrate-drift-tests.md \
         skills/econ-data-analysis/references/data-robustness-checklist.md; do
  [ -f "$f" ] && pass "exists: $f" || fail "missing: $f"
done
grep -q 'references/planning.md' skills/econ-data-analysis/SKILL.md \
  && pass "load-map cites planning.md" || fail "load-map missing planning.md"
grep -q 'references/integrate-drift-tests.md' skills/econ-data-analysis/SKILL.md \
  && pass "load-map cites integrate-drift-tests.md" || fail "load-map missing integrate-drift-tests.md"

# 6. CATEGORIES.md lists every skill on disk.
ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/$||' | sort > /tmp/sra-disk.$$
grep -oE '`[a-zA-Z-]+`' skills/CATEGORIES.md | grep -oE '[a-zA-Z-]+' | sort -u > /tmp/sra-cat.$$
missing_skills=$(comm -23 /tmp/sra-disk.$$ /tmp/sra-cat.$$ | tr '\n' ' ' | xargs)
rm -f /tmp/sra-disk.$$ /tmp/sra-cat.$$
if [ -z "$missing_skills" ]; then
  pass "CATEGORIES.md lists every skill on disk"
else
  fail "CATEGORIES.md missing: $missing_skills"
fi

# 7. hooks.json and hooks-cursor.json are valid JSON.
python3 -c "import json; json.load(open('hooks/hooks.json'))" 2>/dev/null \
  && pass "hooks.json parses as JSON" || fail "hooks.json is not valid JSON"
python3 -c "import json; json.load(open('hooks/hooks-cursor.json'))" 2>/dev/null \
  && pass "hooks-cursor.json parses as JSON" || fail "hooks-cursor.json is not valid JSON"

# 8. exit-plan-mode hook runs and emits valid JSON.
if echo '{"tool_name":"ExitPlanMode"}' | bash hooks/exit-plan-mode 2>/dev/null | python3 -m json.tool >/dev/null 2>&1; then
  pass "exit-plan-mode hook executes and emits valid JSON"
else
  fail "exit-plan-mode hook did not emit valid JSON"
fi

# 9. Workflow principles appear before Iron Law in CLAUDE.md — the
# elevation that this refactor is built around.
wp_line=$(grep -n 'Workflow principles' CLAUDE.md | head -1 | cut -d: -f1)
il_line=$(grep -n 'Iron Law' CLAUDE.md | head -1 | cut -d: -f1)
if [ -n "$wp_line" ] && [ -n "$il_line" ] && [ "$wp_line" -lt "$il_line" ]; then
  pass "Workflow principles appear before Iron Law in CLAUDE.md"
else
  fail "ordering: Workflow principles at L${wp_line:-?}, Iron Law at L${il_line:-?}"
fi

# 10a. Dispatch-template prefix: every `Agent(subagent_type: "superRA:...")`
# dispatch template across the live workflow surface carries the canonical
# "Follow the standard stage-relevant workflow..." prefix. The dispatch
# prompt is additive steering on top of the agent's standard protocol; the
# prefix is the anchor that tells the agent the standard Before-You-Start
# is in effect.
dispatch_files="skills/execution-workflow/SKILL.md
skills/integration-workflow/SKILL.md
skills/merge-workflow/SKILL.md
skills/semantic-merge/SKILL.md
skills/refactor-and-integrate/SKILL.md"
dispatch_count=0
prefix_count=0
for f in $dispatch_files; do
  dc=$(grep -c 'Agent(subagent_type: "superRA:\(implementer\|reviewer\)"):' "$f" 2>/dev/null || echo 0)
  dispatch_count=$((dispatch_count + dc))
done
for f in $dispatch_files; do
  pc=$(grep -c 'Follow the standard stage-relevant workflow' "$f" 2>/dev/null || echo 0)
  prefix_count=$((prefix_count + pc))
done
if [ "$dispatch_count" -gt 0 ] && [ "$prefix_count" -ge "$dispatch_count" ]; then
  pass "dispatch templates carry 'Follow the standard stage-relevant workflow' prefix ($prefix_count prefix mentions >= $dispatch_count templates)"
else
  fail "dispatch-prompt prefix coverage: $prefix_count prefix mentions vs $dispatch_count templates"
fi

# 10b. No dispatch template retains `Work from:` or `Counterpart:` fields
# (legacy over-specification; Work-from is cwd by default, Counterpart is
# set at team-spawn time in Agent Teams mode).
if grep -n 'Work from:\|Counterpart:' $dispatch_files 2>/dev/null | grep -v '^[^:]*:[[:space:]]*#'; then
  fail "dispatch templates still contain 'Work from:' or 'Counterpart:' lines"
else
  pass "no dispatch template carries 'Work from:' or 'Counterpart:' fields"
fi

# 11. README 'Why superRA?' lead section does not mention Iron Law.
why_section=$(awk '/^## Why superRA\?/{flag=1; next} /^## /{flag=0} flag' README.md | head -10)
if echo "$why_section" | grep -qi 'Iron Law'; then
  fail "README 'Why superRA?' lead mentions Iron Law — should be workflow-first"
else
  pass "README 'Why superRA?' lead is workflow-first"
fi

echo
echo "----------------------------------------"
if [ $fail -eq 0 ]; then
  echo "OK ($warn known warnings)"
  exit 0
else
  echo "FAILED: $fail invariant(s) failed, $warn known warning(s)"
  exit 1
fi
