# Slide Layout Checks

Load when checking Beamer output, line wraps, overfull boxes, figures, or final PDF layout.

## Cheap Check Order

1. Build the deck with `latexmk` or use an existing PDF.
2. Parse the LaTeX log for overfull boxes, fatal errors, and missing assets.
3. Extract PDF text boxes with `pdftotext -bbox`.
4. Flag likely wrapped bullets and text near slide boundaries.
5. Inspect flagged pages visually when the cheap check is inconclusive: render with `pdftoppm -png -r 100 -f N -l N deck.pdf page` and read the images.

`uv run --script <skill-dir>/scripts/check_slide_layout.py deck.tex` automates steps 1-4; `--render-flagged DIR` also produces PNGs of flagged pages for step 5. `<skill-dir>` is the directory containing the slide-design `SKILL.md`. Its output is triage evidence, not a final aesthetic verdict.

## Interpreting Findings

The wrap and boundary heuristics are calibrated to the house template (10pt metropolis, `\onehalfspacing`). Other themes or font sizes can produce missed wraps or spurious boundary warnings — inspect flagged pages visually on any deck with a different theme or base font size.

- **Overfull hbox/vbox:** usually a real layout problem. Shorten text, change line breaks, use columns, reduce equation width, or move detail to backup — never `\resizebox` on text or equations (see SKILL.md Core Principle).
- **Missing asset:** fix the path or use a deliberate placeholder command; no unresolved figure paths in final decks. On house decks using `\includeifexists`, the checker also flags PDF-rendered placeholder boxes as `missing-asset` — each resolved before final handoff.
- **Likely wrapped bullet:** rewrite shorter first. If the second line carries needed meaning, split the bullet or lighten the slide.
- **Boundary warning:** inspect the page. Bounding-box extraction is noisy, but text near the edge often means a title, footline, figure label, or equation is at risk.

## One-Line Bullet Heuristic

Render the PDF and inspect text positions; visual screenshots are not needed on first pass:

- Words on the same rendered line share a narrow y-range in the extracted text boxes.
- A bullet likely wrapped when a text run continues on a nearby lower y-range with similar indentation and no new bullet marker.
- The heuristic cannot infer author intent: a flagged wrap prompts review, it is not an automatic failure.
