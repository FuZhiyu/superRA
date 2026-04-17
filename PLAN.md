# Agent-Dispatch Feedback Fixes — Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for doc mechanics. Use `superRA:execution-workflow` to execute this plan. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff. This plan edits skill/agent/hook files — not empirical data — so the usual `superRA:econ-data-analysis` per-step cycle does not apply. The per-step cycle here is **plan → edit → verify (grep / read) → commit**.

**Objective:** Apply five pieces of user feedback from commit `a48f900` (on branch `manual-feedback`) to the superRA plugin. Deliverables are edits to `skills/`, `agents/`, `hooks/`, `tests/`, `README.md`, `RELEASE-NOTES.md`.

**Methodology:** Treat `a48f900` as feedback input (read-only). Branch `feedback/agent-dispatch-fixes` off `econ-adaption` (commit `3755274`). Five feedback items become six tasks (T1–T6) because F2 produces a new section large enough to be its own task while F3+F4 bundle naturally into the same file edit. Dispatch via the three-tier framework defined in feedback F2 itself (dogfooding). Use `Depends on:` declarations on every task (also dogfooding, from F6).

**Feedback Inventory (substitute for Data Inventory):**

Source: `git show a48f900` (also saved to `$TMPDIR/feedback-a48f900.diff`).

| # | Target file(s) on `manual-feedback` | Feedback |
|---|---|---|
| F1 | `skills/agent-orchestration/SKILL.md` | Agent Teams mode is unreliable — archive `references/agent-teams.md` with a banner, remove every active reference. |
| F2 | `skills/agent-orchestration/SKILL.md` | Add workload-balancing guidance: three tiers (trivial→inline; slightly-involved→bundle-and-delegate; complicated→dedicated agent), ≤150k tokens/agent rule, cache-reuse pointer. |
| F3 | `skills/agent-orchestration/SKILL.md` | Delete Decision Framework DOT graph + pattern table (no longer relevant once Teams archived). |
| F4 | `skills/agent-orchestration/SKILL.md` (dispatch template) | `<optional steering>` must be additive — never restate defaults, manifest, or `PLAN.md` content. |
| F5 | `agents/implementer.md`, `agents/reviewer.md` | Multi-agent repo warning: only commit your own edits when other agents' uncommitted changes appear. Teach `git add <specific-path>` mechanics. |
| F6 | `skills/planning-workflow/SKILL.md`, `references/plan-template.md` | Plans need `Depends on:` declarations so orchestrator can dispatch independent tasks in parallel (lightweight DAG, not a DSL). |

**Feedback coverage map:** Every item above is addressed by exactly one task block below. F3 and F4 bundle into T2 with F2 because all three edit the same file in adjacent regions.

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

> **User decision (2026-04-17):** Base this work on `econ-adaption` (commit `3755274`), NOT `manual-feedback`.
> **Question asked:** Which base branch for the fixes?
> **Rationale:** `manual-feedback` has 91 WIP commits ahead of the stable base; the user wants a clean base rather than stacking on WIP.

> **User decision (2026-04-17):** Use the three-tier agent-dispatch framework (trivial→inline; slightly-involved→bundle-and-delegate; complicated→dedicated agent) to pick dispatch mode for each task in this plan itself. Pair with ≤150k tokens/agent.
> **Question asked:** How should the orchestrator dispatch these six tasks?
> **Rationale:** Dogfood the framework we are introducing. Bundles T2+T3+T4 into one dispatch; keeps T1 and T6 dedicated.

---

### Task 1: Archive Agent Teams mode across the plugin

**Depends on:** *(none)*
**Review status:** *(not started)*

**Files touched (verified to exist on `econ-adaption`):**
- `skills/agent-orchestration/SKILL.md`
- `skills/agent-orchestration/references/agent-teams.md`
- `agents/implementer.md`
- `agents/reviewer.md`
- `skills/execution-workflow/SKILL.md`
- `tests/structural-invariants.sh`
- `README.md`
- `RELEASE-NOTES.md`

**Files to discover during implementation (grep and include if matches found):**
- Any skill file under `skills/` with string `Agent Team|TeamCreate|agent-teams` (exclude `references/`, `RELEASE-NOTES.md`, the file being archived).
- `hooks/session-start` if present — strip Teams detection.

**Dispatch tier:** Complicated — dedicated implementer agent, dedicated reviewer. Cross-file grep, test rewrite, doc sweep. Estimated ≤60k tokens for the agent.

- [ ] **Step 1: Plan — enumerate all active references to Agent Teams**

