---
name: using-superRA
description: Meta (session start). Use at the beginning of every session to establish skill-discovery rules, cross-session detection for in-progress analysis work (PLAN.md, worktrees, analysis branches), and instruction priority (user instructions > superRA skills > default system prompt). Mandatory housekeeping before substantive responses; skill-tool invocation required before clarifying questions.
---

## MANDATORY: Session Start Actions

Before your first substantive response, run these cross-session detection checks:
1. Check for PLAN.md in the working directory
2. Check for analysis worktrees (`git worktree list`)
3. Check for analysis branches (`git branch --list 'analysis/*'`)
4. If any exist, report to the user: "Found in-progress analysis work: [details]"

Do NOT skip these because the user "jumped straight into a task." The checks take 5 seconds and prevent lost work.

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. This is not optional. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## Instruction Priority

SuperRA skills override default system prompt behavior, but **user instructions always take precedence**:

1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
2. **SuperRA skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

If CLAUDE.md says "skip data description for this dataset" and a skill says "always describe first," follow the user's instructions. The user is in control.

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

## How to Access Skills

**In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded and presented to you—follow it directly. Never use the Read tool on skill files.

**In Copilot CLI:** Use the `skill` tool. Skills are auto-discovered from installed plugins.

**In Gemini CLI:** Skills activate via the `activate_skill` tool.

**In other environments:** Check your platform's documentation for how skills are loaded.

## Platform Adaptation

Skills use Claude Code tool names. Non-CC platforms: see `references/copilot-tools.md` (Copilot CLI), `references/codex-tools.md` (Codex) for tool equivalents. Gemini CLI users get the tool mapping loaded automatically via GEMINI.md.

# Using Skills

## The Rule

**Invoke relevant or requested skills BEFORE any response or action.** Even a 1% chance a skill might apply means that you should invoke the skill to check. If an invoked skill turns out to be wrong for the situation, you don't need to use it.

```dot
digraph skill_flow {
    "User message received" [shape=doublecircle];
    "Check for in-progress work" [shape=box];
    "Resume analysis?" [shape=diamond];
    "Load plan, continue from checkpoint" [shape=box];
    "Might any skill apply?" [shape=diamond];
    "Invoke Skill tool" [shape=box];
    "Announce: 'Using [skill] to [purpose]'" [shape=box];
    "Has checklist?" [shape=diamond];
    "Create TodoWrite todo per item" [shape=box];
    "Follow skill exactly" [shape=box];
    "Respond (including clarifications)" [shape=doublecircle];

    "User message received" -> "Check for in-progress work";
    "Check for in-progress work" -> "Resume analysis?" [label="plan found"];
    "Check for in-progress work" -> "Might any skill apply?" [label="no plan"];
    "Resume analysis?" -> "Load plan, continue from checkpoint" [label="yes"];
    "Resume analysis?" -> "Might any skill apply?" [label="no"];
    "Load plan, continue from checkpoint" -> "Might any skill apply?";

    "Might any skill apply?" -> "Invoke Skill tool" [label="yes, even 1%"];
    "Might any skill apply?" -> "Respond (including clarifications)" [label="definitely not"];
    "Invoke Skill tool" -> "Announce: 'Using [skill] to [purpose]'";
    "Announce: 'Using [skill] to [purpose]'" -> "Has checklist?";
    "Has checklist?" -> "Create TodoWrite todo per item" [label="yes"];
    "Has checklist?" -> "Follow skill exactly" [label="no"];
    "Create TodoWrite todo per item" -> "Follow skill exactly";
}
```

## Red Flags

These thoughts mean STOP—you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the data first" | Skills tell you HOW to explore. Check first. |
| "Let me load the data quickly" | Data loading requires description discipline. Check for skills. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just run this one merge first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |

## Skill Priority

The macro workflow is **PLAN → IMPLEMENT → VALIDATE → INTEGRATE**. When multiple skills could apply, follow this flow:

1. **PLAN phase skills first** (planning-workflow) — these determine WHAT to do
2. **IMPLEMENT + VALIDATE phase skills second** (execution-workflow, econ-data-analysis) — these guide execution and review
3. **INTEGRATE phase skills last** (integration-workflow, merge-workflow) — these integrate work back

"Let's analyze X" → PLAN phase: planning-workflow (Phase 1 inventory then Phase 2 plan creation).
"Something looks wrong in the data" → investigate using econ-data-analysis describe step.

Within each implementation step, the micro-level discipline is **DESCRIBE → ANALYZE → DOC** (see `econ-data-analysis`).

## Skill Types

**Rigid** (econ-data-analysis, verification-before-completion): Follow exactly. Don't adapt away discipline.

**Flexible** (planning-workflow Phase 1 data inventory): Adapt principles to context.

The skill itself tells you which.

## Semantic Merge

When merging, rebasing, or cherry-picking branches, superRA uses intent-based conflict resolution rather than mechanical ours/theirs. Research-meaningful conflicts are always escalated to the user. See `superRA:semantic-merge` for the full process. A PreToolUse hook automatically reminds you to use this skill when a bare `git merge/rebase/cherry-pick` is detected.

## Agent Teams

When `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is enabled, superRA uses Agent Teams for workflows with iteration loops (execution-workflow, integration-workflow, merge-workflow, semantic-merge). This is automatic — the orchestration skills detect availability and use teams when appropriate. See `superRA:agent-orchestration` for details on team compositions, lifecycle, and session handoff.

## Reviewer–Orchestrator Dynamic

The reviewer is **adversarial by design** — it should be thorough, skeptical, and flag everything it is uncertain about. A false positive costs one orchestrator evaluation; a missed issue can ship wrong results. The orchestrator is the **arbitrator** — it made the plan, talks to the researcher, and has big-picture context the reviewer lacks. It expects over-flagging, evaluates each finding independently, and overrules with documented reasoning when the reviewer is wrong. This dynamic applies across all stages (execution, integration, merge, semantic-merge). See CLAUDE.md workflow principle P1 for the full statement.

## User Instructions

Instructions say WHAT, not HOW. "Analyze X" or "Merge these datasets" doesn't mean skip econ-data-analysis discipline.
