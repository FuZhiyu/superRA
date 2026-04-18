# Agent-Dispatch Feedback Fixes — Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for doc mechanics. Use `superRA:execution-workflow` to execute this plan. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff. This plan edits skill/agent/hook files — not empirical data — so the usual `superRA:econ-data-analysis` per-step cycle does not apply. The per-step cycle here is **plan → edit → verify (grep / read) → commit**.

**Objective:** Apply user feedback from commit `a48f900` (on branch `manual-feedback`) to the superRA plugin. Feedback has two parts: (a) five pieces of new guidance embedded as HTML comments (F1–F6 below), and (b) three direct section removals the user made in `a48f900` that have NOT been merged into `econ-adaption` and must be re-applied. Deliverables are edits to `skills/`, `agents/`, `hooks/`, `tests/`, `README.md`, `RELEASE-NOTES.md`, `CLAUDE.md`.

**Methodology:** Treat `a48f900` as feedback input (read-only). Branch `feedback/agent-dispatch-fixes` off `econ-adaption` (currently `3db7681 bump version` — the PR `refactor/workflow-domain-split` merged into `econ-adaption` after this plan was initially drafted, so the worktree was rebased; file shapes now match the restructured post-refactor state that `a48f900` was raised against). Six tasks (T1–T5 plus a renumbered verification task) cover the six feedback items and three direct removals. Dispatch via the three-tier framework defined in feedback F2 itself (dogfooding). Use `Depends on:` declarations on every task (also dogfooding, from F6).

**Feedback Inventory (substitute for Data Inventory):**

Source: `git show a48f900` (also saved to `$TMPDIR/feedback-a48f900.diff`).

**Part A — HTML-comment feedback (new guidance):**

| # | Target file(s) on `manual-feedback` | Feedback |
|---|---|---|
| F1 | `skills/agent-orchestration/SKILL.md` | Agent Teams mode is unreliable — archive `references/agent-teams.md` with a banner, remove every active reference. |
| F2 | `skills/agent-orchestration/SKILL.md` | Add workload-balancing guidance: three tiers (trivial→inline; slightly-involved→bundle-and-delegate; complicated→dedicated agent), ≤150k tokens/agent rule, cache-reuse pointer. |
| F3 | `skills/agent-orchestration/SKILL.md` | Delete Decision Framework DOT graph + pattern table (no longer relevant once Teams archived). |
| F4 | `skills/agent-orchestration/SKILL.md` (dispatch template) | `<optional steering>` must be additive — never restate defaults, manifest, or `PLAN.md` content. |
| F5 | `agents/implementer.md`, `agents/reviewer.md` | Multi-agent repo warning: only commit your own edits when other agents' uncommitted changes appear. Teach `git add <specific-path>` mechanics. |
| F6 | `skills/planning-workflow/SKILL.md`, `references/plan-template.md` | Plans need `Depends on:` declarations so orchestrator can dispatch independent tasks in parallel (lightweight DAG, not a DSL). |

**Part B — Direct removals the user already made in `a48f900` (must be re-applied on `econ-adaption` because `a48f900` is NOT merged into the current base — only its sibling `refactor/workflow-domain-split` is):**

| # | Target file | Removal |
|---|---|---|
| D1 | `skills/agent-orchestration/SKILL.md` | Delete entire `## Dispatch-Return Deltas` section (lines ~86–91 on current HEAD). Comment on the user's diff was "not needed anymore". |
| D2 | `skills/agent-orchestration/SKILL.md` | Delete entire `## Integration` section at tail (listing Agent-Teams-mode workflow users). Falls out of F1 naturally. |
| D3 | `skills/handoff-doc/SKILL.md` | Delete the `**Not covered by this section:**` bullet block after the User Decisions Log (5 lines). |

**Feedback coverage map:** Every item above is addressed by exactly one task block below. F3, F4, D1, D2 all bundle into T2 with F2 because all five edit `skills/agent-orchestration/SKILL.md` in adjacent regions. D3 bundles into T4 with F6 because both touch doc-discipline skills.