```bash
cd $WORKTREE_ROOT   # /Users/zhiyufu/Dropbox/package_dev/econ-superpowers.worktrees/feedback-agent-dispatch
grep -rn -E "Agent Team|TeamCreate|agent-teams\.md|Team mode" \
  skills/ agents/ hooks/ tests/ README.md RELEASE-NOTES.md CLAUDE.md \
  --exclude-dir=references | tee /tmp/teams-refs-before.txt
wc -l /tmp/teams-refs-before.txt
```

Expected: ≥10 hits. Record the full count in RESULTS.md.

- [ ] **Step 2: Edit — archive the reference file**

Prepend to `skills/agent-orchestration/references/agent-teams.md`:

```markdown
> **ARCHIVED (2026-04-17).** Agent Teams mode proved unreliable in practice
> and is no longer used by any superRA workflow. This file is retained as
> a historical reference only — **do not load it, do not cite it from any
> active skill**. If you are reading this because an agent pointed you
> here, the pointer is stale; please flag it.

```

Do NOT delete the body. Just the banner + one blank line before the existing content.

- [ ] **Step 3: Edit — strip Teams references from active files**

For each file with an active reference (from Step 1 grep output):

1. Read the file, identify the sentence/paragraph/section referencing Teams.
2. If the reference is a standalone section (e.g., `## Agent Teams Mode`, `## If Running as Agent Team Teammate`) → delete the entire section.
3. If the reference is one sentence inside a broader paragraph → delete the sentence, and rewrite the paragraph to read coherently.
4. If the reference sits inside a decision table or DOT graph branch → delete the branch; renumber / restructure if needed.
5. Surrounding prose must still read cleanly after removal — do not leave dangling "See above" or orphan cross-references.

Files known from Step 1 sample (may be more after full grep):

- `skills/agent-orchestration/SKILL.md` — **skip for this task**, handled in T2 which rewrites the skill top-to-bottom including Teams removal.
- `skills/execution-workflow/SKILL.md` — remove the Teams branch from the mode-decision DOT graph (lines around §23–36 on `econ-adaption`); delete `## Agent Teams Mode` section near §297. Keep subagent-mode section only.
- `agents/implementer.md` — delete `## If Running as Agent Team Teammate` section (tail of file on `econ-adaption`).
- `agents/reviewer.md` — delete the analogous `## If Running as Agent Team Teammate` section.

- [ ] **Step 4: Edit — replace the TeamCreate invariant in structural tests**

On `econ-adaption`, `tests/structural-invariants.sh` may or may not contain a TeamCreate-asserting invariant. Confirm by:

```bash
grep -n "TeamCreate\|agent-teams" tests/structural-invariants.sh
```

If an invariant exists, replace its body with an archive-banner assertion:

```bash
# Invariant N: agent-teams reference is archived (not loaded by active skills)
at_ref="skills/agent-orchestration/references/agent-teams.md"
if head -5 "$at_ref" | grep -q "ARCHIVED"; then
  pass "$at_ref carries ARCHIVED banner"
else
  fail "$at_ref is missing the ARCHIVED banner"
fi

# And: no active skill file cites the archived reference
active_refs=$(grep -rln -E "agent-teams\.md|TeamCreate" \
  skills/ agents/ hooks/ \
  --exclude-dir=references \
  --exclude="$at_ref" || true)
if [ -z "$active_refs" ]; then
  pass "no active file references archived agent-teams content"
else
  fail "active files still reference Teams content: $active_refs"
fi
```

If no existing invariant — append the above as a new invariant at the end of the file, numbered sequentially.

- [ ] **Step 5: Edit — README and RELEASE-NOTES**

`README.md`: remove any feature row or sentence describing Agent Teams mode as a supported orchestration pattern. Replace with (only if needed) a single sentence about parallel-subagent dispatch.

`RELEASE-NOTES.md`: **append** (do not rewrite prior entries) a new top entry dated `2026-04-17`:

```markdown
## 2026-04-17 — Agent Teams mode archived

Agent Teams mode was unreliable in practice. `references/agent-teams.md` is
now archived; no active skill loads or cites it. Workflows that previously
offered a Teams branch (execution-workflow, integration-workflow,
merge-workflow, semantic-merge) fall back to parallel-subagent dispatch.
See `agent-orchestration` §Workload Balancing for the dispatch framework.
```

- [ ] **Step 6: Verify + commit**

