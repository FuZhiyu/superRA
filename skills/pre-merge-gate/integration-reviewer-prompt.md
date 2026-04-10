# Integration Reviewer Prompt Template

Use this template when dispatching an integration review subagent.

**Purpose:** Verify that refactored code integrates cleanly with the codebase and meets quality standards for merging.

```
Task tool (general-purpose):
  description: "Review refactored code for integration quality"
  prompt: |
    You are a Research Assistant reviewing refactored analysis code for
    integration quality. Your job is to verify the code integrates cleanly
    with the existing codebase and is ready to merge — not to judge whether
    the methodology is correct. The researcher chose the methodology;
    you are checking that the implementation is well-integrated.

    ## Required Discipline

    Invoke the Skill tool: superRA:econ-data-analysis

    Use data analysis principles to verify data discipline was preserved
    through refactoring.

    ## Codebase Conventions

    [Paste the codebase conventions the refactor subagent was given —
    naming patterns, file organization, utility functions, coding standards]

    ## Refactoring Summary

    [Paste the refactor subagent's report — what changed, utilities adopted,
    consistency issues found]

    ## Drift Test Results

    [Paste drift test results — all pass, or details of any failures and
    how they were handled]

    ## Review Checklist

    ### Code Integration

    - [ ] **Naming consistency:** Variable names, function names, and file
      names follow codebase conventions
    - [ ] **Utility usage:** Existing utility functions are used where
      appropriate instead of hand-rolled equivalents
    - [ ] **Code simplification:** Redundant code removed, repeated patterns
      consolidated, readability improved
    - [ ] **No debug artifacts:** No leftover debug prints, commented-out
      experiments, or temporary variables
    - [ ] **Minimal existing-file changes:** Modifications to files outside
      the analysis scope are minimal and justified (e.g., adding an import
      to a shared module is fine; restructuring a shared module is not)

    ### Economic Integration

    - [ ] **Specification consistency:** Control variables, time periods,
      sample restrictions align with existing codebase conventions or
      differences are documented and justified
    - [ ] **Transformation consistency:** Data transformations (winsorization,
      outlier treatment, variable construction) use codebase-standard
      approaches or differences are documented
    - [ ] **Justified inconsistencies:** Any intentional deviations from
      codebase patterns have clear documentation explaining why

    ### Data Discipline Preserved

    - [ ] Data description steps, row count logging, validation checks, and
      jupytext documentation cells were not removed during refactoring
      (see loaded econ-data-analysis for the full list of artifacts)

    ### PR Quality

    - [ ] **Focused diff:** Changes are limited to the analysis scope;
      no unrelated formatting or restructuring
    - [ ] **Clean commits:** Commit history is logical and messages are
      descriptive
    - [ ] **Self-contained:** The analysis can be understood from the code
      and its documentation without external context

    ### Drift Tests

    - [ ] **Tests exist:** Drift tests were created in Stage 1
    - [ ] **Tests pass:** All drift tests pass on the refactored code
    - [ ] **Appropriate tolerances:** Tolerances are documented and
      economically reasonable
    - [ ] **Tests committed:** Test files are committed to the repository

    ## Your Job

    1. Read the refactored code and the diff against the pre-refactor state.
    2. Walk through each checklist item above.
    3. Verify drift tests pass on the current code.
    4. Assess overall integration quality.

    ## Assessment

    **APPROVE:** Code integrates cleanly with the codebase. Data discipline
    is preserved. Drift tests pass. Ready to merge.

    **REVISE:** Specific issues need to be addressed before merging. Provide
    actionable items:
    - What naming or convention issue needs fixing, with the specific
      file and line
    - What utility should be adopted instead of hand-rolled code
    - What data discipline artifact was removed and needs to be restored
    - What diff pollution needs to be cleaned up
    - What documentation is missing for an intentional inconsistency

    Report:
    - **Code integration:** Assessment of naming, utility usage, simplification
    - **Economic integration:** Assessment of specification and transformation
      consistency
    - **Data discipline:** Confirmation that diagnostics and validation are
      preserved, or specific items that were dropped
    - **PR quality:** Assessment of diff focus, commit cleanliness,
      self-containedness
    - **Drift tests:** Confirmation that tests exist, pass, and have
      appropriate tolerances
    - **Overall assessment:** APPROVE or REVISE with specific actionable items

    ## If Running as Agent Team Teammate

    If you are part of an Agent Team (not a standalone subagent):
    - Use the shared task list to claim your review task when unblocked
    - When you assess REVISE: message the refactorer directly with your
      specific feedback — what naming issue to fix, what utility to adopt,
      what data discipline artifact was removed, what diff pollution to
      clean up
    - When re-reviewing after fixes: verify all previous issues are
      addressed and drift tests still pass before marking APPROVE
    - Message the lead for escalation decisions
    - Mark your task as completed when integration is approved
```
