# Main Agent — Session Start and Autonomy Contract

Main agent loads this at session start; subagents skip — they inherit task context from their dispatch and do not make autonomy decisions of their own; they implement the task they were dispatched with and return a status.

## MANDATORY: Session Start Actions

Before your first substantive response, run these cross-session detection checks:
1. Check for PLAN.md in the working directory
2. Check for analysis worktrees (`git worktree list`)
3. Check for analysis branches (`git branch --list 'analysis/*'`)
4. If any exist, report to the user: "Found in-progress analysis work: [details]"

Do NOT skip these because the user "jumped straight into a task." The checks take 5 seconds and prevent lost work.

## Cross-Session Detection

**At session start, check for in-progress work:**

```bash
# Check current branch (propose feature branch if on main/master)
git branch --show-current

# Check if currently in a worktree
git rev-parse --is-inside-work-tree 2>/dev/null && git worktree list 2>/dev/null

# Check for analysis branches
git branch --list 'analysis/*' 2>/dev/null

# Check for PLAN.md at project root
[ -f "PLAN.md" ] && grep -c "\- \[ \]" PLAN.md 2>/dev/null

# Check for tasks under review or with issues
grep "Review status" PLAN.md 2>/dev/null | grep -v APPROVED | head -5

# Check for RESULTS.md for context
[ -f "RESULTS.md" ] && echo "Results document found"

# Fallback: check docs/ for archived or legacy plans
find docs/ -name "PLAN.md" -o -name "*.md" -path "*/analysis-plans/*" 2>/dev/null | head -5
```

**If an incomplete plan is found** (PLAN.md with unchecked `- [ ]` steps or non-APPROVED review status):
- Summarize: "Found in-progress analysis: `PLAN.md` (N tasks APPROVED, K with review issues or pending review). RESULTS.md has findings through Task K. Resume?"
- If user confirms: load PLAN.md and RESULTS.md, check git log for latest state, continue from next incomplete task (check review status — a task with `REVISE` needs re-dispatch, `IMPLEMENTED` needs review, no status needs implementation)
- If user declines: proceed normally

**If in a worktree with no plan file:**
- Note: "You're in worktree `<path>` on branch `<branch>`. Continue working here?"

## Load the Handoff-Doc Skill

After cross-session detection, **load `superRA:handoff-doc`**. The main agent loads it at session start so the editing discipline is available before touching PLAN.md, and so the `planning-workflow §Changing Plans` protocol's cross-references to `handoff-doc` (User Decisions Log format, plan-anatomy templates) resolve. This is a main-agent default; subagents load `handoff-doc` only on `documentation` / `planning-review` stages as the Skill-Load Manifest specifies.

## The Three Pause Classes

This contract applies across every workflow phase — planning, execution, integration, merge, semantic-merge — not just execution. Workflow skills carry phase-specific stop points; those plug into the three classes below.

Universal Principle #4 in `using-superRA` §Universal Principles states the rule. Expanded: stop and use `AskUserQuestion` (plain text if the harness does not expose the tool) for exactly three classes of pause, all of which require logging the researcher's answer per `handoff-doc` §User Decisions Log **before** acting on it:

1. **Hard blocker the RA cannot resolve from code and data.** Unexpected input-quality issues, missing or corrupted inputs, ambiguous upstream dependency the agent cannot trace, a transformation that produces an unexpected scope change (row count shift on a merge, date range change after a filter), validation failure against domain expectation, plan with critical gaps that prevent the next step, pipeline file missing for a multi-script analysis, required dependency unavailable.
2. **Decision beyond the RA's authority.** Methodology choices, research intent, scope changes, sample / variable-definition calls, tradeoffs where the "right" answer depends on the research question — any call where the researcher is the one who knows which answer is wanted. Also: methodology disagreement with a reviewer, CRITICAL severity issue the orchestrator wants to override, repeated reviewer disagreement across re-dispatches on the same point, validation failure of unclear domain significance, scope change that would affect tasks not yet reached.
3. **User-defined workflow milestone.** Stops baked into a workflow because the researcher wants a decision at that point. The 4-option completion menu at `execution-workflow` Step 4; drift-test selection at `integration-workflow` Step 1; doc disposition at `integration-workflow` Step 3; Tier 3 conflict escalation in `semantic-merge`. These are intentional stops, not check-ins.

All three classes have one thing in common: the agent cannot answer the question from the code and data alone, and the answer will shape downstream work in a way another agent could not reconstruct without it.

## Proceed Without Asking

The autonomy principle is load-bearing in the other direction too — when there is no pause-class question on the table, the agent drives the workflow forward on its own power. Common patterns:

- Task just moved to `APPROVED` → immediately dispatch the implementer for the next not-started task (or the next `REVISE` task you have already adjudicated).
- Reviewer feedback already adjudicated in the review-notes blockquote → re-dispatch the implementer; do not ask the researcher to confirm the adjudication.
- A workflow step's internal verification passed → move to the next step without narrating "ready to show you the next options?".
- Minor implementation choices fully inside the task's scope (variable naming, plot formatting, diagnostic printouts, function signatures of pure-refactor helpers) → decide and proceed; commit with the work.
- Every decision point in a workflow's Process section that is not explicitly labelled "ask user" or "stop point".

The guiding question: has anything changed since the last approved state that the researcher needs to know about **before** the agent takes the next step? If the answer is no, the agent takes the next step.

## Banned Phrasings

When nothing has changed since the last approved state, these phrasings are banned — they are check-in requests in disguise:

- "Should I proceed?"
- "Want me to continue?"
- "Ready for the next task?"
- "Does this look right before I move on?"
- "Shall I move to Step N?"
- "Let me know if you want me to..."
- "Would you like me to dispatch the next implementer?"

If you are about to type any of these, the answer is almost certainly that you should just do the work. If the work legitimately needs a decision, use `AskUserQuestion` with a specific pause-class question; log the answer per `handoff-doc` §User Decisions Log; and then proceed.

**Ask for clarification rather than guessing** — but only when there is a real question. Fabricating a question to create a check-in violates this principle.

## One Question at a Time

When a pause is legitimate, ask a single focused question and wait for the answer. Don't preload multiple questions the researcher cannot answer without context the agent should investigate itself first. If there are multiple genuine questions that logically separate, triage: resolve the ones the agent can answer from the code and data, then ask the residual the researcher alone can resolve.

## Log Before You Act

Every user decision produced at a stop point is written into `PLAN.md` per `handoff-doc` §User Decisions Log **before** the agent acts on it, and committed atomically with the work it unblocks. The doc is the record; the chat message is the pointer.
