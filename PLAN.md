# Fix-Tier Vocabulary — Unified Design Across Review Output and Polish Triage

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This is a **skill-internals edit** — load `document-skills:skill-creator` for SKILL.md / reference-file edits per the repo CLAUDE.md (`When modifying superRA itself … treat the work as skill creation`). The active domain skill is `superRA:writing` (the skill being edited).

**Objective:** Land a single coherent `Fix: mechanical | conventional | authorial` vocabulary that captures the supervision cost of applying any prose finding, and use the same vocabulary at two call sites: (a) review-mode output — replacing the binary `Auto-fixable: Yes / No` field in each `consistency/<dim>.md` output block; (b) polish-mode internal triage — making "apply this in place vs surface to author" an explicit, named outcome so polish stops under-editing on substantive prose issues.

**Methodology:**
- Tier vocabulary defined once in `references/review.md §Fix tiers`. Tier definitions: `mechanical` = surface-only change (orthography, grammar, format), no meaning effect, applied silently; `conventional` = wording or phrasing change that preserves the paragraph's **sequence** (order of ideas), **set** (propositions asserted), and **force** (claim strength / hedge level), applied with a per-item finding-line in the commit message; `authorial` = changes any of sequence / set / force, or commits the author to a choice not yet made, surfaced for the author. The conventional/authorial dividing line is the **sequence-set-force test** carried in the same section.
- Review-mode call site: each `consistency/<dim>.md` finding stamps a `Fix:` line. Polish shape C applies tiered behavior on accepted findings (existing wiring, Task 1).
- Polish-mode call site (Task 2): in shapes A and B, every diagnosed issue is implicitly tiered. `mechanical` and `judgment` apply as minimal edits; `decision` surfaces to the author (chat reply for standalone polish; existing handoff-doc convention when polish rides a workflow).
- Symmetric framing in `polish.md §Minimal-edit discipline`: under-editing and over-editing are equal failure modes; the minimal-edit rule constrains the size of each fix, not the count of fixes.

**Conventions:**
- Tier vocabulary lives in `review.md §Fix tiers` (single source).
- Each `consistency/<dim>.md` output block uses the line `Fix: <tier>` with `<tier>` ∈ {mechanical, conventional, authorial}.
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

- [x] **Plan approved** — researcher signed off on Task 1 (2026-05-05 design discussion); approved Task 2 unified-tier extension on 2026-05-06 after design-principle filter pass; approved Task 3 vocabulary re-cut on 2026-05-08 after sequence/set/force test discussion.
- [x] **Execution complete** — Tasks 1 + 2 + 3 IMPLEMENTED (Commits A, B, C landed). Task 3 re-cut the vocabulary to `mechanical` / `conventional` / `authorial` and added the sequence/set/force test in `review.md §Fix tiers`.
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

> **2026-05-08 — Re-cut tier names and add the sequence/set/force test.** Researcher flagged that `judgment` vs `decision` was opaque — both involved "agent picks among options" and the line collapsed into "agent's confidence", which the prior design had set out to avoid. Decision: rename to `mechanical` / `conventional` / `authorial`, where `conventional` covers any meaning-preserving wording change (rewording, sentence-breaking, parallelism repair, awkward-phrasing fix — not only paper-convention-following), and `authorial` is reserved for changes that move the paragraph's sequence (idea order), set (propositions asserted), or force (claim strength / hedge level). The sequence/set/force test lands in `review.md §Fix tiers` as the rule that draws the conventional/authorial line. Consequences: some prior `judgment` cases shift to `authorial` (e.g., picking a Greek letter when no paper convention exists — surface, don't invent); some shift to `mechanical` (e.g., aesthetic-only "may vs might" with no paper pattern — apply silently, since meaning is preserved and the commit diff is sufficient audit). Applies to: Task 3 (new); supersedes the `judgment` / `decision` names from the 2026-05-05 entry.

> **User decision (2026-05-08):** Proceed with integration.
> **Question asked:** Step 4 completion menu — integrate / change plan / keep as-is / discard.
> **Rationale:** Task 3 APPROVED; Tasks 1 + 2 + 3 all landed; ready for integration-workflow.

---

### Task 1: Replace `Auto-fixable` flag with `Fix:` tier across review-mode output (Commit A)
**Depends on:** *(none)*
**Review status:** IMPLEMENTED
**Integration status:** *(set during integration)*

**Script:** N/A (prose edits across 11 files)
**Input:**
- `skills/writing/references/review.md`
- `skills/writing/references/polish.md`
- `skills/writing/references/long-form-review.md`
- `skills/writing/references/consistency/{argument-logic,citations,code-paper,cross-references,math,notation,numerical,terminology}.md`
- `skills/writing/CLAUDE.md`
**Output:** Same files, edited in place.

- [x] **Step 1: Add §Fix tiers to `review.md`.** Section defines the three tiers (`mechanical` / `judgment` / `decision`) with concrete consistency-dimension examples per tier and the producer-side rule (reviewer picks tier when writing each finding).

