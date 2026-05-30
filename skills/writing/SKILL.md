---
name: writing
description: Use PROACTIVELY whenever reviewing, polishing, proofreading, consistency-checking, refactoring wording, or drafting prose a human will read in an academic paper or manuscript. Triggers organized by mode. Review — "review §X", "check my citations", "find issues in this draft", "consistency sweep". Polish — "polish §X", "tighten this paragraph", "proofread", "clean up these edits", "apply these review findings", "rewrite for clarity". Draft — "draft the methods section", "write up the results from these notes". Language/format-agnostic (LaTeX, Markdown, Quarto, plain text). Loaded by implementer and reviewer subagents at dispatch time when the stage touches writing, per `superRA:using-superRA` §Skill-Load Manifest.
user-invocable: true
---

# Academic Writing

Three working modes — **Review**, **Polish**, **Draft** — share a knowledge base (style, structure, eight consistency dimensions, refactor-and-compile) and one principle.

## These rules are additive

You already know how to write, proofread, replace awkward wording, fix grammar and typos, and calibrate tone to context. This skill does not retrain that — it adds the discipline academic writing on shared author drafts needs: what counts as substance vs prose, how to read the author's in-flight signals (TODOs, DO NOT EDIT, intent comments), the eight consistency dimensions, when to ask vs propose vs perform. Apply both. The rules below constrain or redirect edits where they apply; everywhere else, polish, proofread, and adjust as you normally would. **Silence on a concern is not permission to ignore it** — anything not named here is your call, made with your general writing competence.

## Preserve substance, polish prose

**Preserve** — the argument, the logic, the section/paragraph structure, the technical claims, the author's intent, the tone. These are sovereign; if a contemplated edit would change any of them, stop and ask.

**Polish freely** — wording, sentence structure, clarity, parallelism, hedging calibration, flow, mechanical correctness. This is the editing target.

**Restructuring is out of scope** unless the request authorizes it (and `references/structure.md` is loaded — see Mode routing).

## Write to the reader, not the conversation

Every document this skill touches has an audience that is distinct from the editing conversation. The audience has access to the document itself, plus the background knowledge appropriate to the venue — a journal reader knows the field's standard methods, a slide-deck audience knows the talk's framing, a replication-package reader knows the paper. They have not seen the editing conversation, the codebase, prior drafts, the project's working vocabulary, or any artifact the author and the agent are using to coordinate. Anything that addresses a different audience, references the editing process, or names artifacts outside the audience's reach does not belong in the document. This holds for academic papers (the primary case for this skill) and for any other audience-bound document the skill polishes, drafts, or reviews — working-paper notes, slide decks, replication READMEs, referee responses.

**Before any edit, build the audience model.** Two questions answered explicitly, in your head or in the conversation, before the first character changes:

1. **Who is the audience?** Match the venue: a top-five finance journal reader, a working-paper reader on SSRN, a conference talk audience, the replication-package user, the editor reading a response letter. The venue fixes the conventions — tolerated jargon, expected formality, cite density, level of detail.
2. **What is in the audience's information set?** Concretely: the document itself, in its current draft state; works the document cites (which the audience can look up); background knowledge appropriate to the venue. *Not* in the set: the editing conversation, the repo, the project's working vocabulary, prior drafts the audience has not seen, any classification or label that exists only in the author's or agent's working files.

**Then write or edit against the set.** As each sentence is drafted or polished, check: every term used is either in the set or is defined in the document at first use; every reference (artifact, table, citation, section pointer) resolves from the set; every temporal cue is internal to the document's narrative ("we next turn to robustness"), not external to the editing process ("the table now defines"). A term that fails this check is conversation vocabulary, not document vocabulary — either define it in the document or replace it with the standard term the audience knows.

The line-level marker families and replacement patterns that operationalize this principle for sentence-level editing live in `references/style.md §Audience: write to the reader, not the conversation`. They are the safety net; the audience model is the primary discipline.

## Project Conventions in the handoff doc / CLAUDE.md

A paper's writing-side conventions are paper-specific choices among defensible alternatives — choices a fresh agent would get wrong if not written down. Recording them once prevents re-inference and silent re-decision every session.

**Where they live (lifecycle ladder, ordered by permanence).** `PLAN.md` (workflow-scoped) → `CLAUDE.md` (project-permanent). Long-form review retrofits a PLAN.md around the user's existing draft; reviewers then write findings as task-local review notes. Writing-side conventions live in the `## Project Conventions` header of whichever PLAN.md is in play; when no handoff doc is in play, return the inventory as a conversation reply. Promote up the ladder when the user signals durability — same pattern as theory-modeling's per-task ledger → `PLAN.md` Notation Conventions promotion (`theory-modeling/SKILL.md §Documentation and handoff`).

**What writing contributes (rows alongside data and modeling contributions).**

