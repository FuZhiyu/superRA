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

if [ "$(readlink AGENT.md 2>/dev/null)" = "CLAUDE.md" ]; then
  pass "AGENT.md is a symlink to CLAUDE.md"
else
  fail "AGENT.md must be a symlink to CLAUDE.md"
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
    fail "superRA:$name — invocation does not resolve to a skills/ directory"
  fi
done
[ $broken_live -eq 0 ] && pass "all superRA: invocations in live surface resolve"

# 3. Iron Law preserved in econ-data-analysis main SKILL.md body; the
# Describe / Analyze / Validate content is consolidated back into the
# main body as §Three Concurrent Disciplines (teaching + inline
# severity-marked checklist), replacing the former split between a
# short intro and references/disciplines.md. Pitfalls and Common
# Rationalizations stay in the main body (both roles load them).
# These are load-bearing and must not drift further.
grep -q '^NO TRANSFORMATION WITHOUT PRIOR DESCRIPTION$' skills/econ-data-analysis/SKILL.md \
  && pass "Iron Law in econ-data-analysis main body" \
  || fail "Iron Law missing from econ-data-analysis main body"
for section in '## Three Concurrent Disciplines' '### Describe' '### Analyze' '### Validate' '## Pitfalls' '## Common Rationalizations'; do
  if grep -Fq "$section" skills/econ-data-analysis/SKILL.md; then
    pass "main body contains '$section'"
  else
    fail "main body missing '$section'"
  fi
done
if [ -f skills/econ-data-analysis/references/disciplines.md ]; then
  fail "references/disciplines.md should be deleted — content consolidated into SKILL.md §Three Concurrent Disciplines"
else
  pass "references/disciplines.md correctly absent (consolidated into SKILL.md)"
fi

# 3b. Validate section must carry a Sensitivity analysis sub-section — this
# is the first-class execution-phase discipline. Post-consolidation it
# lives in SKILL.md §Validate.
if grep -Fq '**Sensitivity analysis**' skills/econ-data-analysis/SKILL.md; then
  pass "SKILL.md §Validate contains Sensitivity analysis sub-section"
else
  fail "SKILL.md §Validate missing Sensitivity analysis sub-section"
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

# 6b. Every skill frontmatter parses and descriptions stay concise.
if ruby -e '
require "yaml"
Dir["skills/*/SKILL.md"].sort.each do |f|
  text = File.read(f)
  abort("missing frontmatter #{f}") unless text.start_with?("---\n")
  boundary = text.index("\n---\n", 4) or abort("unterminated frontmatter #{f}")
  data = YAML.safe_load(text[4...boundary]) or abort("empty frontmatter #{f}")
  desc = data["description"].to_s
  abort("description too long #{f}: #{desc.length}") if desc.length > 500
end
' >/dev/null 2>&1; then
  pass "skill frontmatter parses and every description is <=500 chars"
else
  fail "skill frontmatter parse or description-length invariant failed"
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
# (legacy over-specification; Work-from is cwd by default, Counterpart was
# previously set at team-spawn time in the now-archived Agent Teams mode).
if grep -n 'Work from:\|Counterpart:' $dispatch_files 2>/dev/null | grep -v '^[^:]*:[[:space:]]*#'; then
  fail "dispatch templates still contain 'Work from:' or 'Counterpart:' lines"
else
  pass "no dispatch template carries 'Work from:' or 'Counterpart:' fields"
fi

# 11. econ-data-analysis §Three Concurrent Disciplines integration.
# The consolidated section in the SKILL.md main body is the single source
# of truth — teaching content + shared severity-marked checklist that
# both implementer self-check and reviewer verification walk.
# Encoded here: heading exists, severity markers present (≥8 BLOCKING),
# the two-verdict protocol is in place (APPROVE/REVISE, no CONDITIONAL
# APPROVE carryover), and no separate implementation-review.md /
# integration-review.md reference file was created (shared-gating
# decision sanity check).
eda_skill="skills/econ-data-analysis/SKILL.md"
if grep -Fq '## Three Concurrent Disciplines' "$eda_skill"; then
  pass "econ-data-analysis SKILL.md contains '## Three Concurrent Disciplines' heading"
else
  fail "econ-data-analysis SKILL.md missing '## Three Concurrent Disciplines' heading"
