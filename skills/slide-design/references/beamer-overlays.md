# Beamer Overlays

Use this reference when writing or reviewing Beamer slides with incremental reveal, highlights, stable technical walkthroughs, or backup-slide navigation.

## Template

Use `assets/beamer-starter-template.tex` as the copyable starting point. Its overlay command reference block and demo frames are the authoritative examples for the idioms below.

## Choosing Commands

- Use `[<+->]` on `itemize` or `enumerate` for a normal step-by-step list.
- Use `<.->` on subitems when they should appear with the current parent rather than consume a new reveal step.
- Use `\pause` for simple paragraph-level reveals; avoid it inside dense technical frames where explicit overlay numbers are easier to audit.
- Use `\only<N>{...}` when alternative content should take no space on other overlays.
- Use `\visible<N>{...}` or `\uncover<N>{...}` when the layout should not jump as content appears.
- Use `overprint` when several explanations, equations, or captions must occupy the same visual location across overlays.
- Use explicit overlay numbers for equations and dense diagrams; implicit counters become hard to review once the frame has many moving pieces.

## Design Rules

- Reveal at the pace of the spoken argument, not at the pace of the source code.
- Highlight only the current object or relationship. Multiple simultaneous alerts should mean "these are connected now."
- Hide or de-emphasize old details after they stop supporting the current point.
- Avoid layout jumps in technical walkthroughs; use `overprint`, `overlayarea`, `\visible`, or fixed-height boxes.
- Put expert-only derivation steps behind a backup link instead of making the main frame carry every case.

## Review Checks

- Every overlay step has a communication purpose: reveal, focus, compare, hide, or navigate.
- The audience can understand overlay `N` without reading content scheduled for overlay `N+1`.
- Alerts and colors are consistent with the deck's visual vocabulary.
- Links to backup frames work, and backup frames are outside the main slide count when possible.