| Convention | What's recorded | Acid test |
|---|---|---|
| Terminology | Canonical term per key concept where synonyms exist, with first-use location. | Fresh agent would pick a synonym. |
| Abbreviations | Defined short forms, with the spell-out and first-use location. | Fresh agent would re-spell or pick a different acronym. |
| Citation format | Narrative vs parenthetical (`\citet` vs `\citep`), "et al." threshold, multi-citation separator, e.g./i.e./cf. usage. | Fresh agent would guess between conventions. |
| Numerical formatting | Rounding precision, SE/CI delimiter, units, percent-vs-pp convention. | Fresh agent would guess between conventions. |
| Cross-reference phrasing | "Section 3" vs "§3" vs "Sec. 3"; "Table 1" vs "Tab. 1"; label prefixes (`fig:`, `tab:`, `eq:`). | Fresh agent would guess. |
| Voice and tense | "We" vs passive; past for procedure, present for results, or the paper's chosen mix. | Fresh agent would mix conventions inconsistently across sections. |
| Prose typography around notation | Bold/italic/hat conventions for vectors, estimates, random variables when they appear in prose; quote style; em-dash style. | Fresh agent would guess between conventions. |

**Excluded:** math notation (symbol → meaning, equation numbering) is owned by `theory-modeling`'s Notation Conventions table — a sibling subsection inside `## Project Conventions`; section/caption capitalization and page-layout macros are venue / template territory.

**Soft trigger.** On the first long-form review or first draft pass against a paper with no recorded writing-side conventions, inventory them and record them in the relevant handoff doc / CLAUDE.md before substantive editing. Routine polish and single-lane review do not auto-scan.

**Scanning is unspecified.** Agents inventory using the detection language in `references/consistency/*.md` and `references/style.md`; there is no separate scan procedure.

## Before you start

1. **Classify the request into a mode** before reading the file — the mode determines what to load (see Mode routing).
2. **Inspect in-flight author work** with `git status` / `git diff` before editing; an unstaged diff often *is* the polish target.
3. **Inline-directive convention.** `TODO`, `% TODO:`, `\todo{...}`, `[fill in]`, `??`, `XXX`, and crude or placeholder phrasing in the author's draft are **work assigned to the agent** — clean them up inside scope. The author signals leave-alone with an explicit `DO NOT EDIT` (or equivalent hands-off marker) on the line or block; lines so marked are off-limits even within scope.
4. **Intent comments.** Paragraphs in `.tex` / `.md` / `.qmd` carry their purpose as a comment on the line above (`% intent: …` / `<!-- intent: … -->`). Draft mode writes them first from the user's request; polish mode preserves them but never invents them — intent comes from the author, not from agent inference. Full convention in `polish.md §Intent comments` and `draft.md §Intent comments`.

## Mode routing

Loading the listed reference is the authority grant — if `structure.md` is not loaded, structural edits are out of scope by construction.

| Request shape | Mode | Load |
|---|---|---|
| "Review §X for clarity / consistency / structure"; "Check my citations"; "Find issues in this draft" | **Review** | `references/review.md` + relevant knowledge file(s) |
| "Polish §X"; "Tighten this paragraph"; "Clean up these edits"; "Proofread"; "Apply these review findings" | **Polish (sentence/paragraph scope)** | `references/polish.md` + `references/style.md` |
| Polish that explicitly authorizes restructuring ("restructure §X"; "reorganize the intro"; "strengthen this argument") | **Polish (structural scope)** | `references/polish.md` + `references/style.md` + `references/structure.md` |
| "Draft the methods section"; "Write up the results from these notes" | **Draft** | `references/draft.md` + `references/structure.md` + `references/style.md` |

## Knowledge files

| File | Load when |
|---|---|
| `references/style.md` | Sentence- or paragraph-level edits; language/style review; every Polish and Draft self-check. |
| `references/structure.md` | Structure review, drafting a section, or polish that authorizes restructuring. |
| `references/consistency/*.md` (8 dimensions: terminology, notation, cross-references, citations, numerical, math, argument-logic, code-paper) | Review or polish targets that consistency dimension. |
| `references/planning.md` | PLAN phase for large writing work; defines the writing header and PLAN-only long-form review retrofit. |
| `references/long-form-review.md` | Multi-lane review (style/language, structure, or more than one consistency dimension), `deep` thoroughness, or full-paper / pre-submission scope. |
| `references/refactor-and-compile.md` | Find-replace across the document, build/compile any time edits are made. |
| `references/integration.md` | The writing task is riding `superintegrate`. |

## Coupling to superRA workflows

Most writing work is standalone — terminate at edit + commit, or at findings + commit. Larger work routes through `superplan` with `references/planning.md`. Whole-section drafts, whole-paper revisions, and R&R passes continue through the full workflow. Long-form review retrofit uses PLAN.md only: the draft already exists, reviewers inspect it through `superimplement`, and findings live in PLAN.md review notes rather than RESULTS.md.
