# `writing` Skill — Redesign

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. **This project authors / restructures skill files** — every implementer and reviewer dispatch MUST additionally load `document-skills:skill-creator` and apply its conciseness, progressive-disclosure, and one-source-of-truth discipline. Apply `/CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action` (the **necessity principle**) line by line on every edit: for every line you write or keep, ask "without this line, would the agent's behavior be unstable?" If the answer is no, delete it. Wrapper sentences around authoritative content, "here is what you will receive" descriptions, and reminders of harness defaults are `[BLOCKING]` findings, not stylistic preferences. Steps use checkbox (`- [ ]`) syntax.

**Objective:** Reorganize `skills/writing/` so its top-level routing matches the three real working modes — **Review**, **Polish**, **Draft** — instead of superRA workflow phases (PLAN / IMPLEMENT / INTEGRATE), and replace the doctrinal "Iron Law / Three Concurrent Disciplines" framing with one principle (**Preserve substance, polish prose**). Substantive content (style rules, structure rules, consistency dimensions, refactor-and-compile, build commands) is preserved; the skeleton, load conditions, and authority model are rebuilt.

**Methodology:** This is a **reorganization**, not a content rewrite. The existing skill at `skills/writing/` is the input. Re-anchor `SKILL.md` around three modes, author three new mode files (`review.md`, `polish.md`, `draft.md`) that own per-mode workflow + authority, lighten the knowledge files (drop severity-tagging on style/structure heuristics, drop phase framing in headers), retire references whose content is now absorbed (`workflow.md`, `planning.md`, `collaboration.md`), and trim `integration.md`. Verification is dogfooding — invoke each mode against a representative scenario and confirm the right references load and the right behavior fires.

**Design plan reference:** `/Users/zhiyufu/.claude/plans/read-the-current-writing-robust-rivest.md` carries the approved design discussion (problem statement, mode taxonomy, design principles, resolved Q1–Q5). Implementers read this for design intent before authoring.

**Source-of-truth inputs:**

| Source | Path | Use |
|---|---|---|
| Existing `writing` skill | `skills/writing/SKILL.md` + `references/*` | The substantive content being reorganized. Implementers read the relevant pieces before authoring; the goal is to relocate / reframe content, not to re-derive it. |
| Approved design discussion | `/Users/zhiyufu/.claude/plans/read-the-current-writing-robust-rivest.md` | Design intent, the three-mode taxonomy, resolved decisions on polish input shapes, the inline-directive convention, light-vs-deep-polish-as-load-decision. |
| `/CLAUDE.md` §Internal Design Philosophy | repo root | Adaptive-composable workflows, minimal-targeted-instructions, **§Teach the Protocol, Don't Prescribe Each Action** (the necessity principle that every implementer/reviewer applies as a gate). |
| `document-skills:skill-creator` | plugin | Skill-authoring discipline: conciseness, progressive disclosure, one source of truth, frontmatter trigger phrasing. Loaded by every dispatch. |
| `skills/econ-data-analysis/` | repo | Architectural reference only. Do **not** mechanically clone its frame — the original `writing` skill's "Three Concurrent Disciplines" was such a clone and is being removed. |

**Output:**

- **Rewritten:** `skills/writing/SKILL.md`.
- **New:** `skills/writing/references/review.md`, `polish.md`, `draft.md`.
- **Renamed + lightened:** `skills/writing/references/style-checklist.md` → `style.md`; `structure-checklist.md` → `structure.md`. Drop severity tags on heuristic items; drop phase framing in headers.
- **Header rewrite (content unchanged):** `skills/writing/references/consistency/*.md` (8 files), `refactor-and-compile.md`. One-line "load when" header pointing at modes; drop per-file `## Reviewer verdict protocol` boilerplate; drop `Walked in addition to SKILL.md §Three Concurrent Disciplines` cross-references.
- **Trimmed:** `skills/writing/references/integration.md` — heavy trim; only loaded when the writing task rides `integration-workflow`.
- **Deleted:** `skills/writing/references/workflow.md`, `planning.md`, `collaboration.md` (after content absorbed).
- **Routing updates:** `skills/using-superRA/SKILL.md` Skill Inventory writing row, `skills/CATEGORIES.md`, `README.md` writing row reflect the new mode taxonomy. (No change to Skill-Load Manifest add-on table — the row already routes correctly.)
- No code artifacts, no data outputs.

**Expected Results:**

