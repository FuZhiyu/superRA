#!/usr/bin/env bash
# Focused structural invariants for the Sync / Integrate contract.
# Run from the repo root: bash tests/test-sync-integration-contract.sh

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
  "Retired Upstream Intent section absent from runtime surfaces" \
  "## Upstream Intent" \
  skills/*/SKILL.md skills/*/references/*.md agents/*.md README.md CLAUDE.md .codex/agents/*.toml

assert_absent \
  "Retired MERGE_BASE_SHA variable absent from runtime surfaces" \
  "MERGE_BASE_SHA" \
  skills/*/SKILL.md skills/*/references/*.md agents/*.md README.md CLAUDE.md .codex/agents/*.toml

assert_absent \
  "Retired merge-quality reference absent from runtime surfaces" \
  "merge-quality.md" \
  skills/*/SKILL.md skills/*/references/*.md agents/*.md README.md CLAUDE.md .codex/agents/*.toml

assert_absent \
  "Refactor codebase-integration reference retired" \
  "codebase-integration.md" \
  skills/*/SKILL.md skills/*/references/*.md agents/*.md README.md CLAUDE.md .codex/agents/*.toml

assert_absent_regex \
  "Retired Phase B labels absent from runtime surfaces" \
  "Phase B|PhaseB|phase-b|phase b" \
  skills/*/SKILL.md skills/*/references/*.md agents/*.md README.md CLAUDE.md .codex/agents/*.toml

assert_absent_regex \
  "Writing templates defer source citations to markdown-link rule" \
  "file\\.(tex|ext):<line" \
  skills/writing/references/*.md skills/writing/references/consistency/*.md

assert_contains \
  "Skill manifest routes Sync to semantic merge" \
  "skills/using-superRA/SKILL.md" \
  '| `sync` | `superintegrate` Sync | `semantic-merge` |'

assert_contains \
  "Integration workflow dispatches a sync-stage author" \
  "skills/superintegrate/SKILL.md" \
  "Stage: sync"

assert_contains \
  "Integration workflow dispatches a generic sync author" \
  "skills/superintegrate/SKILL.md" \
  "Role: sync author"

assert_contains \
  "Integration workflow dispatches a generic sync reviewer" \
  "skills/superintegrate/SKILL.md" \
  "Role: sync reviewer"

assert_contains \
  "Integration workflow sync author loads mode reference" \
  "skills/superintegrate/SKILL.md" \
  "semantic-merge/references/workflow-sync-author.md"

assert_contains \
  "Integration workflow sync reviewer loads mode reference" \
  "skills/superintegrate/SKILL.md" \
  "semantic-merge/references/workflow-sync-reviewer.md"

assert_contains \
  "Integration workflow computes BASE_HEAD_SHA from base ref" \
  "skills/superintegrate/SKILL.md" \
  'BASE_HEAD_SHA=$(git rev-parse "$BASE_REF")'

assert_contains \
  "Integration workflow defines post-sync governing baseline" \
  "skills/superintegrate/SKILL.md" \
  "BASE_HEAD_SHA..HEAD"

assert_contains \
  "Integration review does not re-review semantic coherence" \
  "skills/superintegrate/SKILL.md" \
  "incoming-intent research or re-review semantic coherence"

assert_contains \
  "Integration workflow keeps Sync branch-level" \
  "skills/superintegrate/SKILL.md" \
  'Sync uses `Stage: sync` with generic sync author / sync reviewer agents'

assert_contains \
  "Skill manifest routes Protect to result protection" \
  "skills/using-superRA/SKILL.md" \
  '| `protection` | `superintegrate` Protect | `result-protection` |'

assert_contains \
  "Integration workflow dispatches Protect as protection stage" \
  "skills/superintegrate/SKILL.md" \
  'Dispatch protection-creator.** `Stage: protection`, canonical implementer template.'

assert_contains \
  "Result protection owns drift-test quality" \
  "skills/result-protection/references/drift-test-quality.md" \
  "# Drift Test Quality Standards"

assert_contains \
  "Econ drift tests load result-protection quality" \
  "skills/econ-data-analysis/references/integrate-drift-tests.md" \
  "skills/result-protection/references/drift-test-quality.md"

assert_contains \
  "Deprecated plan anatomy points to task-file contract" \
  "skills/handoff-doc/references/plan-anatomy.md" \
  "skills/task-tree/references/task-file-contract.md"

assert_contains \
  "Task-file contract keeps Sync Impact temporary" \
  "skills/task-tree/references/task-file-contract.md" \
  '**`## Sync Impact`** — conditional, integration-phase-only, temporary.'

assert_contains \
  "Integration closeout removes Sync Impact" \
  "skills/superintegrate/SKILL.md" \
  'remove every temporary task-local `## Sync Impact` section'

assert_absent \
  "Branch-level Sync Map is retired from runtime surfaces" \
  "## Sync Map" \
  skills/*/SKILL.md skills/*/references/*.md agents/*.md README.md CLAUDE.md superRA/task.md

assert_contains \
  "Workflow sync author keeps branch narrative in git log" \
  "skills/semantic-merge/references/workflow-sync-author.md" \
  "The branch-level narrative — incoming intent, resolution thesis, cluster breakdown — is carried by the merge commit message plus any propagation commit messages, i.e. the git log"

assert_contains \
  "Workflow sync author records pre-sync base input" \
  "skills/semantic-merge/references/workflow-sync-author.md" \
  "PRE_SYNC_BASE_SHA"

assert_contains \
  "Workflow sync author records synced base head input" \
  "skills/semantic-merge/references/workflow-sync-author.md" \
  "BASE_HEAD_SHA"

assert_contains \
  "Workflow sync author lands sync commits" \
  "skills/semantic-merge/references/workflow-sync-author.md" \
  "Land the merge commit plus any propagation commits needed to reach semantic coherence"

assert_contains \
  "Workflow sync author defines task-local Sync impact" \
  "skills/semantic-merge/references/workflow-sync-author.md" \
  "## Sync Impact"

assert_contains \
  "Task-local Sync impact is not an Integrate todo list" \
  "skills/semantic-merge/references/workflow-sync-author.md" \
  "not an Integrate to-do list"

assert_contains \
  "Workflow sync reviewer verifies git-log thesis and impact context" \
  "skills/semantic-merge/references/workflow-sync-reviewer.md" \
  "Confirm the branch-level thesis is carried by the sync commit messages (the git log), not buried in task-local sections."

assert_contains \
  "Workflow sync reviewer returns verdict and reviewed commits" \
  "skills/semantic-merge/references/workflow-sync-reviewer.md" \
  "Return the verdict plus the reviewed sync commit SHA(s)."

assert_contains \
  "Standalone semantic merge records resolution in commit body" \
  "skills/semantic-merge/references/standalone-merge.md" \
  "The commit body captures the resolution thesis"

assert_contains \
  "Semantic merge scope boundary defers codebase coherence" \
  "skills/semantic-merge/SKILL.md" \
  "Broader **codebase-coherence** work"

assert_contains \
  "Refactor and integrate uses Sync impact as evidence only" \
  "skills/refactor-and-integrate/SKILL.md" \
  "use it to justify existing post-sync hunks; it does not create new refactor targets."

assert_contains \
  "Refactor and integrate requires line by line governing diff review" \
  "skills/refactor-and-integrate/SKILL.md" \
  "Review the governing diff line by line."

assert_absent \
  "Refactor and integrate no longer owns drift-test quality" \
  "drift-test-quality.md" \
  "skills/refactor-and-integrate/SKILL.md" \
  "skills/refactor-and-integrate"

assert_contains \
  "Codebase integration requires no-change self-check" \
  "skills/refactor-and-integrate/SKILL.md" \
  "immediately before every return or commit, including no-change cases:"

assert_contains \
  "Codebase integration summarizes ordinary hunks by class" \
  "skills/refactor-and-integrate/SKILL.md" \
  "Summarize ordinary hunks by class."

assert_contains \
  "Codebase integration justifies suspicious hunks explicitly" \
  "skills/refactor-and-integrate/SKILL.md" \
  "Justify suspicious hunks by file and line/hunk."

assert_contains \
  "Codebase integration makes missing self-check blocking" \
  "skills/refactor-and-integrate/SKILL.md" \
  'A missing or stale trail is `[BLOCKING]`, including when no code changed.'

assert_contains \
  "Integration reviewer consumes Sync impact context" \
  "agents/reviewer.md" \
  "In Integrate, any Sync-impact-driven item also records the sync cluster"

assert_contains \
  "Integration reviewer uses BASE_HEAD_SHA pruning sweep" \
  "agents/reviewer.md" \
  'treat `git diff <BASE_HEAD_SHA>..HEAD` as a pruning sweep'

assert_contains \
  "Contributor gate applies no-overprescription line by line" \
  "CLAUDE.md" \
  "self-applies both tests below line by line"

assert_contains \
  "Planning workflow routes writing to planning reference" \
  "skills/superplan/SKILL.md" \
  '`superRA:writing`'

assert_contains \
  "Writing skill exposes planning reference" \
  "skills/writing/SKILL.md" \
  '`references/planning.md` | PLAN phase for large writing work'

assert_contains \
  "Writing planning reference declares PLAN-only retrofit marker" \
  "skills/writing/references/planning.md" \
  "**Writing workflow:** Long-form review retrofit (review-only; no ## Results)"

assert_absent \
  "Planning workflow does not own writing PLAN-only retrofit marker" \
  "Long-form review retrofit" \
  "skills/superplan/SKILL.md"

assert_absent \
  "Planning workflow does not own PLAN-only exception prose" \
  "PLAN-only" \
  "skills/superplan/SKILL.md"

assert_absent \
  "Planning workflow does not own no-RESULTS exception prose" \
  "no RESULTS.md" \
  "skills/superplan/SKILL.md"

assert_absent \
  "Implementation workflow does not own writing PLAN-only retrofit" \
  "Long-form review retrofit" \
  "skills/superimplement/SKILL.md"

assert_absent \
  "Long-form review no longer names REVIEW.md" \
  "REVIEW.md" \
  "skills/writing/references/long-form-review.md"

assert_absent \
  "Long-form review no longer has staged lifecycle labels" \
  "Stage 1" \
  "skills/writing/references/long-form-review.md"

assert_absent \
  "Long-form review no longer has Stage 2 label" \
  "Stage 2" \
  "skills/writing/references/long-form-review.md"

assert_absent \
  "Long-form review no longer uses shared Findings section" \
  "## Findings" \
  "skills/writing/references/long-form-review.md"

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi

exit 0
