---
title: "writing"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Point a bare coding agent at a manuscript paragraph and tell it to "improve the writing," and it rewrites your argument while it is at it: it strengthens a hedge you meant to keep ("may raise" becomes "raises"), reorders the sentences so the paragraph now leads with a different claim, swaps your committed terminology for a synonym it prefers, and leaks the editing chat into the prose ("as the table now defines"). It hands back fluent text that no longer says what you said. This skill draws a hard line — **preserve substance, polish prose.** Your argument, logic, paragraph structure, technical claims, intent, and tone are sovereign; wording, sentence shape, parallelism, hedging calibration, flow, and mechanics are the editing target. When a contemplated edit would shift the sequence of ideas, the set of claims, or the force of a claim, the agent stops and asks instead of deciding for you.

Every pass also builds an audience model first — who reads this venue and what is in their information set — so the prose addresses the journal (or working-paper, or response-letter) reader rather than the conversation, and never names artifacts the reader cannot see.

## Three modes, triggered by how you phrase the request

You select the mode with the verb in your request; there is no flag to set.

- **Review** — "review §3 for clarity", "check my citations", "run a consistency sweep", "find issues in this draft". It reads end-to-end and returns a findings report — each item classified (style / structure / consistency / argument) and located, with a recommended fix. It does not touch the file. Argument findings (a claim the evidence does not support, a load-bearing unstated assumption) are the ones a generic proofreader misses, and Review reads for them deliberately.
- **Polish** — "polish §3", "tighten this paragraph", "proofread", "clean up these edits", "apply these review findings". It edits in place within the scope you set, using the smallest edit that fixes each issue. Mechanical and wording-level fixes land directly; anything that would change the paragraph's sequence, set of claims, or claim strength gets surfaced to you rather than applied. Restructuring (reorder sections, reorganize the intro, strengthen an argument) stays out of scope unless you ask for it explicitly — the agent proposes a restructure but will not perform one without authorization.
- **Draft** — "draft the methods section from these notes", "write up the results from this table". It builds an outline first, drafts paragraph by paragraph in your voice, and self-checks structure and style before handing back.

## The killer pattern: polish a diff

Edit a section by hand, leave the changes **unstaged**, and ask the agent to "polish my unstaged changes." It runs `git diff` first, reads your edit as the polish target, and lands its polish *with* your direction rather than reverting toward the old text — so you never have to name line ranges. The same works on a change you just committed ("polish my last commit"). Concretely: you rewrite the limitations paragraph rough and fast, leave a `[fill in cite]` and a `% TODO: hedge this` in it, and say "polish my unstaged changes" — the agent tightens the wording, resolves the `TODO` and the `[fill in]` in scope, and stops to ask before touching the one sentence where tightening would change what you are claiming. You do the thinking in rough prose; the agent does the finish.

## Directives you leave in the text get acted on

Anything that reads as unfinished work — `TODO`, `% TODO:`, `\todo{...}`, `[fill in]`, `??`, `XXX`, or visibly placeholder phrasing — is treated as work assigned to the agent and cleaned up when it falls in scope. A line or block marked `DO NOT EDIT` is fenced off and left untouched even when it sits inside the scope. A `% intent: …` comment (`<!-- intent: … -->` in Markdown or Quarto) on the line above a paragraph states what that paragraph is for: in Draft mode the agent writes prose that fulfills it, and in Polish mode it reads existing intent comments as a yardstick but never invents one.

## Consistency checks every mode runs

Whatever the mode, it runs eight consistency dimensions over the target: terminology (one canonical term where you have synonyms), notation, cross-references, citations (narrative vs parenthetical, "et al." threshold, entries that match the bib), numerical formatting (rounding, SE/CI delimiters, percent vs pp), math, argument-logic, and code-paper alignment (the regression and sample described in the text checked against the code that produced them). So a polish pass on one paragraph also catches a symbol that drifted from its first definition, a `\citet` that does not match your bibliography, a "Section 3" where the rest of the paper writes "§3", or a coefficient rounded to three decimals in one table and two in another. On the first long-form review or first draft pass against a paper with no recorded writing conventions, it inventories these paper-specific choices (canonical terms, citation style, numerical formatting, cross-reference phrasing) and records them so a later session does not silently re-decide them.

## How you invoke it

This is the domain skill you will most often invoke standalone, directly on your manuscript with no task tree in play — point it at a file, a section, or a diff in LaTeX, Markdown, Quarto, or plain text and ask, using one of the three verbs above. Larger jobs (a whole-section draft, a pre-submission or R&R review) route through superRA planning, but the default is just you, your draft, and a one-line request.

For the full mode routing, the eight consistency dimensions, the fix tiers, and the audience-first discipline, see [writing](skills/writing/SKILL.md).