```bash
# 1. No active references remain
grep -rn -E "Agent Team|TeamCreate|agent-teams\.md|Team mode" \
  skills/ agents/ hooks/ README.md CLAUDE.md \
  --exclude-dir=references | grep -v "ARCHIVED" | tee /tmp/teams-refs-after.txt
test ! -s /tmp/teams-refs-after.txt && echo "OK: no active refs" || echo "FAIL: refs remain"

# 2. Archive banner present
head -5 skills/agent-orchestration/references/agent-teams.md | grep -q "ARCHIVED" \
  && echo "OK: banner" || echo "FAIL: banner missing"

# 3. Invariants pass
bash tests/structural-invariants.sh
```

All three must pass. Update PLAN.md: mark steps `[x]`, set `**Review status:** IMPLEMENTED`. Update RESULTS.md Task 1 section with before/after grep counts. Commit:

```bash
git add skills/ agents/ tests/ README.md RELEASE-NOTES.md PLAN.md RESULTS.md
git commit -m "refactor(agent-orchestration): archive Agent Teams mode"
```

---

### Task 2: Rewrite `agent-orchestration/SKILL.md` — add §Workload Balancing, delete Decision Framework, tighten dispatch template

**Depends on:** Task 1
**Review status:** *(not started)*

**Bundles feedback F2 + F3 + F4** — all three edit `skills/agent-orchestration/SKILL.md` in overlapping regions. One implementer, one reviewer. This is the "slightly involved, bundle-and-delegate" tier.

**Files touched:**
- `skills/agent-orchestration/SKILL.md`
- `tests/structural-invariants.sh` (add §Workload Balancing heading invariant)

**Dispatch tier:** Slightly involved — one bundled dispatch.

- [ ] **Step 1: Plan — read current file, identify target regions**

```bash
wc -l skills/agent-orchestration/SKILL.md
grep -n "^## " skills/agent-orchestration/SKILL.md
```

Expected regions (from `econ-adaption` inspection):
- `## Overview` — will keep, rewrite core-principle bullet.
- `## Decision Framework` — **delete entire section** (F3).
- `## Parallel Dispatch` and below — keep; tighten the dispatch template.

- [ ] **Step 2: Edit — delete Decision Framework section (F3)**

Using Edit tool, remove the heading `## Decision Framework` through the end of the pattern table (the `**Rule of thumb:** ...` line). Keep the `---` separator that follows if present.

- [ ] **Step 3: Edit — rewrite `## Overview` core principle**

Replace the sentence "Use teams when agents need to iterate with each other. Use parallel subagents when you just need results back." with:

```markdown
**Core principle:** parallel-dispatch independent tasks; serialize iterative
loops; do trivial work inline. See §Workload Balancing for how to size each
dispatch.
```

Remove any remaining sentence that refers to Agent Teams or the two-pattern choice.

- [ ] **Step 4: Edit — insert `## Workload Balancing` after `## Overview` (F2)**

Insert exactly this section (between `## Overview` and the next remaining `## ...` heading):

```markdown
## Workload Balancing

Every dispatch has spawn cost — skill-load, context hydration, per-turn
overhead. Treating every sub-task as dispatch-worthy wastes tokens and
serializes work that could run inline; treating every bundle as "split
it up" over-spawns. Pick the tier that matches the work:

### Tier 1 — Trivial: do it inline

The orchestrator executes the task itself, no subagent. Use when the
task fits in a single edit, reads no unfamiliar files, and needs no
domain skill beyond what the orchestrator already has loaded.

- Typo or comment fix in one file.
- A 2-line constant change the orchestrator has already read.
- Removing a known-dead import.

Dispatch cost > work content. Just do it.

### Tier 2 — Slightly involved: bundle and delegate

Group multiple small-to-medium tasks that share context (same file, same
skill load, same domain references) into one dispatch. One agent does the
whole bundle in a single turn.

- Three edits in the same skill file.
- A reviewer sweep over two sibling agent files.
- Updating a template plus its one consumer.

The agent pays the spawn cost once and amortizes it across the bundle.

### Tier 3 — Complicated: one dedicated agent per task

One agent owns one task. Use when the task needs deep context (cross-file
grep, multi-step refactor, full skill-load chain), or its deliverable
will be reviewed in isolation.

- A refactor that touches >5 files across skills + agents + tests.
- A new feature that requires full domain-skill engagement.
- Any task where bundle-context would exceed ~150k tokens.

### Rules of thumb

**≤150k tokens per agent.** When estimating: manifest skill loads (~5–15k
each), `PLAN.md` + `RESULTS.md` (5–50k depending on stage), plus per-task
file reads. If an agent's projected context exceeds ~150k, split the work
across two agents even when the individual items are small — context
thrash degrades output quality more than the cost of a second spawn.

**Reuse existing agents within the cache window.** The Anthropic prompt
cache has a ~5-minute TTL. If a prior agent's turn is still warm and the
next task shares its skill/reference profile, prefer `SendMessage` on the
existing agent over spawning fresh — cached context is effectively free.
Spawn fresh when: the agent has accumulated stale or irrelevant context,
the new task needs a different skill load, or more than ~5 minutes have
elapsed.

**Parallelize independent tasks.** Tasks whose `Depends on:` lines (see
`planning-workflow` §Task Dependencies) are all satisfied and that share
no mutable state should dispatch in a single parallel Agent-tool batch,
one agent per task (subject to the bundling rule above). Serializing
mutually-independent tasks is waste.

---
```

