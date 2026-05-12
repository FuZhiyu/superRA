# Audience Awareness — superRA:writing Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. Use `skill-creator` and the repo-root `CLAUDE.md` for every step that touches `skills/*` (we are editing the writing skill itself — see `CLAUDE.md §Skill Authoring Guidelines`). Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** Teach agents in the `superRA:writing` skill to maintain the conversation/document boundary by building the audience model upstream — before any edit — and to use line-level marker detection as the sentence-scoped safety net.

**Methodology:** Two-edit split. The principle and upstream protocol go in `skills/writing/SKILL.md` (always loaded, so every Review / Polish / Draft task carries the discipline regardless of which references load). The line-level marker families, line-by-line scan protocol, and replacement patterns go in `skills/writing/references/style.md` (loaded by Polish and Draft, and by Review-with-style-scope). A history entry in `skills/writing/CLAUDE.md` records the design choice. The rule is framed around any audience-bound document — academic paper is the primary case, but the principle reads on working-paper notes, slide decks, replication READMEs, and referee responses.

**Conventions:**

- One paragraph per line in all prose written into skill files and handoff docs (no hard wrap inside paragraphs). User preference confirmed in this session.
- Examples in the new SKILL.md / style.md sections stay paper-flavored (academic papers are the canonical case for this skill); the marker families themselves do not name the document type.
- All three edits land in one atomic commit — one concern per `CLAUDE.md §Contributor Discipline`.

**Output:**

- `skills/writing/SKILL.md` — new top-level section `## Write to the reader, not the conversation`, placed between `## Preserve substance, polish prose` and `## Before you start`.
- `skills/writing/references/style.md` — new section `### Audience: write to the reader, not the conversation` leading §How-To; one new bullet in §Gated Checklist Sentence-level rules.
- `skills/writing/CLAUDE.md` — appended history section `## Audience awareness as an upstream audience-model discipline`.

**Expected Results / Hypotheses:** A fresh agent invoked in any of the three modes (Review / Polish / Draft) on a paper-like fragment will (a) elicit or assume the audience model before editing, (b) detect and classify all four families of leakage when present, (c) leave the §Do NOT exceptions alone. The work is teaching prose, not code — there are no quantitative results to predict.

**Sensitivity Analysis:** Two-pronged check at verification time — over-firing (false positives on §Do NOT exceptions) and under-firing (failure to detect any of the four families). Both checked on constructed LaTeX fragments at the verification step.

**Pipeline:** None — three text edits to three skill files, manually applied via Edit. No multi-script pipeline.

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on the required domain gate + plan (`planning-workflow` Phase 2)
- [x] **Execution complete** — all tasks `APPROVED`, pipeline reproducible (`implementation-workflow` Step 3)
- [x] **Drift tests created** — drift tests passing on baseline (`integration-workflow` Protect) — *skipped per user decision 2026-05-11: skill prose is git-tracked; prose-drift safeguards add little over git history.*
- [ ] **Integrated** — integration reviewer `APPROVED` on `BASE_HEAD_SHA..HEAD` after Sync (`integration-workflow` Integrate)
- [ ] **Docs finalized** — RESULTS.md matured, project docs audited, doc-reviewer `APPROVED` (`integration-workflow` Document)
- [ ] **Finished** — branch landed locally, PR opened, or requested cleanup completed (`integration-workflow` Finish)

---

## Project Conventions

Walked at planning time (2026-05-11). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at 178c53d): Contributor guide for superRA internals. Treat skill / agent edits as skill creation (load `skill-creator` first). Read owning files before editing; change one concern at a time; describe the problem in the commit message; verify behavior, not just prose. Design philosophy: adaptive and composable workflows over rigid contingency trees, mechanisms over scenario branches, lean SKILL.md routing to references, gated checklists with `[BLOCKING]` vs `[ADVISORY]` distinction, severity tags only on real verdict-determining gates. Ownership table fixes one source of truth per concern. The §Teach the Protocol, Don't Prescribe Each Action gate (DRY + Necessity tests) is the line-by-line discipline for every instruction added under `skills/*` or `agents/*` — paraphrases of authoritative content, "here is what you will receive" descriptions, default-reminder lines, and wrapper instructions around canned content are anti-patterns.
- `/AGENT.md`, `/AGENTS.md`: aliases for `/CLAUDE.md`.
- `/README.md`: user-facing product description; out of scope for this plan (no edits to it).

