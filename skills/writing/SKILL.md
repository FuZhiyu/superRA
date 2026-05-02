---
name: writing
description: Use PROACTIVELY whenever editing, polishing, proofreading, consistency-checking, refactoring wording, or drafting technical sections of an academic paper or manuscript. Triggers include "polish this section", "proofread", "check consistency", "rename variable X to Y throughout", "write the methods section", "make the intro flow better", LaTeX / manuscript files touched, or any task that edits prose a human will read. Language/format-agnostic (LaTeX, Markdown, Quarto, plain text). Loaded by implementer and reviewer subagents at dispatch time when the stage touches writing, per `superRA:using-superRA` §Skill-Load Manifest.
user-invocable: true
---

# Academic Writing

superRA's writing domain skill. Carries the cross-cutting discipline that applies at every stage of a writing task — the Iron Law (respect the author's intent), the three concurrent disciplines (Preserve, Improve, Verify) with inline severity markers, the pitfalls pointer list, and the common rationalizations. Main body is loaded by implementer and reviewer subagents at every writing-touching dispatch.

## RA framing

You are assisting the researcher, not replacing them. The researcher's voice is the final voice. Your edits serve the researcher's intent — never your own preference. Writing work sits closer to the researcher than data work: the user is often editing the same file you are. Treat their in-progress text as sacred unless the request names it.

## Stage-Scoped References

Companion reference files carry content that applies at a specific phase or operation. Load per stage; do not load them all at every dispatch:

| Reference | Load when |
|---|---|
| `references/planning.md` | PLAN phase — scope inventory, task-size triage, PLAN.md / RESULTS.md decision matrix. Loaded by `planning-workflow` when the task touches writing. |
| `references/workflow.md` | Any phase — the four usage modes (direct-edit / pure-review / review-edit-loop / full-workflow) and the two hard rules (reviewer dispatch never skipped; parallel-dispatch for multi-dimensional consistency). Loaded first by any fresh orchestrator on a writing task. |
| `references/style-checklist.md` | IMPLEMENT phase — sentence + paragraph rules (nominalization, active voice, hedging, parallelism, old→new flow). Loaded when edits touch sentence-level prose. |
| `references/structure-checklist.md` | IMPLEMENT phase — Pyramid Principle (governing idea, MECE, horizontal/vertical logic, SCQ) + section-level anatomy. Loaded when the task drafts or restructures sections. |
| `references/consistency/*.md` | Any phase — eight dimension-scoped files (terminology, notation, cross-references, citations, numerical, math, argument-logic, code-paper). Each is sized for a single parallel reviewer to load one dimension. |
| `references/refactor-and-compile.md` | IMPLEMENT phase — safe context-aware find-replace + build commands per engine (LaTeX / Quarto / Markdown / Pandoc) + warning triage. Loaded whenever edits are made (every batch ends with a build). |
| `references/collaboration.md` | IMPLEMENT phase — detecting and respecting the user's in-progress work; when and how to escalate structural changes. Loaded on every implementation dispatch. |
| `references/integration.md` | INTEGRATE phase — writing-specific pre-merge gates (document builds clean, consistency dimensions pass, voice preserved, scope respected). Loaded at the `integration` stage. |

The main body below is the shared base that both implementer and reviewer load — it carries the Iron Law, §Three Concurrent Disciplines (teaching + inline severity-marked checklist), §Pitfalls pointers (operation-specific references), §Common Rationalizations, and §Key References.

## The Iron Law

```
RESPECT THE AUTHOR'S INTENT
```

The author's **meaning, argument, scope, and structural intent** are sovereign. The RA's job is to serve that intent, not override it.

Three clauses, non-negotiable:

1. **Meaning-preserving edits only.** If a fix would change what the sentence, paragraph, or section *says* (not just how it says it), stop and ask. Word-choice fixes, typo fixes, nominalization fixes, hedging fixes, broken-parallelism fixes, cross-reference fixes — all inside scope when the request covers style, polish, or consistency. Rewrites that change the claim, the emphasis, or the argument — escalate.

