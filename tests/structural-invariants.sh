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
  dc=$(grep -c 'Agent(subagent_type: "superRA:\(implementer\|reviewer\)"):' "$f" 2>/dev/null)
  dc=${dc:-0}
  dispatch_count=$((dispatch_count + dc))
done
for f in $dispatch_files; do
  pc=$(grep -c 'Follow the standard stage-relevant workflow' "$f" 2>/dev/null)
  pc=${pc:-0}
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

# 11. econ-data-analysis §Review & Self-Check Discipline integration.
# The shared-gating section in the SKILL.md main body is the single source
# of truth both implementer self-check and reviewer verification walk.
# Encoded here: heading exists, severity markers present (≥8 GATING), the
# CONDITIONAL APPROVE verdict protocol is spelled out, and no separate
# implementation-review.md / integration-review.md reference file was
# created (shared-gating decision sanity check).
eda_skill="skills/econ-data-analysis/SKILL.md"
if grep -Fq '## Review & Self-Check Discipline' "$eda_skill"; then
  pass "econ-data-analysis SKILL.md contains '## Review & Self-Check Discipline' heading"
else
  fail "econ-data-analysis SKILL.md missing '## Review & Self-Check Discipline' heading"
fi
gating_count=$(grep -c '\[GATING\]' "$eda_skill" 2>/dev/null || echo 0)
if [ "$gating_count" -ge 8 ]; then
  pass "econ-data-analysis SKILL.md has ${gating_count} [GATING] markers (>=8)"
else
  fail "econ-data-analysis SKILL.md has only ${gating_count} [GATING] markers (<8)"
fi
if grep -Fq 'CONDITIONAL APPROVE' "$eda_skill"; then
  pass "econ-data-analysis SKILL.md encodes CONDITIONAL APPROVE verdict"
else
  fail "econ-data-analysis SKILL.md missing CONDITIONAL APPROVE verdict"
fi
if [ -f skills/econ-data-analysis/references/implementation-review.md ] \
   || [ -f skills/econ-data-analysis/references/integration-review.md ]; then
  fail "shared-gating decision violated: implementation-review.md / integration-review.md reference file exists"
else
  pass "no separate implementation-review.md / integration-review.md reference (shared gating in main body)"
fi

# 12. execution-workflow domain-agnosticism invariants (Task 3 restructure).
# The workflow skill should no longer carry data-flavored two-stage review
# language, should encode the one-pass CONDITIONAL APPROVE protocol, and
# should have dropped the data-analysis-specific Sensitivity Analysis Tasks
# and Model Selection sections (replaced by a one-paragraph Model Selection).
ew_skill="skills/execution-workflow/SKILL.md"
if grep -qE 'data integrity|two-stage review|REVISE \(data integrity\)|REVISE \(implementation\)' "$ew_skill"; then
  fail "execution-workflow SKILL.md still contains two-stage-review phrasing (data integrity / two-stage review / REVISE (data integrity) / REVISE (implementation))"
else
  pass "execution-workflow SKILL.md free of two-stage-review phrasing"
fi
if grep -qE '^## Sensitivity Analysis Tasks' "$ew_skill"; then
  fail "execution-workflow SKILL.md still carries '## Sensitivity Analysis Tasks' section (content lives in domain skill)"
else
  pass "execution-workflow SKILL.md has dropped '## Sensitivity Analysis Tasks' section"
fi
if grep -Fq 'CONDITIONAL APPROVE' "$ew_skill"; then
  pass "execution-workflow SKILL.md encodes CONDITIONAL APPROVE verdict"
else
  fail "execution-workflow SKILL.md missing CONDITIONAL APPROVE verdict"
fi