- Top-level invocation `writing` polish on a paragraph loads `SKILL.md` + `polish.md` + `style.md` only — no `planning.md`, no `workflow.md`, no `collaboration.md` doctrine.
- A review request like "check my citations and cross-references" loads `SKILL.md` + `review.md` + the two relevant `consistency/*.md` files; reviewers can be dispatched in parallel.
- A draft request "draft the methods section" loads `SKILL.md` + `draft.md` + `structure.md` + `style.md`.
- `SKILL.md` body passes the §Teach the Protocol gate line by line: every sentence shapes a non-default behavior; no wrapper instructions, no descriptions of dispatch shape, no harness-default reminders.
- A standalone polish does not enforce reviewer dispatch from this skill — that invariant lives in the workflow skills only.
- Dogfood (Task 4) confirms the three modes route correctly and produce sensible behavior on representative inputs.

**Sensitivity / robustness:** N/A (skill-design project). Substitute: Task 4 dogfood exercises Review, Polish (sentence-scope), Polish (structural-scope), and Draft modes on representative inputs to confirm the load-decision authority model behaves.

**Pipeline:** N/A (skill authoring, not analysis).

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on this redesign plan (2026-05-02)
- [ ] **Execution complete** — all tasks `APPROVED`
- [ ] **Drift tests created** — N/A for skill authoring; substitute satisfied by Task 4 dogfood
- [ ] **Integrated** — integration reviewer `APPROVED` on the redesign cumulative diff
- [ ] **Docs finalized** — RESULTS.md matured; routing surfaces (using-superRA / CATEGORIES / README) consistent with the new mode taxonomy
- [ ] **Finished** — branch landed locally, PR opened, or requested cleanup completed

---

## Decisions

> **User decision (2026-04-19):** Iron Law framed as author-respect only; compile is a `[BLOCKING]` item inside §Three Concurrent Disciplines, not part of the Iron Law.
> **Question asked:** Single 3-clause law vs two laws vs author-respect-only with compile demoted.
> **Rationale:** "Respect authors" means respecting the **intention/meaning** of the author — it does *not* mean preserving word choices or typos. The Iron Law forbids overriding authorial intent; word-level fixes remain the RA's job and live in the shared checklist.
> **Status (2026-05-02):** Superseded by the 2026-05-02 redesign decision below — Iron Law framing is being removed entirely. Kept here as historical record of the rationale, which informs the new "Preserve substance, polish prose" principle.

> **User decision (2026-04-19):** Fold figure/table/caption consistency into `consistency/numerical.md`. No separate figure-table reference file.

> **User decision (2026-04-19):** Domain skills are usable standalone — without the full PLAN → IMPLEMENT → VALIDATE → INTEGRATE workflow scaffold. Primary expected usage of the writing skill is standalone; the full workflow applies only to major changes (whole-section drafts, whole-paper revisions).
> **Rationale:** For tiny edits and iterative polish work, the user wants to iterate directly with the main agent.

> **User decision (2026-04-19):** Reviewer dispatch is never skipped, ever. Every mode — including direct-edit — requires an *independent* dispatched reviewer.
> **Status (2026-05-02):** Superseded by the 2026-05-02 redesign decision. Reviewer-dispatch invariants now belong to the workflow skills (`implementation-workflow` etc.), not to the writing skill itself. Standalone polish/draft invocations of `writing` do not enforce reviewer dispatch from inside the skill.

> **User decision (2026-04-19):** Split consistency checks by dimension and dispatch multiple reviewers in parallel, one per dimension. Mirrors the `draft-reviewer:*` plugin's one-agent-per-aspect pattern. (Still in force after the redesign — parallel-dispatch is a workflow-level pattern, the per-dimension `consistency/*.md` files keep their split.)

> **User decision (2026-04-19):** PLAN.md and RESULTS.md are both optional for small/iterative writing tasks. Full handoff-doc discipline only for major changes. (Still in force.)

> **User decision (2026-04-22):** Refresh `domain/writing-skills` against `main`; prioritize the minimum-net-diff path. A semantic merge is acceptable, and rebase/reapply is also authorized if it proves cleaner during conflict resolution.

> **User decision (2026-04-22):** Undo the 2026-04-22 `main` sync. The prior merge misread `main`'s integration intent by carrying forward `skills/using-superRA/SKILL.md`'s `## Universal Principles` block even though `main` had intentionally removed it.

> **User decision (2026-05-02, sync):** Re-sync `domain/writing-skills` against `main` using strict take-main-verbatim discipline on shared surfaces. Result captured in §Sync Map below.