### Module-level docs walked
- `skills/writing/CLAUDE.md` (HEAD at 178c53d): Records the writing skill's history of design decisions. Loaded only by contributors editing the skill (not at runtime). Top-level design choices already recorded: mode-not-phase routing, Preserve-substance-polish-prose, additive-rules framing, load-as-authority-grant for structural edits, TODO-as-task / DO-NOT-EDIT-as-hands-off, intent comments live in file not chat, fix-tier vocabulary shared between review and polish, polish-mode symmetric over-/under-editing framing. The history file is where new design choices are recorded as one short section per decision; Edit 3 of this plan appends one such section.
- `skills/writing/SKILL.md` (HEAD at 178c53d): Three-mode routing (Review / Polish / Draft); shared knowledge files (style, structure, eight consistency dimensions, refactor-and-compile, integration); one principle (Preserve substance, polish prose); additive-rules framing (`Silence on a concern is not permission to ignore it`). Before-you-start: classify mode, inspect in-flight author work, inline-directive convention, intent comments. Standalone-by-default with optional coupling to superRA workflows. Edit 1 of this plan adds one new section between `## Preserve substance, polish prose` and `## Before you start`.
- `skills/writing/references/style.md` (HEAD at 178c53d): Sentence- and paragraph-level heuristics — actions in verbs, old→new info flow, single-hedge-per-claim, active voice with clear agency, parallel structure, noun-cluster avoidance, sentence length, dangling modifiers, paragraph-level rules (topic sentence first, one idea per paragraph, transitions at start, first-sentence link), precision of reference, clarity heuristics. Each section: Principle → Detection trick → Before / after → Do NOT enforce when. Gated Checklist at file end walked by Polish self-check, Draft self-check, and Review's gated walk. Edit 2 of this plan inserts a new section as the first heuristic under §How-To and appends one bullet to §Gated Checklist Sentence-level rules.

### Not walked (not reachable from the planned diff)
- `skills/writing/references/polish.md`, `draft.md`, `review.md`, `structure.md`, `integration.md`, `refactor-and-compile.md`, `long-form-review.md`, `consistency/*` — these reference `style.md §Gated Checklist` via existing pointers; the new bullet is picked up automatically by `Polish self-check`, `Draft self-check`, and Review's style-scoped walk. No edits needed.
- `skills/*` for other domains, `agents/*`, `.codex/*`, `README.md`, harness adapters — out of scope.

## Decisions

> **User decision (2026-05-11):** Proceed with integration.
> **Question asked:** Step 4 completion menu — proceed with integration / keep branch as-is / change the plan / discard. All tasks APPROVED and Execution complete flipped.

> **User decision (2026-05-11):** Skip drift tests entirely; flip `Drift tests created` with a note that skill prose is git-tracked.
> **Question asked:** Protect step — skip drift tests / lightweight presence test / presence + structural test. Work is skill prose, so prose-drift safeguards differ from paper or code drift tests.

---

### Task 1: Edit SKILL.md, style.md, and writing/CLAUDE.md for audience-awareness rule
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** APPROVED
**Final diff self-check:** `git diff 8c3db7d..HEAD -- skills/writing/SKILL.md skills/writing/references/style.md skills/writing/CLAUDE.md`; three additive sections (SKILL.md `## Write to the reader, not the conversation`; style.md `### Audience: write to the reader, not the conversation` + one new bullet in §Gated Checklist Sentence-level rules; writing/CLAUDE.md `## Audience awareness as an upstream audience-model discipline`); suspicious-hunk class is `skills/*` instruction edits — every new line shapes behavior the agent would not produce by default (principle + upstream protocol in SKILL.md, four marker families + replacement patterns + §Do NOT exceptions in style.md, split-rationale in writing/CLAUDE.md history), no paraphrase of authoritative content elsewhere per repo-root CLAUDE.md §Teach the Protocol DRY+Necessity tests.

