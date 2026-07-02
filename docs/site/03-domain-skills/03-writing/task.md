---
title: "writing"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Tell a bare coding agent to "improve the writing" and it rewrites your argument as it goes: it strengthens a hedge you meant to keep, reorders sentences so the paragraph leads with a different claim, swaps your committed term for a synonym, and leaks the editing chat into the prose ("as the table now defines"). The skill's rule is **preserve substance, polish prose** — argument, logic, structure, claims, intent, and tone are sovereign; wording, sentence shape, hedging calibration, flow, and mechanics are the editing target. When an edit would shift the sequence of ideas, the set of claims, or the force of a claim, the agent stops and asks. Every pass also builds an audience model first, so the prose addresses the venue's reader and never names artifacts that reader cannot see.

Beyond holding the line on your argument, the skill brings three things a bare agent does not. It carries a trained academic-writing style — sentence and paragraph rules drawn from the Little Red Schoolhouse and a research-writing handbook, not generic copyedit instincts. It runs a consistency check across eight dimensions, including code-vs-paper: when the prose claims a number, a sign, or a sample size, it checks that the code and tables actually produce it. And it revises in place — once findings exist, it can apply them to the text rather than just listing what is wrong.

## How you ask for it

You do not name the skill or pass a flag. The verb in your request picks the mode: ask to *review* and you get findings, ask to *polish* and you get edits, ask to *draft* and you get new prose. This is the skill researchers run standalone most often — point it at a file, a section, or a diff in LaTeX, Markdown, Quarto, or plain text.

### Review — find problems, leave the text alone

Review reads the draft end-to-end and reports located findings without touching a character. It reads for the argument problems a generic proofreader misses — a claim the evidence does not support, an unstated assumption doing load-bearing work — alongside style, structure, and consistency issues.

> *You say:* "Review §3 for clarity and check that the prose matches Table 2."
> *You get:* a list of findings, each with a file location, a classification, and a one-line fix — for example, "the abstract calls the effect 'significant' but Table 2 reports p = 0.11," reported for you to decide on, not silently changed.

How wide the review fans out follows the scope you give it. A **quick review** — a paragraph or a single section — is one agent making one pass. A **long-form review** — triggered by full-paper, pre-submission, or R&R scope — splits the draft into lanes (language and style, structure, and one lane per consistency dimension) and runs a focused reviewer on each in parallel, because one generalist reviewer reading every lane at once reads each one more shallowly than a specialist would. You do not pick the depth; the agent infers it from how much you point it at.

### Polish — apply edits in place

> *You say:* "Polish §3," or "proofread this," or "apply these review findings."
> *You get:* the text edited in place within the scope you named — tightened wording, repaired parallelism, fixed mechanics — with your argument, claim set, and section order left as they were.

Polish edits sentences and paragraphs; it does not reorganize. Restructuring stays out of scope unless you ask for it ("restructure §3", "reorganize the intro").

### Draft — write new prose from notes

> *You say:* "Draft the methods section from these notes."
> *You get:* an outline first, then prose written in your voice from the notes and the surrounding draft — not a generic write-up that ignores how the rest of the paper reads.

### Usage tips

- **Polish your own edits as a diff.** Edit by hand — commit them or leave them unstaged — then say "polish my unstaged changes" or "polish the changes in the last commit." The agent reads your `git diff` as the polish target and lands its work *with* your direction instead of reverting toward the old text, which means you never have to name line ranges.
- **Leave directives in the text.** Markers like `TODO`, `[fill in]`, `??`, or placeholder phrasing are treated as work to finish in scope; `DO NOT EDIT` blocks are left alone; a `% intent: …` comment above a paragraph tells Draft what to write and Polish what to check against.

For mode routing, the consistency dimensions it checks, fix tiers, and the audience-first discipline, see [writing](skills/writing/SKILL.md).
