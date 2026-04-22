# Agent-Dispatch Feedback Fixes — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-17 (Task 5 complete — all tasks APPROVED)
**Status:** Complete — all 5 tasks implemented and approved; RELEASE-NOTES consolidated

---

## Task 1: Archive Agent Teams mode across the plugin

**Outcome:** All active Teams references removed from files in T1 scope. `skills/agent-orchestration/SKILL.md` references deferred to T2 as planned.

**Before-count (HEAD before edits, T1-scope files only, excluding `agent-orchestration/SKILL.md` and `agent-teams.md`):**

| File | Teams ref count |
|---|---|
| `skills/execution-workflow/SKILL.md` | 10 |
| `skills/using-superRA/SKILL.md` | 3 |
| `skills/integration-workflow/SKILL.md` | 2 |
| `skills/merge-workflow/SKILL.md` | 2 |
| `skills/semantic-merge/SKILL.md` | 2 |
| `agents/implementer.md` | 2 |
| `agents/reviewer.md` | 2 |
| `hooks/session-start` | 2 |
| `CLAUDE.md` | 1 |
| `README.md` | 2 |
| **Total** | **28** |

`skills/agent-orchestration/SKILL.md` had ~10 additional references (T2 scope, not touched in T1).

**After-count (T1-scope files):** 0 active Teams references. Only `skills/agent-orchestration/SKILL.md` still has references — expected, deferred to T2.

**Verification (Step 6):**
1. Active Teams refs outside `agent-orchestration/SKILL.md`: **0** (PASS for T1 scope)
2. Archive banner on `agent-teams.md`: **PASS**
3. Structural invariants: 1 FAIL (invariant 22 active-file check flags `agent-orchestration/SKILL.md` — expected T2 scope; all other invariants PASS)

**Files changed in T1 commit:**
- `skills/agent-orchestration/references/agent-teams.md` — ARCHIVED banner prepended
- `skills/execution-workflow/SKILL.md` — Teams branch removed from DOT graph; `## Agent Teams Mode` section deleted
- `agents/implementer.md` — `## If Running as Agent Team Teammate` deleted
- `agents/reviewer.md` — `## If Running as Agent Team Teammate` deleted
- `skills/integration-workflow/SKILL.md` — `## Agent Teams Mode` deleted
- `skills/merge-workflow/SKILL.md` — `## Agent Teams Mode` deleted
- `skills/semantic-merge/SKILL.md` — `## Agent Teams Mode` deleted; stale `Pairs with` bullet removed
- `skills/using-superRA/SKILL.md` — `## Agent Teams` section deleted; intro sentence updated
- `hooks/session-start` — Teams env-probe and injection removed
- `CLAUDE.md` — `agent-teams.md` pointer removed from ownership description
- `skills/CATEGORIES.md` — description updated
- `README.md` — Teams language removed from feature table and hooks table
- `RELEASE-NOTES.md` — `## 2026-04-17 — Agent Teams mode archived` entry prepended
- `tests/structural-invariants.sh` — invariant 22 body replaced with archive-banner + active-cite check

---

## Task 2: Rewrite `agent-orchestration/SKILL.md` — §Workload Balancing + deletions + template tightening

**Outcome:** All five bundled feedback items (F2, F3, F4, D1, D2) applied to `skills/agent-orchestration/SKILL.md`. New final outline: `## Overview` → `## Workload Balancing` → `## Dispatch Templates` → `## Handling Reviewer Feedback` → `## Review Status Reference`.

**Sections deleted:**
- `## Decision Framework` (F3): DOT graph + pattern table removed. 24 lines removed.
- `## Dispatch-Return Deltas` (D1): 7-line section removed. Convention already lives in agent files §Report Format.
- `## Integration` (D2): 6-line section removed. Teams-specific content has no referent after T1 archival.

**Sections added:**
- `## Workload Balancing` (F2): three-tier framework (Tier 1 trivial/inline, Tier 2 bundle-and-delegate, Tier 3 dedicated-agent) plus three Rules of thumb (≤150k tokens/agent, cache-reuse within TTL, parallelize independent tasks). Separated from `## Dispatch Templates` by `---`.

**Edits within kept sections:**
- `## Overview` (F2 + F3): replaced Teams-framing paragraph ("use teams when…use parallel subagents when…") with: **Core principle:** parallel-dispatch independent tasks; serialize iterative loops; do trivial work inline. Frontmatter description also updated to remove Agent Teams trigger language.
- `## Dispatch Templates` (F4): both implementer and reviewer `<optional steering>` placeholders now read: "Must add information on top of the default; never restate what the default protocol, skill-load manifest, or PLAN.md already says." Additive-only paragraph added after the reviewer template. Stale `Counterpart:` banned-item cleaned. Stale Agent Teams reference removed from the prose paragraph after the templates.