**Script:** N/A (manual edits via `Edit` tool on three files)
**Input:** `skills/writing/SKILL.md`, `skills/writing/references/style.md`, `skills/writing/CLAUDE.md` (current HEAD)
**Output:** Same three files, modified; one atomic commit on branch `domain/writing-skills` titled `skills: add audience-awareness rule to writing skill`.

- [x] **Step 1: Edit `skills/writing/SKILL.md` — add `## Write to the reader, not the conversation` between `## Preserve substance, polish prose` and `## Before you start`.**

Insert verbatim (each paragraph one unwrapped line in the file):

```markdown
## Write to the reader, not the conversation

Every document this skill touches has an audience that is distinct from the editing conversation. The audience has access to the document itself, plus the background knowledge appropriate to the venue — a journal reader knows the field's standard methods, a slide-deck audience knows the talk's framing, a replication-package reader knows the paper. They have not seen the editing conversation, the codebase, prior drafts, the project's working vocabulary, or any artifact the author and the agent are using to coordinate. Anything that addresses a different audience, references the editing process, or names artifacts outside the audience's reach does not belong in the document. This holds for academic papers (the primary case for this skill) and for any other audience-bound document the skill polishes, drafts, or reviews — working-paper notes, slide decks, replication READMEs, referee responses.

**Before any edit, build the audience model.** Two questions answered explicitly, in your head or in the conversation, before the first character changes:

1. **Who is the audience?** Match the venue: a top-five finance journal reader, a working-paper reader on SSRN, a conference talk audience, the replication-package user, the editor reading a response letter. The venue fixes the conventions — tolerated jargon, expected formality, cite density, level of detail.
2. **What is in the audience's information set?** Concretely: the document itself, in its current draft state; works the document cites (which the audience can look up); background knowledge appropriate to the venue. *Not* in the set: the editing conversation, the repo, the project's working vocabulary, prior drafts the audience has not seen, any classification or label that exists only in the author's or agent's working files.

**Then write or edit against the set.** As each sentence is drafted or polished, check: every term used is either in the set or is defined in the document at first use; every reference (artifact, table, citation, section pointer) resolves from the set; every temporal cue is internal to the document's narrative ("we next turn to robustness"), not external to the editing process ("the table now defines"). A term that fails this check is conversation vocabulary, not document vocabulary — either define it in the document or replace it with the standard term the audience knows.

The line-level marker families and replacement patterns that operationalize this principle for sentence-level editing live in `references/style.md §Audience: write to the reader, not the conversation`. They are the safety net; the audience model is the primary discipline.
```

- [x] **Step 2: Edit `skills/writing/references/style.md` — insert new section as the first heuristic under §How-To, and append one bullet to §Gated Checklist Sentence-level rules.**

Insert as first heuristic under §How-To (before the existing `### Actions in verbs (LRS 1-1a)` section):