2. **Scope-bounded edits only.** Edit what was asked. Structural or substantive changes beyond the request are *proposed* (in chat or `PLAN.md`), never performed unilaterally.

3. **In-progress work respected.** Unfinished paragraphs, inline TODOs, `\todo{}` macros, commented-out text, and visibly-being-edited sections are not touched unless the request names them.

**Explicit non-goal.** The Iron Law does NOT require preserving word choices, typos, passive-voice awkwardness, weak diction, or broken parallelism. Fixing those is the RA's job. What it forbids is overriding *authorial intent*.

**Violating the letter of the rules is violating the spirit of the rules.** "Just a small structural improvement" and "the author probably meant X" are Iron Law violations. See §Common Rationalizations.

## Common Rationalizations

LLM-specific excuses that precede Iron Law violations. When you catch yourself forming one of these, stop and escalate.

| Rationalization | Reality |
|---|---|
| "This whole paragraph is clearly better my way — I'll just rewrite it." | Scope + meaning violation. Propose the rewrite; do not perform it. |
| "The author probably meant X — I'll just write X." | Meaning violation. If you have to guess, escalate. |
| "This structure is obviously suboptimal — I should reorder the sections." | Scope violation. Structural changes are out-of-scope unless requested. |
| "The request said 'polish', so editing voice is fair game." | Voice ≠ diction. Fix nominalization / passive / hedging / parallelism. Do not homogenize tone, register, or idiom. |
| "The TODO marker is obviously going to be filled in the same way I'd fill it." | In-progress work violation. Leave TODOs for the author. |
| "Warnings are never important — compile-clean enough." | Verify violation. Triage each warning; escalate on doubt. |
| "I can see the author's point better than they expressed it." | Meaning violation in disguise. Fix the expression, not the point. |
| "They'll notice and push back if they don't like it." | Not a substitute for consent. Pre-approved edits are faster than post-hoc reversions. |

---

## Three Concurrent Disciplines: Preserve–Improve–Verify

Three disciplines underpin every writing task. They are **concurrent, not sequential** — every edit exercises all three.

This section is both **teaching content** (how to do the work) and the **shared checklist**. The implementer walks it before returning DONE; the reviewer walks the same items as verification. The items below apply to every writing task; operation-conditional items (sentence-level style, structure drafting, consistency dimensions, refactor, collaboration) live in §Pitfalls and point at the relevant reference file, walked only when the task performs the corresponding operation.

- `[BLOCKING]` — must fix to earn APPROVE. Encodes the Iron Law, compile/cross-ref integrity, and scope/voice discipline.
- `[ADVISORY]` — best-practice. The reviewer MAY flag as MINOR; does not block APPROVE.

### Reviewer verdict protocol

**Walk §Three Concurrent Disciplines top to bottom, plus the §Pitfalls references matching operations performed in this task. Never halt on a failure.** One comprehensive pass every time — halting early forces a full re-review on the next pass, and reviewer dispatches are costly.

Two verdicts:

- **APPROVE** — no `[BLOCKING]` findings.
- **REVISE** — at least one `[BLOCKING]` finding.

**Handling dependent findings.** When a later finding's assessment depends on an earlier `[BLOCKING]` item being fixed first (e.g., "couldn't assess cross-ref integrity because the compile failed first — re-check after the compile error is fixed"), say so in plain prose alongside the finding. No separate verdict, no formal tag.

**Re-review after REVISE.** Implementer fixes all `[BLOCKING]` findings and re-dispatches. The reviewer then (1) verifies each fix is correct, and (2) re-checks any finding the first pass annotated as depending on an upstream fix. Everything else is accepted from the first pass — no third full walk. APPROVE once all `[BLOCKING]` findings are resolved.

