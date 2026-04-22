#!/usr/bin/env bash
# Focused structural invariants for the Phase B upstream-intent contract.
# Run from the repo root: bash tests/test-phase-b-upstream-intent-contract.sh

set -euo pipefail

cd "$(dirname "$0")/.."

pass=0
fail=0
failed_names=()

record_pass() {
  printf 'PASS  %s\n' "$1"
  pass=$((pass + 1))
}

record_fail() {
  printf 'FAIL  %s\n' "$1"
  fail=$((fail + 1))
  failed_names+=("$1")
}

assert_contains() {
  local name="$1"
  local file="$2"
  local pattern="$3"

  if rg -n --fixed-strings -- "$pattern" "$file" >/dev/null; then
    record_pass "$name"
  else
    printf '      missing pattern: %s (%s)\n' "$pattern" "$file"
    record_fail "$name"
  fi
}

assert_absent() {
  local name="$1"
  local pattern="$2"
  shift 2

  local matches
  matches=$(rg -n --fixed-strings -- "$pattern" "$@" || true)
  if [ -z "$matches" ]; then
    record_pass "$name"
  else
    printf '      unexpected matches for %s:\n%s\n' "$pattern" "$matches"
    record_fail "$name"
  fi
}

assert_absent_regex() {
  local name="$1"
  local pattern="$2"
  shift 2

  local matches
  matches=$(rg -n --regexp "$pattern" "$@" || true)
  if [ -z "$matches" ]; then
    record_pass "$name"
  else
    printf '      unexpected regex matches for %s:\n%s\n' "$pattern" "$matches"
    record_fail "$name"
  fi
}

assert_absent \
  "Retired Integration Intent label removed from canonical runtime surfaces" \
  "Integration Intent" \
  skills agents

assert_absent_regex \
  "Retired Universal Principles header not reintroduced in canonical runtime surfaces" \
  "^## Universal Principles$" \
  skills agents

assert_contains \
  "Plan anatomy defines Upstream Intent heading" \
  "skills/handoff-doc/references/plan-anatomy.md" \
  "## Upstream Intent"

assert_contains \
  "Plan anatomy records the base-branch anchor" \
  "skills/handoff-doc/references/plan-anatomy.md" \
  "**Base branch:**"

assert_contains \
  "Plan anatomy records the frozen merge base" \
  "skills/handoff-doc/references/plan-anatomy.md" \
  "**Frozen merge base SHA:**"

assert_contains \
  "Plan anatomy records the reviewed upstream range" \
  "skills/handoff-doc/references/plan-anatomy.md" \
  "**Reviewed upstream range:**"

assert_contains \
  "Plan anatomy defines upstream change clusters" \
  "skills/handoff-doc/references/plan-anatomy.md" \
  "**Upstream change cluster ("

assert_contains \
  "Plan anatomy defines the default merged expectation" \
  "skills/handoff-doc/references/plan-anatomy.md" \
  "**Default merged expectation:**"

assert_contains \
  "Reviewer protocol records upstream file or commit evidence" \
  "agents/reviewer.md" \
  "upstream file / commit / change"

assert_contains \
  "Reviewer protocol records the minimal allowed branch delta" \
  "agents/reviewer.md" \
  "minimal allowed branch delta"

assert_contains \
  "Reviewer protocol records stale branch-side content that must not survive" \
  "agents/reviewer.md" \
  "stale branch-side content that must not survive"

assert_contains \
  "Implementer protocol requires reading Upstream Intent before integration edits" \
  "agents/implementer.md" \
  'At Stage `integration`, also read `## Upstream Intent`'

assert_contains \
  "Implementer protocol keeps Upstream Intent hands-off" \
  "agents/implementer.md" \
  "do not rewrite, append to, or delete it"

assert_contains \
  "Integration workflow computes MERGE_BASE_SHA from the chosen base branch" \
  "skills/integration-workflow/SKILL.md" \
  'MERGE_BASE_SHA=$(git merge-base HEAD origin/<base-branch>)'

assert_contains \
  "Integration workflow preserves the no-material-upstream-change path" \
  "skills/integration-workflow/SKILL.md" \
  'If (b) finds no material overlap, do not create `## Upstream Intent`.'

assert_contains \
  "Integration workflow requires reviewer confirmation of the surviving diff" \
  "skills/integration-workflow/SKILL.md" \
  'every surviving hunk in `git diff <MERGE_BASE_SHA>..HEAD` is justified'

assert_contains \
  "Refactor-and-integrate uses the frozen merge base diff" \
  "skills/refactor-and-integrate/SKILL.md" \
  "git diff <frozen-merge-base>..HEAD"

assert_contains \
  "Refactor-and-integrate keeps upstream deletions and relocations authoritative" \
  "skills/refactor-and-integrate/SKILL.md" \
  "upstream deletions and relocations remain deleted or relocated"

assert_contains \
  "Codebase integration makes base-diff pruning mandatory" \
  "skills/refactor-and-integrate/references/codebase-integration.md" \
  "Base-diff pruning is part of every integration review pass"

assert_contains \
  "Codebase integration guards against silent restorations" \
  "skills/refactor-and-integrate/references/codebase-integration.md" \
  "Upstream deletions / relocations honored by default"

assert_contains \
  "Merge-quality reference defines the Phase B upstream contract" \
  "skills/refactor-and-integrate/references/merge-quality.md" \
  "### Phase B upstream contract"

assert_contains \
  "Merge-quality reference uses the base-owned-by-default rule" \
  "skills/refactor-and-integrate/references/merge-quality.md" \
  "Start from **base-owned by default**"

assert_contains \
  "Merge-quality reference forbids silent restorations" \
  "skills/refactor-and-integrate/references/merge-quality.md" \
  "**No silent restorations.**"

assert_contains \
  "Semantic merge carries the Phase B base-intent rule" \
  "skills/semantic-merge/SKILL.md" \
  '**Phase B rule:** When this skill is called from `integration-workflow` Phase B, preserve base intent by default.'

assert_contains \
  "Semantic merge uses Upstream Intent as Phase B authority" \
  "skills/semantic-merge/SKILL.md" \
  'When called from Phase B, use `## Upstream Intent` as the authority for what survives'

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi

exit 0
