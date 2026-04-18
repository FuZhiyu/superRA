---
name: semantic-merge
description: Use when about to run `git merge`, `git rebase`, or `git cherry-pick` on research code — or any time incoming changes from another branch may touch results-bearing files, analysis scripts, PLAN.md, RESULTS.md, or drift tests — and you want thoughtful, research-aware conflict resolution rather than mechanical ours/theirs; when pulling main into an analysis branch; when integrating a sibling analysis; when a "simple" conflict might silently change results. Triggers include bare `git merge` / `git rebase` / `git cherry-pick` on a research branch (the merge-guard hook will flag these automatically), "pull main into this branch", "rebase onto main", "cherry-pick commit X", or any merge where at least one hunk touches a results-bearing file. Invoked internally by `merge-workflow` Step 1; also usable standalone for ad-hoc merges outside the analysis-finishing flow.
---

# Semantic Merge

Integrate branches by intent, not by lines. Classify conflicts by research impact, escalate research-meaningful decisions to the user, and use a two-commit structure (mechanical merge + integration commit) with subagent-driven propose+review.

Adapts the general-purpose `semantic-merge-integration` skill for economics research contexts, adding tiered classification, drift test integration, data discipline re-validation through the merge, and RA-framing human-in-the-loop decisions.

**Core principle:** Treat conflicts as intent conflicts first. Research-meaningful conflicts always go to the user. The agent implements the researcher's integration decisions — never judges methodology.

**Announce at start:** "I'm using the semantic-merge skill to integrate these branches."

## When to Use

- User asks to merge, rebase, cherry-pick, or sync branches
- `superRA:merge-workflow` Step 1 delegates to this skill to update an analysis branch from main
- Updating a long-lived analysis branch from main/upstream
- The PreToolUse `merge-guard` hook reminds you when you attempt a bare `git merge/rebase/cherry-pick` outside the analysis-finishing flow

## Invocation Pattern

semantic-merge has two modes. Tier classification and conflict resolution are identical across modes. **Post-merge verification differs** — standalone owns it all; delegated trims the duplicate checks that the caller will re-run.

- **Standalone (ad-hoc merge).** The user asks you to merge, rebase, or cherry-pick, or the `merge-guard` PreToolUse hook fires on a bare git merge command. Load this skill directly, run the process below (including all post-merge verification), and report back to the user. You own the outcome.
- **Delegated from `merge-workflow` Step 1.** The orchestrator running `merge-workflow` loads this skill via an explicit `Skill superRA:semantic-merge` invocation with task: `"merge <base> into <analysis> — delegated mode: skip post-merge drift tests and pipeline run; the caller will verify"`. Run the tier-classification + conflict-resolution parts, then return the tier classification + a one-line incoming-impact verdict (see §What to Report — delegated). The caller (`merge-workflow`) runs post-merge drift tests and integration review on the merged state in its Step 2. Do NOT run drift tests, pipeline, or stale-reference checks yourself in delegated mode — those are the caller's.

### Mode-aware verification

