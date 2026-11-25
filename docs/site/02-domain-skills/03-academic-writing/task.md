---
title: "Academic Writing"
status: not-started
depends_on:  []
---

## Objective

Ask superRA to proofread, polish, draft, or review a file, section, or diff. The academic-writing skill applies by default to `.tex` files. In Markdown, Quarto, and other formats, it applies to publication-quality writing such as manuscripts, exhibit notes, footnotes, appendices, and response letters. Use `communicate` for READMEs, documentation, working notes, and task files.

## Choose how much to edit

The agent follows the mode you name. If you leave the mode open, it uses the state of the draft and what you ask it to deliver.

| Mode | You can say | When the agent chooses it | You get |
|---|---|---|---|
| Proofread | “Proofread the introduction” | The prose is mostly in place, including when you say “Update the paper for the new estimates” | Corrections to typos, grammar, broken references, and statements that mislead readers about a result. Approximations that still hold pass the check. |
| Polish | “Polish the introduction” or “tighten this paragraph” | You want rough prose recast | Edits that solve specific reading problems, such as a sentence that obscures who did what. |
| Draft | “Draft the methods section” | The requested passage is yet to be written | New prose in your voice that gives readers what they need to understand a result, read an exhibit, or assess a claim. The agent applies the Proofread standard to nearby text. |
| Review | “check my citations” | You ask for findings on an existing draft | Findings only, with locations and recommendations. |

The agent follows your argument, tone, and hedges. It can correct a stale number or caption when the message still holds. It asks before changing what a sentence claims or how strongly it says it. To authorize a change in structure, say “reorganize the introduction.”

## Review reports findings for you to decide

- **Each finding** carries a location, a class (style, structure, consistency, or argument), and a recommendation — e.g. "the abstract calls the effect 'significant' but Table 2 reports p = 0.11."
- **Consistency checks** cover eight dimensions: terminology, notation, cross-references, citations, numbers, math, argument logic, and code-vs-paper. A place where the paper is silent or approximate but not misleading gets a one-line note, not a proposed edit.
- **Depth follows scope.** A paragraph gets one reviewer. A multi-lane review runs one reviewer per lane in parallel. A full-paper, pre-submission, or R&R review becomes a review-only task subtree, with findings in each task's review notes.

## Put the paper’s conventions beside the manuscript

Record the paper’s preferred terms, citation and number formats, and voice in `CLAUDE.md` or `AGENTS.md` in the manuscript folder. On a first draft or long-form review, the agent records conventions it can infer and creates the project’s agent instruction file in that folder if needed.

## Steer an individual pass

- **Name the venue.** The agent uses the background knowledge it can expect from that audience.
- **Point to your edits.** Say “polish my unstaged changes” to limit the pass to the lines you edited.
- **Mark the draft.** The agent resolves `TODO`, `[fill in]`, and `??` within the requested scope. Use `DO NOT EDIT` to protect a passage.
- **State a paragraph’s purpose.** Put a `% intent: …` comment above it in LaTeX so the agent can flag a mismatch with the prose.

For mode routing, edit bars, and fix tiers, see [academic-writing](skills/academic-writing/SKILL.md).
