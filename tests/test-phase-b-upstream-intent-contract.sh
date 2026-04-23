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
  "Plan anatomy makes the reviewer own the active Upstream Intent section" \
  "skills/handoff-doc/references/plan-anatomy.md" \
  "Reviewer-owned for the active Phase B round."

assert_contains \
  "Plan anatomy removes Upstream Intent at Phase B closeout" \
  "skills/handoff-doc/references/plan-anatomy.md" \
  'Phase B Step 4 removes the section in the same closeout commit that flips `Refactored`.'

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
  "Reviewer protocol owns the active Upstream Intent section" \
  "agents/reviewer.md" \
  "reviewer-owned for the active Phase B round"

assert_contains \
  "Implementer protocol requires reading task block plus relevant header context" \
  "agents/implementer.md" \
  'Read the full task block and the relevant `PLAN.md` header context before you start.'

assert_contains \
  "Implementer protocol keeps the PLAN header read-only" \
  "agents/implementer.md" \
  "Read it, but do not edit it."

assert_contains \
  "Reviewer protocol keeps narrow re-review plus a branch-wide pruning sweep" \
  "agents/reviewer.md" \
  'treat `git diff <MERGE_BASE_SHA>..HEAD` as a pruning sweep, not a fresh full-task checklist walk'

assert_contains \
  "Integration workflow computes MERGE_BASE_SHA from the chosen base branch" \
  "skills/integration-workflow/SKILL.md" \
  'MERGE_BASE_SHA=$(git merge-base HEAD origin/<base-branch>)'

assert_contains \
  "Integration workflow dispatch loads the Upstream Intent anatomy reference" \
  "skills/integration-workflow/SKILL.md" \
  'References: `superRA:handoff-doc` `references/plan-anatomy.md` §Upstream Intent'

assert_contains \
  "Integration workflow passes base context through the reviewer dispatch" \
  "skills/integration-workflow/SKILL.md" \
  'context while doing (b): base branch `origin/<base-branch>`, frozen'

assert_contains \
  "Integration workflow tells the reviewer to use the handoff reference for section format" \
  "skills/integration-workflow/SKILL.md" \
  "Use the cited handoff reference for the section's"

assert_contains \
  "Integration workflow leaves Upstream Intent absent when not needed" \
  "skills/integration-workflow/SKILL.md" \
  'If (b) finds no material overlap, leave `## Upstream Intent` absent'

assert_contains \
  "Integration workflow requires reviewer confirmation of the surviving diff" \
  "skills/integration-workflow/SKILL.md" \
  'every surviving hunk in `git diff <MERGE_BASE_SHA>..HEAD` is justified'

assert_contains \
  "Integration workflow uses one reviewer pass for re-review plus pruning" \
  "skills/integration-workflow/SKILL.md" \
  "Do one reviewer pass over the cumulative diff."

assert_contains \
  "Integration workflow treats branch-wide confirmation as pruning, not a fresh checklist walk" \
  "skills/integration-workflow/SKILL.md" \
  "Treat that branch-wide pass as pruning, not a fresh checklist walk"

assert_contains \
  "Integration workflow removes Upstream Intent at Phase B closeout" \
  "skills/integration-workflow/SKILL.md" \
  "deletes it in the same closeout commit before proceeding to Phase C"

assert_contains \
  "Refactor-and-integrate keeps the frozen merge base diff for Phase B paths" \
  "skills/refactor-and-integrate/SKILL.md" \
  '**Phase B / upstream-contract path:** implementer runs `git diff <frozen-merge-base>..HEAD`'

assert_contains \
  "Refactor-and-integrate keeps upstream deletions and relocations authoritative" \
  "skills/refactor-and-integrate/SKILL.md" \
  "upstream deletions and relocations remain deleted or relocated"

assert_contains \
  "Refactor-and-integrate defines a non-Phase-B baseline rule" \
  "skills/refactor-and-integrate/SKILL.md" \
  "use the task's governing git range or touched-file diff as the baseline"

assert_contains \
  "Codebase integration makes base-diff pruning mandatory" \
  "skills/refactor-and-integrate/references/codebase-integration.md" \
  "Base-diff pruning is part of every integration review pass"

assert_contains \
  "Codebase integration guards against silent restorations" \
  "skills/refactor-and-integrate/references/codebase-integration.md" \
  "Upstream deletions / relocations honored by default"

assert_contains \
  "Merge-quality reference defines the upstream-intent source section" \
  "skills/refactor-and-integrate/references/merge-quality.md" \
  "### Identify governing upstream intent"

assert_contains \
  "Merge-quality reference uses the base-owned-by-default rule" \
  "skills/refactor-and-integrate/references/merge-quality.md" \
  "Start from **base-owned by default**"

assert_contains \
  "Merge-quality reference supports standalone caller-supplied upstream intent" \
  "skills/refactor-and-integrate/references/merge-quality.md" \
  "Standalone caller: use the caller-supplied context that records upstream intent for this merge"

assert_contains \
  "Merge-quality reference forbids silent restorations" \
  "skills/refactor-and-integrate/references/merge-quality.md" \
  "**No silent restorations.**"

assert_contains \
  "Semantic merge defines the governing upstream-intent rule" \
  "skills/semantic-merge/SKILL.md" \
  '**Upstream-intent rule:** Identify the governing upstream intent before changing files.'

assert_contains \
  "Semantic merge preserves base intent by default" \
  "skills/semantic-merge/SKILL.md" \
  "Preserve base intent by default: the merged tree should match the base branch unless approved task objectives or the recorded contract explicitly authorize a surviving branch-side delta."

assert_contains \
  "Semantic merge supports standalone caller-supplied upstream intent" \
  "skills/semantic-merge/SKILL.md" \
  "Otherwise use the caller-supplied upstream-intent context for the incoming objective and allowed deltas."

assert_absent_regex \
  "Explicit Phase B re-entry mnemonics removed from canonical runtime surfaces" \
  "B->B|B→B|D->B" \
  skills agents

assert_absent \
  "Split ownership wording removed from canonical runtime surfaces" \
  "Shared Phase B ownership with a narrow split" \
  skills agents

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi

exit 0
