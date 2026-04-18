# Agent-Dispatch Feedback Fixes — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-17 (Task 3 implemented)
**Status:** In Progress — Task 1 implemented, pending review; Task 3 implemented, pending review; Tasks 2, 4–5 not started

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