| Step | Standalone | Delegated |
|---|---|---|
| Tier classification | yes | yes |
| Conflict resolution (incl. Tier 2/3 propose+review) | yes | yes |
| Drift tests on merged state | yes | **skip** (caller runs in merge-workflow Step 2a) |
| Pipeline run on merged state | yes | **skip** (caller runs in merge-workflow Step 4) |
| Stale-reference check on merged state | yes | **skip** (covered by caller's integration review in Step 2b) |
| Return tier classification + incoming-impact verdict | n/a | yes (required for merge-workflow's skip logic per Task 11) |

The mechanics of tier classification and conflict resolution below are identical across modes; only the post-merge verification block (Tier 1 step 2-4; Tier 2 step 5; Tier 3 steps 8-9) is mode-gated. Each gate below is annotated `[standalone-only]`.

## The Process

1. **Ground in repo state.**
2. **Run `git merge --no-commit`** and classify:
   - **No conflicts AND no analysis files touched** → **Tier 1** (clean).
   - **No conflicts AND analysis files touched** → run drift tests:
     - Pass → **Tier 1** (clean).
     - Fail → **Tier 3** (semantic).
   - **Conflicts exist** → classify each conflicting file:
     - Config / docs / infra only → **Tier 2** (syntactic).
     - Any research file in conflict → **Tier 3** (semantic).

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
| Results files | Tables, figures, RESULTS.md | 3 |
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
2. `[standalone-only]` Run drift tests (if they exist):
   ```bash
   # Run existing test suite
   ```
3. `[standalone-only]` Run pipeline (if it exists):
   ```bash
   bash run_all.sh  # or equivalent
   ```
4. `[standalone-only]` If everything passes: done.
5. `[standalone-only]` If drift tests fail: abort and escalate to Tier 3.

**Delegated mode:** after step 1 completes the merge, skip steps 2-5 and return tier + incoming-impact per §What to Report — delegated mode. The caller (`merge-workflow`) runs drift tests in its Step 2a and may skip its Step 2b integration review if the incoming-impact verdict shows no analysis-path changes.

### Tier 2: Syntactic Conflicts

Conflicts exist but none touch research-relevant files.

1. **Dispatch merge-proposer:**
   ```
   Agent(subagent_type: "superRA:implementer"):
     Stage: merge
     Task: propose Tier 2 merge — <base>..<incoming-branch>

     Follow the standard stage-relevant workflow and load
       relevant skills and documents to proceed. Additionally, Tier 2 —
       syntactic conflicts only (config/docs/infra); execute the two-commit
       merge (Commit 1 mechanical, Commit 2 integration). <optional steering>.
   ```

2. **Proposer executes** the two-commit merge per the `merge-quality.md` checklist (Commit 1 mechanical, Commit 2 integration).

3. **Dispatch merge-reviewer:**
   ```
   Agent(subagent_type: "superRA:reviewer"):
     Stage: merge
     Task: review the Tier 2 merge proposal
     Git range: <BASE_SHA>..<HEAD_SHA>

     Follow the standard stage-relevant workflow and load
       relevant skills and documents to proceed. Additionally,
       <optional steering>.
   ```

4. **If REVISE:** adjudicate the reviewer's feedback per the orchestrator discipline in `superRA:agent-orchestration` §Handling Reviewer Feedback. Forward accepted issues to the merge-proposer; push back or override others with documented reasoning. Iterate until APPROVE.

5. `[standalone-only]` **Run drift tests.** If pass: done. If fail: escalate to user (Tier 3 handling). **Delegated:** skip — the caller runs drift tests in `merge-workflow` Step 2a. Return tier + incoming-impact per §What to Report — delegated mode.

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

3. **Dispatch merge-proposer** with Tier 3 context:
   ```
   Agent(subagent_type: "superRA:implementer"):
     Stage: merge
     Task: propose Tier 3 merge — <base>..<incoming-branch>

     Follow the standard stage-relevant workflow and load
       relevant skills and documents to proceed. Additionally, this is
       a Tier 3 semantic merge — research-relevant files are in conflict
       and integration decisions require user-facing flags. Produce an
       integration map classifying changes by research role (analysis /
       data processing / methodology / infrastructure / docs / generated)
       and flag research-meaningful decisions for orchestrator escalation.
   ```

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

8. `[standalone-only]` **Run drift tests.** If drift tests fail after integration:
   - Present before/after values to user
   - Assess economic significance (same framework as integration-workflow)
   - **Meaningful drift:** STOP. User decides whether to accept or revise.
   - **Minor variation:** Update test expectations with documented reason.
   
   **Delegated:** skip — the caller runs drift tests in `merge-workflow` Step 2a, which handles meaningful-vs-minor drift per the same framework. Return tier + incoming-impact per §What to Report — delegated mode.

9. `[standalone-only]` **Verify pipeline** runs end-to-end on the merged result. **Delegated:** skip — the caller will verify the pipeline post-merge in its Step 4 (or decide not to per that step's logic).

## Working Principles

- **Intent first.** Understand WHY each side made its changes before deciding which lines to keep.
- **Never ours/theirs blindly.** Except for generated artifacts that will be regenerated immediately.
- **Preserve user work.** Never discard dirty state or unrelated edits without explicit approval.
- **Regenerate over edit.** For generated files (tables, figures, compiled outputs), regenerate from merged source rather than hand-editing.
- **RA framing.** You propose integration, present options, and implement the researcher's decisions. You never judge whether the methodology is correct.
- **Data discipline.** If incoming changes affect data processing, verify describe-analyze-validate artifacts (row-count logs, distribution diagnostics, validation checks) are preserved in the merged result.
- **Drift tests are the safety net.** In standalone mode, always run them after the merge; never skip; never silently update expectations for meaningful changes. In delegated mode, you do NOT run drift tests — `merge-workflow` Step 2a does, against the same discipline — and "skipping" here means handing the responsibility to the caller, not dropping it.

## When to Ask the User

These are the Tier 3 escalations for semantic-merge and the only stop points in the skill — the rest of the merge proposal/review loop runs autonomously per `superRA:using-superRA` §Universal Principles (principle #4). Use `AskUserQuestion` (plain text if unavailable) at every stop below; when the conflict has a closed set of resolutions (`--ours`, `--theirs`, synthesize, regenerate, roll back), pass them as the question options. When the decision is genuinely open-ended (methodology rewrite, sample redefinition), frame the question as free-form prose but still route it through `AskUserQuestion` if available.

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

**Log every answer** per `handoff-doc` §User Decisions Log; include the log entry in the integration commit that implements the resolution. If `PLAN.md` has already been disposed of, record the decision in the merge commit message instead — the commit message is the record of record once the doc is gone.

## What to Report

### Standalone mode

When the merge is complete, summarize:
- **Tier classification** and rationale
- **Incoming intent:** What the incoming changes accomplish
- **Integration decisions:** What was kept from each side, what was synthesized
- **User decisions:** What questions were asked and how the user answered
- **Drift test results:** Pass/fail with details
- **Pipeline status:** Runs or fails
- **Verification:** Stale references checked, data discipline preserved

### Delegated mode (called from `merge-workflow` Step 1)

The caller (`merge-workflow`) uses the return to decide whether to skip its Step 2b post-merge integration review (see `merge-workflow` §Step 2). Return EXACTLY these fields — the skip logic reads them by name:

- **Tier classification:** `Tier 1` / `Tier 2` / `Tier 3` and a one-sentence rationale.
- **Incoming impact:** one line — did the incoming diff touch any file in the analysis paths? Name the paths that were changed. Example: `Incoming impact: touched config/pipeline.yaml and .github/workflows/ci.yml; no analysis-path changes.`
- **Integration decisions + User decisions:** same content as standalone, but keep it to one short paragraph each — the caller will not re-present these to the user.
- **Drift tests:** `not run (delegated; caller will run in Step 2a)`.
- **Pipeline:** `not run (delegated; caller will run in Step 4 or skip per that step's logic)`.
- **Verification:** `deferred to caller's Step 2b integration review`.

The tier classification and the incoming-impact line are load-bearing: `merge-workflow` Step 2 reads them to decide Step 2b skip eligibility.

## Agent Loads

See `superRA:using-superRA` §Skill-Load Manifest — it is the single source of truth for what every dispatched implementer / reviewer loads per Stage. This skill runs the `merge` row.

## Red Flags

**Never:**
- Run bare `git merge` without tier classification in a research context
- Choose `--ours` or `--theirs` for research-relevant files without user input
- Resolve analysis-code conflicts without presenting options to the user
- Judge the researcher's methodology — you integrate, you don't evaluate (see the foundational RA framing in `superRA:using-superRA` §Universal Principles)
- Discard dirty worktree state without explicit approval

**Always:**
- Classify the merge into a tier before proceeding
- Understand incoming intent before resolving conflicts
- Use two-commit structure (mechanical + integration)
- In **standalone mode**, run drift tests and verify the pipeline on the merged result after every merge
- In **delegated mode**, return tier classification + incoming-impact per §What to Report — delegated mode; the caller runs drift tests + pipeline
- Present research-meaningful conflicts to the user with intent and consequences
- Keep and re-validate data discipline artifacts through the merge (describe steps, row counts, validation)

**Drift-test integrity after the merge is governed by the cross-cutting rules in `refactor-and-integrate` reference `drift-test-quality.md` — failing tests after a merge must be adjudicated, not silently re-expected. Load the reference before running post-merge tests.**

## Integration

**Called by:**
- **superRA:merge-workflow** (Step 1) — Update analysis branch from base before merging back, as part of the final phase of the analysis-finishing workflow
- **PreToolUse hook** (merge-guard) — Reminds agent to use this skill for any git merge/rebase/cherry-pick

**Can invoke standalone:** User asks to merge/update branches

**Pairs with:**
- **superRA:integration-workflow** — Runs before this skill in the integration phase (creates drift tests that this skill uses as safety net)

**References:**
- **semantic-merge-integration** (global skill) — General-purpose merge philosophy that this skill adapts for research