# 13. Agent files carry the authoritative Stage table, the dispatch-prompt
# contract phrase, and (reviewer only) the CONDITIONAL APPROVE verdict.
# The Stage table is the single source of truth for which references each
# stage loads; the contract phrase tells agents the dispatch prompt is
# additive-only; CONDITIONAL APPROVE encodes the one-pass verdict protocol
# on the review side.
for f in agents/implementer.md agents/reviewer.md; do
  # Markdown table whose header mentions 'Stage' and whose rows include the
  # four core stages. We grep the rendered markdown; the table rows contain
  # backtick-wrapped stage names like `implementation`.
  if grep -Eq '^\|.*Stage.*\|' "$f" \
     && grep -Fq '`implementation`' "$f" \
     && grep -Fq '`implementation review`' "$f" \
     && grep -Fq '`refactoring`' "$f" \
     && grep -Fq '`integration review`' "$f"; then
    pass "$f contains Stage table with core stages (implementation, implementation review, refactoring, integration review)"
  else
    fail "$f missing Stage table or core stage rows"
  fi
  if grep -Fq "What the dispatch prompt carries — and doesn't" "$f"; then
    pass "$f contains dispatch-prompt contract phrase"
  else
    fail "$f missing dispatch-prompt contract phrase"
  fi
done
if grep -Fq 'CONDITIONAL APPROVE' agents/reviewer.md; then
  pass "agents/reviewer.md encodes CONDITIONAL APPROVE verdict"
else
  fail "agents/reviewer.md missing CONDITIONAL APPROVE verdict"
fi

# 14. Cross-stage orchestration content lives in agent-orchestration, not
# execution-workflow. agent-orchestration/SKILL.md owns five top-level
# sections (Dispatch Templates, Dispatch-Return Deltas, Handling Reviewer
# Feedback, Review Status Reference, Direct Mode); execution-workflow/SKILL.md
# does NOT carry '## Dispatch Templates' as a heading (pointers to
# agent-orchestration only).
ao_skill="skills/agent-orchestration/SKILL.md"
ao_missing=0
for h in '^## Dispatch Templates$' \
         '^## Dispatch-Return Deltas$' \
         '^## Handling Reviewer Feedback' \
         '^## Review Status Reference$' \
         '^## Direct Mode$'; do
  if grep -Eq "$h" "$ao_skill"; then
    :
  else
    fail "agent-orchestration SKILL.md missing heading matching: $h"
    ao_missing=$((ao_missing+1))
  fi
done
[ "$ao_missing" -eq 0 ] && pass "agent-orchestration SKILL.md owns the five cross-stage orchestration sections"
if grep -Eq '^## Dispatch Templates' "skills/execution-workflow/SKILL.md"; then
  fail "execution-workflow SKILL.md still carries '## Dispatch Templates' as a top-level heading (should be lifted to agent-orchestration)"
else
  pass "execution-workflow SKILL.md no longer carries '## Dispatch Templates' as a top-level heading"
fi

# 15. Alias-only protocol skills (implementer-protocol, reviewer-protocol) are
# deleted. Their role is covered by agent-orchestration §Direct Mode plus
# direct links to agents/implementer.md / agents/reviewer.md.
protocol_dirs_present=0
if [ -d "skills/implementer-protocol" ]; then
  fail "skills/implementer-protocol/ should be deleted (covered by agent-orchestration §Direct Mode)"
  protocol_dirs_present=$((protocol_dirs_present+1))
fi
if [ -d "skills/reviewer-protocol" ]; then
  fail "skills/reviewer-protocol/ should be deleted (covered by agent-orchestration §Direct Mode)"
  protocol_dirs_present=$((protocol_dirs_present+1))
fi
[ "$protocol_dirs_present" -eq 0 ] && pass "alias-only protocol skills (implementer-protocol, reviewer-protocol) are absent"

# 16. Data-analysis integration reference exists and encodes shared-flow gating.
# econ-data-analysis/references/integration.md is the single source of truth
# for the data-specific refactoring / integration-review checklist; generic
# code-integration content stays in refactor-and-integrate/references/
# codebase-integration.md; integration-workflow/SKILL.md carries no data-
# specific tokens (workflow-choreography only).
int_ref="skills/econ-data-analysis/references/integration.md"
if [ -f "$int_ref" ]; then
  pass "exists: $int_ref"