> **User decision (2026-05-02, intent-comment discipline):** When editing `.tex` source, agents must use LaTeX inline comments (`%`) to record the intended effect / purpose of paragraphs and sections in-file, so that author intent persists across sessions. Drafted prose carries an `% intent:` line above the paragraph stating one-sentence purpose; polished prose preserves any pre-existing `% intent:` lines and may add inferred ones (with a hedge) when absent. Equivalent comment forms apply to Markdown (`<!-- intent: ... -->`) and Quarto. The discipline lives in the new `polish.md` and `draft.md` mode files plus a one-line summary in `SKILL.md §Before you start`. Authoring of the discipline is Task 4; dogfood (now Task 5) verifies it.
> **Question asked:** "give instructions to agents when editing .tex files, to use latex inline comment to explain the intended effect of the user for the surrounding paragraphs so it's preserved throughout sessions"
> **Rationale:** Writing tasks span sessions and context windows; inline comments in the source file are the only intent record that survives a fresh agent reading the .tex. Without the convention, polish-mode agents in later sessions cannot tell what a paragraph is *trying* to do (only what it currently says), and drift toward mechanically-correct prose that misses the intent.

> **User decision (2026-05-02, redesign):** Redesign `skills/writing/` around three working modes — Review / Polish / Draft — instead of superRA workflow phases. Replace the "Iron Law / Three Concurrent Disciplines" framing (a mechanical clone of `econ-data-analysis`) with a single principle: **Preserve substance, polish prose** (preserve = argument, logic, structure, claims, intent, tone; polish = wording, sentence structure, clarity, parallelism, flow, correctness). The previously-implemented skill stands as the *input* to this redesign — substantive content is preserved, the skeleton is rebuilt.
> **Question asked:** "the current writing skill isn't designed well — unclear when to load what; too much 'preserve voice', too little 'what to do'; design-principle violation. let's redesign."
> **Rationale (resolved during planning):**
> 1. **One `polish.md`** carries all three input shapes (unstaged edits / named target / review-findings list) as sub-sections. Procedural overlap is high; no need to split.
> 2. **`TODO` defaults to task-for-agent.** Inline `TODO`, `\todo{...}`, `% TODO:`, and crude / placeholder phrasing are **work assigned to the agent**. Author signals leave-alone explicitly with `DO NOT EDIT` (or equivalent) on the line/block. This **inverts** the prior `collaboration.md` default. Real polish workflows have authors dumping work-in-progress and expecting the agent to clean it up.
> 3. **Light-vs-deep polish is purely a load decision.** Light polish = `polish.md` + `style.md`; deep (structural) polish = `polish.md` + `style.md` + `structure.md`. Loaded references *are* the authority grant. No procedural difference between the two.
> 4. **Reviewer-dispatch enforcement leaves this skill.** Workflow skills (`implementation-workflow` etc.) own that invariant when a workflow is in play; standalone invocations terminate at edit + commit.
> 5. **Frontmatter trigger phrases reorganized by mode.**
> **Workflow Status impact:** This decision invalidates the prior plan's Tasks 1–8 (their outputs — SKILL.md, references — are being restructured). All `Workflow Status` rollups except this Plan-approved entry remain unchecked. The Sync Map below was for the prior 2026-05-02 main re-sync and is independent of this redesign; it stays until Integrate closeout.

---

## Sync Map

**Base branch:** `main`
**Pre-sync merge base:** `addc9ca7fe1bdbedb080d92095facb649074c1e4`
**Synced base head:** `886fda8b6a7862a0a4af8ec7d30fd53ffed6fea3`
**Incoming range:** `addc9ca..886fda8`
**Sync commits:** `fde4751`, `7a4cf1a`, plus the take-main-verbatim correction commit
**Sync review status:** APPROVED (after one REVISE round)

### Branch Summary

**Incoming intent:** Substantial restructuring of superRA workflow scaffolding while this branch was idle: `execution-workflow` renamed to `implementation-workflow`; `integration-workflow` rewritten around five phases (Protect / Sync / Integrate / Document / Finish); `refactor-and-integrate` narrowed to codebase-coherence with drift-test content moved to a new `result-protection` skill; `semantic-merge` gained mode references; `using-superRA` lost the `## Universal Principles` block (content redistributed); `CLAUDE.md` rewritten around adaptive-composable-workflow design principles. Codex named-agent generation, marketplace metadata, hook surfaces, and harness-compatibility tests advanced.

**Resolution thesis:** Strict take-main-verbatim on every shared infrastructure surface. Re-thread writing-vertical additions only into the surfaces main reshaped. Drop the renamed/deleted artifacts. Refresh stale references inside `skills/writing/` to point at main's current structure. Full file/script impact map and user-decision log live in `SEMANTIC_MERGE.md`.

### Sync Clusters

> **Sync cluster `cluster-1-shared-skills` (2026-05-02):** commits `fde4751`; paths `CLAUDE.md`, `README.md`, `agents/*`, `hooks/merge-guard`, `skills/{agent-orchestration,econ-data-analysis,handoff-doc,refactor-and-integrate,report-in-markdown,semantic-merge,worktree-data-sync}/...`, `skills/using-superRA/references/main-agent.md`, `.codex*/`, `tests/*`; affects no redesign tasks directly.
> **Sync resolution:** Took main verbatim. Branch had no writing-vertical content in any of these files.
> **Integration context:** None.
> **User decision:** None.

