---
title: "Adopt House Beamer Starter Template"
status: approved
depends_on: []
tags: [retrospective]
input:
  - inspo/slide-design-guide/slide_deck_design.tex
output:
  - skills/slide-design/assets/beamer-starter-template.tex
created: 2026-06-11
updated: 2026-06-11
---

## Objective

Replace the bare overlay demo (`assets/minimal-beamer-overlay-template.tex`) with a full house starter template adopted from Julie's slide-design guide deck, so agents start new decks from the house design language instead of assembling a preamble from scratch.

- The template carries the complete house preamble: 16:9 metropolis with the Mondrian palette, frame-title and title-page templates, tikz list markers, top navigation bar, `appendixnumberbeamer`, and semantic commands (`\slidelink`, `\includeifexists`, `\highlight`, `L`/`C`/`R` column types), plus an overlay-command reference block.
- Demo frames preserve the overlay idioms the old template taught: labeled roadmap frame with `\againframe` returns, per-list incremental reveal, stable technical walkthrough in `overlayarea`, and main-to-backup `\slidelink` navigation.
- Incremental reveal becomes opt-in per list (`[<+->]`) rather than the old deck-wide `\beamerdefaultoverlayspecification{<+->}`.
- `SKILL.md`, `references/beamer-techniques.md`, and `references/beamer-overlays.md` point to the template as the single copyable starting point; `beamer-techniques.md` frames its preamble bullets as the fallback path for decks that cannot adopt the template wholesale.
- The reviewer checklist gains an `[ADVISORY]` item: new styling stays within the deck's existing color and command vocabulary instead of ad-hoc colors or one-off styling.
- The `slide-design` rows in `README.md` and `skills/CATEGORIES.md` mention the starter template.

Validation: the template compiles standalone and `check_slide_layout.py` reports no warnings or errors on it.

## Results

### Key Findings

- Added `assets/beamer-starter-template.tex` (~290 lines), adopted from `inspo/slide-design-guide/slide_deck_design.tex` (ignored local copy of the guide deck) and merged with the old template's demo frames. Header comment records the provenance URL.
- Deleted `assets/minimal-beamer-overlay-template.tex`; all pointers in `SKILL.md`, `beamer-techniques.md`, and `beamer-overlays.md` now target the new template.
- The `overprint` demo frame from the old template was not carried over; `overprint` remains documented in the template's overlay-command reference block and in `references/beamer-overlays.md`.
- New `[ADVISORY]` checklist item in `SKILL.md` covers styling-vocabulary discipline; `SKILL.md §Beamer Implementation` now instructs starting new decks from the template.
- `beamer-techniques.md §Preamble And Theme` describes the template as the house preamble and keeps a short fallback list for adapting existing decks; the explicit `\setbeamersize` margin bullet moved into the template.

### Verification

- `uv run --script skills/slide-design/scripts/check_slide_layout.py skills/slide-design/assets/beamer-starter-template.tex --no-fail` — compiles via latexmk; no errors or warnings. Two info-level `possible-wrap` flags on pages 6–7 are the known heuristic false positive for a subitem appearing with its parent.

### Notes

- FiraSans loads conditionally (`\IfFileExists{FiraSans.sty}`), so the template compiles on machines without the font package.