**Output:**
- Updated skill files: `skills/agent-orchestration/SKILL.md`, `skills/planning-workflow/SKILL.md`, `skills/planning-workflow/references/plan-template.md`, `skills/execution-workflow/SKILL.md` (and any dependents named during T1 discovery).
- Updated agent files: `agents/implementer.md`, `agents/reviewer.md`.
- Archived reference: `skills/agent-orchestration/references/agent-teams.md` (prepended banner).
- Updated tests: `tests/structural-invariants.sh`.
- Updated docs: `README.md`, `RELEASE-NOTES.md`.
- Roughly 5–6 atomic commits, one per task.

**Expected Results / Hypotheses:** After all tasks APPROVED, a session reading `skills/agent-orchestration/SKILL.md` end-to-end sees a three-tier dispatch framework with token/cache guidance, no Teams-mode language, a tightened dispatch template, and no Decision Framework DOT graph. A session reading `agents/implementer.md` / `agents/reviewer.md` sees a Shared-Repo Commit Discipline sub-section. A session reading `skills/planning-workflow/SKILL.md` and authoring a new plan uses the new `Depends on:` field per task. Structural invariants pass. No active file grep-matches `TeamCreate|Agent Team|agent-teams\.md` (excluding `RELEASE-NOTES.md`).

**Pipeline:** N/A — this is skill-file editing, not a multi-script analysis. Verification commands are listed per task and in the end-to-end Verification section at the bottom.

**Sensitivity Analysis:** N/A for skill-editing. The analogue is: do the edits preserve behavior for cases the feedback did not address? For each task, the verification step includes a "sanity-read" that confirms surrounding content still reads coherently.

---

## Decisions

> **User decision (2026-04-17):** Skip planning-workflow Phase 1 Data Inventory gate — this task edits skill/agent/hook files, not empirical data. Substitute a "Feedback Inventory" section listing the items from commit `a48f900`.
> **Question asked:** Does the Data Inventory hard gate apply to a skill-editing task?
> **Rationale:** The gate exists to prevent coding against nonexistent data. For file-editing, the analog is enumerating the feedback items — done above. No empirical data to inventory.

> **User decision (2026-04-17):** Base this work on `econ-adaption` (now `3db7681 bump version` after the `refactor/workflow-domain-split` PR merge), NOT `manual-feedback`.
> **Question asked:** Which base branch for the fixes?
> **Rationale:** `manual-feedback` has WIP commits ahead of `econ-adaption`; the user wants the fix grounded on the merged, stable base. After the PR merge (commits `c35c56b` + `3db7681`), `econ-adaption` now contains the restructuring work the feedback was raised against — the worktree was rebased from `3755274` onto `3db7681` before plan execution.

> **User decision (2026-04-17):** Use the three-tier agent-dispatch framework (trivial→inline; slightly-involved→bundle-and-delegate; complicated→dedicated agent) to pick dispatch mode for each task in this plan itself. Pair with ≤150k tokens/agent.
> **Question asked:** How should the orchestrator dispatch these six tasks?
> **Rationale:** Dogfood the framework we are introducing. Bundles T2+T3+T4 into one dispatch; keeps T1 and T6 dedicated.

