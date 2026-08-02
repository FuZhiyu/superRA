# Beamer Overlays

Load when writing or reviewing Beamer slides with incremental reveal, highlights, stable technical walkthroughs, or backup-slide navigation.

## Template

`<skill-dir>/assets/beamer-starter-template.tex` is the copyable starting point; its overlay command reference block and demo frames are the authoritative examples for the idioms below.

## Choosing Commands

- `[<+->]` on `itemize` or `enumerate` for a normal step-by-step list.
- `<.->` on subitems that should appear with the current parent rather than consume a reveal step.
- `\pause` for simple paragraph-level reveals; avoid it in dense technical frames, where explicit overlay numbers are easier to audit.
- `\only<N>{...}` when alternative content should take no space on other overlays.
- `\visible<N>{...}` or `\uncover<N>{...}` when the layout should not jump as content appears.
- `overprint` when several explanations, equations, or captions occupy one visual location across overlays.
- Explicit overlay numbers for equations and dense diagrams — implicit counters get hard to review once a frame has many moving pieces.

## Design Rules

- Reveal at the pace of the spoken argument, not of the source code.
- Highlight only the current object or relationship. Simultaneous alerts mean "these are connected now."
- Hide or de-emphasize old details once they stop supporting the current point.
- Avoid layout jumps in technical walkthroughs — `overprint`, `overlayarea`, `\visible`, or fixed-height boxes.
- Put expert-only derivation steps behind a backup link instead of making the main frame carry every case.

## Review Checks

- Every overlay step has a communication purpose: reveal, focus, compare, hide, or navigate.
- The audience can understand overlay `N` without reading content scheduled for overlay `N+1`.
- Alerts and colors are consistent with the deck's visual vocabulary.
- Links to backup frames work, and backup frames are outside the main slide count when possible.
