# Beamer Techniques

Implementation patterns for creating or refactoring Beamer source; the communication discipline comes from `SKILL.md`.

Copyable examples live in `<skill-dir>/assets/beamer-starter-template.tex`. Keep reference examples short; extend the template when an idiom needs code.

## Preamble And Theme

The starter template is the house preamble: 16:9, metropolis theme with the Mondrian palette, frame-title and title-page templates, tikz list markers, top navigation bar, `appendixnumberbeamer`, and semantic commands (`\slidelink`, `\includeifexists`, `\mathhighlight` (math-only highlight box, MondrianRed!15 background), deck-wide `\semA`/`\semB` semantic colors, `L`/`C`/`R` column types). Copy it for new decks instead of assembling these choices by hand. Incremental reveal is opt-in per list (`[<+->]`), not a deck-wide default — reveal where the spoken argument needs it.

Adapting an existing deck that cannot adopt the template wholesale:

- Prefer 16:9 (`aspectratio=169`) unless the venue requires otherwise.
- Pick a small color vocabulary with stable meanings: current focus, secondary/de-emphasized text, links/backup navigation.
- Define small semantic commands for repeated visual patterns (backup links, highlight boxes, missing-figure placeholders) instead of hand-styling each instance; lift them from the template where they fit.
- Remove navigation symbols unless they serve a purpose; keep slide numbers when audience questions benefit from location.

## Frame Structure

- `\begin{frame}{Takeaway or purpose}` when the title can carry the point.
- `[label=...]` on frames needing backup links or `\againframe`.
- `[noframenumbering]` for appendix/backup frames that should not count in the main talk length.
- `\section` and optional roadmap returns to reset audience context, not merely to mirror paper sections.
- One communication job per main frame: setup, takeaway, evidence, mechanism, transition, or recovery.

## Frame Reuse

- `[label=name]` on a frame to be shown again — roadmap, agenda, recurring framework slide.
- `\againframe{name}` repeats the full frame; `\againframe<overlay>{name}` repeats one overlay state.
- `[noframenumbering]` on repeated roadmap frames that should not inflate the slide count.
- Overlay-specific alerts in the original roadmap let repeated versions highlight the current section.
- Reuse stable orientation frames; duplicate only when the repeat needs materially different content.

## Fast Iteration

- Label frames while developing: `\begin{frame}[label=model-slide]{...}`.
- `\includeonlyframes{model-slide,roadmap}` in the preamble compiles only the listed labeled frames.
- Comment out `\includeonlyframes{...}` before final builds.
- Repeated frames: include the original labeled frame in `\includeonlyframes` — `\againframe` depends on it.
- Debug layout and overlays with subset compiles, then run a full compile before handoff: slide numbers, navigation, references, and appendix links behave differently in the full deck.

## Layout Tools

- `columns` for two genuinely parallel objects: model vs data, figure vs takeaway, table vs interpretation. Not for squeezing unrelated content onto one slide.
- `overlayarea` or fixed-height boxes when overlays would otherwise shift content.
- `overprint` for mutually exclusive text/equation/caption variants in one location.
- Small negative vertical spacing only after rendering confirms it is needed; shorten content first.
- No `\resizebox` on text or equations (see SKILL.md Core Principle).

## Figures, Tables, And Equations

Simplification principles — what to show, what to move to backup — are in SKILL.md §Simplification.

- Figures: make the intended comparison visible through title, annotation, crop, or highlight; the audience should not have to discover it.
- `\underbrace`, `\alert`, and aligned equations connect equation parts to text. Keep labels short.

## Navigation And Backup

- Hyperlink backup slides a live question may need.
- Put an explicit "Back" link on backup frames.
- Keep backup frame titles specific enough for the speaker to find them quickly.
- Exclude backup slides from main numbering where possible.

## Assets And Robustness

- Wrap optional figures in a missing-figure placeholder command when drafts circulate before all figures exist.
- Keep figure paths stable relative to the deck source.
- Run `uv run --script <skill-dir>/scripts/check_slide_layout.py` after Beamer edits affecting text length, overlays, figures, equations, or tables.
- On a flagged page, inspect the rendered page or simplify the source before adding spacing hacks.