> **User decision (2026-04-17, merge-time):** Relocate §Shared-Repo Commit Discipline (F5) into `skills/using-superRA/SKILL.md` (next to main's centralized shared-agent discipline), with one-line pointers in `agents/implementer.md` + `agents/reviewer.md`. The discipline binds the main/orchestrator agent too, not just subagents — any agent that stages a commit must respect it.
> **Question asked:** Where should §Shared-Repo Commit Discipline live now that main consolidated shared-agent content in using-superRA?
> **Rationale:** DRY with main's task 6 consolidation; user noted main agent must also respect the discipline when other agents are active.

> **User decision (2026-04-17, merge-time):** Move top-level `PLAN.md` + `RESULTS.md` to `docs/plans/2026-04-17-agent-dispatch-feedback-{plan,results}.md` at the integration commit, following main's `docs/plans/` convention.
> **Question asked:** Delete the top-level plan docs or preserve them under `docs/plans/`?
> **Rationale:** Preserve the auditable record of the feedback round; align with main's convention.

> **User decision (2026-04-17, merge-time):** Delete `## Agent reuse vs fresh dispatch` from `skills/agent-orchestration/SKILL.md` (introduced on main via task 17) as part of the merge integration commit.
> **Question asked:** Preserve main's §Agent reuse vs fresh dispatch?
> **Rationale:** User-directed drop; keeps agent-orchestration lean and focused on Workload Balancing + Dispatch Templates.

---

### Task 1: Archive Agent Teams mode across the plugin

**Depends on:** *(none)*
**Review status:** APPROVED

**Files touched (verified to exist on `econ-adaption`):**
- `skills/agent-orchestration/SKILL.md`
- `skills/agent-orchestration/references/agent-teams.md`
- `agents/implementer.md`
- `agents/reviewer.md`
- `skills/execution-workflow/SKILL.md`
- `tests/structural-invariants.sh`
- `README.md`
- `RELEASE-NOTES.md`

**Files discovered during implementation (grep found and included):**
- `hooks/session-start` — stripped Teams detection (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` probe + `agent_teams_note` variable).
- `skills/integration-workflow/SKILL.md` — `## Agent Teams Mode` section removed.
- `skills/merge-workflow/SKILL.md` — `## Agent Teams Mode` section removed.
- `skills/semantic-merge/SKILL.md` — `## Agent Teams Mode` section removed; stale `Pairs with` bullet pointing at `agent-orchestration` removed.
- `skills/using-superRA/SKILL.md` — `## Agent Teams` section removed; intro line updated.
- `CLAUDE.md` — `agent-teams.md` reference removed from `agent-orchestration` ownership bullet.
- `skills/CATEGORIES.md` — category description updated.

**Dispatch tier:** Complicated — dedicated implementer agent, dedicated reviewer. Cross-file grep, test rewrite, doc sweep. Estimated ≤60k tokens for the agent.

- [x] **Step 1: Plan — enumerate all active references to Agent Teams**

Before-count across active files (excluding `agent-orchestration/SKILL.md` which is T2 scope and `agent-teams.md` itself): ~28 references across 10 files (`execution-workflow` ×10, `using-superRA` ×3, `integration-workflow` ×2, `merge-workflow` ×2, `semantic-merge` ×2, `agents/implementer.md` ×2, `agents/reviewer.md` ×2, `hooks/session-start` ×2, `CLAUDE.md` ×1, `README.md` ×2). `agent-orchestration/SKILL.md` had ~10 additional references (deferred to T2).

- [x] **Step 2: Edit — archive the reference file**

Prepended ARCHIVED banner + blank line to `skills/agent-orchestration/references/agent-teams.md`. Body preserved.

- [x] **Step 3: Edit — strip Teams references from active files**

Removed Teams references from all active files. `skills/agent-orchestration/SKILL.md` skipped per plan — handled in T2. Files edited:
- `skills/execution-workflow/SKILL.md`: removed Teams branch from DOT graph and deleted `## Agent Teams Mode` section.
- `agents/implementer.md`: deleted `## If Running as Agent Team Teammate` section.
- `agents/reviewer.md`: deleted `## If Running as Agent Team Teammate` section.
- `skills/integration-workflow/SKILL.md`, `skills/merge-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md`: deleted `## Agent Teams Mode` sections.
- `skills/using-superRA/SKILL.md`: deleted `## Agent Teams` section; updated intro sentence.
- `hooks/session-start`: removed `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` probe and `agent_teams_note` injection.
- `CLAUDE.md`: removed `agent-teams.md` pointer from `agent-orchestration` ownership description.
- `skills/CATEGORIES.md`: updated description for `agent-orchestration`.

- [x] **Step 4: Edit — replace the TeamCreate invariant in structural tests**

Replaced the `TeamCreate`-asserting body of invariant 22 in `tests/structural-invariants.sh` with archive-banner assertion + active-file cite check. Extended to also scan `skills/`, `agents/`, `hooks/` for active Teams references (excluding the archived file itself and `RELEASE-NOTES.md`).

- [x] **Step 5: Edit — README and RELEASE-NOTES**

`README.md`: updated `agent-orchestration` row description and `session-start` hook description to remove Teams language. `RELEASE-NOTES.md`: prepended `## 2026-04-17 — Agent Teams mode archived` entry.

- [x] **Step 6: Verify + commit**

Verification results:
1. Active Teams refs: only `skills/agent-orchestration/SKILL.md` (expected — T2 scope, not yet cleaned).
2. Archive banner: PASS.
3. Structural invariants: 1 FAIL (invariant 22 active-file check flags `agent-orchestration/SKILL.md` — expected, T2 handles it). All other invariants PASS.

---

### Task 2: Rewrite `agent-orchestration/SKILL.md` — add §Workload Balancing, delete Decision Framework + Dispatch-Return Deltas + Integration, tighten dispatch template

**Depends on:** Task 1
**Review status:** APPROVED

**Bundles feedback F2 + F3 + F4 + D1 + D2** — all five edit `skills/agent-orchestration/SKILL.md` in overlapping regions. One implementer, one reviewer. This is the "slightly involved, bundle-and-delegate" tier.

**Files touched:**
- `skills/agent-orchestration/SKILL.md`
- `tests/structural-invariants.sh` (invariant 14 updated; invariant 26 added)

**Dispatch tier:** Slightly involved — one bundled dispatch.

- [x] **Step 1: Plan — read current file, identify target regions**

Pre-edit outline on `econ-adaption` (after T1):
- `## Overview` — rewrote core-principle bullet (dropped Teams framing).
- `## Decision Framework` — **deleted entire section** (F3).
- `## Dispatch Templates` — edited `<optional steering>` placeholder (F4).
- `## Dispatch-Return Deltas` — **deleted entire section** (D1).
- `## Handling Reviewer Feedback` — kept (unchanged by feedback).
- `## Review Status Reference` — kept.
- `## Integration` — **deleted entire section** (D2).

- [x] **Step 2: Edit — delete Decision Framework section (F3)**

Removed `## Decision Framework` heading through the `**Rule of thumb:**` closing line (the DOT graph + pattern table). Transition to `## Dispatch Templates` is clean.

- [x] **Step 2b: Edit — delete Dispatch-Return Deltas section (D1)**

Removed `## Dispatch-Return Deltas` heading and its 7-line body. Convention is already specified in `agents/implementer.md` and `agents/reviewer.md` §Report Format.

- [x] **Step 2c: Edit — delete `## Integration` section (D2)**

Removed entire `## Integration` section (bulleted list of Teams-using skills + fallback paragraph). No referent after Teams archived.

- [x] **Step 3: Edit — rewrite `## Overview` core principle**

Replaced Teams-framing paragraph with: **Core principle:** parallel-dispatch independent tasks; serialize iterative loops; do trivial work inline. Also updated frontmatter description to remove Agent Teams language.

- [x] **Step 4: Edit — insert `## Workload Balancing` after `## Overview` (F2)**

Inserted three-tier section (Tier 1 trivial inline, Tier 2 bundle-and-delegate, Tier 3 dedicated agent) plus Rules of thumb (≤150k tokens/agent, cache-reuse, parallelize independent tasks) followed by `---` separator before `## Dispatch Templates`.

- [x] **Step 5: Edit — tighten `<optional steering>` placeholder (F4)**

Both implementer and reviewer templates now use: `<optional steering — focus area, prior-round adjudication notes, or warnings. Must add information on top of the default; never restate what the default protocol, skill-load manifest, or PLAN.md already says.>`. Additive-only paragraph added immediately after the reviewer template. Cleaned stale `Counterpart:` banned-item text and removed stale Agent Teams reference from Dispatch Templates prose.

- [x] **Step 6: Edit — update and add structural invariants**

Invariant 14 updated: `## Dispatch-Return Deltas` removed from checked heading list; `## Workload Balancing` added; two new checks for absence of `## Dispatch-Return Deltas` and `## Integration`. Invariant 26 added: checks for `## Workload Balancing` heading, three tier headings, `150k`, and `cache` references.

- [x] **Step 7: Verify + commit**

All structural invariants PASS (2 known pre-existing WARNs). Final outline: `## Overview`, `## Workload Balancing`, `## Dispatch Templates`, `## Handling Reviewer Feedback (Orchestrator Discipline)`, `## Review Status Reference`. No `## Decision Framework`. No Teams-era headings.

---

### Task 3: Add §Shared-Repo Commit Discipline to implementer + reviewer (F5)

**Depends on:** *(none)* — independent of Tasks 1 and 2 (different files).
**Review status:** APPROVED

**Files touched:**
- `agents/implementer.md`
- `agents/reviewer.md`

**Dispatch tier:** Slightly involved — mirrored sub-section in two files. One implementer bundle.

- [x] **Step 1: Plan — identify insertion points**

Read both files in full; located commit-handling sections. In `implementer.md`: git add/commit at lines 140–141, inside `### Update the Docs and Commit` as numbered item 3. In `reviewer.md`: `git commit -m "review: Task N <verdict>"` at line 132, as step 5 of the "On first review" numbered list. Inserted the new sub-section between items 2 and 3 (implementer) and between items 4 and 5 (reviewer).

- [x] **Step 2: Edit — insert the sub-section into `agents/implementer.md`**

Insert (preserving surrounding context):

```markdown
### Shared-Repo Commit Discipline

Other agents may be running in parallel in the same repository, and
their uncommitted edits may land in your `git status` output. **Only
commit the files you modified this turn.** Never commit sweeps.

Before staging:

1. Run `git status` and list every modified/new file. For each one,
   decide: did I touch this file (directly via Write/Edit) in this
   turn?
2. If yes → stage it by exact path: `git add path/to/file`.
3. If no → leave it untouched. Do NOT `git add -A`, `git add .`, or
   `git add -u`. Those stage other agents' in-flight work and produce
   cross-agent commit contamination that is hard to unwind.
4. Before `git commit`, run `git diff --cached` and confirm only your
   edits are staged. If you see unexpected content, unstage it with
   `git restore --staged path/to/file`.

If you see unfamiliar uncommitted changes and cannot tell whether they
are another agent's in-flight work or stale local state, stop and ask
the orchestrator — do not unilaterally discard or commit them.
```

- [x] **Step 3: Edit — insert the same sub-section into `agents/reviewer.md`**

Inserted identical text block. `agents/reviewer.md` on `econ-adaption` has no explicit `git add` block — only `git commit` at step 5 of the "On first review" list. Sub-section placed between steps 4 and 5 of that list (reviewer's commit step is just one line; the section precedes it as the discipline to apply before that commit).

- [x] **Step 4: Verify + commit**

```bash
# 1. Both files carry the sub-section
grep -l "Shared-Repo Commit Discipline" agents/implementer.md agents/reviewer.md | wc -l
# expected: 2

# 2. No contradicting language elsewhere
grep -n "git add -A\|git add \." agents/*.md | grep -v "Shared-Repo\|forbidden\|never\|not " || echo "OK"
```

Update PLAN.md + RESULTS.md. Commit:

```bash
git add agents/implementer.md agents/reviewer.md PLAN.md RESULTS.md
git commit -m "docs(agents): add §Shared-Repo Commit Discipline (implementer + reviewer)"
```

---

### Task 4: Add `Depends on:` field to plan template + §Task Dependencies in planning-workflow (F6) + delete handoff-doc "Not covered by this section" block (D3)

**Depends on:** Task 1 (both edit `skills/execution-workflow/SKILL.md`; serialize to avoid merge).
**Review status:** APPROVED

**Files touched:**
- `skills/planning-workflow/SKILL.md`
- `skills/planning-workflow/references/plan-template.md`
- `skills/execution-workflow/SKILL.md` (teach orchestrator to read `Depends on:`)
- `skills/handoff-doc/SKILL.md` (D3 — delete the `**Not covered by this section:**` block from User Decisions Log)

**Dispatch tier:** Complicated — schema change propagates across three files and the orchestrator's dispatch logic; also one small doc-discipline edit. Dedicated implementer + reviewer.

- [x] **Step 1: Edit — add `### Task Dependencies` sub-section to planning-workflow**

In `skills/planning-workflow/SKILL.md`, insert a new sub-section under Phase 2 (or wherever the Task Decomposition / Step Granularity content currently sits — read the file first to find the right place). Content:

```markdown
### Task Dependencies

Not every task is sequential. Identify independent branches at plan
time so the orchestrator can dispatch them in parallel (see
`agent-orchestration` §Workload Balancing).

**Format.** Each task block declares a `**Depends on:**` line listing
upstream task numbers, or `*(none)*` if the task has no upstream
dependency. The field is **required** — an omitted field is a plan
failure.

**When a task depends on another.**
- It reads the other task's output files.
- It needs a sample / variable / methodology decision finalized in the
  other task.
- It runs sensitivity / robustness on the other task's baseline
  results.

**When a task is independent (`Depends on: *(none)*`).**
- Loads its own raw inputs, produces its own outputs.
- Sits in a separate pipeline branch that doesn't meet downstream.

**Orchestration contract.** The `execution-workflow` orchestrator reads
these fields. Tasks whose dependencies are all `APPROVED` may be
dispatched as a single parallel Agent-tool batch, subject to
`agent-orchestration` §Workload Balancing. Mutually independent tasks
SHOULD run in parallel; serializing them is waste.

**Plan-time DAG sanity.** After writing all tasks, trace the dependency
edges. No cycles. No `Depends on: Task 99` pointing at a task that
doesn't exist. The terminal task(s) (no downstream) should be the ones
that produce the top-line results.
```

- [x] **Step 2: Edit — update the self-review checklist**

Add one item to `## Self-Review` in `skills/planning-workflow/SKILL.md`:

```markdown
**7. Dependency graph sanity.** Every task has a `**Depends on:**` line.
No cycles. If the plan has ≥2 independent branches, at least one pair of
tasks is marked parallelizable.
```

- [x] **Step 3: Edit — add `Depends on:` to the plan template task block**

In `skills/planning-workflow/references/plan-template.md`, modify the task-block structure (§"Task Block Structure") to insert the new field on the line directly under the task title, before `**Review status:**`:

```markdown
### Task N: [Phase Name]
**Depends on:** Task N-1 [, Task N-2] | *(none)*
**Review status:** *(set during execution — do not fill at planning time)*
```

Also add a short prose paragraph before the code example explaining the new field. Keep the existing worked example; add `**Depends on:** *(none)*` to it.

- [x] **Step 3b: Edit — delete handoff-doc "Not covered by this section" block (D3)**

In `skills/handoff-doc/SKILL.md` §User Decisions Log, locate and delete the `**Not covered by this section:**` block (bullet list explaining what isn't a user decision) plus the "If you are not sure whether an answer counts..." paragraph that follows. The preceding three-line user-decision format box and the following `## What Counts as Stale` heading stay intact. The block was removed on `manual-feedback` with no replacement; the user's edit implies the discussion is better handled by the positive-inclusion rule alone without the negation list.

- [x] **Step 4: Edit — teach execution-workflow about `Depends on:`**

Read `skills/execution-workflow/SKILL.md`. Find the Step where the orchestrator picks the next task to dispatch (the "decompose / dispatch next" step). Insert a paragraph:

```markdown
**Before dispatching, read each pending task's `Depends on:` field.**
Tasks whose dependencies are all `APPROVED` may be dispatched as a
single parallel Agent-tool batch (subject to `agent-orchestration`
§Workload Balancing). Serialize only when no parallel batch is
available.
```

Keep the existing prose; this is an addition, not a replacement.

- [x] **Step 5: Verify + commit**

```bash
# 1. New section in planning-workflow
grep -q "^### Task Dependencies" skills/planning-workflow/SKILL.md && echo "OK" || echo "FAIL"

# 2. Template field
grep -q "^\*\*Depends on:\*\*" skills/planning-workflow/references/plan-template.md && echo "OK" || echo "FAIL"

# 3. Self-review item
grep -q "Dependency graph sanity" skills/planning-workflow/SKILL.md && echo "OK" || echo "FAIL"

# 4. Execution-workflow update
grep -q "Depends on:" skills/execution-workflow/SKILL.md && echo "OK" || echo "FAIL"

# 5. Handoff-doc "Not covered" block removed
! grep -q "^\*\*Not covered by this section:\*\*" skills/handoff-doc/SKILL.md && echo "OK" || echo "FAIL"

# 6. Invariants
bash tests/structural-invariants.sh
```

Update PLAN.md + RESULTS.md. Commit:

```bash
git add skills/planning-workflow/ skills/execution-workflow/SKILL.md skills/handoff-doc/SKILL.md PLAN.md RESULTS.md
git commit -m "feat(planning-workflow): add task-dependency declarations; teach execution-workflow to batch parallel tasks; drop handoff-doc user-decisions negation block"
```

---

### Task 5: End-to-end verification + RELEASE-NOTES consolidation

**Depends on:** Task 1, Task 2, Task 3, Task 4
**Review status:** IMPLEMENTED

**Files touched:**
- `RELEASE-NOTES.md`

**Dispatch tier:** Trivial — orchestrator inline. No subagent.

- [x] **Step 1: End-to-end verification**

Run every check listed in the bottom-of-plan Verification section. All must pass before the RELEASE-NOTES consolidation.

- [x] **Step 2: Edit — consolidate RELEASE-NOTES**

Append (or merge with Task 1's entry) a consolidated top-of-file entry:

```markdown
## 2026-04-17 — Agent dispatch refactor (feedback round)

- `agent-orchestration`: Agent Teams mode archived (unreliable); replaced
  with §Workload Balancing (three-tier framework + ≤150k tokens/agent
  rule + cache-reuse pointer). Decision Framework graph removed. Dispatch
  template `<optional steering>` tightened to additive-only.
- `agents/implementer` + `agents/reviewer`: new §Shared-Repo Commit
  Discipline guards against cross-agent commit contamination.
- `planning-workflow`: plans now declare `**Depends on:**` per task;
  `execution-workflow` batches parallelizable tasks per those fields.
```

If Task 1's entry already covers Teams archival, collapse into this one entry.

- [x] **Step 3: Commit**

```bash
git add RELEASE-NOTES.md PLAN.md RESULTS.md
git commit -m "docs(release-notes): consolidate 2026-04-17 agent-dispatch feedback round"
```

---

## Verification (end-to-end, run after all tasks `APPROVED`)

```bash
cd $WORKTREE_ROOT

# 1. Invariant tests pass
bash tests/structural-invariants.sh

# 2. No active Team references
grep -rn -E "Agent Team|TeamCreate|agent-teams\.md" \
  skills/ agents/ hooks/ README.md CLAUDE.md \
  --exclude-dir=references | grep -v "ARCHIVED" | grep -v "^RELEASE-NOTES"
# must be empty

# 3. Archive banner
head -5 skills/agent-orchestration/references/agent-teams.md | grep -q "ARCHIVED"

# 4. Three-tier framework
grep -c "^### Tier [123]" skills/agent-orchestration/SKILL.md    # expect 3
grep -q "150k" skills/agent-orchestration/SKILL.md
grep -q "cache" skills/agent-orchestration/SKILL.md

# 5. Dispatch template additive-only
grep -A2 "<optional steering" skills/agent-orchestration/SKILL.md | grep -q "additive\|add information"

# 6. Shared-repo discipline
test $(grep -l "Shared-Repo Commit Discipline" agents/*.md | wc -l) -eq 2

# 7. Task-dependency field in template
grep -q "^\*\*Depends on:\*\*" skills/planning-workflow/references/plan-template.md

# 8. Direct removals from a48f900 applied
! grep -q "^## Dispatch-Return Deltas" skills/agent-orchestration/SKILL.md
! grep -q "^## Integration" skills/agent-orchestration/SKILL.md
! grep -q "^\*\*Not covered by this section:\*\*" skills/handoff-doc/SKILL.md

# 9. Commit history is clean (one commit per task)
git log --oneline econ-adaption..HEAD
# expected: 1 plan-bootstrap commit + 4-5 task commits
```

---

## No Placeholders

- Exact file paths present in every task.
- Verification commands are literal and runnable.
- Every edit above shows the exact text to insert, not "TBD" or "something like this".
