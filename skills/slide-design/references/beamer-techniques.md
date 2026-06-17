# Beamer Techniques

Use this reference when creating or refactoring Beamer source. It covers common implementation patterns; the communication discipline still comes from `SKILL.md`.

For copyable examples, use `<skill-dir>/assets/beamer-starter-template.tex`. Keep new examples in references short; extend the template when an idiom needs code.

## Preamble And Theme

The starter template is the house preamble: 16:9, metropolis theme with the Mondrian palette, frame-title and title-page templates, tikz list markers, top navigation bar, `appendixnumberbeamer`, and semantic commands (`\slidelink`, `\includeifexists`, `\mathhighlight` (math-only highlight box, MondrianRed!15 background), deck-wide `\semA`/`\semB` semantic colors, `L`/`C`/`R` column types). Copy it for new decks instead of assembling these choices by hand. Incremental reveal is opt-in per list (`[<+->]`), not a deck-wide default — reveal where the spoken argument needs it.

When adapting an existing deck that cannot adopt the template wholesale:

- Prefer 16:9 (`aspectratio=169`) for modern seminar rooms unless the venue requires otherwise.
- Pick a small color vocabulary and assign stable meanings: current focus, secondary/de-emphasized text, links/backup navigation.
- Define small semantic commands for repeated visual patterns (backup links, highlight boxes, missing-figure placeholders) rather than hand-styling each instance; lift them from the template where they fit.
- Remove navigation symbols unless they serve a clear purpose; keep slide numbers when audience questions benefit from location.

## Frame Structure

- Use `\begin{frame}{Takeaway or purpose}` when the title can carry the point.
- Use `[label=...]` on frames that need backup links or `\againframe`.
- Use `[noframenumbering]` for appendix/backup frames that should not count in the main talk length.
- Use `\section` and optional roadmap returns to reset audience context, not merely to mirror paper sections.
- Keep one communication job per main frame: setup, takeaway, evidence, mechanism, transition, or recovery.

## Frame Reuse

- Use `[label=name]` on a frame that should be shown again, such as a roadmap, agenda, or recurring framework slide.
- Use `\againframe{name}` to repeat the full frame, or `\againframe<overlay>{name}` to repeat a specific overlay state.
- Add `[noframenumbering]` to repeated roadmap frames when they should not inflate the talk's slide count.
- Use overlay-specific alerts in the original roadmap so repeated versions can highlight the current section.
- Prefer reuse for stable orientation frames; duplicate the frame only when the repeated version needs materially different content.

## Fast Iteration

- Label frames while developing: `\begin{frame}[label=model-slide]{...}`.
- Use `\includeonlyframes{model-slide,roadmap}` in the preamble to compile only selected labeled frames.
- Comment out `\includeonlyframes{...}` before final builds.
- For repeated frames, include the original labeled frame in `\includeonlyframes`; `\againframe` depends on that source frame.
- Use subset compiles for layout and overlay debugging, then run a full compile before handoff because slide numbers, navigation, references, and appendix links can behave differently in the full deck.

## Layout Tools

- Use `columns` for two genuinely parallel objects: model vs data, figure vs takeaway, table vs interpretation. Avoid columns when they only squeeze unrelated content onto one slide.
- Use `overlayarea` or fixed-height boxes when overlays would otherwise shift content.
- Use `overprint` for mutually exclusive text/equation/caption variants in the same location.
- Use small negative vertical spacing only after rendering confirms it is needed; prefer shortening content first.
- No `\resizebox` on text or equations (see SKILL.md Core Principle).

## Figures, Tables, And Equations

For simplification principles (what to show, what to move to backup), see SKILL.md §Simplification.

- For figures, make the intended comparison visible through title, annotation, crop, or highlight; do not rely on the audience discovering it.
- Use `\underbrace`, `\alert`, and aligned equations to connect equation parts to text, but keep labels short.

## Navigation And Backup

- Use hyperlinks for backup slides when a live question may need them.
- Add an explicit "Back" link on backup frames to return to the main path.
- Keep backup frame titles specific enough that the speaker can find them quickly.
- Exclude backup slides from main numbering when possible.

## Assets And Robustness

- Wrap optional figures in a missing-figure placeholder command when drafts may circulate before all figures exist.
- Keep figure paths stable relative to the deck source.
- Run `uv run --script <skill-dir>/scripts/check_slide_layout.py` after Beamer edits that affect text length, overlays, figures, equations, or tables.
- When the checker flags a page, inspect the rendered page or simplify the source before adding spacing hacks.