> **Sync cluster `cluster-2-routing-rethread` (2026-05-02):** commits `fde4751`; paths `skills/using-superRA/SKILL.md`, `skills/planning-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/CATEGORIES.md`, `README.md`; affects redesign Task 3 (routing surfaces will be edited again to update writing-row descriptions for the new mode taxonomy).
> **Sync resolution:** Took main's restructured surfaces verbatim, then added writing-vertical rows.
> **Integration context:** Task 3 of this redesign edits the same row descriptions (one-liner update only — the row's existence is established correctly).
> **User decision:** Main re-sync (2026-05-02 first §Decisions entry).

> **Sync cluster `cluster-3-stale-refs-in-writing` (2026-05-02):** commits `fde4751`; paths `skills/writing/SKILL.md`, `skills/writing/references/{workflow,integration,planning,collaboration}.md`; affects redesign Tasks 1–3 (these files are being restructured / deleted).
> **Sync resolution:** Refreshed stale references against main's renamed/restructured surfaces.
> **Integration context:** All four files touched by this cluster are restructured or deleted in the redesign — Task 1 rewrites `SKILL.md`, Task 3 deletes `workflow.md` / `planning.md` / `collaboration.md` and trims `integration.md`. The post-sync refresh is being superseded, but the rename-fix work it did is what the redesign starts from (so the redesign sees the correct file names, not the pre-rename ones).
> **User decision:** None.

> **Sync cluster `cluster-4-correction-take-main-verbatim` (2026-05-02):** commits the take-main-verbatim correction; paths `.agents/**`, `.codex/INSTALL.md`, `.gitattributes`, `AGENT.md`, `GEMINI.md`, `docs/README.codex.md`, `hooks/{autoload-superra,...}`, harness adapter references, archived plans, etc.; affects no redesign tasks.
> **Sync resolution:** `git checkout main -- <path>` for every divergent path outside the writing-vertical allowlist.
> **Integration context:** None.
> **User decision:** None new.

> **Sync review notes (2026-05-02, RESOLVED — round 1):** four findings (CRITICAL × 2, MAJOR × 2) all resolved by `cluster-4-correction-take-main-verbatim`. APPROVED.

---

## Project Conventions

Walked at planning time (2026-04-19); refreshed lightly at this redesign (2026-05-02) — Repo root and module-level docs unchanged in substance from the prior walk.

### Repo root
- `/CLAUDE.md` (HEAD at 886fda8): superRA contributor guidelines, **§Teach the Protocol, Don't Prescribe Each Action gate** (the necessity principle every implementer/reviewer applies line-by-line on every edit), **§Adaptive, Composable Workflows** (mechanisms over contingency trees, re-entry is normal, gates are local discipline, domain/utility skills stand alone), **§Ownership Boundaries** (one source of truth per concern), **§Skill Authoring Guidelines** (load `skill-creator` before editing any `skills/*/SKILL.md`).
- `/AGENTS.md`, `/AGENT.md`, `/GEMINI.md`: aliases / mirrors of `/CLAUDE.md`.
- `/README.md` (HEAD at 886fda8): plugin overview + skill inventory table.

### Module-level docs to walk on demand
- `skills/CATEGORIES.md` — authoritative skill categorization.
- `skills/using-superRA/SKILL.md` — Skill Inventory and Skill-Load Manifest. Writing row description gets refreshed in Task 3.
- `skills/handoff-doc/` + `references/{plan-anatomy,results-anatomy}.md` — PLAN.md / RESULTS.md editing discipline.
- `skills/econ-data-analysis/SKILL.md` + `references/*` — architectural reference (do not mechanically clone — the prior writing skill's clone is what is being removed).
- `skills/writing/` — the existing skill being redesigned. Implementers read the relevant files for content reuse.

### Not walked (not reachable from the planned diff)
- `Code/`, `Data/`, `Output/` — no such directories; this is a skill plugin.
- `docs/archive/`, `hooks/` — out of scope.

---

## Task 1: Rewrite `SKILL.md` + author three mode files

**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:**

**Files:**
- `skills/writing/SKILL.md` — full rewrite (replaces the existing 171-line Iron-Law-and-Disciplines body).
- `skills/writing/references/review.md` — new.
- `skills/writing/references/polish.md` — new.
- `skills/writing/references/draft.md` — new.

**Input:**
- `/Users/zhiyufu/.claude/plans/read-the-current-writing-robust-rivest.md` — design intent, mode taxonomy, resolved decisions.
- `skills/writing/SKILL.md` (current) — content to be relocated / reframed; do not re-derive substance from scratch.
- `skills/writing/references/{workflow,planning,collaboration}.md` — content to extract into the new mode files (especially polish-mode input shapes from `collaboration.md` §Detection patterns + §Edit-vs-propose-vs-ask matrix; review-as-planning from `planning.md`; usage-mode descriptions from `workflow.md`).
- `/CLAUDE.md` §Teach the Protocol, Don't Prescribe Each Action — the necessity gate; apply line by line.
- `document-skills:skill-creator` — authoring discipline.

**Output:** `SKILL.md` + 3 mode files matching the design plan structure. Concrete shape:

- **`SKILL.md` body** (target ≤120 lines) sections, in order: frontmatter (mode-organized triggers); §What this skill does (one paragraph: Review / Polish / Draft); §Preserve substance, polish prose (one short paragraph stating preserve-list / polish-list / no-restructure-without-authorization); §Before you start (request / input / inline-directive convention with `TODO`-as-task-for-agent default and `DO NOT EDIT` as the explicit hands-off marker); §Mode routing table (Review / Polish-sentence-scope / Polish-structural-scope / Draft) with "load X" being the authority grant; §Knowledge files table (style.md, structure.md, consistency/*.md, refactor-and-compile.md with one-line "load when"); §Coupling to superRA workflows (one short paragraph noting reviewer-dispatch invariants live in the workflow skills, not here); §Sources.
- **`review.md`** — review-mode workflow: read the draft, classify findings (style / structure / consistency / argument), report. Includes the "review-as-planning" pattern (review feeds into a `PLAN.md` for downstream revision); cross-references `consistency/*.md` for parallel-reviewer pattern. No `[BLOCKING]/[ADVISORY]` decoration on heuristic items.
- **`polish.md`** — polish-mode workflow with three labeled sub-sections for input shapes (unstaged edits / named target / review-findings list), the `TODO`-is-task / `DO NOT EDIT`-is-hands-off convention spelled out as a first-class rule, the "edit vs propose vs ask" decision matrix (relocated from `collaboration.md`), and a one-paragraph note that structural edits are out-of-scope unless `structure.md` is also loaded.
- **`draft.md`** — draft-mode workflow: gather inputs (notes, outline, results, prior section), build outline first, draft, self-check against `style.md` and `structure.md`. Acknowledges that draft work is more likely than the other modes to ride the full superRA workflow when large.

- [x] **Step 1: Read inputs and freeze the design**

Implementer reads `/Users/zhiyufu/.claude/plans/read-the-current-writing-robust-rivest.md` end-to-end first. Then reads the four files being relocated/replaced (`skills/writing/SKILL.md`, `references/workflow.md`, `references/planning.md`, `references/collaboration.md`) to identify which content lands in `SKILL.md`, which in `review.md`, which in `polish.md`, which in `draft.md`, and which is dropped. Implementer also reads the existing `style-checklist.md`, `structure-checklist.md`, and one or two `consistency/*.md` to confirm what knowledge content is *not* being touched in this task.

- [x] **Step 2: Draft `SKILL.md`**

Apply the §Teach the Protocol gate line by line as you write. Banned: wrapper sentences around authoritative content, "here is what you will receive" descriptions, restating the Skill-Load Manifest, reminders that the agent should "load skills the manifest says to load." Required: every line earns its keep — name a non-default behavior, a safety invariant, or an ordering constraint the agent would not infer.

- [x] **Step 3: Draft `review.md`, `polish.md`, `draft.md`**

Same gate applies. Each file ≤150 lines; one-line "load when" header pointing at modes; no `## Reviewer verdict protocol` boilerplate (that lives in workflow skills). The polish-mode `TODO`-is-task-for-agent / `DO NOT EDIT`-is-hands-off convention is spelled out once in `polish.md` (the `SKILL.md §Before you start` summary points at it).

- [x] **Step 4: Self-review against `skill-creator` discipline + necessity gate**

Walk every line of the four new files through the `/CLAUDE.md` necessity test. Delete any line that fails. Verify each mode file's load-when condition matches the routing table in `SKILL.md` exactly. Update `RESULTS.md` Task 1 (key findings: line counts, what was relocated where, what was deleted as redundant). Mark steps `[x]`, set `**Review status:** IMPLEMENTED`. Commit atomically: `skill: writing SKILL.md + mode files (review/polish/draft) for the redesign`.

---

## Task 2: Lighten knowledge files and trim `integration.md`

**Depends on:** *(none — can run in parallel with Task 1)*
**Review status:** APPROVED
**Integration status:**

**Files:**
- Renamed: `skills/writing/references/style-checklist.md` → `style.md`; `structure-checklist.md` → `structure.md` (use `git mv`).
- Header rewrite (content unchanged): `skills/writing/references/style.md`, `structure.md`, `refactor-and-compile.md`, and 8 × `consistency/*.md`.
- Trimmed: `skills/writing/references/integration.md`.

**Input:**
- The current files listed above.
- The redesign plan file for the "drop severity tags on heuristic items" and "drop phase framing" rules.
- `/CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action`.

**Output:**

- `style.md` and `structure.md`: drop `[BLOCKING]/[ADVISORY]` severity tagging on the heuristic rules in §Gated Checklist (these are heuristics; tagging them as verdict-determining was the symptom of the doctrinal framing); drop the "Walked in addition to `skills/writing/SKILL.md` §Three Concurrent Disciplines" cross-reference; drop the per-file `## Reviewer verdict protocol` boilerplate; rewrite the one-line file-top header to point at modes ("Load when polish or draft mode applies sentence-level rules" / "...applies structural rules") not phases. Substance of every rule unchanged.
- `consistency/*.md` (8 files) — same header rewrite. The dimension content stays as-is (the `[BLOCKING]/[ADVISORY]` tagging on consistency findings is load-bearing for reviewer output and stays). Drop the per-file `## Reviewer verdict protocol` boilerplate (workflow skills own that). Drop the "Walked in addition to SKILL.md §Three Concurrent Disciplines" cross-reference where present.
- `refactor-and-compile.md` — drop the cross-reference to `SKILL.md §Three Concurrent Disciplines §Verify`; rewrite header to point at modes; substance unchanged.
- `integration.md` — heavy trim. Most of the existing six gates are restatements of mode-level discipline (build clean, consistency dimensions pass, scope respected). Keep only the items that are specific to *integration* of writing (full-document build on the merged state, outline-stability check, voice-preserved sample, scope-tracing). One-line "load when" header pointing at `integration-workflow` riding a writing branch. Target ≤80 lines (down from 119).

- [x] **Step 1: Rename style-checklist.md → style.md and structure-checklist.md → structure.md (git mv)**

```bash
cd skills/writing/references
git mv style-checklist.md style.md
git mv structure-checklist.md structure.md
```

The bare-`git mv` is the rename atom; commit after Step 5 with the body edits in the same commit so reviewers see the move + edits together.

- [x] **Step 2: Rewrite headers in `style.md`, `structure.md`, `refactor-and-compile.md`, 8 × `consistency/*.md`**

For each file, the top section (typically the first 5–10 lines) is rewritten to: a one-line "Load when …" sentence pointing at modes, the source-citation paragraph (kept), and one-line statement of severity-marker convention if the file uses one. **Drop:** "Load at the IMPLEMENT phase…" framing; "Walked in addition to `skills/writing/SKILL.md` §Three Concurrent Disciplines …" cross-references; the per-file `## Reviewer verdict protocol` block at the end of each file.

- [x] **Step 3: Drop `[BLOCKING]/[ADVISORY]` severity tagging on heuristic rules in `style.md` and `structure.md`**

Style and structure rules are heuristics with explicit "Do NOT apply when …" exceptions. Tagging them as verdict-determining is the doctrinal residue. The Gated Checklist sections become an unbulleted-or-bulleted list of rule names with the same prose, no severity prefix. (The `[BLOCKING]` tag at the bottom of `style.md` on the "every applied rule traceable to a real problem" handoff item stays — that *is* a behavior-shaping rule.)

- [x] **Step 4: Trim `integration.md`**

Drop redundant gates that restate mode-level discipline. Keep gates specific to integration: full-document build on the merged state; outline stability across the diff; voice-preserved sample (the three-hunk check stays); scope-respected hunk-trace. Drop the data-analysis-touching note's prose detail (one sentence pointer to `econ-data-analysis/references/integration.md` is enough). Target ≤80 lines.

- [x] **Step 5: Self-review + commit**

Verify each rewritten header passes the §Teach the Protocol gate. Verify no surviving cross-reference points at `§Three Concurrent Disciplines` or `Walked in addition to SKILL.md §Three …`. Update `RESULTS.md` Task 2. Mark steps `[x]`, set `**Review status:** IMPLEMENTED`. Commit atomically: `skill: writing knowledge-file lightening + integration.md trim`.

---

## Task 3: Retire deprecated references and update routing

**Depends on:** Task 1, Task 2
**Review status:** APPROVED
**Integration status:**

**Files:**
- Deleted: `skills/writing/references/workflow.md`, `planning.md`, `collaboration.md`.
- Edited: `skills/using-superRA/SKILL.md` (writing row in Skill Inventory), `skills/CATEGORIES.md` (writing row), `README.md` (writing row).
- Edited if needed: `skills/writing/SKILL.md` (only if Task 1 left forward-references that need cleanup) and any `consistency/*.md` cross-reference that pointed at `workflow.md` / `planning.md` / `collaboration.md`.

**Input:**
- Tasks 1 and 2 outputs.
- `grep -rn 'references/workflow\.md\|references/planning\.md\|references/collaboration\.md' skills/writing/` — must return empty after this task.
- `grep -rn 'writing/references/workflow\|writing/references/planning\|writing/references/collaboration' .` from repo root — must return empty after this task.

**Output:**

- The three deprecated reference files removed (`git rm`).
- Routing rows for `writing` updated to reflect the new mode taxonomy (one-liner edit per row — the row's existence and correct skill-name is established already).

- [x] **Step 1: Verify content extraction is complete + sweep doctrinal residue**

```bash
# All references to the deprecated files inside the writing skill must be gone:
grep -rn 'references/workflow\.md\|references/planning\.md\|references/collaboration\.md' skills/writing/

# All references to the deprecated files anywhere in the repo:
grep -rn 'writing/references/\(workflow\|planning\|collaboration\)' .

# Doctrinal residue from the prior Iron Law / Three Concurrent Disciplines framing
# (Task 2 left these alone because content was scoped as unchanged; Task 3 fixes them):
grep -rn 'Iron Law\|Three Concurrent Disciplines\|Preserve.Improve.Verify\|§Preserve\|§Improve\|§Verify' skills/writing/
```

For the doctrinal-residue grep, expected hits per the Task 2 implementer's flag: `consistency/argument-logic.md`, `consistency/citations.md`, `consistency/math.md`, `consistency/terminology.md`. Rewrite each in place to invoke the new principle ("Preserve substance, polish prose" — `SKILL.md`) instead. Substance of the rule the citation invokes is unchanged; only the principle name changes.

If any matches in the first two greps survive, the implementer must trace each one and resolve before deletion: either the new mode files / SKILL.md should carry the absorbed content (back to Task 1), or the cross-reference is stale (fix it in place).

- [x] **Step 2: Delete the deprecated reference files**

```bash
git rm skills/writing/references/workflow.md
git rm skills/writing/references/planning.md
git rm skills/writing/references/collaboration.md
```

- [x] **Step 3: Update routing surfaces**

- `skills/using-superRA/SKILL.md` Skill Inventory writing row — refreshed to "Review / Polish / Draft modes, preserve-substance-polish-prose principle, per-dimension consistency reviewers." The Skill-Load Manifest add-on row already routes `superRA:writing` correctly — no change there.
- `skills/CATEGORIES.md` writing row — description refreshed; the pre-rename `style-checklist.md` / `structure-checklist.md` paths flagged by Task 2's last reviewer (and by this task's `Additionally:` line) corrected to `style.md` / `structure.md`; mode references (`review.md`, `polish.md`, `draft.md`) added to the file list.
- `README.md` writing-row description (Domain skills table) — refreshed to the three-mode framing while preserving the per-dimension parallel-consistency-reviewer note.
- `skills/integration-workflow/SKILL.md:358` (cross-skill stale-ref fix discovered in Step 1) — the "Writing-vertical tasks" lighten-when bullet pointed at the now-deleted `writing/references/workflow.md` and used the four-standalone-modes framing. Rewritten to point at `skills/writing/SKILL.md` and the new mode taxonomy; substance preserved.

- [x] **Step 4: Self-review + commit**

Re-run all three grep checks from Step 1 on the post-edit state — the first two must return empty (or only return matches inside test files / archived docs / `docs/plans/` that legitimately reference the historical structure); the third (doctrinal residue) must return empty inside `skills/writing/` proper. Update `RESULTS.md` Task 3. Mark steps `[x]`, set `**Review status:** IMPLEMENTED`. Commit atomically: `skill: writing — retire workflow/planning/collaboration refs + Iron Law residue sweep + routing-row refresh`.

---

## Task 4: Add intent-comment discipline to `polish.md` / `draft.md` / `SKILL.md`

**Depends on:** Task 1
**Review status:** IMPLEMENTED
**Integration status:**

**Files:**
- `skills/writing/references/polish.md` — add §Intent comments section.
- `skills/writing/references/draft.md` — add §Intent comments section.
- `skills/writing/SKILL.md` §Before you start — add one-line summary that points at the §Intent comments sections in the mode files.

**Input:**
- Task 1's authored mode files.
- The 2026-05-02 §Decisions entry for this task (the convention is decided there; this task implements it).
- `/CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action` — necessity gate applies as usual.

**Output:** A short, format-aware discipline that lives in the mode files and is summarized in `SKILL.md`. Concrete shape:

- **Convention.** When editing `.tex`, an `% intent: <one-sentence purpose>` line sits on its own line **immediately before** the paragraph or section it documents. Markdown / Quarto: `<!-- intent: <one-sentence purpose> -->` in the same position. The comment captures *what the paragraph is trying to do for the reader* — the argument it advances, the question it answers, the position it stakes — not what it currently says.
- **Draft mode.** Before drafting a paragraph, write the intent comment first. Use it as the brief; then draft prose that fulfills it. The comment ships with the prose.
- **Polish mode.** Read pre-existing `% intent:` comments before editing — they are the preservation target (more authoritative than the paragraph's current wording, since the wording is exactly what's being polished). When intent comments are absent on a paragraph being polished, the agent **may** add an inferred comment with a hedge (`% intent (inferred): ...`) — never silently. The author can ratify (delete the `(inferred)` qualifier) or correct on review.
- **Review mode.** Use intent comments as the yardstick: does the prose actually accomplish the stated intent? Drift between intent and prose is a finding.

- [x] **Step 1: Add §Intent comments to `polish.md`**

A short section (≤25 lines) covering: the convention (format per file extension); how polish mode uses pre-existing comments; the "may add inferred, must hedge" rule with explicit persistence-of-`(inferred)`-until-author-ratifies; one example with `% intent:` line.

- [x] **Step 2: Add §Intent comments to `draft.md`**

A short section (≤20 lines) covering: write the intent first as the drafting brief; the comment ships with the prose; format per file extension; clarification that draft-authored intent is not hedged. One example.

- [x] **Step 3: Add one-line summary to `SKILL.md §Before you start`**

Item 4 added below the inline-directive convention pointing at the §Intent comments sections in `polish.md` and `draft.md`.

- [x] **Step 4: Self-review + commit**

Verify the convention is stated identically across the three files (format spec) and that the `polish.md` "may add inferred" rule is explicit about the hedge. Apply the §Teach the Protocol gate — every line earns its keep. Update `RESULTS.md` Task 4. Mark steps `[x]`, set `**Review status:** IMPLEMENTED`. Commit atomically: `skill: writing — intent-comment discipline in polish/draft/SKILL`.

---

## Task 5: Dogfood — three-mode verification

**Depends on:** Tasks 1, 2, 3, 4
**Review status:**
**Integration status:**

**Files:** RESULTS.md Task 4 entry. No skill / reference edits expected unless the dogfood surfaces a bug; in that case adjustments are committed separately with a message naming the dogfood observation that prompted the fix.

**Input:** A representative paragraph or short section per mode (orchestrator may supply or fabricate the test inputs).

**Output:** Four short dogfood reports in `RESULTS.md` Task 4 confirming that each mode loads the right references, the authority model behaves (deep polish doesn't fire without `structure.md` loaded), and the inline-directive convention (TODO-as-task vs DO-NOT-EDIT-as-hands-off) is respected.

- [ ] **Step 1: Mode = Review**

Pick a paragraph with deliberate cross-reference and citation drift. Invoke `superRA:writing`. Verify: `SKILL.md` + `review.md` + the relevant `consistency/*.md` files load. Findings classify correctly. No edits performed.

- [ ] **Step 2: Mode = Polish (sentence/paragraph scope)**

Pick a paragraph with: an inline `% TODO: rewrite this more crisply`, crude phrasing ("the result is super strong"), a structural problem (buried main message), and a `DO NOT EDIT` block somewhere. Verify: `SKILL.md` + `polish.md` + `style.md` load. Inline TODO and crude phrasing get cleaned up; `DO NOT EDIT` block untouched; structural problem **not** addressed (out of scope by load configuration).

- [ ] **Step 3: Mode = Polish (structural scope)**

Same paragraph as Step 2, with explicit user request "restructure for clearer argument". Verify: `SKILL.md` + `polish.md` + `style.md` + `structure.md` load. Structural problem now addressed (authority grant present).

- [ ] **Step 4: Mode = Draft**

Pick a small section (e.g., a methodology paragraph) with notes / outline as input. Verify: `SKILL.md` + `draft.md` + `structure.md` + `style.md` load. Output is sensible new prose. Verify the draft includes `% intent:` (or format-equivalent) comments above the paragraph(s).

- [ ] **Step 5: Intent-comment discipline (Task 4 verification)**

Two sub-checks in one paragraph:
- (a) Polish-mode preservation: a paragraph with a pre-existing `% intent: ...` comment is polished; the comment is preserved verbatim and the polished prose still fulfills the stated intent.
- (b) Polish-mode inferred-add: a paragraph **without** an intent comment is polished; the agent adds `% intent (inferred): ...` (with the hedge marker) above the paragraph rather than silently.

- [ ] **Step 6: Document findings + adjustments + commit**

Each adjustment is its own commit naming the dogfood observation. If no adjustments needed, commit `RESULTS.md` Task 5 only with a one-line dogfood-passed note. Mark steps `[x]`, set `**Review status:** IMPLEMENTED`.
