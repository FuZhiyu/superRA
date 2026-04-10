---
name: semantic-merge
description: Use when merging, rebasing, or cherry-picking branches — classifies conflicts by research impact, escalates research-meaningful decisions to user, and uses two-commit integration with subagent-driven propose+review
---

# Semantic Merge

Integrate branches by intent, not by lines. Classify conflicts by research impact, escalate research-meaningful decisions to the user, and use a two-commit structure (mechanical merge + integration commit) with subagent-driven propose+review.

Adapts the general-purpose `semantic-merge-integration` skill for economics research contexts, adding tiered classification, drift test integration, data discipline preservation, and RA-framing human-in-the-loop decisions.

**Core principle:** Treat conflicts as intent conflicts first. Research-meaningful conflicts always go to the user. The agent implements the researcher's integration decisions — never judges methodology.

**Announce at start:** "I'm using the semantic-merge skill to integrate these branches."

## When to Use

- User asks to merge, rebase, cherry-pick, or sync branches
- Finishing-analysis Step 4d needs to merge an analysis branch (invoked automatically)
- Updating a long-lived analysis branch from main/upstream
- The PreToolUse hook reminds you when you attempt a bare `git merge/rebase/cherry-pick`

## The Process

```dot
digraph semantic_merge {
    rankdir=TB;

    "Ground in repo state" [shape=box];
    "Run git merge --no-commit" [shape=box];
    "Conflicts?" [shape=diamond];
    "Analysis files touched?" [shape=diamond];
    "Run drift tests" [shape=box];
    "Drift tests pass?" [shape=diamond];
    "Classify conflicting files" [shape=box];
    "Research files in conflict?" [shape=diamond];

    "Tier 1: Clean" [shape=box style=filled fillcolor=lightgreen];
    "Tier 2: Syntactic" [shape=box style=filled fillcolor=lightyellow];
    "Tier 3: Semantic" [shape=box style=filled fillcolor=lightsalmon];

    "Ground in repo state" -> "Run git merge --no-commit";
    "Run git merge --no-commit" -> "Conflicts?";
    "Conflicts?" -> "Analysis files touched?" [label="no"];
    "Analysis files touched?" -> "Tier 1: Clean" [label="no"];
    "Analysis files touched?" -> "Run drift tests" [label="yes"];
    "Run drift tests" -> "Drift tests pass?";
    "Drift tests pass?" -> "Tier 1: Clean" [label="pass"];
    "Drift tests pass?" -> "Tier 3: Semantic" [label="fail"];
    "Conflicts?" -> "Classify conflicting files" [label="yes"];
    "Classify conflicting files" -> "Research files in conflict?";
    "Research files in conflict?" -> "Tier 2: Syntactic" [label="no — config/docs/infra only"];
    "Research files in conflict?" -> "Tier 3: Semantic" [label="yes"];
}
```

### Step 1: Ground in Repo State

Before changing anything:

```bash
# Current state
git status
git branch --show-current
git log --oneline -5

# Merge base and incoming range
MERGE_BASE=$(git merge-base HEAD <incoming-branch>)
git log --oneline $MERGE_BASE..<incoming-branch>

# What files are touched
git diff --name-only $MERGE_BASE..<incoming-branch>
```

If the worktree is dirty, preserve it safely before merge work:
```bash
git stash push -m "pre-merge snapshot"
```

### Step 2: Classify the Merge

Test the merge without committing:

```bash
git merge --no-commit <incoming-branch>
```

**If clean (no conflicts):**
- Check if incoming changes touch analysis files (scripts, data processing, results)
- If no analysis files touched → **Tier 1** (complete the merge with `git merge --continue` or `git commit`)
- If analysis files touched → run drift tests on the merged tree
  - Drift tests pass → **Tier 1** (complete the merge)
  - Drift tests fail → abort the test merge (`git merge --abort`), proceed to **Tier 3**

**If conflicts exist:**
- Abort the test merge: `git merge --abort`
- Classify each conflicting file:

| File Type | Examples | Tier |
|-----------|----------|------|
| Analysis scripts | `.py`, `.jl`, `.R` with analysis content | 3 |
| Data processing | Variable construction, sample filters | 3 |
| Results files | Tables, figures, RESULTS_UPDATE.md | 3 |
| Research planning | PLAN.md | 3 |
| Drift tests | `tests/` guarding analysis results | 3 |
| Configuration | Build scripts, CI, project config | 2 |
| Infrastructure | Utility functions, shared modules | 2 |
| Documentation | README, non-results docs | 2 |
| Generated files | Compiled outputs, caches | 2 |

