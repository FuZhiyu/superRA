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

assert_contains \
  "Skill manifest routes Sync to semantic merge" \
  "skills/using-superRA/SKILL.md" \
  '| `sync` | `integration-workflow` Sync | `semantic-merge` |'

assert_contains \
  "Integration workflow dispatches a sync-stage author" \
  "skills/integration-workflow/SKILL.md" \
  "Stage: sync"

assert_contains \
  "Integration workflow dispatches a generic sync author" \
  "skills/integration-workflow/SKILL.md" \
  "Role: sync author"

assert_contains \
  "Integration workflow dispatches a generic sync reviewer" \
  "skills/integration-workflow/SKILL.md" \
  "Role: sync reviewer"

assert_contains \
  "Integration workflow sync author loads mode reference" \
  "skills/integration-workflow/SKILL.md" \
  "semantic-merge/references/workflow-sync-author.md"

assert_contains \
  "Integration workflow sync reviewer loads mode reference" \
  "skills/integration-workflow/SKILL.md" \
  "semantic-merge/references/workflow-sync-reviewer.md"

assert_contains \
  "Integration workflow computes BASE_HEAD_SHA from base ref" \
  "skills/integration-workflow/SKILL.md" \
  'BASE_HEAD_SHA=$(git rev-parse "$BASE_REF")'

assert_contains \
  "Integration workflow defines post-sync governing baseline" \
  "skills/integration-workflow/SKILL.md" \
  "BASE_HEAD_SHA..HEAD"

assert_contains \
  "Integration review does not re-review semantic coherence" \
  "skills/integration-workflow/SKILL.md" \
  "Do not recreate incoming-intent"

assert_contains \
  "Skill manifest keeps Sync branch-level" \
  "skills/using-superRA/SKILL.md" \
  '`Stage: sync` is branch-level'

assert_contains \
  "Skill manifest routes Protect to result protection" \
  "skills/using-superRA/SKILL.md" \
  '| `protection` | `integration-workflow` Protect | `result-protection` |'

assert_contains \
  "Integration workflow dispatches Protect as protection stage" \
  "skills/integration-workflow/SKILL.md" \
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
  "Plan anatomy defines Sync Map section" \
  "skills/handoff-doc/references/plan-anatomy.md" \
  "## Sync Map"

assert_contains \
  "Plan anatomy says Integrate does not turn Sync notes into backlog" \
  "skills/handoff-doc/references/plan-anatomy.md" \
  "It does not re-review semantic sync or turn Sync notes into a backlog."

assert_contains \
  "Plan anatomy keeps Sync impact task-local and temporary" \
  "skills/handoff-doc/references/plan-anatomy.md" \
  '**`**Sync impact:**`** is temporary Sync/Integrate scaffolding'

assert_contains \
  "Workflow sync author owns the Sync Map format" \
  "skills/semantic-merge/references/workflow-sync-author.md" \
  "## Sync Map"

assert_contains \
  "Workflow sync author records pre-sync merge base" \
  "skills/semantic-merge/references/workflow-sync-author.md" \
  "**Pre-sync merge base:**"

assert_contains \
  "Workflow sync author records synced base head" \
  "skills/semantic-merge/references/workflow-sync-author.md" \
  "**Synced base head:**"

assert_contains \
  "Workflow sync author records sync commits" \
  "skills/semantic-merge/references/workflow-sync-author.md" \
  "**Sync commits:**"

assert_contains \
  "Workflow sync author defines task-local Sync impact" \
  "skills/semantic-merge/references/workflow-sync-author.md" \
  '**Sync impact:** Cluster `<cluster-id>` explains <task-specific post-sync context>.'

assert_contains \
  "Task-local Sync impact is not an Integrate todo list" \
  "skills/semantic-merge/references/workflow-sync-author.md" \
  "not an Integrate to-do list"

assert_contains \
  "Workflow sync reviewer verifies Sync Map and impact context" \
  "skills/semantic-merge/references/workflow-sync-reviewer.md" \
  "Check the Sync Map against the diff and incoming intent."

assert_contains \
  "Workflow sync reviewer records Sync review status" \
  "skills/semantic-merge/references/workflow-sync-reviewer.md" \
  'record the verdict in `**Sync review status:**`'

assert_contains \
  "Standalone semantic merge owns standalone record format" \
  "skills/semantic-merge/references/standalone-merge.md" \
  "## Codebase Context"

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
  'As **integration reviewer**, consume task-local `**Sync impact:**`'

assert_contains \
  "Integration reviewer uses BASE_HEAD_SHA pruning sweep" \
  "agents/reviewer.md" \
  'treat `git diff <BASE_HEAD_SHA>..HEAD` as a pruning sweep'

assert_contains \
  "Contributor gate applies no-overprescription line by line" \
  "CLAUDE.md" \
  "self-applies both tests below line by line"

echo
echo "Passed: $pass    Failed: $fail"
if [ $fail -gt 0 ]; then
  echo "Failing cases: ${failed_names[*]}"
  exit 1
fi

exit 0