### Preserve (scope + voice)

The most common writing-RA failure is over-editing — rewriting beyond what was asked. Preserve is the discipline that blocks that failure.

- `[BLOCKING]` **No edits outside the requested scope.** If the request is "polish §3.2", §3.1 and §3.3 are untouched. If the request is "fix citations", prose style is not refactored.
- `[BLOCKING]` **Author's voice recognizable in the diff.** Diction, register, and sentence-shape preserved. The diff should read as the author's own revision, not a different writer's paraphrase. If a fluent reader could read the edited passage and the original side-by-side and fail to recognize the same author, Preserve has failed.
- `[BLOCKING]` **User's in-progress edits respected.** TODOs, `\todo{}` macros, `%` comments, commented-out text, unfinished paragraphs, placeholder phrases (`[fill in]`, `??`, `XXX`) — not touched unless the request names them. Detection patterns: `references/collaboration.md`.
- `[ADVISORY]` **Minimal edit.** For each identified problem, apply the smallest edit that fixes it. A nominalization fix replaces one noun with one verb, not the whole sentence.

### Improve (clarity + structure, as requested)

Inside the scope of the request, apply writing discipline — but only where it actually fires. Do not invent problems to fix.

- `[BLOCKING]` **Edits address the specific problem named in the request.** "Polish" means sentence-level clarity. "Tighten" means length reduction. "Check consistency" means report, not rewrite. The request defines the job.
- `[BLOCKING]` **For consistency-check tasks: every mismatch found is reported; none silently fixed beyond scope.** A citation-consistency reviewer reports the orphan citation; it does not rewrite the bibliography.
- `[ADVISORY]` **Sentence-level style rules applied where they fire.** Actions-in-verbs (nominalization), old→new info flow, active voice with clear agency, single-hedge-per-claim, parallel structure, noun-cluster avoidance — see `references/style-checklist.md`. Rules are heuristics, not mandates; do not over-apply.
- `[ADVISORY]` **Paragraph-level flow checked.** Topic sentence present, old→new order inside the paragraph, transitions at paragraph start. See `references/style-checklist.md` §Paragraph-level rules.
- `[ADVISORY]` **Structure (when drafting sections).** Governing idea first, MECE support, section-level anatomy appropriate to section type (intro / methods / results / conclusion). See `references/structure-checklist.md`.

### Verify (compile + consistency)

Every batch of edits ends with a build and a cross-reference check. A diff that doesn't compile is not shippable.

- `[BLOCKING]` **Document compiles after the edit.** Errors block handoff; warnings are triaged. Build command per engine and triage heuristics in `references/refactor-and-compile.md` §Compile.
- `[BLOCKING]` **No new cross-reference breaks.** `\ref`, `\eqref`, `\cite`, `\label`, and equivalent Markdown / Quarto references resolve. Compare the set of unresolved references before vs after the edit; none introduced by the edit. See `references/consistency/cross-references.md`.
- `[BLOCKING]` **Numbers-in-text match numbers-in-tables** *if the edit touched any quantitative claim*. Every number in the edited prose traces to a source table, figure, or explicit calculation. See `references/consistency/numerical.md`.
- `[ADVISORY]` **Build warnings enumerated in handoff** with ≤1-line rationale each. Overfull-hbox on a margin-adjacent paragraph: ignore. Undefined-reference: escalate. Missing-citation: escalate. See `references/refactor-and-compile.md` §Compile.

### Implementation standards

