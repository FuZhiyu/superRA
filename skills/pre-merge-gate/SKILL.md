---
name: pre-merge-gate
description: Use before merging analysis work — creates drift tests to guard key results, refactors code for codebase integration, and reviews integration quality
---

# Pre-Merge Gate

Before merging analysis work, protect results with drift tests, refactor code for codebase integration, and verify integration quality. Only invoked from finishing-analysis when the user chooses merge or PR.

**Core principle:** Tests guard results. Integration review identifies what needs changing. Refactoring addresses specific issues. Nothing merges without integration reviewer approval.

**Announce at start:** "I'm using the pre-merge-gate skill to prepare this work for integration."

## The Process

```dot
digraph pre_merge_gate {
    rankdir=TB;

    subgraph cluster_stage1 {
        label="Stage 1: Drift Test Creation";
        "Extract key results from RESULTS_UPDATE.md" [shape=box];
        "Present candidates to user" [shape=box];
        "Dispatch test-creator subagent" [shape=box];
        "Dispatch test-reviewer subagent" [shape=box];
        "Test reviewer: APPROVE?" [shape=diamond];
        "Test-creator fixes issues" [shape=box];
        "Run tests — establish green baseline" [shape=box];
        "Commit test files" [shape=box];
    }

    subgraph cluster_stage2 {
        label="Stage 2: Integration Review → Refactor Loop";
        "Identify codebase conventions" [shape=box];
        "Dispatch integration-reviewer subagent" [shape=box];
        "Integration reviewer: APPROVE?" [shape=diamond];
        "Dispatch refactor subagent with specific feedback" [shape=box];
        "Run drift tests after refactoring" [shape=box];
        "Drift tests pass?" [shape=diamond];
        "Assess economic significance" [shape=diamond];
        "STOP — ask user with before/after" [shape=box style=filled fillcolor=lightyellow];
        "Update test expectations, document reason" [shape=box];
        "Commit refactored code" [shape=box];
        "Final commit" [shape=box style=filled fillcolor=lightgreen];
    }

    "Extract key results from RESULTS_UPDATE.md" -> "Present candidates to user";
    "Present candidates to user" -> "Dispatch test-creator subagent";
    "Dispatch test-creator subagent" -> "Dispatch test-reviewer subagent";
    "Dispatch test-reviewer subagent" -> "Test reviewer: APPROVE?";
    "Test reviewer: APPROVE?" -> "Run tests — establish green baseline" [label="APPROVE"];
    "Test reviewer: APPROVE?" -> "Test-creator fixes issues" [label="REVISE"];
    "Test-creator fixes issues" -> "Dispatch test-reviewer subagent" [label="re-review"];
    "Run tests — establish green baseline" -> "Commit test files";

    "Commit test files" -> "Identify codebase conventions";
    "Identify codebase conventions" -> "Dispatch integration-reviewer subagent";
    "Dispatch integration-reviewer subagent" -> "Integration reviewer: APPROVE?";
    "Integration reviewer: APPROVE?" -> "Final commit" [label="APPROVE"];
    "Integration reviewer: APPROVE?" -> "Dispatch refactor subagent with specific feedback" [label="REVISE"];
    "Dispatch refactor subagent with specific feedback" -> "Run drift tests after refactoring";
    "Run drift tests after refactoring" -> "Drift tests pass?";
    "Drift tests pass?" -> "Commit refactored code" [label="pass"];
    "Drift tests pass?" -> "Assess economic significance" [label="fail"];
    "Assess economic significance" -> "STOP — ask user with before/after" [label="meaningful"];
    "Assess economic significance" -> "Update test expectations, document reason" [label="minor variation"];
    "Update test expectations, document reason" -> "Commit refactored code";
    "Commit refactored code" -> "Dispatch integration-reviewer subagent" [label="re-review"];
}
```

## Stage 1: Drift Test Creation

Drift tests guard key results from unintended changes during refactoring or future modifications. They are the safety net that makes refactoring safe.

### Steps

1. **Extract key results from RESULTS_UPDATE.md.** Read the results document and use economic reasoning to identify KEY results -- main findings that define the analysis conclusions, not every intermediate number.

2. **Present candidates to user.** Show the user which results you consider key and ask for confirmation:
   ```
   These results seem like the key findings to protect with drift tests:
   - [result 1: description and value]
   - [result 2: description and value]
   - ...

   Which of these should be protected? Any to add or remove?
   ```

3. **Dispatch test-creator:** `Agent(subagent_type: "implementer")` with skill `superRA:econ-data-analysis` and domain reference `./references/drift-test-quality.md`. Provide: analysis objective, methodology context, data sources, the user-confirmed list of key results, and project test conventions.

4. **Dispatch test-reviewer:** `Agent(subagent_type: "reviewer")` with skill `superRA:econ-data-analysis` and domain reference `./references/drift-test-quality.md`. Provide: the created tests and the key results they should protect.

5. **If REVISE:** test-creator fixes the issues raised by the reviewer, then test-reviewer re-reviews. Iterate until APPROVE.

6. **Run tests to establish green baseline.** All drift tests must pass on the current code before proceeding. If tests fail on the existing code, the tests are wrong -- fix them.

7. **Commit test files.**
   ```bash
   git add tests/
   git commit -m "add drift tests for key analysis results"
   ```