**Structural invariants:**
- Invariant 14 updated: `## Workload Balancing` replaces `## Dispatch-Return Deltas` in the checked heading list; two new checks confirm `## Dispatch-Return Deltas` and `## Integration` are absent.
- Invariant 26 added: checks for `## Workload Balancing` heading, all three tier headings, `150k` token rule, and `cache` reuse guidance.
- All invariants PASS after edits (2 known pre-existing WARNs for upstream refs in writing-skills).

**Files changed:**
- `skills/agent-orchestration/SKILL.md` — sections deleted + rewritten + §Workload Balancing inserted + dispatch templates tightened
- `tests/structural-invariants.sh` — invariant 14 updated; invariant 26 added

---

## Task 3: Add §Shared-Repo Commit Discipline to implementer + reviewer (F5)

**Outcome:** `### Shared-Repo Commit Discipline` sub-section inserted into both `agents/implementer.md` and `agents/reviewer.md`. Content is identical in both files per the plan spec.

**Insertion points:**
- `agents/implementer.md`: inserted as a `###` sub-section between step 2 ("Update RESULTS.md") and the atomic-commit example within `### Update the Docs and Commit`. The prior `3. **Single atomic commit.**` numbered item was converted to a bold paragraph to avoid numbered-list collision with the new sub-section's own 4-step list.
- `agents/reviewer.md`: inserted as a `###` sub-section between step 4 (set Review status) and step 5 (commit PLAN.md) within the "On first review" flow under `### How You Write a Review`.

**Verification:**
1. `grep -l "Shared-Repo Commit Discipline" agents/*.md | wc -l` → **2** (PASS)
2. `git add -A` / `git add .` mentions in both files are inside the "do NOT" prohibition — no contradicting language (PASS)

**Files changed in T3 commit:**
- `agents/implementer.md` — `### Shared-Repo Commit Discipline` sub-section inserted; atomic-commit step converted from numbered item to bold paragraph
- `agents/reviewer.md` — `### Shared-Repo Commit Discipline` sub-section inserted

---

## Task 4: Add `Depends on:` field to plan template + §Task Dependencies in planning-workflow (F6) + delete handoff-doc "Not covered by this section" block (D3)

**Outcome:** All four edits applied. `planning-workflow` now teaches authors to declare task dependencies; `execution-workflow` reads those fields before dispatch; the plan template requires the field in every task block; `handoff-doc` User Decisions Log drops the negation list (D3).

**Edits made:**

1. `skills/planning-workflow/SKILL.md` — inserted `### Task Dependencies` sub-section after `### Step Granularity` inside Phase 4. Covers format, when-depends-on, when-independent, orchestration contract, and plan-time DAG sanity. Also added item 7 ("Dependency graph sanity") to `## Self-Review`.

2. `skills/planning-workflow/references/plan-template.md` — added prose paragraph explaining the `**Depends on:**` field requirement before the task-block code example; added `**Depends on:** Task N-1 [, Task N-2] | *(none)*` as the first field in the task-block skeleton.

3. `skills/execution-workflow/SKILL.md` — inserted a paragraph at the top of Step 2 ("Execute Tasks") instructing the orchestrator to read `Depends on:` fields before dispatch and batch independent tasks per `agent-orchestration` §Workload Balancing.

4. `skills/handoff-doc/SKILL.md` — deleted the `**Not covered by this section:**` bullet block (two bullets) and the `If you are not sure whether an answer counts...` paragraph from §User Decisions Log. Section now reads directly from the three-line format example to `## What Counts as Stale`.

**Verification results (Step 5):**
1. `### Task Dependencies` heading in planning-workflow: PASS
2. `**Depends on:**` field in plan-template: PASS
3. "Dependency graph sanity" in self-review: PASS
4. `Depends on:` text in execution-workflow: PASS
5. `**Not covered by this section:**` absent from handoff-doc: PASS
6. Structural invariants: 2 pre-existing FAILs (invariant 14 asserts `## Dispatch-Return Deltas` exists — stale, T2 scope; invariant 22 flags `agent-orchestration/SKILL.md` active Teams refs — T2 scope). No new failures introduced by T4.

---

## Task 5: End-to-end verification + RELEASE-NOTES consolidation

**Outcome:** All 9 end-to-end checks passed (orchestrator inline). RELEASE-NOTES consolidated.

**Verification results:**
1. Structural invariants: all PASS (2 known warnings only — pre-existing upstream refs in writing-skills).
2. Active Teams refs in skills/agents/hooks/README/CLAUDE: **0** (empty grep).
3. Archive banner on `agent-teams.md`: **PASS**.
4. Three-tier headings (Tier 1/2/3): **3** (PASS). `150k` present. `cache` present.
5. `<optional steering>` additive-only language: **PASS**.
6. Shared-Repo Commit Discipline in both agent files: **PASS** (2 files).
7. `**Depends on:**` in `plan-template.md`: **PASS**.
8. D1/D2/D3 removals: all **PASS**.
9. Commit log: clean task commits on `feedback/agent-dispatch-fixes`.

**RELEASE-NOTES:** T1's separate "Agent Teams mode archived" entry collapsed into one consolidated "Agent dispatch refactor (feedback round)" entry covering all five feedback items.