- `[BLOCKING]` Each step implements what the request or `PLAN.md` specifies; deviations are rewritten into the step text, not layered on top.
- `[BLOCKING]` No dangling `TODO` / `XXX` / placeholder strings introduced by the edit (the author's own TODOs are untouched per Preserve).
- `[BLOCKING]` Structural changes (section reorder, subsection add/remove, large insertions/deletions) are *proposed*, not performed, unless the request explicitly authorizes them.

### Documentation and handoff

- `[BLOCKING]` `PLAN.md` task block and `RESULTS.md` task section updated in place (if the workflow mode uses them — small edits run with `references/planning.md` decision matrix saying no PLAN.md is needed, and then the commit message carries the record).
- `[BLOCKING]` For consistency-sweep tasks: findings reported in the handoff (`PLAN.md` / chat / review notes) with file + line locations, severity, and evidence.
- `[ADVISORY]` Build warnings and triage decisions listed in the handoff.

### Stage-scoped discipline (not walked at every implementation dispatch)

- **`integration` stage** — `references/integration.md` carries the pre-merge gates (full build, cross-ref integrity across the merged state, voice preserved across the full diff, scope respected, consistency dimensions relevant to edited sections pass). Loaded by implementer and reviewer at the `integration` stage per `superRA:using-superRA` §Skill-Load Manifest.

---

## §Pitfalls (operation-conditional)

The universal checks live in §Three Concurrent Disciplines above. The pointers below apply only when you perform the corresponding operation. Load the referenced file(s); walk its gated checklist as part of your self-check; the reviewer walks the same file as verification.

- **Sentence-level edits** (polish, proofread, tighten) → `references/style-checklist.md`
- **Structural / section drafting** (write the methods section, restructure the intro) → `references/structure-checklist.md`
- **Multi-dimensional consistency sweep** → `references/consistency/*.md` — dispatch **one reviewer per file in parallel**; see `references/workflow.md` §Mode (b) Pure review.
- **Single-dimension consistency check** (e.g., "check my citations") → load the one relevant `references/consistency/*.md` file (e.g., `consistency/citations.md`).
- **Terminology / notation refactor** (rename `r_i` → `r_{i,t}` throughout; change "treatment group" → "treated sample") → `references/refactor-and-compile.md` §Refactor + `consistency/terminology.md` + `consistency/notation.md`.
- **Build / compilation fix** (the document stopped compiling) → `references/refactor-and-compile.md` §Compile.
- **User-work detected in repo** (uncommitted edits, inline TODOs, recent hunks) → `references/collaboration.md`.

## §Mode selection

See `references/workflow.md` for the four usage modes: (a) **direct edit** — orchestrator edits in-session, then dispatches an independent reviewer; (b) **pure review** — one or more parallel reviewers, no edits; (c) **review → edit → re-review loop** — iterative; (d) **full workflow** — PLAN → IMPLEMENT → VALIDATE → INTEGRATE for major changes.

Two hard rules:

1. **Reviewer dispatch is never skipped.** In every mode — including direct edit — the reviewer is a separately-dispatched agent. Self-review by the orchestrator is not a substitute. This preserves the implementer–reviewer pair principle that runs through every superRA workflow.
2. **Parallel-dispatch multiple reviewers for multi-dimensional consistency work.** One reviewer per `consistency/*.md` file, dispatched in a single message with multiple Agent-tool calls. Each reviewer is focused on its one dimension.

## §Key References

- `references/planning.md` — scope inventory, task-size triage, PLAN / RESULTS optionality
- `references/workflow.md` — four usage modes + two hard rules
- `references/style-checklist.md` — sentence + paragraph rules (LRS, Chaubey)
- `references/structure-checklist.md` — Pyramid Principle + section anatomy (Minto, Chaubey, LRS)
- `references/consistency/*.md` — eight dimension-scoped files for parallel review
- `references/refactor-and-compile.md` — safe find-replace + build gate
- `references/collaboration.md` — respect the user's in-progress work
- `references/integration.md` — pre-merge gates for writing tasks
- Chaubey, V. (2018), *The Little Book on Research Writing* (BulletBooks).
- Minto, B. *The Pyramid Principle* — governing idea, MECE, SCQ.
- Little Red Schoolhouse (UChicago ENGL 13000/33000) — actions-in-verbs, character, cohesion, information flow, argument structure.
