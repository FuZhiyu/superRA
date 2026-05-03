---
name: writing
description: Use PROACTIVELY whenever reviewing, polishing, proofreading, consistency-checking, refactoring wording, or drafting prose a human will read in an academic paper or manuscript. Triggers organized by mode. Review — "review §X", "check my citations", "find issues in this draft", "consistency sweep". Polish — "polish §X", "tighten this paragraph", "proofread", "clean up these edits", "apply these review findings", "rewrite for clarity". Draft — "draft the methods section", "write up the results from these notes". Language/format-agnostic (LaTeX, Markdown, Quarto, plain text). Loaded by implementer and reviewer subagents at dispatch time when the stage touches writing, per `superRA:using-superRA` §Skill-Load Manifest.
user-invocable: true
---

# Academic Writing

Three working modes — **Review**, **Polish**, **Draft** — share a knowledge base (style, structure, eight consistency dimensions, refactor-and-compile) and one principle.

## Preserve substance, polish prose

**Preserve** — the argument, the logic, the section/paragraph structure, the technical claims, the author's intent, the tone. These are sovereign; if a contemplated edit would change any of them, stop and ask.

**Polish freely** — wording, sentence structure, clarity, parallelism, hedging calibration, flow, mechanical correctness. This is the editing target.

**Restructuring is out of scope** unless the request authorizes it (and `references/structure.md` is loaded — see Mode routing).

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
| `references/style.md` | Sentence- or paragraph-level edits (every Polish, every Draft self-check). |
| `references/structure.md` | Drafting a section, or polish that authorizes restructuring. |
| `references/consistency/*.md` (8 dimensions: terminology, notation, cross-references, citations, numerical, math, argument-logic, code-paper) | Review or polish targets that one dimension. Multi-dimension reviews dispatch one reviewer per file in parallel. |
| `references/refactor-and-compile.md` | Find-replace across the document, build/compile any time edits are made. |
| `references/integration.md` | The writing task is riding `integration-workflow`. |

## Coupling to superRA workflows

Most writing work is standalone — terminate at edit + commit, or at findings + commit. Larger work (whole-section drafts, whole-paper revisions, R&R passes) routes through `planning-workflow` → `implementation-workflow` → `integration-workflow`; the reviewer-dispatch invariant and the parallel-dispatch pattern for consistency reviews are owned by those workflow skills, not by this skill.
