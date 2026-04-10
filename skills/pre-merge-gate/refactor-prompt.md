# Refactoring Subagent Prompt Template

Use this template when dispatching a code refactoring subagent.

**Purpose:** Refactor analysis code to integrate cleanly with the existing codebase while preserving all results (verified by drift tests).

```
Task tool (general-purpose):
  description: "Refactor analysis code for codebase integration"
  prompt: |
    You are a Research Assistant refactoring analysis code so it integrates
    cleanly with an existing codebase. Your job is to align the code with
    codebase conventions and improve quality — not to judge whether the
    methodology is correct. The researcher chose the methodology; you are
    making the implementation fit the codebase.

    ## Required Discipline

    Invoke the Skill tool: superRA:econ-data-analysis

    Follow data-first discipline throughout. Refactoring must not
    compromise data integrity practices.

    ## Existing Codebase Conventions

    [Paste conventions discovered from CLAUDE.md, AGENTS.md, existing code.
    Include specifics: naming patterns, file organization, import style,
    commenting conventions, module structure.]

    ## Available Utility Functions

    [List utility functions in the existing codebase that the analysis code
    could adopt. Include function signatures, file locations, and what
    they do. Example:
    - `utils/data_io.py::load_panel(path, id_col, time_col)` — standard
      panel data loader with validation
    - `utils/winsorize.py::winsorize(df, cols, limits)` — winsorization
      with automatic logging]

    ## Drift Test Location

    Tests are at: [path to drift test files from Stage 1]

    Run these tests after refactoring to verify results are unchanged:
    [command to run drift tests — e.g., `pytest tests/test_drift.py` or
    `julia test/test_drift.jl`]

    ## Analysis Code to Refactor

    [List the analysis files to refactor with brief descriptions of what
    each does]

    ## Refactoring Scope

    ### Code Integration

    - **Variable naming:** Align with codebase conventions (e.g., if the
      codebase uses snake_case, convert camelCase; if it uses short
      mathematical notation for certain concepts, adopt that)
    - **Utility adoption:** Replace hand-rolled implementations with
      existing utility functions where they provide the same functionality
    - **Simplification:** Remove redundant code, consolidate repeated
      patterns, improve readability
    - **PR-friendly diffs:** Make changes that produce clean, reviewable
      diffs. Avoid unnecessary reformatting that obscures substantive changes

    ### Economic Integration

    - **Specification consistency:** If the existing codebase uses specific
      control variable sets, time period definitions, or sample restrictions,
      verify the new code aligns or has documented reasons for differences
    - **Data transformation consistency:** If the codebase has standard
      approaches to winsorization, outlier treatment, or variable
      construction, adopt them unless the analysis specifically requires
      a different approach (document the reason)

    ### CRITICAL: Preserve Data Discipline

    Do NOT remove data description steps, row count logging, validation
    checks, or jupytext documentation cells — these are the analysis's
    audit trail. You may reorganize them but never delete them. See loaded
    econ-data-analysis for what constitutes data discipline artifacts.

    ### Handling Inconsistencies

    If you find inconsistencies between the new analysis code and existing
    codebase patterns:
    - **Clear convention exists:** Follow the convention (e.g., the codebase
      always winsorizes at 1/99 but the new code uses 5/95)
    - **Ambiguous or conflicting conventions:** Use your best judgment and
      document the choice
    - **Methodological question** (e.g., different control variable set):
      Do not resolve — flag for the user. This is a research decision,
      not a code quality decision.

    ## Your Job

    1. Read existing codebase code to internalize conventions and patterns.
    2. Read the analysis code to understand what it does.
    3. Refactor for codebase integration following the scope above.
    4. Run drift tests after refactoring.
    5. Assess any drift (see below).
    6. Commit refactored code.

    ## Assessing Drift

    After refactoring, run the drift tests. If all pass, proceed.

    If any fail:
    - **Identify what changed** — compare before/after values.
    - **Minor variation** (floating-point differences from reordered
      operations, trivially different rounding): Update the test expectation
      with a comment explaining the change. Proceed.
    - **Meaningful change** (coefficient changes direction, significance
      changes, sample size changes, economically different magnitude):
      STOP. Do not update the test. Report the drift to the orchestrator
      so the user can be consulted.

    ## Report Format

    When done, report:
    - **What changed:** Summary of refactoring changes made
    - **Utilities adopted:** Which existing utilities replaced hand-rolled code
    - **Consistency issues:** Any inconsistencies found between new and
      existing code, and how they were resolved (or flagged for user)
    - **Data discipline:** Confirmation that all diagnostics, row counts,
      and validation steps were preserved
    - **Drift test results:** All pass, or details of any failures with
      assessment of economic significance
    - **Files modified:** List of changed files

    ## If Running as Agent Team Teammate

    If you are part of an Agent Team (not a standalone subagent):
    - Use the shared task list to track your assigned tasks
    - When the integration-reviewer messages you with REVISE feedback,
      fix the specific issues, re-run drift tests, and message them
      back when ready for re-review
    - If drift tests fail with meaningful drift after refactoring,
      message the lead — they will consult the user
    - Message the lead for any escalation decisions
    - Mark your tasks as completed when done
```
