---
name: integration-workflow
description: superRA workflow INTEGRATE step. Use after execution-workflow has verified reproducibility and the user has chosen merge/PR — creates drift tests to guard key results, refactors code for codebase fit (with refactor-review loop), generates the work-journal report, and handles the development documents (PLAN.md / RESULTS_UPDATE.md). Hands off to merge-workflow for the actual main update + merge/PR.
---

# Integration Workflow

Workflow skill for the **INTEGRATE** phase of the superRA workflow. Owns the four steps that prepare an analysis branch for merging into main: protect results with drift tests, refactor code for codebase integration, generate the work-journal report, and handle the development documents. Hands off the actual merge/PR mechanics to `superRA:merge-workflow`.

Assumes execution-workflow has already verified reproducibility and the user has chosen Option 1 (merge locally) or Option 2 (push + PR). If you find yourself running reproducibility checks or presenting the 4-option menu, something is wrong: that work belongs in execution-workflow.

**Core principle:** Tests guard results. Integration review identifies what needs changing. Refactoring addresses specific issues. Nothing hands off to merge-workflow without integration reviewer approval, a clean report, and the dev documents disposed of.

**Announce at start:** "I'm using the integration-workflow skill to prepare this work for integration."

## The Process

```dot
digraph integration_workflow {
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

## Dispatch Convention

Every dispatch in this skill uses the pointer-based template — pass only the stage label, the domain reference path, and any task-specific pointers (key results, code under review, prior reviewer findings). The `implementer` and `reviewer` agent definitions own the report format, handoff protocol, and skill-load defaults; do not duplicate that content into the dispatch prompt. Both agents auto-load `superRA:econ-data-analysis` and `superRA:script-to-notebook` for analysis-touching stages.

When a reviewer returns REVISE in either stage, **adjudicate the feedback before forwarding it.** See "Handling Reviewer Feedback (Orchestrator Discipline)" in `superRA:execution-workflow` for the protocol — the same discipline applies here. You are the senior researcher; the reviewer is an advisor. Read the cited code, classify each issue, override with documented reasoning if the reviewer is wrong, push back with counter-evidence if the reviewer misread the code.

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

3. **Dispatch test-creator:**
   ```
   Agent(subagent_type: "implementer"):
     Stage: drift test creation
     Skills: superRA:integration-workflow
     Domain reference: drift-test-quality.md
     Key results to protect: [user-confirmed list with values]
     Test conventions: [project test framework, test directory]
   ```

4. **Dispatch test-reviewer:**
   ```
   Agent(subagent_type: "reviewer"):
     Stage: drift test
     Skills: superRA:integration-workflow
     Domain reference: drift-test-quality.md
     Tests under review: [paths to created test files]
     Key results they should protect: [list]
   ```

5. **If REVISE:** adjudicate the reviewer's issues per the orchestrator discipline above. For accepted issues, re-dispatch the test-creator with the specific feedback. Re-dispatch the test-reviewer. Iterate until APPROVE.

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

2. **Dispatch integration-reviewer:**
   ```
   Agent(subagent_type: "reviewer"):
     Stage: integration
     Skills: superRA:integration-workflow
     Domain reference: codebase-integration.md
     Code under review: [paths]
     Codebase conventions: [where they're documented — CLAUDE.md, AGENTS.md, etc.]
     Drift tests: [paths]
     Diff: <BASE_SHA>..<HEAD_SHA>
   ```

3. **If APPROVE:** No refactoring needed. Proceed to final commit.

4. **If REVISE:** Adjudicate the reviewer's feedback per the orchestrator discipline above. For accepted issues, refactor:

   a. **Dispatch refactorer:**
      ```
      Agent(subagent_type: "implementer"):
        Stage: refactoring
        Skills: superRA:integration-workflow
        Domain reference: codebase-integration.md
        Reviewer issues to address: [accepted items, file:line, what to fix]
        Codebase conventions: [pointers]
        Drift tests: [paths — must keep passing]
        Code to refactor: [paths]
      ```

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

## Step 3: Generate Report

After integration review APPROVES the refactored code, create a work-journal entry documenting the analysis. Use `RESULTS_UPDATE.md` as source material — the finishing report is the polished version; RESULTS_UPDATE.md was the development log.

**Entry file:** `[WORK_JOURNAL_DIR]/YYYY-MM-DD-[Author]-[Description].md`
- Resolve path from project guidance (AGENTS.md, CLAUDE.md, README)
- Default: `notes/` or `work-journal/`

**Frontmatter:**
```yaml
---
author: "[[Author]]"
date: YYYY-MM-DD
timestamp: "YYYY-MM-DDTHH:MM:SS"
project: "[[ProjectName]]"
git_commit: [current HEAD hash]
git_message: "[latest commit message]"
tags: ["work-journal", "analysis"]
permalink: working-journal/YYYY-MM-DD-author-description
---
```

**Content structure** (flexible, but typically includes):
- Objective
- Data description (sources, sample, key variables)
- Methodology
- Results with tables and figures
- Technical details

**Rules:**
- **Factual and objective** — state what was done and found
- **Every claim cited** — link to code files, output files, or documentation
- **No speculation** — don't interpret economic meaning unless the user explicitly asked
- **Relative paths** — `[descriptive text](relative/path/from/report/to/file)`

**Figure handling:**
- PDF figures → convert to PNG, copy to `attachments/` subdirectory
- Embed with relative paths and cite original source
- ```markdown
  ![Descriptive caption](./attachments/YYYY-MM-DD-description.png)
  Source: [Original](relative/path/to/original/figure.pdf)
  ```

**Report verification** (inline checklist):
- [ ] All claims cited and accurate?
- [ ] Numbers match source files?
- [ ] No speculation or subjective language?
- [ ] Figures copied and cite sources?
- [ ] File paths resolve correctly?

If issues found, fix before finalizing.

## Step 4: Handle Development Documents

`PLAN.md` and `RESULTS_UPDATE.md` are development artifacts — they cannot remain at project root on the main branch.

**Ask the user:**
```
PLAN.md and RESULTS_UPDATE.md are development documents. Options:
1. Move to relevant module directory (alongside the analysis code for future reference)
2. Consolidate key findings into existing documentation
3. Delete (git history preserves them on this branch)
Which option?
```

**Option 1 (Move to module):**
```bash
# User specifies target directory
mkdir -p <target-dir>
git mv PLAN.md <target-dir>/
git mv RESULTS_UPDATE.md <target-dir>/
git mv results_attachments/ <target-dir>/ 2>/dev/null
git commit -m "move analysis plan and results to <target-dir>"
```

**Option 2 (Consolidate):**
- Identify which existing documentation should be updated
- Extract key findings from RESULTS_UPDATE.md
- Merge into existing docs (user guides which docs)
- Remove original files:
```bash
git rm PLAN.md RESULTS_UPDATE.md
rm -rf results_attachments/
git add -A results_attachments/ 2>/dev/null
git commit -m "consolidate analysis results into project docs"
```

**Option 3 (Delete):**
```bash
git rm PLAN.md RESULTS_UPDATE.md
rm -rf results_attachments/
git add -A results_attachments/ 2>/dev/null
git commit -m "remove development documents (preserved in branch history)"
```

## Hand-Off to merge-workflow

After Steps 1–4 are complete (drift tests committed, refactoring approved, report written, dev docs disposed of), invoke `superRA:merge-workflow` to update with main, run post-merge verification (drift tests + fresh integration review), and execute the local merge or PR push. Do not attempt the merge mechanics yourself — merge-workflow owns them.

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
- **superRA:execution-workflow** Step 4 -- When the user chooses Option 1 (merge) or Option 2 (PR) after execution-workflow has verified reproducibility

**Hands off to:**
- **superRA:merge-workflow** -- For main update + post-merge verification + actual merge/PR

**Requires:**
- **RESULTS_UPDATE.md** -- Source of key results for drift tests
- **Committed analysis code** -- Must be committed before drift tests are created
- **Reproducibility already verified** by execution-workflow Step 3

**Subagents should use:**
- **superRA:econ-data-analysis** -- Data discipline principles for all subagents