- [ ] **Step 5: Edit — tighten `<optional steering>` placeholder (F4)**

Locate the Parallel Dispatch subsection that shows the dispatch-template code block(s). In each `<optional steering>` placeholder (there is typically one implementer example and one reviewer example, but on `econ-adaption` there may only be one — read first, then edit):

Change the placeholder text to:

```
<optional steering — focus area, prior-round adjudication notes, or
warnings. Must add information on top of the default; never restate
what the default protocol, skill-load manifest, or PLAN.md already
says.>
```

Immediately below the code block(s), add exactly one paragraph:

```markdown
**Optional steering is strictly additive.** If your `Additionally:` line
only paraphrases the default protocol, the skill-load manifest, or
`PLAN.md` content, delete it — re-statement of content the agent will
read itself is noise that clutters the dispatch without adding signal.
```

- [ ] **Step 6: Edit — add structural invariant for §Workload Balancing**

Append to `tests/structural-invariants.sh`, numbered sequentially:

```bash
# Invariant N: agent-orchestration carries the three-tier Workload Balancing framework
ao="skills/agent-orchestration/SKILL.md"
if grep -q "^## Workload Balancing" "$ao"; then
  pass "$ao has §Workload Balancing heading"
else
  fail "$ao is missing §Workload Balancing heading"
fi
tier_count=$(grep -c "^### Tier [123]" "$ao" || true)
if [ "$tier_count" -eq 3 ]; then
  pass "$ao has all three tiers"
else
  fail "$ao has $tier_count tiers (expected 3)"
fi
if grep -q "150k" "$ao" && grep -q "cache" "$ao"; then
  pass "$ao references 150k-token rule and cache reuse"
else
  fail "$ao missing 150k or cache-reuse guidance"
fi
```

- [ ] **Step 7: Verify + commit**

```bash
# 1. Structure checks
bash tests/structural-invariants.sh

# 2. Template placeholder tightened
grep -A1 "<optional steering" skills/agent-orchestration/SKILL.md | \
  grep -q "additive\|add information" && echo "OK: tightening" || echo "FAIL"

# 3. Decision Framework gone
! grep -q "^## Decision Framework" skills/agent-orchestration/SKILL.md \
  && echo "OK: deleted" || echo "FAIL: still present"

# 4. Sanity-read — check rendered outline
grep "^## " skills/agent-orchestration/SKILL.md
```

Outline should read: `## Overview`, `## Workload Balancing`, `## Parallel Dispatch` (and any subsections below); no `## Decision Framework`; no Teams-era `## Agent Teams` headings.

Update PLAN.md: mark `[x]`, set `**Review status:** IMPLEMENTED`. Update RESULTS.md Task 2 with the new outline. Commit:

```bash
git add skills/agent-orchestration/SKILL.md tests/structural-invariants.sh PLAN.md RESULTS.md
git commit -m "docs(agent-orchestration): add §Workload Balancing; delete Decision Framework; tighten dispatch template"
```

---

### Task 3: Add §Shared-Repo Commit Discipline to implementer + reviewer (F5)

**Depends on:** *(none)* — independent of Tasks 1 and 2 (different files).
**Review status:** *(not started)*

**Files touched:**
- `agents/implementer.md`
- `agents/reviewer.md`

**Dispatch tier:** Slightly involved — mirrored sub-section in two files. One implementer bundle.

- [ ] **Step 1: Plan — identify insertion points**

Read both files in full; locate the existing commit-handling section in each. Typical cue: a bullet or code block showing `git add ... && git commit -m ...`. The new sub-section goes immediately before that, or immediately after (wherever reads better for each file — they may not have identical structure on `econ-adaption`).

```bash
grep -n "git add\|git commit" agents/implementer.md agents/reviewer.md
```

- [ ] **Step 2: Edit — insert the sub-section into `agents/implementer.md`**

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

- [ ] **Step 3: Edit — insert the same sub-section into `agents/reviewer.md`**

