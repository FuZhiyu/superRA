# Fix-Tier Vocabulary — Unified Design Across Review Output and Polish Triage

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This is a **skill-internals edit** — load `document-skills:skill-creator` for SKILL.md / reference-file edits per the repo CLAUDE.md (`When modifying superRA itself … treat the work as skill creation`). The active domain skill is `superRA:writing` (the skill being edited).

**Objective:** Land a single coherent `Fix: mechanical | judgment | decision` vocabulary that captures the supervision cost of applying any prose finding, and use the same vocabulary at two call sites: (a) review-mode output — replacing the binary `Auto-fixable: Yes / No` field in each `consistency/<dim>.md` output block; (b) polish-mode internal triage — making "apply this in place vs surface to author" an explicit, named outcome so polish stops under-editing on substantive prose issues.

**Methodology:**
- Tier vocabulary defined once in `references/review.md §Fix tiers`. Tier definitions: `mechanical` = one correct fix, no semantic call; `judgment` = one likely fix exists, agent picks using paper-internal conventions; `decision` = right fix needs author input.
- Review-mode call site: each `consistency/<dim>.md` finding stamps a `Fix:` line. Polish shape C applies tiered behavior on accepted findings (existing wiring, Task 1).
- Polish-mode call site (Task 2): in shapes A and B, every diagnosed issue is implicitly tiered. `mechanical` and `judgment` apply as minimal edits; `decision` surfaces to the author (chat reply for standalone polish; existing handoff-doc convention when polish rides a workflow).
- Symmetric framing in `polish.md §Minimal-edit discipline`: under-editing and over-editing are equal failure modes; the minimal-edit rule constrains the size of each fix, not the count of fixes.

**Conventions:**
- Tier vocabulary lives in `review.md §Fix tiers` (single source).
- Each `consistency/<dim>.md` output block uses the line `Fix: <tier>` with `<tier>` ∈ {mechanical, judgment, decision}.
- `long-form-review.md` summary table uses `severity × fix-tier` counts.
- Field name is `Fix:` — short, unambiguous in the output block.
- Polish-mode triage uses the same vocabulary; do not invent a parallel one.

**Output:** Edits to:
- `skills/writing/references/review.md` (define §Fix tiers; rename from §Output contract: Fix tiers; first paragraph names two call sites)
- `skills/writing/references/polish.md` (extend shape C with tier-based application policy; add tier-based apply policy for shapes A/B; replace §Minimal-edit discipline framing)
- `skills/writing/references/long-form-review.md` (replace `Auto-fixable` references; update summary-table description)
- `skills/writing/references/consistency/{argument-logic,citations,code-paper,cross-references,math,notation,numerical,terminology}.md` — eight output blocks
- `skills/writing/CLAUDE.md` (replace the auto-fixable bullet under §Multi-agent review pattern with a fix-tier rationale bullet that names both call sites; add design-note paragraph on under-editing failure mode)
- `skills/writing/feedback_polish_under_editing.md` — delete after Task 2 absorbs its load-bearing content (git history preserves the original)

**Expected Results:** A single coherent vocabulary across reviewer output, orchestrator summary, polish-shape-C handoff, and polish-shape-A/B internal triage. Replaces the binary that conflated supervision cost with auto-fixability and leaves polish mode without a named surface-back path.

**Sensitivity Analysis:** N/A (skill-prose change, no analytic results).

**Pipeline:** N/A (verification is a `grep` regression and a manual read-through of touched files; smoke-test on the failure-mode profile from the absorbed feedback file).

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on Task 1 (2026-05-05 design discussion); approved Task 2 unified-tier extension on 2026-05-06 after design-principle filter pass.
- [ ] **Execution complete** — Task 1 + Task 2 `APPROVED`; no `Auto-fixable` strings remain; polish.md framing balanced.
- [ ] **Drift tests created** — N/A (skill-prose; the `grep` checks in each task are the regression tests)
- [ ] **Integrated** — integration reviewer `APPROVED`
- [ ] **Docs finalized** — RESULTS.md matured, CLAUDE.md design notes rewritten
- [ ] **Finished** — branch landed / PR opened per researcher's choice

---

## Project Conventions

Walked at planning time (2026-05-05); re-confirmed 2026-05-06 for Task 2 — no new walks needed (Task 2 edits the same skill directory).

### Repo root
- `/CLAUDE.md` (HEAD at 505a975): Contributor guidelines for editing superRA itself. Hard rule: "When modifying superRA itself — skills, hooks, agents, harness adapters, or internal docs — treat the work as skill creation." Carries the DRY / Necessity gate, ownership-boundaries table, and the anti-pattern list (wrapper instructions, "what you will receive" descriptions, reminders of harness defaults). **Load-bearing for Task 2:** the design-principle filter that dropped 4 of 5 feedback suggestions is rooted here.
- `/AGENTS.md`, `/AGENT.md`: aliases of `/CLAUDE.md` for Codex-facing contributors.
- `/README.md`: user-facing overview of superRA — stays untouched by this change.

