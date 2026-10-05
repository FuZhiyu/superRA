---
title: "Academic Writing"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

`academic-writing` edits your prose without changing what you said. Argument, structure, claims, intent, and tone are yours: an edit that would change them stops and asks. Wording, sentence shape, hedging calibration, flow, and mechanics are fair game. Point it at a file, a section, or a diff in LaTeX, Markdown, Quarto, or plain text — standalone or inside a task.

## Your verb picks the mode

| You say | Mode | You get |
|---|---|---|
| "Review §3 for clarity and check that the prose matches Table 2." | Review | Located findings; the text is untouched |
| "Polish §3," "proofread this," "apply these review findings." | Polish | Edits in place; argument, claims, and section order unchanged |
| "Draft the methods section from these notes." | Draft | New prose, outlined first and matched to the surrounding draft |

Polish does not reorganize unless you ask: "restructure §3," "reorganize the intro."

## Review reports findings for you to decide

- **Each finding** carries a location, a class (style, structure, consistency, or argument), and a recommendation — e.g. "the abstract calls the effect 'significant' but Table 2 reports p = 0.11."
- **Consistency checks** cover eight dimensions: terminology, notation, cross-references, citations, numbers, math, argument logic, and code-vs-paper (whether the code and tables produce what the prose claims).
- **Depth follows scope.** A paragraph gets one reviewer. A multi-lane review runs one reviewer per lane in parallel. A full-paper, pre-submission, or R&R review becomes a review-only task subtree, with findings in each task's review notes.

## Steer it from the draft

- **Name the venue.** The agent writes for that reader — a journal reader, a conference audience, an editor reading a response letter — and keeps editing-process references ("as the table now defines") out of the text.
- **Polish your own edits as a diff.** Edit by hand, then say "polish my unstaged changes" or "polish the changes in the last commit." The polish follows your direction instead of reverting toward the old text.
- **Leave markers.** `TODO`, `[fill in]`, and `??` get finished in scope; `DO NOT EDIT` blocks are left alone.
- **Write intent comments.** A `% intent: …` (or `<!-- intent: … -->`) above a paragraph records what it should do. Review flags prose that drifts from it; Polish asks before resolving a conflict.
- **Edit the recorded conventions.** On a first draft or long-form review, the agent records paper-specific choices — canonical terms, citation and number formats, voice — under `## Project Conventions` on the manuscript task, or in `CLAUDE.md`. Change them there to change what every pass enforces.

For mode routing, fix tiers, and the consistency dimensions, see [academic-writing](skills/academic-writing/SKILL.md).