**Final tier = max across all conflicting files.** If any file is Tier 3, the whole merge is Tier 3.

### Tier 1: Clean Merge

No subagents needed. Execute directly.

1. Complete the merge (if `--no-commit` test merge is still staged, commit it; otherwise run a fresh merge):
   ```bash
   git merge <incoming-branch>  # or git commit if --no-commit is staged
   ```
2. Run drift tests (if they exist):
   ```bash
   # Run existing test suite
   ```
3. Run pipeline (if it exists):
   ```bash
   bash run_all.sh  # or equivalent
   ```
4. If everything passes: done.
5. If drift tests fail: abort and escalate to Tier 3.

### Tier 2: Syntactic Conflicts

Conflicts exist but none touch research-relevant files.

1. **Dispatch merge-proposer:** `Agent(subagent_type: "implementer")` with skill `superRA:econ-data-analysis` and domain reference `./references/merge-quality.md`. Provide:
   - Merge context (branches, merge base, tier)
   - Incoming commit messages and diffs since merge base
   - List of conflicting files with their classification
   - Current branch purpose

2. **Proposer executes** two-commit merge:
   - **Commit 1 (mechanical):** Resolve conflicts with lowest-assumption reconciliation. Restore buildable state. No opportunistic cleanup.
   - **Commit 2 (integration):** Adapt code, docs, tests so the branch incorporates incoming intent. Rewrite stale names, paths, references.

3. **Dispatch merge-reviewer:** `Agent(subagent_type: "reviewer")` with skill `superRA:econ-data-analysis` and domain reference `./references/merge-quality.md`. Provide:
   - Merge context
   - Proposer's report (integration map, decisions, rationale)

4. **If REVISE:** Proposer fixes issues, reviewer re-reviews. Iterate until APPROVE.

5. **Run drift tests.** If pass: done. If fail: escalate to user (Tier 3 handling).

### Tier 3: Semantic / Research Conflicts

Conflicts touch research-relevant files, or drift tests fail on a clean merge.

1. **Ground in repo state** (Step 1 above, if not already done).

2. **Understand incoming intent.** Read commit messages and diffs since merge base. Classify changes by role:
   - Research output (analysis scripts, regressions, results)
   - Data processing (merges, filters, variable construction)
   - Methodology (specifications, controls, clustering)
   - Infrastructure (utilities, shared modules)
   - Documentation (README, methodology docs)
   - Generated outputs (tables, figures)

3. **Dispatch merge-proposer** (`implementer` agent + `./references/merge-quality.md`) with Tier 3 context. Provide:
   - Everything from Tier 2, plus:
   - Classification of changes by research role
   - Drift test results (if available)
   - Expected integration map with research-meaningful decisions flagged for user

4. **Present integration map to user.** The proposer's report identifies conflicts and proposes resolutions. Present research-meaningful decisions:

   ```
   Incoming changes affect research-relevant files. Integration map:

   1. [variable_construction.py] Incoming redefines `excess_return`
      from arithmetic to log returns. Your analysis uses this in
      Table 3. → REQUIRES YOUR DECISION
      Options: keep yours / adopt theirs / let me investigate

   2. [sample_filters.py] Incoming adds exclusion for firms with
      < 3 years of data. Your sample currently includes them.
      → REQUIRES YOUR DECISION
      Options: keep yours / adopt theirs / investigate impact

   3. [config.yaml] Incoming updates data paths. No research impact.
      → Will adopt incoming (auto-resolve)

   Which option for each?
   ```

5. **Execute merge** following user's decisions. Two commits:
   - Commit 1 (mechanical): resolve conflicts per user decisions
   - Commit 2 (integration): adapt remaining code to reflect the integrated intent

6. **Dispatch merge-reviewer** (`reviewer` agent + `./references/merge-quality.md`). Verify:
   - User's decisions were implemented correctly
   - No stale references to pre-merge state
   - Data discipline artifacts preserved
   - Intent from both sides is reflected

7. **If REVISE:** Proposer fixes, reviewer re-reviews.

