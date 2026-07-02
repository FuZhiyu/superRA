---
title: "slide-design"
status: not-started
depends_on:  []
tags: []
created: 2026-06-18
---

## Objective

Ask a bare agent to "make slides from this paper" and it ports the paper onto the screen: a frame crammed with the full derivation, a table with every column, a paragraph of caveats next to the headline, everything shrunk with `\resizebox` until it fits. That deck is correct and unreadable — a slide is a live communication artifact, and an audience with imperfect attention and uneven background cannot recover the point from a page built for a silent reader. The skill's rule is **preserve the truth of the claim, but prioritize the version the audience can understand now**: derivations, robustness, caveats, and expert objections move to oral narration, notes, or backup slides when they would overload the main path, and `\resizebox` on text or equations is banned — when content overflows you simplify, split the slide, or cut to backup, not shrink.

The hard part is judging what the audience knows at each moment, so the skill runs an **audience-context pass** before any wording or styling: pick a representative listener for *this* talk (not an ideal reader of the paper), and for every dense slide state what they already know, what they do not, and what they may wrongly infer from a familiar term. Three technique families fall out of that judgment — **context engineering** (lead with the takeaway, open sections with the question the next block answers), **attention management** (every visible element competes; remove, gray out, delay, or overlay anything that is not the current point), and **simplification** (one sharp line over a complete sentence, the minimum equation the live point needs). Beamer is the first-class target, with a house starter template and a layout-triage script, but the principles carry across PowerPoint, Keynote, and browser decks.

## How to ask for it

Say what you are making and the discipline triggers on its own — you do not name the skill or pass a flag. The verb picks the mode the same way the writing skill works: ask to *create* a deck and you get new slides, ask to *review* one and you get located findings, ask to *polish* or *fix* and you get edits in place.

> "Turn §4 of the paper into a ten-minute conference talk. The audience is asset-pricing empiricists, not my coauthors."

Two things are worth telling the agent explicitly, because they steer the judgment the skill exists to make.

### Name the audience, not just the topic

The representative listener is the one input the agent cannot infer from the paper. A job-market committee, a field seminar, a general-interest plenary, and your own group all need different framing of the same result. Name them, and say where the talk sits — the opening of a section, a five-minute lightning slot, a poster walk-through — so the agent can decide what context to establish before each claim and what familiar-looking term might be read three ways by three subfields in the room.

### Split the main path from backup

Tell the agent what the talk must land in real time versus what only needs to be reachable if someone asks. Typical-audience context stays on the main path; the full derivation, the robustness battery, and the expert objection go to backup slides the agent links from the main slide. This is the move that keeps a slide honest without crowding it — the rigor is one click away in the room, not deleted and not competing for attention on screen.

### For Beamer decks

New decks start from the skill's house starter template (theme, palette, frame and title layouts, list markers, semantic commands) rather than a hand-built preamble, so a deck looks consistent from the first slide. Before you read a draft PDF, the agent can run a layout-triage pass — a cheap nonvisual check that flags likely line wraps, overfull boxes, text near the slide edge, and missing figures — so the obvious layout breakage is caught before the visual review.

For the audience-context inventory, the context/attention/simplification technique catalog, the Beamer overlay and layout references, the layout-triage script, and the planning-stage main-vs-backup policy, see [slide-design](skills/slide-design/SKILL.md).
