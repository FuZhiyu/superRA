# Fix-Tier Replacement Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This is a **skill-internals edit** — load `document-skills:skill-creator` for SKILL.md / reference-file edits per the repo CLAUDE.md (`When modifying superRA itself … treat the work as skill creation`). The active domain skill is `superRA:writing` (the skill being edited).

**Objective:** Replace the binary `Auto-fixable: Yes / No` field in each `consistency/<dim>.md` output format with a 3-tier `Fix:` field that captures the supervision cost of applying a finding, and wire the new contract through `polish.md` shape C and `long-form-review.md` so review → polish handoff stays mechanical.

**Methodology:**
- Define the three tiers — `mechanical` / `judgment` / `decision` — once in `references/review.md` (the single home every consistency reviewer already loads); other files reference that section.
- `mechanical` = one correct fix, no semantic call. `judgment` = one likely fix exists, agent picks using paper conventions. `decision` = needs author input.
- Polish-mode shape C applies `mechanical` in a silent batch, applies `judgment` with one finding-line per item in the commit message, and surfaces `decision` items for the author.

**Conventions:**
- Tier vocabulary lives in `review.md §Output contract: Fix tiers` (single source).
- Each `consistency/<dim>.md` output block uses the line `Fix: <tier>` with `<tier>` ∈ {mechanical, judgment, decision}.
- `long-form-review.md` summary table uses `severity × fix-tier` counts (replacing `severity × auto-fixable`).
- Field name is `Fix:` (not `Fix-tier:` or `Action:`) — short, unambiguous in the output block.

**Output:** Edits to:
- `skills/writing/references/review.md` (add §Output contract: Fix tiers)
- `skills/writing/references/polish.md` (extend §Input shape C with tier-based application policy)
- `skills/writing/references/long-form-review.md` (replace `Auto-fixable` references; update summary-table description)
- `skills/writing/references/consistency/{argument-logic,citations,code-paper,cross-references,math,notation,numerical,terminology}.md` — eight output blocks
- `skills/writing/CLAUDE.md` (replace the auto-fixable bullet under §Multi-agent review pattern with a fix-tier rationale bullet)

**Expected Results:** A single coherent contract across reviewer output → orchestrator summary → polish handoff, replacing the binary that conflated supervision cost with auto-fixability.

**Sensitivity Analysis:** N/A (skill-prose change, no analytic results).

**Pipeline:** N/A (single conceptual change; verification is a `grep -r "Auto-fixable"` returning zero hits and a manual read-through of the touched files).

---

## Workflow Status

- [x] **Plan approved** — researcher signed off (chose Option A — tiered action — over Option B in 2026-05-05 design discussion)
- [ ] **Execution complete** — Task 1 `APPROVED`, no `Auto-fixable` strings remain
- [ ] **Drift tests created** — N/A (skill-prose; the `grep` check is the regression test)
- [ ] **Integrated** — integration reviewer `APPROVED`
- [ ] **Docs finalized** — RESULTS.md matured, CLAUDE.md design note rewritten
- [ ] **Finished** — branch landed / PR opened per researcher's choice

---

## Project Conventions

Walked at planning time (2026-05-05). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at 505a975): Contributor guidelines for editing superRA itself. Hard rule: "When modifying superRA itself — skills, hooks, agents, harness adapters, or internal docs — treat the work as skill creation." Also carries the DRY / Necessity gate, ownership-boundaries table, and the anti-pattern list (wrapper instructions, "what you will receive" descriptions, reminders of harness defaults).
- `/AGENTS.md`, `/AGENT.md`: aliases of `/CLAUDE.md` for Codex-facing contributors.
- `/README.md`: user-facing overview of superRA — stays untouched by this change.

### Module-level docs walked
- `skills/writing/CLAUDE.md` (HEAD at 505a975): Design notes for the writing skill. Records the eight load-bearing decisions including the §Multi-agent review pattern bullet on the auto-fixable flag — that bullet is rewritten by this plan.

### Not walked (not reachable from the planned diff)
- `skills/{econ-data-analysis,theory-modeling,planning-workflow,…}/` — the change is local to `skills/writing/`.
- `agents/`, `hooks/`, `tests/`, `scripts/` — no role / harness / generator surface affected.

---

### Task 1: Replace `Auto-fixable` flag with `Fix:` tier across the writing skill
**Depends on:** *(none)*
**Review status:** *(set during execution)*
**Integration status:** *(set during integration)*

**Script:** N/A (prose edits across 11 files)
**Input:**
- `skills/writing/references/review.md`
- `skills/writing/references/polish.md`
- `skills/writing/references/long-form-review.md`
- `skills/writing/references/consistency/{argument-logic,citations,code-paper,cross-references,math,notation,numerical,terminology}.md`
- `skills/writing/CLAUDE.md`
**Output:** Same files, edited in place.