8. **Run drift tests.** If drift tests fail after integration:
   - Present before/after values to user
   - Assess economic significance (same framework as pre-merge-gate)
   - **Meaningful drift:** STOP. User decides whether to accept or revise.
   - **Minor variation:** Update test expectations with documented reason.

9. **Verify pipeline** runs end-to-end on the merged result.

## Working Principles

- **Intent first.** Understand WHY each side made its changes before deciding which lines to keep.
- **Never ours/theirs blindly.** Except for generated artifacts that will be regenerated immediately.
- **Preserve user work.** Never discard dirty state or unrelated edits without explicit approval.
- **Regenerate over edit.** For generated files (tables, figures, compiled outputs), regenerate from merged source rather than hand-editing.
- **RA framing.** You propose integration, present options, and implement the researcher's decisions. You never judge whether the methodology is correct.
- **Data discipline.** If incoming changes affect data processing, verify describe-analyze-doc artifacts are preserved in the merged result.
- **Drift tests are the safety net.** Always run them after merge. Never skip. Never silently update expectations for meaningful changes.

## When to Ask the User

**Always ask:**
- Variable definition conflicts (affects economic interpretation)
- Sample construction conflicts (changes who/what is studied)
- Econometric specification conflicts (changes the model)
- Data source changes (changes underlying facts)
- Results interpretation changes (research conclusion territory)
- Drift test failures after merge (results protection)
- Both sides imply different valid research approaches

**Do not ask** (resolve automatically):
- Infrastructure/config conflicts with no research impact
- Documentation conflicts where intent is clear from context
- Generated file conflicts (regenerate from sources)
- Formatting or style conflicts

**Present ambiguity in terms of intent and consequences**, not raw diff chunks:
- Bad: "Lines 42-58 conflict between HEAD and incoming"
- Good: "Incoming changes redefine `excess_return` from arithmetic to log returns. Your branch uses this in regression Table 3."

## What to Report

When the merge is complete, summarize:
- **Tier classification** and rationale
- **Incoming intent:** What the incoming changes accomplish
- **Integration decisions:** What was kept from each side, what was synthesized
- **User decisions:** What questions were asked and how the user answered
- **Drift test results:** Pass/fail with details
- **Pipeline status:** Runs or fails
- **Verification:** Stale references checked, data discipline preserved

## Agent Types and Domain References

- **`implementer`** agent + `./references/merge-quality.md` — For merge proposals
- **`reviewer`** agent + `./references/merge-quality.md` — For merge review

All agents also load `superRA:econ-data-analysis` for data discipline.

## Agent Teams Mode

When Agent Teams are available (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`), the propose+review cycle can be orchestrated as a team for Tier 2 and Tier 3 merges.

**Invoke `superRA:agent-orchestration` for the Semantic Merge Team recipe** — it has the team composition (2 teammates), task graph, iteration patterns, and lead responsibilities.

The lead still handles tier classification, user-facing decisions (Tier 3 integration map), commits at each stage, and drift test verification.

## Red Flags

**Never:**
- Run bare `git merge` without tier classification in a research context
- Choose `--ours` or `--theirs` for research-relevant files without user input
- Skip drift tests after merge
- Silently update drift test expectations for meaningful result changes
- Resolve analysis-code conflicts without presenting options to the user
- Proceed past failing drift tests without escalation
- Judge the researcher's methodology — you integrate, you don't evaluate
- Discard dirty worktree state without explicit approval

**Always:**
- Classify the merge into a tier before proceeding
- Understand incoming intent before resolving conflicts
- Use two-commit structure (mechanical + integration)
- Run drift tests after every merge
- Present research-meaningful conflicts to the user with intent and consequences
- Preserve data discipline artifacts through the merge
- Verify pipeline runs on the merged result

## Integration

**Called by:**
- **superRA:finishing-analysis** (Step 4d) — Update analysis branch from base before merging back
- **PreToolUse hook** (merge-guard) — Reminds agent to use this skill for any git merge/rebase/cherry-pick

**Can invoke standalone:** User asks to merge/update branches

**Pairs with:**
- **superRA:pre-merge-gate** — Runs before this skill in finishing-analysis (creates drift tests that this skill uses as safety net)
- **superRA:agent-orchestration** — Semantic Merge Team recipe for Tier 2/3 merges

**References:**
- **semantic-merge-integration** (global skill) — General-purpose merge philosophy that this skill adapts for research
