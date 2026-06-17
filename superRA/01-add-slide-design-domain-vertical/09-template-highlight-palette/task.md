---
title: "Fold highlight Into the Mondrian Palette"
status: approved
depends_on:  []
tags: []
input:
  - skills/slide-design/assets/beamer-starter-template.tex
output:
  - skills/slide-design/assets/beamer-starter-template.tex
created: 2026-06-12
---

## Objective

The starter template's `\highlight` uses ad-hoc `red!20` — outside the four-color vocabulary the preamble declares as "the deck's whole color vocabulary," and exactly what the Quick Checklist's ad-hoc-color `[ADVISORY]` warns against. It also wraps its argument in math mode (`$\displaystyle#1$`) despite the generic name.

- The background derives from the Mondrian palette (e.g. `MondrianRed!15`); a comment states the math-only contract, or the command is renamed so the contract is visible in the name — implementer's choice. If renamed, update the semantic-command inventory in `references/beamer-techniques.md §Preamble And Theme` and any in-template usage.

Validation: the template compiles and `check_slide_layout.py` reports no error/warning findings (the known info-level `possible-wrap` false positives recorded in `01-beamer-starter-template` are acceptable).

## Results

Two files edited:

**[skills/slide-design/assets/beamer-starter-template.tex](../../../skills/slide-design/assets/beamer-starter-template.tex):**
- Renamed `\highlight` to `\mathhighlight` (contract visible in name).
- Changed background from ad-hoc `red!20` to `MondrianRed!15` (within the Mondrian palette).
- Added a two-line comment documenting: math-only argument contract, Mondrian palette sourcing.

**[skills/slide-design/references/beamer-techniques.md](../../../skills/slide-design/references/beamer-techniques.md):**
- `§Preamble And Theme` semantic-command inventory updated: `\highlight` replaced with `\mathhighlight (math-only highlight box, MondrianRed!15 background)`.

No in-template usage sites needed updating (`\highlight` was defined but not used in the demo frames).

**Validation output:**

```
[info] possible-wrap page 6: ...
[info] possible-wrap page 7: ...
```

Template compiles; `check_slide_layout.py` reports no error/warning findings. Only the two known info-level `possible-wrap` false positives are present.