Insert the identical text block. The reviewer commits only when updating review status / adjudication annotations, but the discipline applies equally — a reviewer who `git add -A`s will pull in the implementer's in-flight edits for the next task.

If `agents/reviewer.md` on `econ-adaption` has a structurally different commit section (e.g., no `git add` block at all), insert the sub-section at the top of its "How you commit" region — do not invent a commit section if the reviewer file doesn't have one, but confirm placement is consistent by reading both files first.

- [ ] **Step 4: Verify + commit**

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

### Task 4: Add `Depends on:` field to plan template + §Task Dependencies in planning-workflow (F6)

**Depends on:** Task 1 (both edit `skills/execution-workflow/SKILL.md`; serialize to avoid merge).
**Review status:** *(not started)*

**Files touched:**
- `skills/planning-workflow/SKILL.md`
- `skills/planning-workflow/references/plan-template.md`
- `skills/execution-workflow/SKILL.md` (teach orchestrator to read `Depends on:`)

**Dispatch tier:** Complicated — schema change propagates across three files and the orchestrator's dispatch logic. Dedicated implementer + reviewer.

- [ ] **Step 1: Edit — add `### Task Dependencies` sub-section to planning-workflow**

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

- [ ] **Step 2: Edit — update the self-review checklist**

Add one item to `## Self-Review` in `skills/planning-workflow/SKILL.md`:

```markdown
**7. Dependency graph sanity.** Every task has a `**Depends on:**` line.
No cycles. If the plan has ≥2 independent branches, at least one pair of
tasks is marked parallelizable.
```

- [ ] **Step 3: Edit — add `Depends on:` to the plan template task block**

In `skills/planning-workflow/references/plan-template.md`, modify the task-block structure (§"Task Block Structure") to insert the new field on the line directly under the task title, before `**Review status:**`:

```markdown
### Task N: [Phase Name]
**Depends on:** Task N-1 [, Task N-2] | *(none)*
**Review status:** *(set during execution — do not fill at planning time)*
```

Also add a short prose paragraph before the code example explaining the new field. Keep the existing worked example; add `**Depends on:** *(none)*` to it.

- [ ] **Step 4: Edit — teach execution-workflow about `Depends on:`**

Read `skills/execution-workflow/SKILL.md`. Find the Step where the orchestrator picks the next task to dispatch (the "decompose / dispatch next" step). Insert a paragraph:

```markdown
**Before dispatching, read each pending task's `Depends on:` field.**
Tasks whose dependencies are all `APPROVED` may be dispatched as a
single parallel Agent-tool batch (subject to `agent-orchestration`
§Workload Balancing). Serialize only when no parallel batch is
available.
```

Keep the existing prose; this is an addition, not a replacement.

- [ ] **Step 5: Verify + commit**

```bash
# 1. New section in planning-workflow
grep -q "^### Task Dependencies" skills/planning-workflow/SKILL.md && echo "OK" || echo "FAIL"

# 2. Template field
grep -q "^\*\*Depends on:\*\*" skills/planning-workflow/references/plan-template.md && echo "OK" || echo "FAIL"

# 3. Self-review item
grep -q "Dependency graph sanity" skills/planning-workflow/SKILL.md && echo "OK" || echo "FAIL"

# 4. Execution-workflow update
grep -q "Depends on:" skills/execution-workflow/SKILL.md && echo "OK" || echo "FAIL"

# 5. Invariants
bash tests/structural-invariants.sh
```

Update PLAN.md + RESULTS.md. Commit:

```bash
git add skills/planning-workflow/ skills/execution-workflow/SKILL.md PLAN.md RESULTS.md
git commit -m "feat(planning-workflow): add task-dependency declarations; teach execution-workflow to batch parallel tasks"
```

---

### Task 5: End-to-end verification + RELEASE-NOTES consolidation

**Depends on:** Task 1, Task 2, Task 3, Task 4
**Review status:** *(not started)*

**Files touched:**
- `RELEASE-NOTES.md`

**Dispatch tier:** Trivial — orchestrator inline. No subagent.

- [ ] **Step 1: End-to-end verification**

Run every check listed in the bottom-of-plan Verification section. All must pass before the RELEASE-NOTES consolidation.

- [ ] **Step 2: Edit — consolidate RELEASE-NOTES**

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

- [ ] **Step 3: Commit**

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

# 8. Commit history is clean (one commit per task)
git log --oneline econ-adaption..HEAD
# expected: 4-5 commits, each describing one task
```

---

## No Placeholders

- Exact file paths present in every task.
- Verification commands are literal and runnable.
- Every edit above shows the exact text to insert, not "TBD" or "something like this".
