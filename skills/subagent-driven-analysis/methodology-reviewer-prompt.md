# Methodology & Code Quality Reviewer Prompt Template

Use this template when dispatching a methodology reviewer subagent.

**Purpose:** Verify the analysis uses appropriate methods, produces economically sensible results, and the code is clean and reproducible.

**Only dispatch after data integrity review passes.**

```
Task tool (econ-superpowers:data-analysis-reviewer or general-purpose):
  description: "Review methodology and code quality for Task N"
  prompt: |
    You are reviewing analysis code for methodological correctness and
    code quality. Data integrity has already been verified.

    ## What Was Requested

    [FULL TEXT of task requirements from plan]

    ## What Implementer Built

    [From implementer's report]

    ## Your Job

    Review the implementation for:

    **Methodology:**
    - Does the analysis match what was planned?
    - Are statistical methods appropriate for the data structure?
    - Are assumptions stated and reasonable?
    - Do results match economic intuition?
    - Are edge cases handled (e.g., small samples, extreme values)?

    **Code quality:**
    - Is the code clean and readable?
    - Are variable names descriptive?
    - Is the jupytext structure logical (one operation per cell)?
    - Could someone unfamiliar with the project follow the script?

    **Reproducibility:**
    - Does the pipeline file include this script (if multi-script analysis)?
    - Are outputs saved to the correct location?
    - Are random seeds set (if applicable)?
    - Do file paths work from the project root?

    **Plan alignment:**
    - Does the implementation match the plan specification?
    - Were any deviations from the plan documented and justified?
    - Should the plan be updated based on what was found?

    Report:
    - Strengths (good practices observed)
    - Issues: Critical / Major / Minor
    - Assessment: APPROVE / REVISE / MAJOR REVISION
    - Suggested plan updates (if findings require changing upcoming steps)
```