### Module-level docs walked
- `skills/writing/CLAUDE.md` (HEAD at 505a975): Design notes for the writing skill. Records §These rules are additive (agent already knows how to polish; skill adds discipline only — load-bearing for Task 2 design-principle filter), §Multi-agent review pattern (auto-fixable bullet rewritten by Task 1; extended by Task 2 for the polish-mode call site), and §What this skill deliberately does not carry (severity tagging on heuristic style/structure rules — Task 2 does NOT touch).

### Not walked (not reachable from the planned diff)
- `skills/{econ-data-analysis,theory-modeling,planning-workflow,…}/` — both tasks are local to `skills/writing/`.
- `agents/`, `hooks/`, `tests/`, `scripts/` — no role / harness / generator surface affected.

---

## User Decisions Log

> **2026-05-05 — Tier vocabulary.** Researcher chose Option A (3-tier `Fix: mechanical | judgment | decision`) over Option B (kept binary). The binary forced a continuous supervision-cost axis into two buckets and pre-judged what polish would do. Applies to: Task 1.

> **2026-05-06 — Unify under-editing fix into the same vocabulary.** Researcher pushed back on a first-pass plan that absorbed the full feedback file. Direction: filter feedback through the skill's own design principles (additive-rules framing; DRY/Necessity gate); keep generalizable changes only. Outcome: drop diagnose-first procedural step, gated-checklist intro reframe, cross-paragraph audit subsection, end-of-polish self-check, mode-specific tier examples; keep symmetric over/under-editing warning + decision-tier surfacing path for polish shapes A/B. Applies to: Task 2.

---

### Task 1: Replace `Auto-fixable` flag with `Fix:` tier across review-mode output (Commit A)
**Depends on:** *(none)*
**Review status:** IMPLEMENTED (Steps 1–3 done in working tree, uncommitted; Steps 4–6 pending)
**Integration status:** *(set during integration)*

**Script:** N/A (prose edits across 11 files)
**Input:**
- `skills/writing/references/review.md`
- `skills/writing/references/polish.md`
- `skills/writing/references/long-form-review.md`
- `skills/writing/references/consistency/{argument-logic,citations,code-paper,cross-references,math,notation,numerical,terminology}.md`
- `skills/writing/CLAUDE.md`
**Output:** Same files, edited in place.

- [x] **Step 1: Add §Output contract: Fix tiers to `review.md`** — done in working tree (uncommitted). Renamed to `§Fix tiers` in Task 2 Step 1 to match unified vocabulary.

- [x] **Step 2: In each `consistency/<dim>.md` output block, replace the Auto-fixable line** — done in working tree. All eight files now read `Fix: mechanical | judgment | decision   # see review.md §Output contract: Fix tiers`. The pointer text is updated to `§Fix tiers` in Task 2 Step 1.

- [x] **Step 3: Extend `polish.md §Input shape C` with the tier-based application policy** — done in working tree.

- [ ] **Step 4: Update `long-form-review.md` to reference the tier instead of the flag**

  Two edits:
  - In the third bullet under §Doc convention ("Final summary block at the top…"), replace `severity × auto-fixable counts table` with `severity × fix-tier counts table`, and replace `auto-fixable batch table sized for polish-mode shape C handoff` with `per-tier batch table (mechanical / judgment / decision) sized for polish-mode shape C handoff`.
  - In the second bullet under §Doc convention ("Per-aspect blocks ARE task blocks…"), replace `including the new \`Auto-fixable: Yes / No\` line` with `including the \`Fix:\` tier line per \`review.md §Fix tiers\``.

- [ ] **Step 5: Update `CLAUDE.md §Multi-agent review pattern` bullet**

  Replace the existing fifth bullet with a fix-tier rationale bullet that names **both** call sites — review output (this task) and polish-mode internal triage (Task 2). Load-bearing facts: (a) one vocabulary, two call sites; (b) defined once in `references/review.md §Fix tiers`; (c) the binary's failure mode (continuous axis forced into two buckets) is the load-bearing reason against re-compressing.

- [ ] **Step 6: Verify, update RESULTS.md, commit Commit A**

  Run `grep -rn "Auto-fixable\|auto-fixable" skills/writing/` — expect zero hits except the CLAUDE.md history bullet naming the prior flag. Read each touched file end-to-end. Update RESULTS.md Task 1. Mark all Task 1 steps `[x]`. Set `**Review status:** APPROVED`. Commit code + handoff docs atomically as Commit A.

---