- [ ] **Step 1: Add §Output contract: Fix tiers to `review.md`**

  After §Workflow and before §Thoroughness, insert a new section that defines the three tiers and the producer-side rule (the reviewer picks the tier when writing each finding). Keep it tight — a short paragraph per tier plus a one-line "applies to every `consistency/<dim>.md` output block" pointer.

  ```markdown
  ## Output contract: Fix tiers

  Every consistency-dimension finding carries a `Fix:` line with one of three tiers, chosen by the reviewer when the finding is written. The tier captures the supervision a downstream apply pass needs — not whether the finding *can* be auto-fixed (anything can; the question is the cost of being wrong).

  - **`mechanical`** — one correct fix exists and no semantic call is needed. Typo, missing definite article, missing `\hat` on an established estimate, undefined acronym on first use. Applied silently in batch.
  - **`judgment`** — one likely fix exists but the agent must pick using paper-internal conventions. Terminology-variant collapse, choice between equally legal hedge phrasings, picking which Greek letter wins when the paper has not committed yet. Applied with one finding-line per item in the commit message so the author can audit.
  - **`decision`** — the right fix needs author input. Cross-section claim that may or may not generalize, sign disagreement between prose and a table that could be either way, restructure suggestion. Surfaced for the author; not applied.

  The tier replaces the earlier `Auto-fixable: Yes / No` flag. Each `consistency/<dim>.md` output block names this section as the source of legal values.
  ```

- [ ] **Step 2: In each `consistency/<dim>.md` output block, replace the Auto-fixable line**

  Eight files: `argument-logic.md`, `citations.md`, `code-paper.md`, `cross-references.md`, `math.md`, `notation.md`, `numerical.md`, `terminology.md`. In every output-format code block, replace the line

  ```
  Auto-fixable: Yes / No
  ```

  with

  ```
  Fix: mechanical | judgment | decision   # see review.md §Output contract: Fix tiers
  ```

  No other text in those files changes. Verify with `grep -rn "Auto-fixable" skills/writing/` returning empty.

- [ ] **Step 3: Extend `polish.md §Input shape C` with the tier-based application policy**

  Currently shape C says "apply each accepted finding as a minimal edit". Add a short paragraph after that sentence that distinguishes the three tiers' apply behaviors:

  ```markdown
  Each accepted finding carries a `Fix:` tier (`review.md §Output contract: Fix tiers`); polish-shape-C apply behavior follows the tier:

  - `mechanical` — apply silently; group into one batch commit per dimension.
  - `judgment` — apply, but write one finding-line per item in the commit message naming the choice made.
  - `decision` — surface for the author; do not apply.

  An accepted-but-deferred `decision` item stays in the findings list with a note recording why it was not applied.
  ```

- [ ] **Step 4: Update `long-form-review.md` to reference the tier instead of the flag**

  Two edits:
  - In the third bullet under §Doc convention ("Final summary block at the top…"), replace `severity × auto-fixable counts table` with `severity × fix-tier counts table`, and replace `auto-fixable batch table sized for polish-mode shape C handoff` with `per-tier batch table (mechanical / judgment / decision) sized for polish-mode shape C handoff`.
  - In the second bullet under §Doc convention ("Per-aspect blocks ARE task blocks…"), replace `including the new `Auto-fixable: Yes / No` line` with `including the `Fix:` tier line per `review.md §Output contract: Fix tiers``.

- [ ] **Step 5: Update `CLAUDE.md §Multi-agent review pattern` bullet**

  Replace the existing fifth bullet (the "Auto-fixable flag in every `consistency/<dim>.md` output format" bullet) with a bullet that records the tier rationale:

  ```markdown
  - **Fix-tier (`mechanical` / `judgment` / `decision`) in every `consistency/<dim>.md` output format.** Replaces an earlier binary `Auto-fixable: Yes / No` flag (2026-05-02 → 2026-05-05). The binary forced a continuous axis (supervision cost) into two buckets and pushed operational triage into the review output, which made the reviewer pre-judge what polish would do. The tier is honest about the spectrum and lets polish-mode shape C batch `mechanical`, log `judgment` per item, and surface `decision` to the author. Defined once in `references/review.md §Output contract: Fix tiers`; the eight `consistency/<dim>.md` output blocks reference that section. If a future contributor wants to compress the tiers back to a flag, the binary's failure mode is the load-bearing reason it was rejected — re-litigating requires a new failure mode, not a preference for terseness.
  ```

- [ ] **Step 6: Verify, update RESULTS.md, commit**

  Run `grep -rn "Auto-fixable\|auto-fixable" skills/writing/` — expect zero hits except inside the CLAUDE.md history bullet that names the prior flag (one occurrence is acceptable; flag for the orchestrator if more). Read each touched file end-to-end once. Update RESULTS.md Task 1 with the verification command output and a one-line summary. Mark all PLAN.md steps `[x]`, set `**Review status:** IMPLEMENTED`. Commit code + handoff docs atomically.
