# Session Bootstrap — Cross-Session Detection

Main agent loads this at session start; subagents skip — they inherit task context from their dispatch.

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
