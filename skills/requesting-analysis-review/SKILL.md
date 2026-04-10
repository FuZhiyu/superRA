---
name: requesting-analysis-review
description: Use when completing analysis tasks or before merging to verify data integrity, implementation correctness, and reproducibility
---

# Requesting Analysis Review

Dispatch a reviewer subagent to catch data integrity and implementation issues before they cascade. The reviewer gets precisely crafted context for evaluation — never your session's history.

**Core principle:** Review early, review often. Data bugs compound silently.

**Scope:** This skill is for **ad-hoc single-pass reviews** — quick checks, before-merge verification, or when data looks unexpected. For **structured per-task review** (data integrity gate then implementation correctness), use the two-stage review in `superRA:executing-analysis` instead.

## When to Request Review

**Mandatory:**
- After each task (built into executing-analysis two-stage review; this skill for ad-hoc cases)
- After completing a major analysis phase
- Before merge to main

**Optional but valuable:**
- When data looks unexpected (fresh perspective)
- Before downstream analysis (validate inputs)
- After complex merges or variable construction

## How to Request

**1. Get git SHAs:**
```bash
BASE_SHA=$(git rev-parse HEAD~1)  # or origin/main
HEAD_SHA=$(git rev-parse HEAD)
```

**2. Dispatch analysis-reviewer subagent:**

Use Task tool with superRA:data-analysis-reviewer type, fill template at `analysis-reviewer.md`

**Placeholders:**
- `{WHAT_WAS_IMPLEMENTED}` - What analysis step you completed
- `{PLAN_OR_REQUIREMENTS}` - What the plan specified
- `{BASE_SHA}` - Starting commit
- `{HEAD_SHA}` - Ending commit
- `{DESCRIPTION}` - Brief summary

**3. Act on feedback:**
- Fix Critical issues immediately (wrong results)
- Fix Major issues before proceeding (likely problems)
- Note Minor issues for later (suggestions)
- Push back if reviewer is wrong (with reasoning)

## Review Dimensions

The reviewer evaluates across these dimensions:

| Dimension | What It Checks |
|-----------|----------------|
| **Data integrity** | Descriptions before transforms, row counts logged, no silent data loss |
| **Code quality** | Clean, readable, jupytext format, logical structure |
| **Implementation** | Code correctly implements what was specified, results make economic sense |
| **Reproducibility** | Pipeline runs, outputs from committed code, paths correct |
| **Documentation** | Decisions justified, narrative interleaved, major choices explained |

## Example

```
[Just completed Task 2: Merge holdings with fund characteristics]

You: Let me request analysis review before proceeding.

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch superRA:data-analysis-reviewer subagent]
  WHAT_WAS_IMPLEMENTED: Merged fund holdings with characteristics, constructed portfolio weights
  PLAN_OR_REQUIREMENTS: Task 2 from PLAN.md
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661
  DESCRIPTION: Left join on fund_id × date, 4.7M rows, 2% unmatched

[Subagent returns]:
  Principle 1 (Description): PASS
  Principle 2 (Documentation): NEEDS WORK — missing markdown cell for unmatched rate decision
  Principle 3 (Validation): PASS
  Issues:
    Major: No investigation of 2% unmatched — is this systematic?
    Minor: Weight variable not benchmarked against published figures
  Assessment: REVISE

You: [Investigate unmatched rate, add markdown cell documenting 2% unmatched, benchmark weights]
[Re-dispatch reviewer for re-review]

[Subagent returns]:
  All checks: PASS
  Assessment: APPROVE

[Continue to Task 3]
```

## Integration

**Executing Analysis (two-stage review):**
- Built into the per-task review cycle (data integrity → implementation correctness)
- Automatic after each task — uses dedicated reviewer prompt templates

**Ad-Hoc (this skill):**
- Single-pass review for quick checks
- Before merge, when data looks unexpected, after complex operations

## Red Flags

**Never:**
- Skip review because "the data looks fine"
- Ignore Critical issues (wrong results)
- Proceed with unfixed Major issues
- Dismiss data quality concerns

**If reviewer wrong:**
- Push back with evidence (published benchmarks, source documentation)
- Show data that proves the approach is correct

See template at: requesting-analysis-review/analysis-reviewer.md
