# Slide Layout Checks

Use this reference when checking Beamer output, line wraps, overfull boxes, figures, or final PDF layout.

## Cheap Check Order

1. Build the deck with `latexmk` or use an existing PDF.
2. Parse the LaTeX log for overfull boxes, fatal errors, and missing assets.
3. Extract PDF text boxes with `pdftotext -bbox`.
4. Flag likely wrapped bullets and text near slide boundaries.
5. Inspect only the flagged pages visually when the cheap check is inconclusive: render them with `pdftoppm -png -r 100 -f N -l N deck.pdf page` and read the images.

`uv run --script scripts/check_slide_layout.py deck.tex` automates steps 1-4; add `--render-flagged DIR` to also produce PNGs of flagged pages for step 5. Treat its output as triage evidence, not a final aesthetic verdict.

## Interpreting Findings

The wrap and boundary heuristics are calibrated to the house template (10pt metropolis, `\onehalfspacing`). On other themes or font sizes they may produce false negatives (missed wraps) or false positives (spurious boundary warnings) — treat findings as triage prompts, not determinate verdicts, and inspect flagged pages visually when the deck uses a different theme or base font size.

- **Overfull hbox/vbox:** usually a real Beamer layout problem. Fix by shortening text, changing line breaks, using columns, reducing equation width, or moving detail to backup — never by `\resizebox` on text or equations (see SKILL.md Core Principle).
- **Missing asset:** fix the path or use a deliberate placeholder command. Do not leave unresolved figure paths in final decks. For house decks using `\includeifexists`, the checker also flags placeholder boxes rendered in the PDF as `missing-asset` warnings — each must be resolved before final handoff.
- **Likely wrapped bullet:** rewrite shorter first. If the second line carries needed meaning, consider splitting into two bullets or making the slide lighter.
- **Boundary warning:** inspect the page. Bounding-box extraction can be noisy, but text near the slide edge often means a title, footline, figure label, or equation is at risk.

## One-Line Bullet Heuristic

The reliable way to know whether a bullet stayed on one line is to render the PDF and inspect text positions. Visual screenshots are not required for first pass:

- In extracted PDF text boxes, words on the same rendered line share a narrow y-range.
- A bullet likely wrapped when a text run continues on a nearby lower y-range with similar indentation and no new bullet marker.
- This heuristic catches likely wraps but cannot infer author intent. A flagged wrap is a prompt to review the bullet, not an automatic failure.