### Task 2: Wire fix-tier vocabulary into polish-mode internal triage (Commit B)
**Depends on:** Task 1 (Step 1 renames the section; Steps 4–5 already finalize the references and the CLAUDE.md bullet that Task 2 extends)
**Review status:** *(set during execution)*
**Integration status:** *(set during integration)*

**Script:** N/A (prose edits across 4 files + 1 deletion)
**Input:**
- `skills/writing/references/review.md`
- `skills/writing/references/polish.md`
- `skills/writing/CLAUDE.md`
- `skills/writing/feedback_polish_under_editing.md` (to be deleted)
**Output:** First three edited in place; feedback file deleted.

- [ ] **Step 1: Rename `review.md §Output contract: Fix tiers` → `§Fix tiers`; first paragraph names two call sites.**

  Two-sentence rewrite of the section's opening paragraph: review-mode findings stamp `Fix:` on each line of the `consistency/<dim>.md` output blocks; polish-mode internal triage classifies each diagnosed issue along the same axis to decide apply-vs-surface. Tier definitions kept verbatim — no added examples (mode-specific examples drop per design-principle filter; tier classification is situational, not type-bound). Update the cross-references in the eight `consistency/<dim>.md` output blocks and `polish.md §Input shape C` to point at `§Fix tiers`.

- [ ] **Step 2: Replace `polish.md §Minimal-edit discipline` framing.**

  Replace the line *"Over-editing is the most common failure mode of polish mode — every word changed beyond the minimum risks drifting past the requested scope and into the author's substance."* with a balanced two-failure-mode statement: over-editing drifts past scope; under-editing ships mechanical-only fixes on prose with substantive issues. **The minimal-edit rule constrains the size of each fix, not the number of fixes.** Three sentences max.

- [ ] **Step 3: Add tier-based apply policy for polish shapes A and B.**

  Currently shape C names the apply-vs-surface split via `Fix:` tiers. Shapes A and B do not. Add one short paragraph (placed after §Edit vs propose vs ask, before §Minimal-edit discipline): in shapes A/B, every diagnosed issue is implicitly tiered per `review.md §Fix tiers`. Apply `mechanical` and `judgment` tier issues as minimal edits; surface `decision`-tier issues to the author (chat reply for standalone polish; existing handoff-doc convention when the polish rides a workflow — do not restate). The §Edit-vs-propose-vs-ask matrix already handles meaning-changing edits ("Ask"); this paragraph names the surface path so that *not silently fixing* is a recognized outcome rather than under-editing.

- [ ] **Step 4: `skills/writing/CLAUDE.md` design-note paragraph(s).**

  Augment the §Multi-agent review pattern bullet rewritten in Task 1 Step 5 (or add a sibling §Polish-mode triage entry — implementer's choice depending on which placement reads more coherently in context):
  - Records that fix tiers are a **shared apply-discipline vocabulary** across review output and polish internal triage. Future contributors proposing a separate polish-side vocabulary must argue why two beat one for the same axis.
  - Records the under-editing failure mode and the framing-suppression cause (the prior `polish.md` line "Over-editing is the most common failure mode" was actively suppressing baseline diagnostic competence) as the rationale for Step 2. Future contributors tempted to put back a "watch out for over-editing" warning without naming the symmetric failure must re-read this entry.

- [ ] **Step 5: Delete `skills/writing/feedback_polish_under_editing.md`.**

  Load-bearing content absorbed into Steps 2 and 4; git history preserves the original. Cite the absorbing commit hash in the CLAUDE.md entry from Step 4 once Commit B lands so the trail is recoverable.

- [ ] **Step 6: Verify, update RESULTS.md, commit Commit B.**

  - `grep -rn "Auto-fixable\|auto-fixable" skills/writing/` returns zero hits except the CLAUDE.md history bullet.
  - `grep -rn "Fix tiers\|Fix:" skills/writing/references/ skills/writing/CLAUDE.md` shows one definition site (`review.md`), references in `polish.md` (shape C + new shape-A/B paragraph), eight `consistency/<dim>.md` output blocks, one `long-form-review.md` reference, one `CLAUDE.md` design-note bullet.
  - Read `polish.md` end-to-end as a fresh agent: confirm the framing is balanced (no "over-editing is the dominant failure mode" line), and the surface-to-author path for `decision`-tier issues is named for shapes A/B as well as shape C.
  - Manual smoke test on the failure-mode profile from the (now-deleted) feedback file: recap-only topic sentence + nominalized opener + broken parallelism. Expectation: agent diagnoses, classifies per its own judgment, and surfaces decision-tier issues instead of skipping straight to typo fixes.
  - Update RESULTS.md Task 2. Mark all Task 2 steps `[x]`. Set `**Review status:** APPROVED`. Commit code + handoff docs atomically as Commit B.