```markdown
### Audience: write to the reader, not the conversation

**Principle.** Stated in `SKILL.md §Write to the reader, not the conversation`. Build the audience model and their information set before editing; treat the markers below as the safety net for lines where the upstream check did not catch a leak. Examples below use academic papers (the skill's primary case), but the marker families read on any audience-bound document.

**Detection trick — four marker families.** For every line in scope, walk the families in order; if a line matches, classify by family and rewrite per the replacement pattern. Do not generalize from one marker to a paragraph-level rewrite — the rule is line-level.

1. **Editing-history temporal markers.** `now`, `currently`, `at this point`, `previously`, `the new`, `the updated`, `the revised`, `as discussed`, `as we mentioned`. The audience has no "before"; the marker is relative to a timeline they do not share. (Exception: section transitions like *we now turn to …* are conventional discourse, not edit-history references — see §Do NOT.)
2. **Audience self-references.** `paper-facing`, `internal table`, `for the paper`, `internally`, `behind the scenes`, `the version shown to readers`, `the public version`. Naming an audience implies a second audience; that distinction is internal to the editing process, not the document.
3. **Process-internal artifacts.** Repo paths (`input/country_information.csv`), input-file column names (`the AE column`), branch names, script names, variable names that do not appear in the document, internal classification labels. The audience has no repo. Published replication packages are referenced in the data/code availability section by public identifier, not inline by file path.
4. **Conversation jargon used as document vocabulary.** Working terms the author and agent have been using to communicate that are not defined in the document — project nicknames, draft-stage shorthand, glossary terms that live in chat or in a working doc but not in the manuscript / deck / README. Test against the audience's info set (`SKILL.md §Write to the reader, not the conversation`): if the term is not in the set and not defined at first use in the document, it is conversation vocabulary.

**Replacement patterns.**

- *Editing-history temporal marker.* Before: *The table now defines coreAE as …* → After: *Table 2 defines coreAE as …*
- *Audience self-reference.* Before: *In the paper-facing table, we define …* → After: *Table 2 defines …*
- *Process-internal artifact.* Before: *Throughout, AE refers to the IMF World Economic Outlook "Advanced Economies" classification, applied via the `AE` column of `input/country_information.csv`.* → After: *Throughout, AE refers to the IMF World Economic Outlook "Advanced Economies" classification.*
- *Conversation jargon.* Either define the term once in the document's own voice at first use, or replace with the standard term the audience knows. If neither is appropriate (the term has no document-side equivalent and is not worth defining), the sentence is reaching outside the audience's set and the surrounding argument needs rewriting, not patching — surface as `authorial` per §Triage.

**Do NOT rewrite when:**

- The temporal cue is internal to the document's own narrative ("we now turn to robustness", "the next subsection extends this") — these are conventional discourse markers.
- The artifact reference is to a public, citable resource that the document's data/code availability section points to. (Even then, the inline reference is the public identifier, not a local repo path.)
- The term is a genuine field term of art the venue's audience knows, not conversation jargon. Test: would a typical reader / viewer / user at this venue recognize the term without the document defining it?
```

Append to §Gated Checklist Sentence-level rules (after the existing `- Ambiguous pronouns (this, it) given an explicit antecedent noun.` bullet):

```markdown
- Audience awareness: line scanned against the four marker families (editing-history temporal, audience self-reference, process-internal artifact, conversation jargon) per §Audience. Term-level check references the audience's information set per `SKILL.md §Write to the reader, not the conversation`.
```

- [x] **Step 3: Edit `skills/writing/CLAUDE.md` — append new history section `## Audience awareness as an upstream audience-model discipline` after the existing `## History` section.**

Insert at end of file (each paragraph one unwrapped line):

```markdown
## Audience awareness as an upstream audience-model discipline

(2026-05-11.) `SKILL.md §Write to the reader, not the conversation` carries the principle and the upstream protocol — identify the audience, build their information set, check every term and reference against it before editing. The principle is in `SKILL.md` (not in a reference) because it is unconditional: every Review, Polish, and Draft task starts the same way, and `style.md` is not loaded by every Review scope. `style.md §Audience` carries the line-level marker families and replacement patterns; it is the safety net for sentence-scoped editing when the upstream check did not catch a leak. The split is the same pattern used for "Preserve substance, polish prose" (principle in SKILL.md, operational guidance in references).

The rule is framed around "any audience-bound document," not solely the academic paper, even though academic papers are the skill's primary case. The deliberate generalization keeps the principle usable when the skill polishes a slide deck, a working-paper note, a replication-package README, or a referee response. Examples in both SKILL.md and `style.md §Audience` stay paper-flavored so the canonical case reads cleanly; the marker families themselves do not name the document type.

Future contributors tempted to collapse the rule into a single location should re-check: collapsing into `style.md` would lose the Review-scope coverage that does not load style; collapsing into SKILL.md would force every Review agent to load the marker families even when style is not in scope. Future contributors tempted to re-narrow the rule to "academic paper" specifically should re-check which non-paper documents the writing skill is being invoked on; the breadth is intentional and cheap.
```

- [x] **Step 4: Validate — verify the result, document, commit.**

Validate the three edits against repo-root `CLAUDE.md §Teach the Protocol, Don't Prescribe Each Action` (DRY + Necessity). For each new line added, confirm it shapes behavior the agent would not already produce. Also confirm: no paraphrase of authoritative content (the four marker families are new content, not restatements); no "here is what you will receive" descriptions; no default-reminders. Run `git status` and `git diff --stat` — only the three target files modified, no others touched. Update PLAN.md (mark steps `[x]`, set Review status: IMPLEMENTED). Update RESULTS.md (record what landed, with paths and one-line summaries per file). Commit with title `skills: add audience-awareness rule to writing skill`, body explaining the conversation/document-boundary failure mode and the SKILL.md / style.md split. One atomic commit covering all three files + PLAN.md + RESULTS.md.