fi
blocking_count=$(grep -c '\[BLOCKING\]' "$eda_skill" 2>/dev/null || echo 0)
if [ "$blocking_count" -ge 8 ]; then
  pass "econ-data-analysis SKILL.md has ${blocking_count} [BLOCKING] markers (>=8)"
else
  fail "econ-data-analysis SKILL.md has only ${blocking_count} [BLOCKING] markers (<8)"
fi
if grep -qE '\[GATING\]|\[STANDARD\]' "$eda_skill"; then
  fail "econ-data-analysis SKILL.md still contains [GATING] or [STANDARD] markers — should be [BLOCKING] after severity consolidation"
else
  pass "econ-data-analysis SKILL.md free of legacy [GATING] / [STANDARD] markers"
fi
if grep -Fq 'CONDITIONAL APPROVE' "$eda_skill"; then
  fail "econ-data-analysis SKILL.md still mentions CONDITIONAL APPROVE — should be removed with verdict simplification"
else
  pass "econ-data-analysis SKILL.md free of CONDITIONAL APPROVE references"
fi
if [ -f skills/econ-data-analysis/references/implementation-review.md ] \
   || [ -f skills/econ-data-analysis/references/integration-review.md ]; then
  fail "shared-gating decision violated: implementation-review.md / integration-review.md reference file exists"
else
  pass "no separate implementation-review.md / integration-review.md reference (shared gating in main body)"
fi

# 12. execution-workflow domain-agnosticism invariants.
# The workflow skill should no longer carry data-flavored two-stage review
# language or legacy CONDITIONAL APPROVE references, and should have
# dropped the data-analysis-specific Sensitivity Analysis Tasks section.
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
  fail "execution-workflow SKILL.md still mentions CONDITIONAL APPROVE — should be removed with verdict simplification"
else
  pass "execution-workflow SKILL.md free of CONDITIONAL APPROVE references"
fi

# 13. Agent files point at the manifest for stage-based loads; the
# dispatch-prompt contract phrase is preserved; reviewer uses the
# two-verdict APPROVE/REVISE protocol (no CONDITIONAL APPROVE).
for f in agents/implementer.md agents/reviewer.md; do
  if grep -Fq 'Skill-Load Manifest' "$f"; then
    pass "$f points at using-superRA §Skill-Load Manifest"
  else
    fail "$f missing pointer to using-superRA §Skill-Load Manifest"
  fi
  if grep -Fq 'dispatch prompt carries' "$f"; then
    pass "$f preserves the dispatch-prompt contract paragraph"
  else
    fail "$f missing dispatch-prompt contract paragraph"
  fi
done
if grep -Fq 'CONDITIONAL APPROVE' agents/reviewer.md; then
  fail "agents/reviewer.md still mentions CONDITIONAL APPROVE — should be removed with verdict simplification"
else
  pass "agents/reviewer.md free of CONDITIONAL APPROVE references"
fi

# 14. Cross-stage orchestration content lives in agent-orchestration, not
# execution-workflow. agent-orchestration/SKILL.md owns these top-level
# sections: Workload Balancing, Dispatch Templates, Handling Reviewer
# Feedback, Review Status Reference. Dispatch-Return Deltas was removed
# (D1 in the feedback round — content lives in agents/implementer.md and
# agents/reviewer.md §Report Format). Direct Mode was relocated to
# using-superRA in Round 3 and no longer appears here. execution-workflow/
# SKILL.md does NOT carry '## Dispatch Templates' as a heading (pointers to
# agent-orchestration only).
ao_skill="skills/agent-orchestration/SKILL.md"
ao_missing=0
for h in '^## Workload Balancing$' \
         '^## Dispatch Templates$' \
         '^## Handling Reviewer Feedback' \
         '^## Review Status Reference$'; do
  if grep -Eq "$h" "$ao_skill"; then
    :
  else
    fail "agent-orchestration SKILL.md missing heading matching: $h"
    ao_missing=$((ao_missing+1))
  fi
done
[ "$ao_missing" -eq 0 ] && pass "agent-orchestration SKILL.md owns the four cross-stage orchestration sections (Workload Balancing, Dispatch Templates, Handling Reviewer Feedback, Review Status Reference)"
if grep -Eq '^## Dispatch-Return Deltas$' "$ao_skill"; then
  fail "agent-orchestration SKILL.md still carries '## Dispatch-Return Deltas' (removed in D1 — content lives in agent files)"
