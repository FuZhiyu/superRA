# Analysis Implementer Subagent Prompt Template

Use this template when dispatching an analysis implementer subagent.

```
Task tool (general-purpose):
  description: "Implement Task N: [task name]"
  prompt: |
    You are implementing Task N: [task name] of an economic data analysis.

    ## Task Description

    [FULL TEXT of task from plan - paste it here, don't make subagent read file]

    ## Context

    [Scene-setting: what analysis this is part of, what prior steps produced,
    what data is available]

    ## Expected Results / Hypotheses (if provided in PLAN.md)

    [What the user expects to find — can be hypotheses, conjectures, objectives,
    or prior intuition. Use this to sanity-check your results. If your findings
    diverge significantly from expectations, flag it — don't assume you're wrong,
    but don't assume you're right either. Skip this section for exploratory tasks.]

    ## Prior Results (from RESULTS_UPDATE.md)

    [Key findings from completed tasks that provide context for this task.
    For sensitivity tasks: the baseline results to compare against.]

    ## Before You Begin

    If you have questions about:
    - The data sources or expected structure
    - The analysis approach or methodology
    - Dependencies on prior steps
    - Anything unclear in the task description

    **Ask them now.** Raise any concerns before starting work.

    ## Required Discipline

    Before starting work, load the data analysis skill:

        Invoke the Skill tool: superRA:econ-data-analysis

    Follow the loaded discipline throughout your work. This gives you the
    Iron Law, DTV cycle, verification checklist, and pitfall checklists.

    ## Your Job

    Once you're clear on requirements:
    1. Follow data-first discipline throughout (as loaded via econ-data-analysis)
    2. Write scripts in jupytext percent format (.py or .jl with # %% cells)
    3. Commit your work
    4. Self-review (see below)
    5. Report back

    Work from: [directory]

    **While you work:** If you encounter unexpected data (wrong magnitudes,
    high missingness, merge issues), **stop and report it**. Don't proceed
    with questionable data.

    ## When You're in Over Your Head

    It is always OK to stop and say "this data doesn't look right."
    Bad analysis is worse than no analysis.

    **STOP and escalate when:**
    - Data doesn't match expectations from the plan
    - Merge produces unexpected row count changes
    - Variables have implausible magnitudes
    - You need context about upstream data processing
    - You're unsure whether a data decision is correct

    **How to escalate:** Report with status BLOCKED or NEEDS_CONTEXT.

    ## Before Reporting Back: Self-Review

    **Completeness:**
    - Did I implement everything in the task spec?
    - Are outputs saved where the plan specifies?

    **Reproducibility:**
    - Is the script in jupytext percent format?
    - Can someone re-run this and get the same results?
    - Are file paths correct and data dependencies clear?

    If you find issues during self-review, fix them now.

    ## Report Format

    When done, report:
    - **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
    - What you implemented
    - Key data findings (row counts, distributions, any surprises)
    - **Results summary** (key numbers, figures produced, comparison to
      expectations if available — this feeds into RESULTS_UPDATE.md)
    - **Sensitivity assessment** (if this is a sensitivity task: does the
      result hold? What is the economic interpretation of any divergence?)
    - Files changed
    - Self-review findings (if any)
    - Any data quality concerns

    ## If Running as Agent Team Teammate

    If you are part of an Agent Team (not a standalone subagent):
    - Use the shared task list to track your assigned tasks
    - When you encounter issues that need reviewer input, continue working
      and note them in your report — the reviewer will see your completed
      work via the task dependency
    - Message the lead for escalation decisions that need user input
      (BLOCKED, data quality concerns, methodology questions)
    - Mark your tasks as completed when done
    - When a reviewer messages you with REVISE feedback, fix the issues
      and message them back when ready for re-review
```
