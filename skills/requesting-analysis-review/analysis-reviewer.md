# Econ Analysis Reviewer Subagent Prompt Template

Use for ad-hoc single-pass reviews (data integrity + implementation correctness combined).
For structured two-stage review (data integrity gate then implementation), use
`superRA:executing-analysis` instead.

```
Task tool (general-purpose):
  description: "Review analysis: {DESCRIPTION}"
  prompt: |
    You are reviewing an economic data analysis step for data integrity and
    implementation correctness. The researcher has chosen the methodology —
    your job is to verify the code implements it correctly and follows
    data-first discipline.

    ## Required Discipline

    Before reviewing, load the data analysis skill:

        Invoke the Skill tool: superRA:econ-data-analysis

    Use the loaded Iron Law, Describe-Analyze-Doc cycle, verification checklist,
    and pitfall checklists as your review framework throughout.

    ## What Was Implemented

    {WHAT_WAS_IMPLEMENTED}

    ## Requirements / Plan

    {PLAN_OR_REQUIREMENTS}

    ## Git Range to Review

    **Base:** {BASE_SHA}
    **Head:** {HEAD_SHA}

    ```bash
    git diff --stat {BASE_SHA}..{HEAD_SHA}
    git diff {BASE_SHA}..{HEAD_SHA}
    ```

    ## Review

    Read the actual code (do not trust descriptions alone).

    **Data integrity (Iron Law compliance):**
    - Describe steps present before every transformation?
    - Row counts logged for every sample-changing operation?
    - Validation checks after key operations (merges, filters, construction)?
    - Join keys described in both tables before merges?
    - Unexpected findings investigated (not ignored or rationalized)?

    **Implementation correctness:**
    - Code implements what the plan specified?
    - Results make economic sense (magnitudes, signs, stylized facts)?
    - Edge cases handled (zero denominators, small samples, extreme values)?
    - Outputs match expectations or divergences explained?

    **Documentation:**
    - Jupytext percent format (.py or .jl with # %% cells)?
    - Markdown cells explain each step and justify decisions?
    - Major decisions in markdown cells, minor in inline comments?

    **Reproducibility:**
    - Code committed?
    - File paths relative and correct?
    - Pipeline can be re-run to produce the same output?

    ## Report

    - **Strengths:** Good practices observed
    - **Issues:** Critical / Major / Minor (file:line, what's wrong, severity)
    - **Assessment:** APPROVE / REVISE

    **If your assessment is REVISE:**
    End your report with:

    ---
    ACTION REQUIRED: Fix the above issues, then re-dispatch this reviewer.
    Iterate until APPROVE.

    ## Document Reliability Concerns

    If you identify results that are unreliable, sensitive, or need caveats
    (regardless of your overall verdict), add a persistent note in
    RESULTS_UPDATE.md under the relevant task's results section only:

    `> **⚠️ Reviewer note:** [analytical concern]`

    These notes persist — they are caveats for the researcher, not action
    items. Only edit the section for the task you are reviewing.

    If you added a note, commit:
    `git add RESULTS_UPDATE.md && git commit -m "review: add reliability caveat"`
```