else
  pass "agent-orchestration SKILL.md no longer carries '## Dispatch-Return Deltas'"
fi
if grep -Eq '^## Integration$' "$ao_skill"; then
  fail "agent-orchestration SKILL.md still carries '## Integration' (removed in D2 — Teams-mode-specific content archived)"
else
  pass "agent-orchestration SKILL.md no longer carries '## Integration' section"
fi
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
# for the data-specific `integration` stage checklist; generic code-integration
# content stays in refactor-and-integrate/references/codebase-integration.md;
# integration-workflow/SKILL.md carries no data-specific tokens
# (workflow-choreography only).
int_ref="skills/econ-data-analysis/references/integration.md"
if [ -f "$int_ref" ]; then
  pass "exists: $int_ref"
else
  fail "missing: $int_ref"
fi
int_blocking=$(grep -c '\[BLOCKING\]' "$int_ref" 2>/dev/null || echo 0)
if [ "$int_blocking" -ge 3 ]; then
  pass "$int_ref has ${int_blocking} [BLOCKING] markers (>=3)"
else
  fail "$int_ref has only ${int_blocking} [BLOCKING] markers (<3)"
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

# 20. using-superRA is the master skill: carries the principles + inventory +
# skill-load manifest + execution modes; references/main-agent.md is
# the main-agent-only bootstrap reference; <SUBAGENT-STOP> is retired.
us_skill="skills/using-superRA/SKILL.md"
us_missing=0
for h in '^## Skill-Load Manifest$' \
         '^## Skill Inventory$' \
         '^## Execution Modes$'; do
  if grep -Eq "$h" "$us_skill"; then
    :
  else
    fail "using-superRA SKILL.md missing heading matching: $h"
    us_missing=$((us_missing+1))
  fi
done
[ "$us_missing" -eq 0 ] && pass "using-superRA SKILL.md carries Skill-Load Manifest + Skill Inventory + Execution Modes"
# Six Stage rows in the manifest, backtick-wrapped stage names in column 1.
# `refactoring` and `integration-review` collapsed into a single `integration` row.
stage_rows=$(grep -cE '^\| `(implementation|integration|drift-test|merge|documentation|planning-review)`' "$us_skill")
if [ "$stage_rows" -eq 6 ]; then
  pass "using-superRA Skill-Load Manifest has exactly 6 Stage rows"
else
  fail "using-superRA Skill-Load Manifest has $stage_rows Stage rows (expected 6)"
fi
# handoff-doc is mentioned in the manifest preamble and in the documentation/
# planning-review rows (Task 6 dropped it from everyday implementer/reviewer
# rows); it also appears in the skill inventory. >=3 live mentions is the floor.
handoff_hits=$(grep -c 'handoff-doc' "$us_skill")
if [ "$handoff_hits" -ge 3 ]; then
  pass "using-superRA SKILL.md mentions handoff-doc in >=3 places"
else
  fail "using-superRA SKILL.md mentions handoff-doc only $handoff_hits times (expected >=3)"
fi
if grep -Fq '<SUBAGENT-STOP>' "$us_skill"; then
  fail "using-superRA SKILL.md still contains <SUBAGENT-STOP> (should be retired in Round 3)"
else
  pass "using-superRA SKILL.md is free of <SUBAGENT-STOP>"
fi
if [ -f skills/using-superRA/references/main-agent.md ]; then
  pass "exists: skills/using-superRA/references/main-agent.md"
else
  fail "missing: skills/using-superRA/references/main-agent.md"
fi

# 21b. Codex plugin/install surfaces exist and point at the canonical skills tree.
python3 -c "import json; data=json.load(open('.codex-plugin/plugin.json')); assert data['name']=='superra'; assert data['skills']=='./skills/'" 2>/dev/null \
  && pass ".codex-plugin/plugin.json exists and points at ./skills/" \
  || fail ".codex-plugin/plugin.json missing or malformed"
python3 -c "import json; data=json.load(open('.agents/plugins/marketplace.json')); entry=data['plugins'][0]; assert entry['name']=='superra'; assert entry['source']['path']=='./'" 2>/dev/null \
  && pass ".agents/plugins/marketplace.json exists and points at plugin root" \
  || fail ".agents/plugins/marketplace.json missing or malformed"

