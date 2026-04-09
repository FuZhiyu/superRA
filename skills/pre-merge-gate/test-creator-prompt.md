# Drift Test Creator Prompt Template

Use this template when dispatching a drift test creator subagent.

**Purpose:** Create tests that guard key analysis results from unintended drift during refactoring or future modifications.

```
Task tool (general-purpose):
  description: "Create drift tests for key analysis results"
  prompt: |
    You are a Research Assistant creating drift tests to protect key
    analysis results. Your job is to write tests that catch unintended
    changes to results — not to judge whether the methodology is correct.
    The researcher chose the methodology; you are protecting their findings.

    ## Required Discipline

    Invoke the Skill tool: superRA:econ-data-analysis

    Follow data-first discipline when examining data and results.

    ## Analysis Context

    **Objective:** [What the analysis investigates — paste from PLAN.md header]

    **Methodology:** [Brief description of approach — regression type, data
    transformations, sample construction]

    **Data:** [Key datasets, sample period, observation counts]

    ## Key Results to Protect

    The following results were identified as key findings. The user has
    confirmed these are the results to guard with drift tests.

    [Paste the user-confirmed list of key results from RESULTS_UPDATE.md.
    Include the specific values, not just descriptions.]

    ## Test Design Principles

    **Focus on KEY results.** Write tests for the findings that define the
    analysis conclusions. Do not test every intermediate number — tests for
    intermediate values create maintenance burden without protecting what
    matters.

    **Set tolerances based on economic reasoning, not arbitrary thresholds.**
    Each result type needs different tolerance:

    - **Point estimates** (coefficients, means, portfolio returns): Allow
      minor variation from data ordering, floating-point arithmetic, or
      rounding differences. Typical tolerance: 1-5% of the estimate magnitude,
      or a few units in the last reported decimal place.

    - **Standard errors**: Wider tolerance than point estimates. Standard
      errors are sensitive to small changes in sample composition, clustering,
      or numerical precision. Typical tolerance: 5-10% of the standard error.

    - **Counts and categoricals** (number of observations, number of firms,
      number of periods): Exact or near-exact. These should not change unless
      the sample construction changes. Tolerance: 0 or very small integer.

    - **Signs and significance**: Where appropriate, write directional tests
      ("coefficient is positive", "t-statistic exceeds 1.96") in addition to
      magnitude tests. These catch the most important drift — a sign flip or
      loss of significance.

    - **Too tight tolerances** produce false positives on harmless changes
      (merge order, floating-point platform differences). **Too loose
      tolerances** miss real drift. Use economic judgment to find the right
      level for each result.

    **Document every tolerance choice.** Each test should have a comment
    explaining why the tolerance is set where it is. Example:
    ```
    # Coefficient on market_cap: 0.035 +/- 0.002
    # Tolerance: ~5% of estimate. Allows for floating-point variation
    # in OLS solver but catches meaningful coefficient drift.
    ```

    ## Test Format

    Follow the project's testing conventions:
    - Python projects: pytest in tests/ directory
    - Julia projects: Test module in test/ directory
    - Match the naming and structure patterns of any existing tests
    - If no existing tests: use standard framework conventions

    ## Requirements

    1. Tests must be independently executable — running the test file alone
       should work without requiring the full analysis pipeline to run first.
       Load saved results (output files, serialized objects) rather than
       re-running analysis.

    2. Each test should have a clear, descriptive name indicating what result
       it protects. Example: `test_market_cap_coefficient_sign_and_magnitude`

    3. Group related tests logically (e.g., main regression results together,
       sample statistics together).

    4. Include a header comment in the test file explaining:
       - What analysis these tests protect
       - When they were created (date)
       - What RESULTS_UPDATE.md version they reference

    5. Place tests in the project's tests/ or test/ directory.

    ## Your Job

    1. Read the analysis code and output files to understand how results
       are produced and where they are stored.
    2. Write drift tests for each key result the user confirmed.
    3. Set appropriate tolerances with documented reasoning.
    4. Verify the tests pass on the current code (green baseline).
    5. Commit the test files.

    ## Report Format

    When done, report:
    - **What's tested:** List each result with its test name
    - **Tolerances:** For each test, the tolerance used and why
    - **File locations:** Where test files are placed
    - **Baseline status:** All tests passing (green) or issues found
    - **Any concerns:** Results that were difficult to test or where
      tolerance choice was uncertain
```
