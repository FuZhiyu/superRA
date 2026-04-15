# superRA Plugin Restructure — Results

Stage 1 dev log. Populated as each task completes.

## Task 1: Standardize Dispatch-Prompt Protocol

**Outcome:** 16 dispatch templates across 5 workflow-adjacent skill files now open with the canonical prefix "Follow the standard stage-relevant workflow and load relevant skills and documents to proceed. Additionally, …". Legacy `Work from:` and `Counterpart:` fields are removed from every template; free-form `Note:` fields in `merge-workflow` and `semantic-merge` Tier 3 are folded into the `Additionally:` tail so all task-specific steering flows through one channel.

**Files touched:**

- `skills/execution-workflow/SKILL.md` — 3 primary templates (analysis-task implementer, data-integrity reviewer, implementation reviewer) rewritten; added a short prose preamble describing the prefix contract; the `Agent Teams only` Counterpart comments are gone (teammate pairing now lives in `agent-orchestration` team recipes only).
- `skills/integration-workflow/SKILL.md` — 6 templates rewritten: test-creator, test-reviewer, integration-reviewer, refactorer, Step 3 doc-writer, Step 3 doc-reviewer.
- `skills/merge-workflow/SKILL.md` — 2 templates rewritten: post-merge integration reviewer, post-merge refactorer; `Note:` fields folded into `Additionally:`.
- `skills/semantic-merge/SKILL.md` — 3 templates rewritten: Tier 2 merge-proposer, Tier 2 merge-reviewer, Tier 3 merge-proposer; Tier 3 context folded into `Additionally:`.
- `skills/refactor-and-integrate/SKILL.md` — 2 illustrative examples in §"Dispatch Convention" brought into alignment so the skill's own guidance matches what the workflow skills now emit.

**Structural-invariants test updated.** Two new assertions in `tests/structural-invariants.sh`:

1. Every `Agent(subagent_type: "superRA:implementer"|"superRA:reviewer")` dispatch template in the five files above carries the "Follow the standard stage-relevant workflow" prefix (prefix-count ≥ template-count).
2. No dispatch template retains `Work from:` or `Counterpart:` lines.

Full run: 24 PASS, 2 known WARN (pre-existing upstream refs), 0 FAIL.

**RELEASE-NOTES.md** top (Unreleased) entry expanded to cover the dispatch-protocol standardization alongside the DAV restructure that was already in the entry.

**Out of scope (tracked for follow-on tasks):** the domain-agnosticism restructure of `execution-workflow` (one-pass review, generic Step 3, generic completion menu), integrating §Review & Self-Check Discipline into `econ-data-analysis/SKILL.md` main body, and agent-file Stage table updates. These depend on Task 1 landing first.