- [x] **Step 2: In each `consistency/<dim>.md` output block, replace the Auto-fixable line.** All eight files (`argument-logic`, `citations`, `code-paper`, `cross-references`, `math`, `notation`, `numerical`, `terminology`) now read `Fix: mechanical | judgment | decision   # see review.md §Fix tiers`.

- [x] **Step 3: Extend `polish.md §Input shape C` with the tier-based application policy.** Mechanical applied silently in batch; judgment applied with one finding-line per item in commit message; decision surfaced for author.

- [x] **Step 4: Update `long-form-review.md` to reference the tier instead of the flag.** Per-aspect-blocks bullet points at `review.md §Fix tiers`; final-summary bullet uses `severity × fix-tier counts table` and `per-tier batch table (mechanical / judgment / decision)`.

- [x] **Step 5: Update `skills/writing/CLAUDE.md §Multi-agent review pattern` bullet.** Records: continuous supervision-cost axis vs binary; one definition site (`review.md §Fix tiers`); binary's failure mode is the load-bearing reason against re-compression.

- [x] **Step 6: Verify, update RESULTS.md, commit Commit A.** `grep` returns only the two intentional history mentions of the prior flag (in `CLAUDE.md` and `review.md` — both name the binary as the prior flag for traceability).

---

### Task 2: Wire fix-tier vocabulary into polish-mode internal triage (Commit B)
**Depends on:** Task 1
**Review status:** IMPLEMENTED
**Integration status:** *(set during integration)*

**Script:** N/A (prose edits across 3 files + 1 deletion)
**Input:**
- `skills/writing/references/review.md`
- `skills/writing/references/polish.md`
- `skills/writing/CLAUDE.md`
- `skills/writing/feedback_polish_under_editing.md` (deleted)
**Output:** First three edited in place; feedback file deleted.

- [x] **Step 1: First paragraph of `review.md §Fix tiers` names two call sites.** Review-mode findings stamp `Fix:` on each line of every `consistency/<dim>.md` output block; polish-mode internal triage classifies each diagnosed issue along the same axis (`polish.md §Triage`). Tier definitions kept verbatim — no added examples per the design-principle filter (tier classification is situational, not type-bound).

- [x] **Step 2: Replaced `polish.md §Minimal-edit discipline` framing.** Over- and under-editing are equal failure modes; minimal-edit rule constrains the size of each fix, not the count. Adds a one-line pointer to `style.md §Gated Checklist` for diagnosis and `§Triage` for routing.

- [x] **Step 3: Added `polish.md §Triage`** between §Intent comments and §Minimal-edit discipline. Names the apply-in-place behavior for `mechanical` / `judgment` tiers and the surface-back path for `decision` tier (chat reply for standalone; handoff-doc when the polish rides a workflow). Also clarifies that the §Edit-vs-propose-vs-ask matrix routes meaning-changing edits to **Ask**; triage names the surface path for issues that diagnose cleanly but need author input on the *right answer*.

- [x] **Step 4: `skills/writing/CLAUDE.md` design-note edits.** Augmented the existing §Multi-agent review pattern fix-tier bullet with the second-call-site pointer; added a new §Polish-mode triage section that records the shared-vocabulary rationale and the under-editing failure mode + framing-suppression cause.

- [x] **Step 5: Deleted `skills/writing/feedback_polish_under_editing.md`.** Recoverable via `git log --diff-filter=D -- skills/writing/feedback_polish_under_editing.md`. Recovery path cited in the CLAUDE.md §Polish-mode triage section.

- [x] **Step 6: Verified.** `grep -rn "Auto-fixable\|auto-fixable" skills/writing/` returns 2 hits — both intentional history mentions naming the prior flag (`CLAUDE.md:51`, `review.md:21`). `grep -rn "§Fix tiers\|## Fix tiers\|§Triage\|## Triage" skills/writing/` shows one definition site (`review.md:13`), one polish.md shape C, one polish.md §Triage, one long-form-review.md, eight consistency files, two CLAUDE.md mentions. Manual end-to-end read of `polish.md` confirms: framing balanced, §Triage names the surface path for shapes A/B, §Minimal-edit discipline reframed as size-of-each-fix.

---

### Task 3: Re-cut tier vocabulary to `mechanical` / `conventional` / `authorial` and add the sequence/set/force test (Commit C)
**Depends on:** Task 2
**Review status:** APPROVED
**Integration status:** *(set during integration)*

**Script:** N/A (prose edits across 12 files)
**Input:**
- `skills/writing/references/review.md`
- `skills/writing/references/polish.md`
- `skills/writing/references/long-form-review.md`
- `skills/writing/references/consistency/{argument-logic,citations,code-paper,cross-references,math,notation,numerical,terminology}.md`
- `skills/writing/CLAUDE.md`

**Output:** Same files, edited in place. The §Fix tiers section in `review.md` is rewritten with the new tier names and the sequence/set/force test; the eight consistency output blocks, `polish.md`, `long-form-review.md`, and `CLAUDE.md` are updated to use the new names.

