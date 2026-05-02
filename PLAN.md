# `writing` Domain Skill

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This project authors new skill files — every implementer and reviewer dispatch MUST additionally load `document-skills:skill-creator` and apply its conciseness, progressive-disclosure, and one-source-of-truth discipline. Preserve carefully-tuned content patterns (Iron Law, Common Rationalizations table, RA-framing, `[BLOCKING]`/`[ADVISORY]` severity markers) per `/CLAUDE.md §Skill Changes`. Steps use checkbox (`- [ ]`) syntax.

**Objective:** Ship `skills/writing/` as a new superRA domain vertical parallel to `econ-data-analysis` — a practical, checklist-oriented skill that teaches agents to edit, polish, proofread, consistency-check, refactor wording, and draft technical sections of academic papers while respecting the researcher's intent and producing compilable documents.

**Methodology:** Skill-authoring project, not data analysis. Distill source material (Little Red Schoolhouse notes at `/Users/zhiyufu/Dropbox/PhD/writing_resources/`, Chaubey's *Research Writing*, Pyramid Principle) into mechanically-checkable rules; split consistency checks by dimension so multiple reviewers dispatch in parallel; encode flexible usage modes (direct-edit / pure-review / review-edit loop / full workflow) in a dedicated `workflow.md` reference. Mirror `econ-data-analysis` architecture: main SKILL.md (Iron Law + Common Rationalizations + §Three Concurrent Disciplines + §Pitfalls) plus stage-scoped references under `skills/writing/references/`. Verification is dogfooding — run the skill on a real manuscript section and watch it behave.

**Source Material Inventory:**

**READ BEFORE DRAFTING OR REVIEWING.** Every implementer and reviewer must load the corresponding source material before writing or validating a reference file. The task steps below condense rules to check — they are not a substitute for reading the originals. Full catalog + reading map at `docs/writing-references/README.md`.

### Available
| Source | Path | Purpose |
|--------|------|---------|
| Little Red Schoolhouse (LRS) writing notes — 14 PDFs | `/Users/zhiyufu/Dropbox/PhD/writing_resources/LittleRedHouse/` (Dropbox-synced, not committed) | UChicago ENGL 13000/33000 slides. Actions-in-verbs (1-1a), character (1-1b), coherence/cohesion (2), old→new info flow (3-4), introductions (5, 6), argument structure (Arg 1–3), downstream revision (DS 1–2), triage. Main input to `style-checklist.md` and `structure-checklist.md`. |
| Chaubey, "Research Writing" | `docs/writing-references/Chaubey_Research_Writing.pdf` (committed) | Academic-writing rules targeted at the economics audience — structure, precision, reader-model. Main input to `style-checklist.md` and `structure-checklist.md`. |
| Pyramid Principle (Minto) | Web reference list in `docs/writing-references/README.md` (Minto / McKinsey / StrategyU / Mental Models / Think Insights / ModelThinkers / Management Consulted) | Governing idea, MECE, horizontal/vertical logic, SCQ (Situation–Complication–Question). Main input to `structure-checklist.md`. |
| Economics-writing guidance | Web reference list in `docs/writing-references/README.md` (Brandeis, CGDev, IZA DP15057, Bellemare, Conversable Economist) | Supporting guidance for section-level structure in `structure-checklist.md`. |
| `draft-reviewer:*` plugin subagents | `~/.claude/plugins/draft-reviewer/` | Dimension split for `consistency/*.md`. Harvest the *dimensions*, re-derive the content in superRA style. |
| `skills/econ-data-analysis/` | repo (`skills/econ-data-analysis/SKILL.md` + `references/*`) | Architectural template for main SKILL.md + references layout, Iron Law pattern, shared checklist with severity markers. |

### Quality Notes
- LRS notes are University of Chicago ENGL 13000/33000 slide content — concrete checklist-able rules, high confidence.
- Draft-reviewer agents supply review *dimensions*; the actual rule content for each dimension is re-derived in superRA's style so the plugin is a harvest target, not a runtime dependency.
- `docs/writing-references/README.md` carries the reading-map per task — check it before dispatching an implementer.

**Conventions:** (populated as the skill emerges — emergent section titles, reference-file naming, severity-marker usage land here)

**Output:** One new skill at `skills/writing/SKILL.md` with eleven references (2 top-level + 1 workflow + 8 consistency-dimension files, see Task blocks), plus routing updates to `skills/using-superRA/`, `skills/planning-workflow/`, `skills/integration-workflow/`, `skills/merge-workflow/`, `skills/CATEGORIES.md`, and `README.md`. Possible amendment to `/CLAUDE.md` making the "domain skills are standalone-usable" property explicit. No code artifacts, no data outputs.

**Expected Results:** (a) The Iron Law **"Respect the Author's Intent"** fires on deliberate scope-violation attempts; (b) the §Three Concurrent Disciplines shared checklist catches compile failures and cross-reference breaks; (c) parallel-dispatched consistency reviewers (one per `consistency/*.md`) cover a real manuscript section faster than a single reviewer would; (d) the skill loads cleanly standalone without the PLAN→IMPLEMENT→VALIDATE→INTEGRATE workflow wrapper for tiny edits and pure-review sessions; (e) no regression in the existing `econ-data-analysis` flow.

**Sensitivity / robustness:** N/A (skill-design project). Substitute: the Phase H dogfood runs three mode variants (direct edit, review-edit loop, optional full workflow) so the skill is exercised across its documented usage modes.

**Pipeline:** N/A (skill authoring, not analysis).

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on this plan (2026-04-19)
- [ ] **Execution complete** — all tasks `APPROVED`
- [ ] **Drift tests created** — **N/A for skill authoring**; substitute satisfied by Task 8 dogfood (three-mode real-session verification) + skill-graph consistency sweep
- [ ] **Refactored** — final integration-review approval on the consolidated skill changes
- [ ] **Docs finalized** — README / RELEASE-NOTES / CATEGORIES / CLAUDE.md audited and consistent with the new skill
- [ ] **Merged** — branch merged to main or PR opened

---

## Decisions

> **User decision (2026-04-19):** Iron Law framed as author-respect only; compile is a `[BLOCKING]` item inside §Three Concurrent Disciplines, not part of the Iron Law.
> **Question asked:** Single 3-clause law vs two laws vs author-respect-only with compile demoted.
> **Rationale:** "Respect authors" means respecting the **intention/meaning** of the author — it does *not* mean preserving word choices or typos. The Iron Law forbids overriding authorial intent; word-level fixes remain the RA's job and live in the shared checklist.

> **User decision (2026-04-19):** Fold figure/table/caption consistency into `consistency/numerical.md`. No separate figure-table reference file.
> **Question asked:** Separate `figure-table-checklist.md` vs folded.

> **User decision (2026-04-19):** Domain skills are usable standalone — without the full PLAN → IMPLEMENT → VALIDATE → INTEGRATE workflow scaffold. Primary expected usage of the writing skill is standalone; the full workflow applies only to major changes (whole-section drafts, whole-paper revisions).
> **Question asked:** Should `workflow.md` expose a lightweight escape hatch for tiny polish tasks?
> **Rationale:** For tiny edits and iterative polish work, the user wants to iterate directly with the main agent. `workflow.md` documents four modes: direct-edit, pure-review, review-edit-loop, full-workflow. `CLAUDE.md` will be audited (Task 7) to confirm this property is stated explicitly.

> **User decision (2026-04-19):** Reviewer dispatch is never skipped, ever. Every mode — including direct-edit — requires an *independent* dispatched reviewer.
> **Question asked:** Implied by the direct-mode discussion.
> **Rationale:** Preserves workflow principle #1. Orchestrator may step into the implementer role (direct edit while in live conversation), but the reviewer role is always a fresh dispatched agent.

> **User decision (2026-04-19):** Split consistency checks by dimension and dispatch multiple reviewers in parallel, one per dimension. Mirrors the `draft-reviewer:*` plugin's one-agent-per-aspect pattern.
> **Question asked:** Implied — follows the draft-reviewer architecture.

> **User decision (2026-04-19):** PLAN.md and RESULTS.md are both optional for small/iterative writing tasks. Full handoff-doc discipline only for major changes.
> **Question asked:** Implied by the workflow-mode discussion.

> **User decision (2026-04-22):** Refresh `domain/writing-skills` against `main`; prioritize the minimum-net-diff path. A semantic merge is acceptable, and rebase/reapply is also authorized if it proves cleaner during conflict resolution.
> **Question asked:** Which integration base and sync strategy should this branch use now that `main` has several major improvements?
> **Rationale:** The goal is to preserve the writing-vertical work while absorbing current `main` improvements with the smallest justified cumulative diff.

> **User decision (2026-04-22):** Undo the 2026-04-22 `main` sync. The prior merge misread `main`'s integration intent by carrying forward `skills/using-superRA/SKILL.md`'s `## Universal Principles` block even though `main` had intentionally removed it.
> **Question asked:** "Undo these merges. I don't think you fully capture the integration idea: in the main, we intentionally dropped the universal principles; in the current branch we still kept it. Why? can you go through the log and the handoff doc to explain the rationale"
> **Rationale:** Main's history shows the removal was deliberate de-duplication, not drift: `564021b` simplified skills by cutting duplicate protocol text, and `72c38e3` explicitly moved the four-principle content to its owning files (`main-agent.md`, workflow structure, `handoff-doc`, reviewer/integration references). The archived codex-compatibility handoff (`docs/plans/2026-04-17-codex-compatibility-plan.md`, Task 5 Step 3) also states that minimum-net-diff syncs should take `main` verbatim on shared files and re-thread only branch-specific additive surfaces. Reverting the sync restores that discipline.

> **User decision (2026-05-02):** Re-sync `domain/writing-skills` against `main` using strict take-main-verbatim discipline on shared surfaces. Main has advanced significantly since the rollback: `execution-workflow` was renamed to `implementation-workflow`; `refactor-and-integrate/references/{codebase-integration,drift-test-quality,merge-quality}.md` were deleted (drift-test content moved to the new `result-protection` skill); `semantic-merge` gained mode references (`standalone-merge.md`, `workflow-sync-author.md`, `workflow-sync-reviewer.md`); `using-superRA/references/codex-tools.md` was renamed to `codex-instructions.md`; `using-superRA/references/{direct-mode-implementer,direct-mode-reviewer}.md` were added; `integration-workflow` was restructured into Protect/Sync/Integrate/Document/Finish phases; `CLAUDE.md` was substantially rewritten around adaptive-composable-workflow design principles.
> **Question asked:** "sync this branch with the main"
> **Rationale:** Took main verbatim on every shared infrastructure file (CLAUDE.md, README.md, agents/*, hooks/merge-guard, all econ-data-analysis/*, agent-orchestration/*, handoff-doc/*, refactor-and-integrate/SKILL.md, semantic-merge/*, report-in-markdown/*, using-superRA/references/main-agent.md, worktree-data-sync/SKILL.md, plus all codex/* and tests/*). Re-threaded writing-vertical additions only into the surfaces main reshaped: added a writing row to `using-superRA/SKILL.md` Skill Inventory + Skill-Load Manifest add-on table; added a writing row to `planning-workflow/SKILL.md` Phase 1 vertical table; added writing notes to `integration-workflow/SKILL.md` §Protect (build + outline-stability substitutes for drift tests) and §When to Lighten (modes a/b/c skip the workflow); added writing rows to `skills/CATEGORIES.md` and `README.md` domain tables. Dropped `skills/execution-workflow/` (renamed) and the four deleted reference files. Refreshed stale references inside `skills/writing/` to point at the new structure (`execution-workflow` → `implementation-workflow`, `merge-workflow` → folded into `integration-workflow` Finish, `§Universal Principles` references rephrased generically since main moved that content to its owning files).

---

## Sync Map

**Base branch:** `main`
**Pre-sync merge base:** `addc9ca7fe1bdbedb080d92095facb649074c1e4`
**Synced base head:** `886fda8b6a7862a0a4af8ec7d30fd53ffed6fea3`
**Incoming range:** `addc9ca..886fda8`
**Sync commits:** `fde4751`, `7a4cf1a`, *(this correction commit)*
**Sync review status:** IMPLEMENTED (after one REVISE round)

### Branch Summary

**Incoming intent:** Substantial restructuring of superRA workflow scaffolding while this branch was idle: `execution-workflow` renamed to `implementation-workflow`; `integration-workflow` rewritten around five phases (Protect / Sync / Integrate / Document / Finish); `refactor-and-integrate` narrowed to codebase-coherence with drift-test content moved to a new dedicated `result-protection` skill (three references — `codebase-integration.md`, `drift-test-quality.md`, `merge-quality.md` — deleted); `semantic-merge` gained mode references (`standalone-merge.md`, `workflow-sync-author.md`, `workflow-sync-reviewer.md`); `using-superRA` lost the `## Universal Principles` block (content redistributed to owner files; `codex-tools.md` renamed to `codex-instructions.md`; `direct-mode-implementer.md` and `direct-mode-reviewer.md` added); `CLAUDE.md` substantially rewritten around adaptive-composable-workflow design principles. Codex named-agent generation, marketplace metadata, hook surfaces, and harness-compatibility tests advanced.

**Resolution thesis:** Strict take-main-verbatim on every shared infrastructure surface (the writing branch had no design intent for any of those files). Re-thread writing-vertical additions only into the surfaces main reshaped, in the spots where main's restructure left explicit hooks for new verticals. Drop the renamed/deleted artifacts. Refresh stale references inside `skills/writing/` so they point at main's current structure rather than the pre-restructure structure they were authored against. The full file/script impact map and user-decision log live in `SEMANTIC_MERGE.md` (entry titled "Semantic Merge Record — 2026-05-02").

### Sync Clusters

> **Sync cluster `cluster-1-shared-skills` (2026-05-02):** commits `fde4751`; paths `CLAUDE.md`, `README.md`, `agents/*`, `hooks/merge-guard`, `skills/{agent-orchestration,econ-data-analysis,handoff-doc,refactor-and-integrate,report-in-markdown,semantic-merge,worktree-data-sync}/...`, `skills/using-superRA/references/main-agent.md`, `.codex*/`, `tests/*`; affects no writing-skill tasks directly.
> **Incoming intent:** Adaptive-composable-workflow design refresh and Codex compatibility hardening across shared infrastructure.
> **Sync resolution:** Took main verbatim. Branch had no writing-vertical content in any of these files.
> **Integration context:** None — these surfaces are owned by main and do not carry writing-vertical surface area.
> **User decision:** None.

> **Sync cluster `cluster-2-routing-rethread` (2026-05-02):** commits `fde4751`; paths `skills/using-superRA/SKILL.md`, `skills/planning-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/CATEGORIES.md`, `README.md`; affects Task 6.
> **Incoming intent:** Restructure routing surfaces — `using-superRA` Skill-Load Manifest split into Generic + Domain add-on tables; `planning-workflow` Phase 1 vertical table is the routing surface for new domains; `integration-workflow` reorganized into Protect / Sync / Integrate / Document / Finish.
> **Sync resolution:** Took main's restructured surfaces verbatim, then added writing-vertical rows: domain row in `using-superRA/SKILL.md` Skill Inventory + Domain add-on row; `Writing` row in `planning-workflow/SKILL.md` Phase 1 vertical table noting that modes a/b/c skip the workflow; one §Protect sentence + one §When to Lighten bullet in `integration-workflow/SKILL.md` documenting that writing substitutes build + outline-stability for drift tests; writing rows in `CATEGORIES.md` Domain table and `README.md` Domain Skills table.
> **Integration context:** Task 6 Step 2 originally specified four Skill-Load Manifest rows (`planning-review`, `implementation`, `integration`, `documentation`) but main collapsed those into a single Domain add-on row composed with the Generic stage table. The actual implementation matches main's structure — Task 6 Step 2 wording is now describing the pre-restructure manifest shape and should be revised next time the task block is touched. Routing implementation itself is correct.
> **User decision:** Main re-sync (2026-05-02 §Decisions entry).

> **Sync cluster `cluster-4-correction-take-main-verbatim` (2026-05-02):** commits *(this correction commit)*; paths `.agents/**`, `.codex/INSTALL.md`, `.gitattributes`, `AGENT.md`, `GEMINI.md`, `docs/README.codex.md`, `docs/drafts/workflow-diagram.mmd`, `docs/plans/2026-04-{16,17,19,21}-*.md` (14 files), `docs/process-issues-2026-04-16.md`, `hooks/{autoload-superra,ensure-agent-orchestration,ensure-using-superra,exit-plan-mode,hooks-cursor.json,hooks.json,session-start}`, `skills/report-in-markdown/references/baseline-io.md`, `skills/using-superRA/references/{claude-tools,gemini-tools}.md`, `tests/hooks/*.sh`, `tests/structural-invariants.sh`; affects no writing-skill tasks.
> **Incoming intent:** Implicit. Where the branch had pre-merge drift from main on shared infrastructure (hook surfaces, harness adapter references, archived plans, agents-harness symlinks, etc.), main's state is the intended baseline.
> **Sync resolution:** For every divergent path that is NOT in the writing-vertical allowlist (writing skill, writing-references docs, PLAN/RESULTS/SEMANTIC_MERGE, five rethreaded routing surfaces): `git checkout main -- <path>` if main has it; `git rm <path>` if main does not. Brings post-merge `git diff --name-only main..HEAD` to a clean minimum-net-diff state — every surviving difference is now a legitimate writing-vertical artifact, a routing-rethread row, or a branch handoff doc.
> **Integration context:** Three concrete behavioral consequences resolved by this correction: (a) the three autoload hooks (`autoload-superra`, `ensure-using-superra`, `ensure-agent-orchestration`) are now wired in `hooks/hooks.json` again — runtime autoload of `superRA:using-superRA` would have been broken on this branch otherwise; (b) `.agents/skills/*` symlinks are restored — the agents-harness skill-discovery surface now matches main; (c) `skills/using-superRA/references/gemini-tools.md` no longer says "execution-workflow" (main renamed it; the silent retention had been a CRITICAL finding). See `SEMANTIC_MERGE.md` §"Semantic Merge Record — 2026-05-02 (correction commit)" for the full file/script impact map.
> **User decision:** None new — the original 2026-05-02 "sync this branch with main" intent is what this correction is fulfilling.

> **Sync review notes (2026-05-02, REVISE round 1, RESOLVED):**
> 1. [CRITICAL] Silent re-introduction of pre-rename `execution-workflow` text in `skills/using-superRA/references/gemini-tools.md`. — RESOLVED by `cluster-4`.
> 2. [CRITICAL] Take-main-verbatim rule applied selectively (~50 paths still carried branch-side state). — RESOLVED by `cluster-4`.
> 3. [MAJOR] `SEMANTIC_MERGE.md` File / Script Impact Map did not match the actual diff. — RESOLVED by appending the correction-commit record to `SEMANTIC_MERGE.md`.
> 4. [MAJOR] `PLAN.md §Decisions (2026-05-02)` and `RESULTS.md` understated the scope of pre-merge drift. — RESOLVED by this Sync Map update + the RESULTS.md correction note.

> **Sync cluster `cluster-3-stale-refs-in-writing` (2026-05-02):** commits `fde4751`; paths `skills/writing/SKILL.md`, `skills/writing/references/{workflow,integration,planning,collaboration}.md`; affects Tasks 1, 4, 5, 6 (their output files).
> **Incoming intent:** Implicit — main's renames and deletions mean any reference to `execution-workflow`, `merge-workflow`, `§Universal Principles`, or the deleted `refactor-and-integrate/references/` files inside the writing skill is now broken.
> **Sync resolution:** Refreshed stale references: `execution-workflow` → `implementation-workflow`; `merge-workflow` → folded into `integration-workflow` Finish (no separate skill); `§Universal Principles #N` references rephrased generically (the principles still hold, but the named anchor was removed when main redistributed the content); deleted-file pointer in `writing/references/integration.md` redirected to the skill-level `superRA:refactor-and-integrate`.
> **Integration context:** All resolved within the merge commit. No follow-on Integrate work needed for these references.
> **User decision:** None.

---

## Project Conventions

Walked at planning time (2026-04-19). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at b58c3fc): superRA contributor guidelines. Four load-bearing workflow principles (implementer–reviewer pair at every step, handoff docs are the auditable record, fast-early-strict-before-merge + semantic merges, autonomous with human in the loop); RA-framing; lean-agents-rich-references architectural pattern; DRY / composability / extensibility rules; roadmap for new verticals; §Skill Changes requires real-session testing and warns against editing tuned content (Red Flags tables, rationalization lists, severity protocols) on stylistic preference.
- `/AGENTS.md`: symlink to `/CLAUDE.md`.
- `/GEMINI.md`: mirror of `/CLAUDE.md` for Gemini harness.
- `/README.md` (HEAD at b58c3fc): plugin overview + skill inventory table. Lists Workflow / Domain / Utility / Meta categories and which skills belong to each.

### Module-level docs to walk on demand
- `skills/CATEGORIES.md` — authoritative skill categorization; writing skill must be added to the Domain section.
- `skills/econ-data-analysis/SKILL.md` + `skills/econ-data-analysis/references/*` — architectural template for the writing skill.
- `skills/using-superRA/SKILL.md` + `references/main-agent.md` — Skill Inventory and Skill-Load Manifest must be extended.
- `skills/handoff-doc/` — PLAN.md + RESULTS.md editing discipline (already loaded for this plan).
- `skills/planning-workflow/SKILL.md` — vertical routing table needs a writing row.
- `skills/integration-workflow/SKILL.md` + `skills/merge-workflow/SKILL.md` — needs a writing branch (build + outline-stability gate in place of drift tests).
- `skills/refactor-and-integrate/` — paired with writing's `references/integration.md`, no change expected.

### Not walked (not reachable from the planned diff)
- `Code/`, `Data/`, `Output/` — no such directories; this is a skill plugin, not an analysis repo.
- `docs/archive/` — out of scope.
- `hooks/` — merge-guard already handles semantic-merge routing; no change expected for the writing vertical.

---

## Task 1: Scaffold `skills/writing/SKILL.md` — Iron Law + §Three Concurrent Disciplines

**Depends on:** *(none)*
**Review status:** APPROVED (2026-04-19, integration re-review)
**Integration status:**

**Files:** `skills/writing/SKILL.md` (new)
**Input:**
- `skills/econ-data-analysis/SKILL.md` — architectural template (Iron Law + §Three Concurrent Disciplines + §Pitfalls + §Common Rationalizations anatomy); read end-to-end before drafting.
- `/Users/zhiyufu/.claude/plans/bubbly-wondering-parnas.md` — this project's own plan file; has the Iron Law final wording and the full §Three Concurrent Disciplines checklist.
- `/CLAUDE.md` §RA framing + §Design Principles — for the standalone-usability property and the reviewer-dispatch rule.
- `docs/writing-references/README.md` — big-picture orientation to why this skill exists.

**Output:** `skills/writing/SKILL.md` with frontmatter + RA framing + Iron Law + Common Rationalizations table + §Three Concurrent Disciplines (Preserve / Improve / Verify) + §Pitfalls pointer list + §Mode-selection pointer + §Key References. No referenced files exist yet — §Pitfalls and §Key References point forward.

- [x] **Step 1: Draft frontmatter + RA framing**

```markdown
---
name: writing
description: Use PROACTIVELY whenever editing, polishing, proofreading, consistency-checking, refactoring wording, or drafting technical sections of an academic paper or manuscript. Triggers include "polish this section", "proofread", "check consistency", "rename variable X to Y throughout", "write the methods section", "make the intro flow better", LaTeX / manuscript files touched, or any task that edits prose a human will read. Language/format-agnostic (LaTeX, Markdown, Quarto, plain text). Loaded by implementer and reviewer subagents at dispatch time when the stage touches writing, per superRA:using-superRA §Skill-Load Manifest.
---

## RA framing

You are assisting the researcher, not replacing them. The researcher's voice is the final voice. Your edits serve the researcher's intent — never your own preference.
```

- [x] **Step 2: Write the Iron Law**

Heading: `## The Iron Law: RESPECT THE AUTHOR'S INTENT`. Three clauses:

1. **Meaning-preserving edits only.** If a fix would change what the sentence/paragraph *says* (not just how it says it), stop and ask. Word-choice fixes, typo fixes, nominalization fixes, hedging fixes, broken-parallelism fixes, cross-reference fixes — all inside scope when the request covers style/polish/consistency. Rewrites that change the claim, emphasis, or argument — escalate.
2. **Scope-bounded edits only.** Edit what was asked. Structural or substantive changes beyond the request are *proposed* (in chat or PLAN.md), never performed unilaterally.
3. **In-progress work respected.** Unfinished paragraphs, inline TODOs, commented-out text, and visibly-being-edited sections are not touched unless the request names them.

**Explicit non-goal:** The Iron Law does NOT require preserving word choices, typos, passive-voice awkwardness, or weak diction. Fixing those is the RA's job. What it forbids is overriding *authorial intent*.

- [x] **Step 3: Write §Common Rationalizations table**

Heading: `## §Common Rationalizations`. Table columns `Rationalization | Reality`:

| Rationalization | Reality |
|---|---|
| "This whole paragraph is clearly better my way — I'll just rewrite it." | Scope + meaning violation. Propose the rewrite; do not perform it. |
| "The author probably meant X — I'll just write X." | Meaning violation. If you have to guess, escalate. |
| "This structure is obviously suboptimal, I should reorder the sections." | Scope violation. Structural changes are out-of-scope unless requested. |
| "The request said 'polish', so editing voice is fair game." | Voice ≠ diction. Fix nominalization / passive / hedging. Do not homogenize tone. |
| "The TODO marker is obviously going to be filled in the same way I'd fill it." | In-progress work violation. Leave TODOs for the author. |
| "Warnings are never important — compile-clean enough." | Verify violation. Triage each warning; escalate on doubt. |

- [x] **Step 4: Write §Three Concurrent Disciplines (Preserve / Improve / Verify) — shared checklist**

Heading: `## §Three Concurrent Disciplines: Preserve–Improve–Verify`. Walked top-to-bottom for every writing task. Severity markers `[BLOCKING]` / `[ADVISORY]`. Shared between implementer self-check and reviewer verification.

```markdown
### Preserve (scope + voice)
- [BLOCKING] No edits outside the requested scope
- [BLOCKING] Author's voice recognizable in the diff (diction, register, sentence-shape preserved)
- [BLOCKING] User's in-progress edits respected — TODOs, commented-out text, unfinished paragraphs not touched unless the request names them
- [ADVISORY] Style corrections applied minimally — smallest edit that fixes the identified problem

### Improve (clarity + structure, as requested)
- [BLOCKING] Edits address the specific problem named in the request
- [BLOCKING] For consistency-check tasks: every mismatch found is reported; none silently fixed beyond scope
- [ADVISORY] Sentence-level style rules applied where they fire (→ references/style-checklist.md)
- [ADVISORY] Paragraph-level flow checked (topic sentence, old→new order, transitions)

### Verify (compile + consistency)
- [BLOCKING] Document compiles after the edit (errors block; warnings triaged)
- [BLOCKING] No new cross-reference breaks (\ref, \cite, \eqref, label consistency)
- [BLOCKING] Numbers-in-text match numbers-in-tables if the edit touched quantitative claims
- [ADVISORY] Build warnings enumerated in handoff with ≤1-line rationale each
```

- [x] **Step 5: Write §Pitfalls pointer list + §Mode selection + §Key References**

```markdown
## §Pitfalls (operation-conditional)
- Sentence-level edits → references/style-checklist.md
- Structural / section drafting → references/structure-checklist.md
- Multi-dimensional consistency sweep → references/consistency/*.md (dispatch one reviewer per file in parallel; see references/workflow.md)
- Single-dimension consistency check → load the one relevant consistency/*.md
- Terminology / notation refactor → references/refactor-and-compile.md + consistency/terminology.md + consistency/notation.md
- Build / compilation fix → references/refactor-and-compile.md §Compile
- User-work detected in repo → references/collaboration.md

## §Mode selection
See references/workflow.md for the four modes (direct-edit / pure-review / review-edit-loop / full-workflow). Two hard rules: (1) reviewer dispatch is never skipped; (2) for multi-dimensional consistency work, dispatch reviewers in parallel, one per dimension.

## §Key References
- planning.md — scope inventory, PLAN/RESULTS optionality
- workflow.md — usage modes + dispatch rules
- style-checklist.md — sentence + paragraph rules
- structure-checklist.md — Pyramid Principle + section anatomy
- consistency/*.md — one file per review dimension (8 total)
- refactor-and-compile.md — safe find-replace + build gate
- collaboration.md — user-work respect patterns
- integration.md — pre-merge gates
```

- [x] **Step 6: Self-review against template + commit**

Self-check: (a) Iron Law protected by a Common Rationalizations table covering all three clauses? (b) Every §Three Concurrent Disciplines item has a severity marker? (c) §Pitfalls pointers list all eight consistency dimensions generically as `consistency/*.md`? Update RESULTS.md Task 1 with key findings (Iron Law final text, checklist item counts). Update PLAN.md: mark steps `[x]`, set `**Review status:** IMPLEMENTED`. Commit atomically: `skill: scaffold writing/SKILL.md with Iron Law + shared disciplines`.

---

## Task 2: `style-checklist.md` + `structure-checklist.md`

**Depends on:** Task 1
**Review status:** APPROVED (2026-04-19, integration re-review)
**Integration status:**

**Files:** `skills/writing/references/style-checklist.md` (new), `skills/writing/references/structure-checklist.md` (new)
**Input:**
- **For `style-checklist.md`:** LRS 1-1a (actions/nominalization), LRS 1-1b (character), LRS 2 (coherence/cohesion), LRS 3-4 (info flow) at `/Users/zhiyufu/Dropbox/PhD/writing_resources/LittleRedHouse/`; `docs/writing-references/Chaubey_Research_Writing.pdf` sections on sentence-level clarity.
- **For `structure-checklist.md`:** LRS 5, LRS 6 (introductions), LRS Arg 1–3 (argument structure), LRS triage in the same LittleRedHouse directory; `docs/writing-references/Chaubey_Research_Writing.pdf` sections on paper structure; Pyramid Principle web references listed in `docs/writing-references/README.md`; supporting economics-writing guidance (Brandeis, CGDev, IZA DP15057, Bellemare, Conversable Economist) — also in `docs/writing-references/README.md`.
- **Template:** `skills/econ-data-analysis/references/*.md` — study the how-to + gated-checklist layout and severity-marker discipline before drafting.

**Output:** two reference files, each a how-to + gated checklist. **Read the source PDFs first** — the task steps below are a condensed target, not a substitute for the originals.

- [x] **Step 1: Draft `style-checklist.md`**

Structure: §How-To (teaching content with before/after examples) + §Gated Checklist (severity-marked). Cover: nominalization (detect + move action to verb; keep nominalization for daisy-chain / after-strong-verb / field-term cases); noun-cluster avoidance (break clusters of 3+ modifying nouns); active voice with clear agency; single-hedge-per-claim rule; parallel structure for lists and comparisons; sentence-length guidance (~20–25 words); dangling-modifier check; old→new information flow inside paragraphs; topic-sentence-first; transition placement at paragraph start. Each rule cites LRS or Chaubey section.

- [x] **Step 2: Draft `structure-checklist.md`**

Structure: §How-To + §Gated Checklist. Cover: Pyramid Principle (governing idea first, MECE supporting points, horizontal logic — sibling points parallel in type, vertical logic — each level answers questions raised above); SCQ (Situation–Complication–Question) for intros; section-level anatomy (intro: motivation → gap → RQ → contribution → roadmap; methods: data + specification + identification; results: main first then robustness; conclusion: restate + limitations, no new findings); title-should-state-finding rule; table-of-contents paragraph at end of intro; "no mystery novel" front-loading rule.

- [x] **Step 3: Cross-link from SKILL.md §Pitfalls + self-review + commit**

Ensure SKILL.md §Pitfalls pointers resolve. Self-check: every rule has a ≤10-word name + 1–2 sentence explanation + source citation; severity markers on every checklist item; no "TBD" or "similar to". Update RESULTS.md Task 2. Commit: `skill: writing style + structure checklists`.

---

## Task 3: `consistency/*.md` — 8 dimension-scoped reference files

**Depends on:** Task 1
**Review status:** APPROVED (2026-04-19, integration re-review)
**Integration status:**

**Files:** `skills/writing/references/consistency/terminology.md`, `consistency/notation.md`, `consistency/cross-references.md`, `consistency/citations.md`, `consistency/numerical.md`, `consistency/math.md`, `consistency/argument-logic.md`, `consistency/code-paper.md` (all new)
**Input:**
- `~/.claude/plugins/draft-reviewer/agents/*.md` — seven subagent definitions (argument-logic-reviewer, citation-checker, code-paper-consistency, consistency-checker, mathematical-reviewer, proofreader, writing-clarity-reviewer). **Read the subagent that corresponds to your target dimension before drafting.** Each subagent's checklist is the spine for the corresponding `consistency/*.md`.
- `skills/econ-data-analysis/SKILL.md` §Three Concurrent Disciplines — severity-marker model (`[BLOCKING]` / `[ADVISORY]`).
- `docs/writing-references/Chaubey_Research_Writing.pdf` — for citation / argument / consistency norms in economics.

**Output:** eight small reference files, each sized for a single parallel reviewer to load. **The dimensions come from the draft-reviewer plugin; the superRA-style rule content is re-derived.**

- [x] **Step 1: Draft `terminology.md` + `notation.md` + `cross-references.md`**

- `terminology.md`: term-drift scan (variable-name drift, synonyms drift within a section, defined-term reuse discipline, glossary audit, treatment-group-vs-treatment-sample style mismatches). Severity-marked gated checklist + how-to.
- `notation.md`: math symbol consistency (bold/italic/hat conventions, subscript/superscript reuse, Greek-letter conflicts, abbreviations).
- `cross-references.md`: `\ref` / `\eqref` / `\cite` / label resolution; figure/table/section numbering consistency; undefined-reference scan.

- [x] **Step 2: Draft `citations.md` + `numerical.md`**

- `citations.md`: citation completeness (every non-common-knowledge claim cited); reference-citation matching (no orphan citations or uncited references); format consistency (author-year vs numbered); outdated-working-paper detection; foundational-reference audit.
- `numerical.md`: numbers-in-text vs numbers-in-tables (every number in prose traces to a table/figure cell); figure–caption–text alignment (caption matches what's shown and what prose claims); table caption accuracy; ±-sign / units / percentage-point vs percent consistency.

- [x] **Step 3: Draft `math.md` + `argument-logic.md` + `code-paper.md`**

- `math.md`: derivation step-by-step correctness; proof integrity; statistical-model correctness (iid assumptions stated where used, standard-error clustering named); notation stability across sections.
- `argument-logic.md`: claim–evidence mapping (every main claim traces to a cited source or an empirical finding in this paper); causal inference validity (identification assumption stated, alternative explanations addressed); overclaiming detection; hedging appropriate to evidence strength.
- `code-paper.md`: methodology match (code implements what paper describes); variable-definition alignment; sample-construction alignment; reproducibility from paper alone. Only loaded when the paper wraps an empirical code project.

- [x] **Step 4: Cross-link + self-review + commit**

Each file ≤ ~150 lines (fits in a single reviewer's context comfortably). Each has severity-marked checklist items. SKILL.md §Pitfalls pointer `consistency/*.md` resolves to all eight. Update RESULTS.md Task 3. Commit: `skill: writing consistency references (8 dimensions)`.

---

## Task 4: `refactor-and-compile.md` + `collaboration.md`

**Depends on:** Task 1
**Review status:** APPROVED (2026-04-19, integration re-review)
**Integration status:**

**Files:** `skills/writing/references/refactor-and-compile.md` (new), `skills/writing/references/collaboration.md` (new)
**Input:** plan file (refactor-and-compile + collaboration sections), LaTeX / Quarto / Markdown build conventions (generic)
**Output:** two operational reference files

- [x] **Step 1: Draft `refactor-and-compile.md`**

Two sections: §Refactor (safe context-aware find-replace — always preview matches, always confirm word-boundary, always check plural/singular forms, always check case variants; provide worked examples of false-positive matches like `estimate` matching inside `underestimate`) and §Compile (build commands per engine: `latexmk -pdf`, `quarto render`, `pandoc`; warning triage heuristics — ignore overfull-hbox by default, escalate undefined references, escalate missing citations; error escalation rules).

- [x] **Step 2: Draft `collaboration.md`**

Cover: detecting user's in-progress work (uncommitted edits via `git status`, inline TODOs, `\todo{}` macros, commented-out text, recently-modified hunks); respecting it (never touch lines the user is actively editing); when to ask (structural changes, any edit that would change the argument); how to frame proposed structural changes (show the current vs proposed outline; don't just do it); escalation patterns (escalate via `AskUserQuestion` when available, plain text otherwise).

- [x] **Step 3: Cross-link + self-review + commit**

Self-check: do the two files respect the one-source-of-truth principle (no duplication with style-checklist or consistency refs)? Severity markers present? Update RESULTS.md Task 4. Commit: `skill: writing refactor-and-compile + collaboration refs`.

---

## Task 5: `planning.md` + `workflow.md` — mode-heavy orchestration guidance

**Depends on:** Tasks 2, 3, 4
**Review status:** APPROVED (2026-04-19, integration re-review)
**Integration status:**

**Files:** `skills/writing/references/planning.md` (new), `skills/writing/references/workflow.md` (new)
**Input:** all prior references (to reference from workflow-mode descriptions), plan file
**Output:** two reference files — what a fresh orchestrator loads first on any writing task

- [x] **Step 1: Draft `planning.md`**

Sections: §Scope Inventory (who asked, what level of document, which sections, deadline) + §Task-Size Triage + §PLAN.md/RESULTS.md Decision Matrix. Decision matrix:

| Task shape | PLAN.md? | RESULTS.md? | Mode (see workflow.md) |
|---|---|---|---|
| Typo / one-sentence polish | No | No | Direct-edit |
| Single-aspect review (e.g., citations) | No | No | Pure-review |
| Multi-aspect consistency sweep | Optional | Optional | Pure-review + parallel reviewers |
| Iterative proofread of a section | Optional | No | Review-edit loop |
| Drafting a new section / major revision | Yes | Yes | Full workflow |
| Whole-paper review / pre-submission sweep | Yes | Yes | Full workflow |

- [x] **Step 2: Draft `workflow.md` — four modes + hard rules**

Four modes:
- **(a) Direct edit.** Orchestrator edits directly while in live conversation with the researcher, then dispatches an independent reviewer. Appropriate for tiny polishes, typo fixes, single-paragraph rewrites at the researcher's explicit request.
- **(b) Pure review.** No edits. Dispatch one or more reviewer agents in parallel, each loaded with one `consistency/*.md` (or `style-checklist.md` / `structure-checklist.md`). Report findings; the researcher decides what to act on.
- **(c) Review → edit → re-review loop.** Iterative. Each cycle is one reviewer dispatch → orchestrator adjudicates → orchestrator (or dispatched implementer) edits → fresh reviewer dispatch. Common for consistency sweeps and proofreading passes.
- **(d) Full workflow.** Plug into PLAN → IMPLEMENT → VALIDATE → INTEGRATE (`planning-workflow` → `execution-workflow` → `integration-workflow` → `merge-workflow`). Used only for major changes.

Two hard rules:
1. **Reviewer dispatch is never skipped.** In every mode — including direct-edit — the reviewer is a separately-dispatched agent. Self-review by the orchestrator is not a substitute.
2. **Parallel-dispatch multiple reviewers for multi-dimensional consistency work.** One reviewer per `consistency/*.md` file. Single message, multiple Agent-tool calls. Each reviewer is focused on its one dimension.

- [x] **Step 3: Cross-link + self-review + commit**

`workflow.md` references each `consistency/*.md` by name; `planning.md` references `workflow.md`. Update RESULTS.md Task 5. Commit: `skill: writing planning + workflow refs`.

---

## Task 6: `integration.md` + routing updates

**Depends on:** Tasks 1, 2, 3, 4, 5
**Review status:** APPROVED (2026-04-19, integration re-review)
**Integration status:**
**Sync impact:** Cluster `cluster-2-routing-rethread` reshaped the routing surfaces this task targets. Main collapsed the four Skill-Load Manifest stages this task specified (`planning-review`, `implementation`, `integration`, `documentation`) into a single Domain add-on row composed with the Generic stage table; `merge-workflow/SKILL.md` is now folded into `integration-workflow` Finish; `integration-workflow` is now Protect/Sync/Integrate/Document/Finish (not the old A/B/C/D shape this task's Step 3 referenced). The actual routing rows landed in this sync match main's structure — only the task-block wording is now describing a shape that no longer exists. Source: `PLAN.md ## Sync Map`.

**Files:** `skills/writing/references/integration.md` (new); **edits:** `skills/using-superRA/SKILL.md` (Skill Inventory + Skill-Load Manifest), `skills/planning-workflow/SKILL.md` (vertical table), `skills/integration-workflow/SKILL.md` (writing branch), `skills/merge-workflow/SKILL.md` (writing branch), `skills/CATEGORIES.md`, `README.md`
**Input:** `skills/econ-data-analysis/references/integration.md` (template), all prior writing references
**Output:** `integration.md` + routing diff across six files

- [x] **Step 1: Draft `integration.md`**

Pre-merge gates: (a) document builds clean on the merged state; (b) all `consistency/*.md` dimensions relevant to the edited sections pass; (c) voice preserved across the full diff (sample check — random 3 hunks, does the diff still sound like the author?); (d) scope respected (no edits outside the original request). Severity-marked shared checklist.

- [x] **Step 2: Routing updates — `using-superRA`, `planning-workflow`, CATEGORIES, README**

- Add `writing` row to `using-superRA/SKILL.md` §Skill Inventory (one-liner pointing at `skills/writing/SKILL.md`).
- Add four rows to §Skill-Load Manifest covering `planning-review`, `implementation`, `integration`, `documentation` stages in the writing domain.
- Add `writing` row to `planning-workflow/SKILL.md` Phase 1 vertical routing table (trigger: editing/polishing/proofreading/consistency/refactor/draft tasks).
- Add `writing` row to `skills/CATEGORIES.md` under Domain.
- Add `writing` row to `README.md` domain-skill table.

- [x] **Step 3: Routing updates — `integration-workflow` (merge-workflow N/A in this repo)**

- `integration-workflow/SKILL.md` Phase A: added writing-vertical branch — "build + outline-stability check" replaces drift tests for writing-only tasks; writing tasks that produce numbers get drift tests in addition. Points at `writing/references/integration.md`.
- `integration-workflow/SKILL.md` Phase D Step 3a: added writing-vertical post-merge verification note — document build + outline-stability in place of `run_all.sh` / `pipeline.jl` for pure writing tasks.
- **No separate `merge-workflow` skill exists in this repo** — merge/PR choreography is Phase D of `integration-workflow`. The PLAN.md Step 3 phrasing ("merge-workflow/SKILL.md") was an over-specification; the effective routing lives inside `integration-workflow` Phase D and the Phase D writing note covers the same concern.

- [x] **Step 4: Self-review + commit**

Self-check: every routing table has the new row; Skill-Load Manifest entries are consistent with writing's actual reference file names; no route leads to a nonexistent file. Update RESULTS.md Task 6. Commit: `skill: writing integration ref + routing updates`.

---

## Task 7: `CLAUDE.md` audit

**Depends on:** Task 1
**Review status:** APPROVED (2026-04-19, integration re-review)
**Integration status:**

**Files:** `/CLAUDE.md` (possibly edited)
**Input:** `/CLAUDE.md` §Design Principles and §Roadmap sections, the two 2026-04-19 memory entries `feedback_domain_skills_standalone.md` and `feedback_reviewer_dispatch_never_skipped.md`
**Output:** confirmation that CLAUDE.md states (a) "domain skills are usable standalone without the workflow scaffold" and (b) "reviewer dispatch is never skipped, even in standalone modes"; edit if either is missing/ambiguous

- [x] **Step 1: Read `/CLAUDE.md` §Design Principles + §Roadmap end-to-end and audit**

Record in RESULTS.md Task 7 whether properties (a) and (b) are already stated, partially stated, or absent.

- [x] **Step 2: If absent or ambiguous — amend**

Add a short paragraph under §Architectural pattern (or §Domain verticals) stating the standalone-usability property. Add a short clause to workflow principle #1 (or a dedicated note) stating that reviewer dispatch is never skipped across modes. Keep the additions concise — this is a cross-cutting correction, not a rewrite.

- [x] **Step 3: Commit**

If edits were made: commit separately with `docs: CLAUDE.md — standalone skill usability + reviewer-dispatch rule`. If no edits needed: note in RESULTS.md Task 7 that the properties were already traceable, mark task APPROVED without a commit. Update RESULTS.md Task 7.

---

## Task 8: Dogfood — three-mode verification

**Depends on:** Tasks 1, 2, 3, 4, 5, 6, 7
**Review status:**
**Integration status:**

**Files:** no code/skill edits expected (only adjustments if dogfood surfaces bugs)
**Input:** a real manuscript section (user-nominated) or a suitable sample
**Output:** three dogfood reports in RESULTS.md Task 8; any adjustments to references committed separately

- [ ] **Step 1: Mode (a) — direct edit**

Pick a trivial polish task ("fix a typo" or "tighten this sentence"). Invoke the writing skill directly (no planning-workflow wrapper). Orchestrator performs the edit; dispatches one reviewer loaded with `writing/SKILL.md` + `style-checklist.md`. Verify: Iron Law fires if a scope violation is injected; reviewer returns APPROVE or REVISE per severity.

- [ ] **Step 2: Mode (c) — review → edit → re-review loop**

Pick a section with known inconsistencies (or inject some). Dispatch two parallel reviewers: one loaded with `consistency/terminology.md`, one with `consistency/cross-references.md`. Orchestrator adjudicates findings, edits, re-dispatches fresh reviewers. Verify: parallel dispatch actually runs in parallel; each reviewer stays scoped to its dimension; iteration terminates on APPROVE.

- [ ] **Step 3 (optional): Mode (d) — full workflow**

Only if a real drafting task is available. Run a small section through `planning-workflow` → `execution-workflow` → `integration-workflow` with the writing vertical. Verify routing works end-to-end.

- [ ] **Step 4: Adjust + commit adjustments**

Any reference that didn't fire correctly gets a small fix. Each fix is its own commit with a message naming the dogfood observation that prompted it. Update RESULTS.md Task 8 with the three dogfood reports. Mark task APPROVED when all three modes pass (or (d) is skipped with justification).
