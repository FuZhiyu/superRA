---
title: "writing"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

Tell a bare coding agent to "improve the writing" and it rewrites your argument as it goes: it strengthens a hedge you meant to keep, reorders sentences so the paragraph leads with a different claim, swaps your committed term for a synonym, and leaks the editing chat into the prose ("as the table now defines"). The skill's rule is **preserve substance, polish prose** — argument, logic, structure, claims, intent, and tone are sovereign; wording, sentence shape, hedging calibration, flow, and mechanics are the editing target. When an edit would shift the sequence of ideas, the set of claims, or the force of a claim, the agent stops and asks. Every pass also builds an audience model first, so the prose addresses the venue's reader and never names artifacts that reader cannot see.

## How you ask for it

The verb in your request picks the mode — no flag. **Review** ("review §3 for clarity", "check my citations") reads end-to-end and returns located findings without touching the text; it reads for argument problems a generic proofreader misses, like a claim the evidence does not support. **Polish** ("polish §3", "proofread", "apply these review findings") edits in place within your scope; restructuring stays out unless you ask. **Draft** ("draft the methods section from these notes") outlines first, then writes in your voice.

This is the skill you will most often run standalone — point it at a file, section, or diff in LaTeX, Markdown, Quarto, or plain text. Two non-obvious moves:

- **Polish your own edits as a diff.** Edit by hand, leave the changes **unstaged**, and say "polish my unstaged changes." The agent reads your `git diff` as the polish target and lands its work *with* your direction instead of reverting toward the old text, so you never name line ranges. The same works on a recent commit.
- **Leave directives in the text.** Markers like `TODO`, `[fill in]`, `??`, or placeholder phrasing are treated as work to finish in scope; `DO NOT EDIT` blocks are left alone; a `% intent: …` comment above a paragraph tells Draft what to write and Polish what to check against.

For mode routing, the consistency dimensions it checks, fix tiers, and the audience-first discipline, see [writing](skills/writing/SKILL.md).