### Task 2: Verify the rule on constructed examples
**Depends on:** Task 1
**Review status:** APPROVED
**Integration status:** APPROVED
**Final diff self-check:** `git diff 8c3db7d..HEAD -- PLAN.md RESULTS.md`; no surviving hunks in `skills/writing/**` for this task (verification only — no skill-file change required, exactly the design intent); surviving change classes are RESULTS.md §Task 2 verification record (positive detection / no-over-firing / audience-model elicitation / authorial-surface report) plus PLAN.md Task 2 step `[x]` flips, status transitions, and §Decisions log entries; no suspicious hunks (no `skills/*` instruction edits in this task's diff).

**Script:** N/A (Polish-mode dispatch on a constructed LaTeX fragment; results recorded in RESULTS.md)
**Input:** One constructed LaTeX fragment combining all three concerns (positive detection, no over-firing, audience-model elicitation) at `/tmp/audience-awareness-verification/draft.tex`. Bundled into one fragment per `agent-orchestration §Workload Balancing` Tier 2 (shared context, same skill load) rather than three separate dispatches as originally planned — the bundling does not weaken the test because each concern lives in its own intent-tagged paragraph.
**Output:** Verification record in RESULTS.md §Task 2.

- [x] **Step 1: Construct the test fragment.**

Three intent-tagged paragraphs in `/tmp/audience-awareness-verification/draft.tex`:

- Paragraph 1 — positive detection. Contains all four marker families: process-internal artifact (`AE column of input/country_information.csv`), audience self-reference (`In the paper-facing table`), editing-history temporal (`The table now defines`), conversation jargon (`We use the AE/EM cut … the EM-versus-AE split follows the same convention`).
- Paragraph 2 — no over-firing. Contains all three §Do NOT exceptions: conventional discourse transition (`We now turn to robustness`), public citable resource (Zenodo DOI), genuine field term of art (`heteroskedasticity-robust standard errors`).
- Paragraph 3 — audience-model elicitation. One short sentence with no leakage but ambiguous venue (`This paper investigates the AE/EM sovereign-spread puzzle`).

- [x] **Step 2: Dispatch a Polish-mode implementer on the fragment with the updated skill files loaded.**

Dispatched `superRA:implementer` with `Stage: implementation` on `/tmp/audience-awareness-verification/draft.tex`, instructed to operate in writing-skill Polish mode (load `references/polish.md` + `references/style.md`) and report the four-question record (which marker family per edit; which §Do NOT exception fired on skipped edits; what audience model was built before editing; what was surfaced as `authorial` per §Triage rather than applied silently).

- [x] **Step 3: Verification results recorded in RESULTS.md §Task 2.**

Outcomes detailed in RESULTS.md §Task 2. Summary:

- Detection: 4 of 4 marker families detected and classified correctly; all four replacement patterns matched the proposed `style.md §Audience` patterns.
- No over-firing: all three §Do NOT exceptions correctly skipped (conventional discourse, public citable resource, genuine field term of art); also kept `IMF World Economic Outlook` as an additional public citable resource not in the named test set.
- Audience model: built explicitly before editing — venue (empirical macro-finance working paper or top finance-journal submission) and information set articulated for the ambiguous paragraph 3 before any edit.
- `authorial` surface: paragraph 3's topic-vs-contribution gap surfaced as `authorial` per §Triage rather than silently rewritten — exactly the design intent.

No edits to the three skill files were needed; the rule wording is correct as committed in `dfe87bc`.

- [x] **Step 4: Validate — verify the result, document, commit.**

RESULTS.md §Task 2 populated with the four-question record from the dispatch. PLAN.md Task 2 updated (steps `[x]`, Review status `IMPLEMENTED`). Verification fragment cleaned up from `/tmp/audience-awareness-verification/` after the commit. Commit title `verify: audience-awareness rule on constructed fragments`.