## Stage 2: Integration Review → Refactor Loop

The integration reviewer is the gatekeeper. Review first to identify what needs changing, then refactor to address specific issues. Nothing moves forward without integration reviewer approval.

### Steps

1. **Identify existing codebase conventions.** Read:
   - CLAUDE.md, AGENTS.md, or project configuration for coding standards
   - Existing code in the repository for naming patterns, file organization, utility functions
   - Available utility functions that the new code should adopt

2. **Dispatch integration-reviewer:** `Agent(subagent_type: "reviewer")` with skill `superRA:econ-data-analysis` and domain reference `./references/codebase-integration.md`. Provide: the analysis code, codebase conventions, drift test results, and the diff against the base branch.

3. **If APPROVE:** No refactoring needed. Proceed to final commit.

4. **If REVISE:** The reviewer identified specific issues. Refactor to address them:

   a. **Dispatch refactorer:** `Agent(subagent_type: "implementer")` with skill `superRA:econ-data-analysis` and domain reference `./references/codebase-integration.md`. Provide: the reviewer's specific feedback items, codebase conventions, available utility functions, drift test file locations, and the analysis code to refactor.

   b. **After refactoring: run drift tests.**
      - **Pass:** Commit and re-submit for review.
      - **Fail:** Assess economic significance of the drift.
        - **Meaningful drift** (results change substantively): STOP. Show the user before/after values and ask how to proceed. Do not silently accept changed results.
        - **Minor variation** (rounding, floating-point, inconsequential magnitude change): Update test expectations with the new values, document the reason in a comment, and proceed.

   c. **Commit refactored code.**
      ```bash
      git add -A
      git commit -m "refactor analysis code for codebase integration"
      ```

   d. **Re-dispatch integration-reviewer.** Loop back to step 2. Iterate until APPROVE.

5. **Final commit** after integration reviewer APPROVE.
   ```bash
   git add -A
   git commit -m "address integration review feedback"
   ```

## When to Lighten

**Standalone analysis (no existing codebase to integrate with):**
- Stage 1 (drift tests): Always run. Tests protect results regardless of codebase context.
- Stage 2 (integration review → refactor): Lighter pass -- focus on code quality and clarity rather than codebase convention alignment. Integration reviewer may APPROVE with no refactoring needed.

**Small changes (single-file analysis, few results):**
- Stage 1: Still run, but fewer tests needed.
- Stage 2: Integration reviewer may APPROVE immediately if code is clean.

## Handling Drift Test Failures After Refactoring

This is the critical judgment call in the process. When drift tests fail after refactoring:

1. **Identify what changed.** Compare the before/after values.
2. **Assess economic significance.** Is this a meaningful change in results, or a trivial numerical difference?
   - Point estimates shifting by more than the tolerance you set: investigate.
   - Sign changes or significance changes: always meaningful.
   - Standard errors changing modestly: usually minor (sensitive to implementation details).
3. **If meaningful:** Do not proceed. Show the user exactly what changed and let them decide.
4. **If minor:** Update the test expectation, add a comment explaining why (e.g., "tolerance updated: refactored merge order produces equivalent result within floating-point precision"), and proceed.

## Agent Types and Domain References

- **`implementer`** agent + `./references/drift-test-quality.md` — For test creation
- **`reviewer`** agent + `./references/drift-test-quality.md` — For test review
- **`implementer`** agent + `./references/codebase-integration.md` — For refactoring
- **`reviewer`** agent + `./references/codebase-integration.md` — For integration review

All agents also load `superRA:econ-data-analysis` for data discipline.

## Agent Teams Mode

When Agent Teams are available (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`), the gate can be orchestrated as a team instead of sequential subagent dispatches. This enables direct iteration between creator/reviewer and integration-reviewer/refactorer without the orchestrator relaying messages.

**Invoke `superRA:agent-orchestration` for the Pre-Merge Gate Team recipe** — it has the full team composition (4 teammates), task graph with dependencies, iteration patterns, lead responsibilities, and session handoff protocol.

The lead still handles user-facing decisions (drift test candidates, meaningful drift escalation), commits at stage boundaries, and team cleanup after final APPROVE.

## Red Flags

**Never:**
- Skip Stage 1 (drift tests) -- they are the safety net for everything that follows
- Refactor before integration reviewer has identified issues -- review first, then fix
- Proceed past failing drift tests without assessment
- Silently update test expectations for meaningful result changes
- Remove data diagnostics, row counts, or validation steps during refactoring
- Judge the researcher's methodology choice -- focus on implementation correctness
- Refactor before drift tests are committed and green
- Merge without integration reviewer APPROVE

**Always:**
- Ask the user which results to protect before creating tests
- Run integration review before any refactoring
- Run drift tests after every refactoring change
- Re-submit to integration reviewer after every refactoring round
- Stop and ask the user when drift indicates meaningful result changes
- Preserve all data discipline artifacts (describe steps, row counts, validation)
- Commit at each stage boundary

## Integration

**Called by:**
- **superRA:finishing-analysis** -- When user chooses Option 1 (merge) or Option 2 (PR)

**Requires:**
- **RESULTS_UPDATE.md** -- Source of key results for drift tests
- **Committed analysis code** -- Must be committed before drift tests are created

**Subagents should use:**
- **superRA:econ-data-analysis** -- Data discipline principles for all subagents