# 21c. Codex repo-local skill exposure mirrors the canonical skills tree.
codex_links_missing=0
for skill in $(ls -d skills/*/ 2>/dev/null | sed 's|skills/||;s|/$||'); do
  link=".agents/skills/$skill"
  if [ ! -L "$link" ]; then
    fail "$link must be a symlink to ../../skills/$skill"
    codex_links_missing=$((codex_links_missing+1))
    continue
  fi
  target=$(readlink "$link")
  if [ "$target" = "../../skills/$skill" ]; then
    :
  else
    fail "$link points to $target (expected ../../skills/$skill)"
    codex_links_missing=$((codex_links_missing+1))
  fi
done
[ "$codex_links_missing" -eq 0 ] && pass ".agents/skills exposes every canonical skill via symlink"

# 21d. Generated Codex agents stay in sync with the canonical role specs.
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check >/dev/null 2>&1 \
  && pass "generated project-scoped Codex agents are up to date" \
  || fail "project-scoped Codex agents drift from agents/*.md"
python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py >/dev/null 2>&1 \
  && pass "codex agent sync script tests pass" \
  || fail "codex agent sync script tests failed"

# 21. Stage tables retired on agent files; frontmatter preload applied;
# auto-load language retired from live prose (PLAN.md, RELEASE-NOTES.md, and
# RESULTS.md excluded — these carry self-referential retirement language
# describing the decision and its documentation history).
for f in agents/implementer.md agents/reviewer.md; do
  if head -20 "$f" | grep -Fq 'superRA:using-superRA'; then
    pass "$f frontmatter preloads superRA:using-superRA"
  else
    fail "$f frontmatter does not preload superRA:using-superRA"
  fi
done
impl_row_hits=$(grep -c '^| `implementation`' agents/implementer.md agents/reviewer.md 2>/dev/null | awk -F: '{s+=$2} END {print s+0}')
if [ "$impl_row_hits" -eq 0 ]; then
  pass "agent files no longer carry the old multi-row Stage table (no '| \`implementation\`' rows)"
else
  fail "agent files still carry $impl_row_hits '| \`implementation\`' rows (old Stage table)"
fi
dtc_row_hits=$(grep -c '^| `drift test creation`' agents/implementer.md agents/reviewer.md 2>/dev/null | awk -F: '{s+=$2} END {print s+0}')
if [ "$dtc_row_hits" -eq 0 ]; then
  pass "agent files no longer carry '| \`drift test creation\`' rows"
else
  fail "agent files still carry $dtc_row_hits '| \`drift test creation\`' rows"
fi
al_hits=$(grep -rl 'auto-load' agents/ skills/ README.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$al_hits" -eq 0 ]; then
  pass "auto-load language retired from live prose (agents/, skills/, README.md)"
else
  fail "auto-load still appears in $al_hits file(s) under agents/, skills/, or README.md"
fi

# 22. Agent Teams mode is archived: references/agent-teams.md carries the
# ARCHIVED banner and no active file under skills/, agents/, or hooks/
# cites it. SKILL.md no longer carries '### Team Recipes' or a top-level
# '## Direct Mode' heading.
at_ref="skills/agent-orchestration/references/agent-teams.md"
if [ -f "$at_ref" ]; then
  if head -10 "$at_ref" | grep -q 'ARCHIVED'; then
    pass "$at_ref carries ARCHIVED banner"
  else
    fail "$at_ref is missing the ARCHIVED banner"
  fi
else
  fail "missing: $at_ref"
fi
# No active file under skills/ (excluding the archived reference itself and
# its subtree), agents/, or hooks/ cites the archived content or the Teams
# mode. RELEASE-NOTES.md is excluded — historical references are expected.
active_team_refs=$(grep -rln -E 'agent-teams\.md|TeamCreate|Agent Team|Team mode' \
  skills/ agents/ hooks/ 2>/dev/null \
  | grep -v '^skills/agent-orchestration/references/agent-teams\.md$' \
  || true)
if [ -z "$active_team_refs" ]; then
  pass "no active file under skills/, agents/, or hooks/ cites archived agent-teams content"
else
  fail "active files still reference Teams content: $active_team_refs"
fi
if grep -Fq '### Team Recipes' skills/agent-orchestration/SKILL.md; then
  fail "agent-orchestration SKILL.md still contains '### Team Recipes' (stale)"
else
  pass "agent-orchestration SKILL.md no longer contains '### Team Recipes'"
fi
if grep -Eq '^## Direct Mode$' skills/agent-orchestration/SKILL.md; then
  fail "agent-orchestration SKILL.md still contains '## Direct Mode' heading (relocated to using-superRA)"
else
  pass "agent-orchestration SKILL.md no longer contains a top-level '## Direct Mode' heading"
fi

# 23. Direct Mode canonicalized in using-superRA §Execution Modes; no other
# SKILL.md carries a §Direct Mode reference.
if grep -Fq '## Execution Modes' "$us_skill" && grep -Fq 'Direct mode' "$us_skill"; then
  pass "using-superRA SKILL.md carries Execution Modes and Direct mode content"
else
  fail "using-superRA SKILL.md missing Execution Modes or Direct mode content"
fi
dm_hits=$(grep -rl '§Direct Mode' skills/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$dm_hits" -eq 0 ]; then
  pass "no SKILL.md carries a §Direct Mode reference (all retargeted to §Execution Modes)"
else
  fail "§Direct Mode still referenced in $dm_hits SKILL.md file(s)"
fi

# 24. Handoff-doc principles: the four document principles live in
# handoff-doc/SKILL.md under §The Four Principles (the canonical home).
# using-superRA must not duplicate that content — it owns universal principles,
# skill inventory, and the manifest; handoff-doc discipline is referenced, not
# restated. handoff-doc is loaded by doc-creators and on demand by other agents.
hd_skill="skills/handoff-doc/SKILL.md"
if grep -Eq '^4\. \*\*Ownership by role' "$hd_skill"; then
  fail "handoff-doc SKILL.md still contains old principle #4 'Ownership by role'"
else
  pass "handoff-doc SKILL.md no longer contains old principle #4 'Ownership by role'"
fi
if grep -Eq '^5\. \*\*Explicit what-changed' "$hd_skill"; then
  fail "handoff-doc SKILL.md still contains old principle #5 'Explicit what-changed'"
else
  pass "handoff-doc SKILL.md no longer contains old principle #5 'Explicit what-changed'"
fi
if grep -Fq '## The Four Principles' "$hd_skill"; then
  pass "handoff-doc SKILL.md carries '## The Four Principles' heading"
else
  fail "handoff-doc SKILL.md missing '## The Four Principles' heading"
fi
hd_principle_count=$(awk '/^## The Four Principles/{flag=1; next} /^## /{flag=0} flag' "$hd_skill" | grep -cE '^[0-9]+\. \*\*')
if [ "$hd_principle_count" -eq 4 ]; then
  pass "handoff-doc §The Four Principles has exactly 4 numbered principles"
else
  fail "handoff-doc §The Four Principles has $hd_principle_count numbered principles (expected 4)"
fi
if grep -Fq '## Handoff Doc Discipline' "$us_skill"; then
  fail "using-superRA SKILL.md still carries '## Handoff Doc Discipline' section — handoff-doc owns this now"
else
  pass "using-superRA SKILL.md no longer carries '## Handoff Doc Discipline' section (owned by handoff-doc)"
fi

# 25. econ-data-analysis/references/integration.md contains the new
# Document-code consistency [BLOCKING] item added in Round 3.
if grep -Fq 'Document-code consistency' skills/econ-data-analysis/references/integration.md; then
  pass "integration.md contains 'Document-code consistency' item"
else
  fail "integration.md missing 'Document-code consistency' item"
fi

# 26. agent-orchestration carries the three-tier Workload Balancing framework
# (F2 in the feedback round). Must have the heading, all three tier headings,
# the 150k-token rule, and the cache-reuse guidance.
ao="skills/agent-orchestration/SKILL.md"
if grep -q "^## Workload Balancing" "$ao"; then
  pass "$ao has §Workload Balancing heading"
else
  fail "$ao is missing §Workload Balancing heading"
fi
tier_count=$(grep -c "^### Tier [123]" "$ao" || true)
if [ "$tier_count" -eq 3 ]; then
  pass "$ao has all three tiers"
else
  fail "$ao has $tier_count tiers (expected 3)"
fi
if grep -q "150k" "$ao"; then
  pass "$ao references 150k-token rule"
else
  fail "$ao missing 150k guidance"
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