- [x] **Step 1: Rewrite `review.md §Fix tiers` with the new names and the sequence/set/force test.** Replace the three tier bullets with:
  - `mechanical` — surface-only change (orthography, grammar, format, missing article, undefined acronym on first use, missing `\hat` on an established estimate). The fix does not change meaning. Apply silently in batch.
  - `conventional` — wording, phrasing, or sentence shape. Preserves the paragraph's **sequence** (order of ideas), **set** (propositions asserted), and **force** (claim strength / hedge level). Examples: de-nominalization, breaking a long sentence, repairing parallelism, removing redundant phrasing, terminology-variant collapse to the paper's established choice. Apply, with one finding-line per item in the commit message so the author can audit.
  - `authorial` — changes sequence, set, or force; or commits the author to a choice not yet made (terminology pick when the paper has not committed; Greek letter pick when the parameter is undefined elsewhere; claim that may not generalize; sign disagreement between prose and table; topic sentence rewrite that moves the paragraph's argument). Surface to author; do not apply.

  Add a one-paragraph **sequence/set/force test** as the rule that draws the conventional/authorial line: "If sequence + set + force are all preserved, the edit is `conventional` regardless of how aggressive the rewrite is. If any one shifts, it is `authorial`." Carry 4–6 worked examples across the boundary (sentence-break — conventional; sentence-reorder — authorial; nominalization fix — conventional; hedge strengthening — authorial; coordinate sentence merge — conventional, but subordinating one to the other — authorial; topic-sentence move — authorial). The closing sentence of §Fix tiers names the prior `judgment` / `decision` vocabulary as the prior names so readers chasing old commit messages can match the terms.

- [x] **Step 2: Update the legal-values comment line in each `consistency/<dim>.md` output block.** Eight files (`argument-logic`, `citations`, `code-paper`, `cross-references`, `math`, `notation`, `numerical`, `terminology`) — change `Fix: mechanical | judgment | decision   # see review.md §Fix tiers` to `Fix: mechanical | conventional | authorial   # see review.md §Fix tiers`.

- [x] **Step 3: Update `polish.md` to use the new tier names.**
  - `§Input shape C` — the three apply-behavior bullets become: `mechanical` apply silently (batch commit per dimension); `conventional` apply with a per-item finding-line in the commit message; `authorial` surface for the author.
  - `§Triage` — body and parenthetical examples updated. Apply `mechanical` and `conventional` tier issues as minimal edits in place; surface `authorial`-tier issues. Update the example list under "issues that diagnose cleanly but need author input" to drop the now-misclassified ones (a redundant-quote suspicion is conventional unless it changes the set; a weak topic sentence rewrite is authorial because it moves sequence) and keep the claim-evidence gap as the canonical authorial example.
  - `§Minimal-edit discipline` — no tier-name reference; leave as is.

- [x] **Step 4: Update `long-form-review.md`.** Per-aspect-blocks bullet pointer at `review.md §Fix tiers` is unchanged in target; final-summary `severity × fix-tier counts table` and `per-tier batch table (mechanical / judgment / decision)` enumerations become `(mechanical / conventional / authorial)`. Any prose mentioning the tier names follows.

- [x] **Step 5: Update `skills/writing/CLAUDE.md`.**
  - §Multi-agent review pattern fix-tier bullet — rename tiers throughout; preserve the load-bearing rationale (continuous supervision-cost axis vs binary; one definition site; binary's failure mode). Add a parenthetical history note: "tier names re-cut 2026-05-08 from the prior `judgment` / `decision` to `conventional` / `authorial` after the `judgment` vs `decision` line collapsed into agent confidence — the sequence/set/force test in `review.md §Fix tiers` is the load-bearing reason against re-introducing the older names."
  - §Polish-mode triage — rename tiers throughout; preserve the under-editing failure-mode and framing-suppression cause.
  - History prose elsewhere in the file — the prior `judgment` / `decision` strings stay only in the explicit history mention added above; everywhere else they update.

- [x] **Step 6: Verify and commit Commit C.** Run:
  - `grep -rn "judgment\|decision" skills/writing/references/ skills/writing/CLAUDE.md` — expect only intentional history mentions (§Fix tiers closing sentence; CLAUDE.md §Multi-agent review pattern parenthetical). Each remaining hit is verified by reading the line.
  - `grep -rn "conventional\|authorial" skills/writing/` — expect: `review.md §Fix tiers` (definition site + worked examples), eight `consistency/<dim>.md` files, `polish.md §Input shape C` and `§Triage`, `long-form-review.md`, `CLAUDE.md` two sections.
  - Manual end-to-end read of `review.md §Fix tiers` confirms the sequence/set/force test reads cleanly and the worked examples cover the boundary; `polish.md §Triage` tier names match the §Fix tiers definition; the eight consistency output blocks all carry the new legal-values line.

  Commit message: `skill: writing — re-cut fix-tier vocabulary to mechanical/conventional/authorial`. Body cites the 2026-05-08 decision log entry and the sequence/set/force test as the dividing rule.