else
  fail "missing: $int_ref"
fi
int_gating=$(grep -c '\[GATING\]' "$int_ref" 2>/dev/null || echo 0)
if [ "$int_gating" -ge 3 ]; then
  pass "$int_ref has ${int_gating} [GATING] markers (>=3)"
else
  fail "$int_ref has only ${int_gating} [GATING] markers (<3)"
fi
if grep -Fq 'single source of truth for data-analysis integration discipline' "$int_ref"; then
  pass "$int_ref contains shared-flow preamble phrase"
else
  fail "$int_ref missing shared-flow preamble phrase"
fi
ci_ref="skills/refactor-and-integrate/references/codebase-integration.md"
if grep -Eq '^## Economic Integration$|^## Data Discipline Through Refactoring$' "$ci_ref"; then
  fail "$ci_ref still carries '## Economic Integration' or '## Data Discipline Through Refactoring' heading (should be moved to $int_ref)"
else
  pass "$ci_ref no longer carries data-specific headings"
fi
iw_skill="skills/integration-workflow/SKILL.md"
if grep -qE 'winsorization|Economic Integration' "$iw_skill"; then
  fail "$iw_skill still contains data-specific tokens (winsorization / Economic Integration)"
else
  pass "$iw_skill free of data-specific tokens"
fi

# 17. README Workflow Map section exists and carries a Mermaid diagram (or
# a pipe-table fallback with >=5 data rows). The map visualizes the
# Stage-table in agents/implementer.md and agents/reviewer.md.
if grep -Fq '## Workflow Map' README.md; then
  pass "README.md contains '## Workflow Map' heading"
  # Extract the 100 lines after the heading to check for a mermaid fence or
  # a pipe-table with >=5 data rows.
  wm_region=$(awk '/^## Workflow Map/{flag=1} flag{print; n++; if(n>=100)exit}' README.md)
  if echo "$wm_region" | grep -q '^```mermaid'; then
    pass "Workflow Map contains a mermaid fenced code block"
  else
    # Fallback: count pipe-table data rows (lines starting with '|' and
    # containing at least 2 '|' characters, excluding separator rows).
    table_rows=$(echo "$wm_region" | grep -cE '^\|.*\|' | head -1)
    sep_rows=$(echo "$wm_region" | grep -cE '^\|[ :-]+\|' | head -1)
    data_rows=$((table_rows - sep_rows))
    if [ "$data_rows" -ge 5 ]; then
      pass "Workflow Map pipe-table has $data_rows data rows (>=5)"
    else
      fail "Workflow Map has neither a mermaid fence nor a pipe-table with >=5 data rows"
    fi
  fi
else
  fail "README.md missing '## Workflow Map' heading"
fi

# 18. README 'Why superRA?' lead section does not mention Iron Law.
why_section=$(awk '/^## Why superRA\?/{flag=1; next} /^## /{flag=0} flag' README.md | head -10)
if echo "$why_section" | grep -qi 'Iron Law'; then
  fail "README 'Why superRA?' lead mentions Iron Law — should be workflow-first"
else
  pass "README 'Why superRA?' lead is workflow-first"
fi

# 19. DRY / composability / extensibility design principle present in CLAUDE.md
# (Task 11 elevation). README.md no longer carries stale 'two-stage review'
# phrasing from the pre-Round-1 review-protocol docs (Task 11 scrub).
if grep -Fq 'DRY, composability, extensibility' CLAUDE.md; then
  pass "CLAUDE.md contains 'DRY, composability, extensibility' design principle"
else
  fail "CLAUDE.md missing 'DRY, composability, extensibility' design principle (Task 11)"
fi
if grep -Fq 'two-stage review' README.md; then
  fail "README.md still contains stale 'two-stage review' phrasing (should be scrubbed by Task 11)"
else
  pass "README.md free of stale 'two-stage review' phrasing"
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
