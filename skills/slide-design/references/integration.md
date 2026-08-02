# Slide-Design Integration

Load during final deck polish or integration.

## Deck-Wide Review

- The deck route matches the audience-context inventory: setup appears before claims that require it.
- Takeaways are consistent across title, roadmap, section openers, evidence slides, and conclusion.
- Notation, colors, alert conventions, abbreviations, and visual encodings mean the same thing throughout.

## Build And Layout Gate

- The deck builds from committed source, or the final PDF comes from a documented command.
- Missing figures, overfull boxes, and likely text overflow are fixed or justified in the task record.
- Pages flagged by `uv run --script <skill-dir>/scripts/check_slide_layout.py` are inspected before final handoff.
- Links to backup slides, appendix slides, external slides, and data sources resolve where possible.

## Communication Polish

- A distracted audience member can rejoin at section starts, roadmap returns, and dense technical slides.
- Dense equations, tables, and figures reveal the intended comparison or mechanism, not just the complete object.
- Expert-facing caveats stay off the main path unless the typical audience needs them immediately.
