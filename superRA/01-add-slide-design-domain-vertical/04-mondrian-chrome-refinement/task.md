---
title: "Refine Mondrian Chrome and Semantic Color Discipline in Starter Template"
status: approved
depends_on: [01-beamer-starter-template]
tags: [retrospective]
input:
  - skills/slide-design/assets/beamer-starter-template.tex
output:
  - skills/slide-design/assets/beamer-starter-template.tex
created: 2026-06-12
---

## Objective

Refine the starter template's visual chrome so the Mondrian language reads as a grid (color planes bounded by black lines, not floating accents) and so red/blue are reserved for meaning in the text rather than spent on decoration.

- **Frame title becomes a Mondrian grid cell.** Blue cell bounded by the black grid (2.2pt vertical line plus full-width 1.6pt rule), with a flat red plane (4.85em × 0.87ex, title-page proportions) sitting on the rule at the right margin. The red plane anchors to the rule, not the title line, so it stays put when long titles wrap; `\hangindent` aligns continuation lines with the title text.
- **Frame-title template survives `\appendix`.** Wrap it in `\MondrianFrametitle` and re-assert it after `\appendix`, where metropolis's hook resets headline/frametitle/footline to plain; also re-assert frame numbering (`\metroset{numbering=fraction}`, giving appendix-local "1 / m" via `appendixnumberbeamer`) and replace the nav-bar headline with an equal-height empty spacer so appendix titles keep the same vertical position.
- **Title page joins the same grid.** Color blocks sit directly on a full-width black grid line (no floating blocks); the red block is phi-wider and phi-flatter than the blue (equal area, asymmetric shape); rules thicken to 1.6pt to match the frame-title grid.
- **Color becomes semantic.** New `\semA` (red) / `\semB` (blue) macros for contrasting two central concepts deck-wide, with guidance to rename per project and use each color only for its concept. List markers (itemize squares, enumerate diamonds) switch from red/blue/black to neutral grayscale so color in body text always carries meaning; the chrome keeps color on every slide. The semantic-command inventory in `references/beamer-techniques.md §Preamble And Theme` lists `\semA`/`\semB`.
- **Marker baselines are corrected.** Itemize squares center on the text line (`baseline=-0.4ex`); enumerate diamonds align their number with the text baseline (`baseline=(n.base)`).
- **Bold weight calibrated for FiraSans.** The `medium` package option (`\usepackage[lf,medium]{FiraSans}`) makes Medium the bold weight — Bold/SemiBold are too heavy for full-sentence lead-ins.

Validation: the template compiles standalone and `check_slide_layout.py` reports no warnings or errors on it.

## Results

### Key Findings

- The frame-title header, title page, and appendix re-assertion are now one coherent grid system: every color plane touches a black line, and the red plane's 4.85em × 0.87ex proportions repeat across title page and frame titles.
- Reserving red/blue for `\semA`/`\semB` required neutralizing the list markers; nesting depth is now encoded by gray value (`MondrianBlack` → `!55`/`!65` → `!35`) and marker size.
- Metropolis's `\appendix` hook silently discards custom frametitle templates; the `\MondrianFrametitle` macro wrapper plus post-`\appendix` re-assertion is the durable fix, demonstrated in the template's appendix section.

### Verification

- `uv run --script skills/slide-design/scripts/check_slide_layout.py skills/slide-design/assets/beamer-starter-template.tex --no-fail` — compiles via latexmk; no errors or warnings. Two info-level `possible-wrap` flags on pages 6–7 are the known heuristic false positive for a subitem appearing with its parent (same as recorded in `01-beamer-starter-template`).
- Reviewer compiled and rendered title page, body, and appendix frames: grid geometry, wrapped-title anchoring, phi proportions (4.85em ≈ 3em·φ, 0.87ex ≈ 1.4ex/φ, equal areas to rounding), and the metropolis `\appendix` reset claim all verified against the installed packages.
- After the review-minor fixes: appendix frame renders with appendix-local numbering ("1 / 1" while the main deck shows "4 / 4") and the compile log has zero font-substitution warnings with the FiraSans `medium` option.
