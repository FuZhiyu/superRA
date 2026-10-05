---
title: "slide-design"
status: not-started
depends_on:  []
tags: []
created: 2026-06-18
---

## Objective

`slide-design` builds and reviews decks as live talks. The main path lands the point the audience can follow now; derivations, robustness, caveats, and expert objections move to narration, notes, or backup slides. Overflowing content gets simplified, split, or moved to backup — never shrunk with `\resizebox`. Beamer is the first-class target; the principles carry to PowerPoint, Keynote, and browser decks.

## Name the audience and what must land live

Say what you want — a new deck, a review, a polish pass — and who is in the room.

> "Turn §4 of the paper into a ten-minute conference talk. The audience is asset-pricing empiricists, not my coauthors."

- **Name the audience and the slot.** The representative listener is the one input the agent cannot infer from the paper: a job-market committee, a field seminar, and a plenary need different framing of the same result. Say where the talk sits — a five-minute lightning slot, a section of a longer talk.
  - Before any wording, the agent works out, per dense slide, what that listener already knows, what they don't, and which familiar term they may misread.
- **Split the main path from backup.** Say what the talk must land in real time and what only needs to be reachable if someone asks. The full derivation, the robustness battery, and the expert objection go to backup slides linked from the main slide.

## Beamer decks get a template and a layout check

- **New decks start from the skill's [starter template](skills/slide-design/assets/beamer-starter-template.tex)** — theme, palette, frame and title layouts, semantic commands — so the deck is consistent from the first slide.
- **A [layout-triage script](skills/slide-design/scripts/check_slide_layout.py) can run before you read the PDF**, flagging likely line wraps, overfull boxes, text near the slide edge, and missing figures.

For the audience-context discipline, technique catalog, and Beamer overlay and layout references, see [slide-design](skills/slide-design/SKILL.md).
