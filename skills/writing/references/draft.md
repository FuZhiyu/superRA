# Draft Mode

> Load when the request is to write new prose — "draft the methods section", "write up the results from these notes", "compose the introduction from this outline". Output is new prose, structurally and stylistically self-checked before handoff.

## Workflow

1. **Gather inputs.** Notes, outline, results tables, prior section drafts the new prose must connect to, the surrounding sections in the document. If a critical input (e.g., the results table the section is supposed to describe) is missing, ask before drafting. If a handoff doc carrying `## Project Conventions` is in play, read its writing-side rows and align to them; if those rows are empty on the first draft pass against the paper, populate them before drafting (per `SKILL.md §Project Conventions in the handoff doc / CLAUDE.md`).
2. **Build the outline first.** Per `structure.md` (Pyramid Principle): governing idea, MECE support, section-level anatomy appropriate to section type (intro / methods / results / conclusion). The outline is one level deeper than what will appear as headings — every paragraph has a stated purpose before it has prose.
3. **Draft.** One paragraph at a time. Each paragraph carries a topic sentence at the front (or a deliberate exception; `style.md` §Paragraph-level rules names them). Old → new information flow within the paragraph. Cross-references and citations are placed as the prose is written, not retrofitted later.
4. **Self-check** against `style.md` §Gated Checklist (sentence-level rules) and `structure.md` §Gated Checklist (section anatomy). The self-check is a real walk, not a rubber stamp; if a rule fires and the prose doesn't comply, fix it before handoff.
5. **Build.** Compile the document; resolve cross-reference breaks before handoff. See `refactor-and-compile.md` §Compile.

## Intent comments

Each drafted paragraph ships with an intent comment on the line immediately above it, recording the paragraph's purpose for the reader:

- `.tex` → `% intent: <one-sentence purpose>`
- `.md` / `.qmd` → `<!-- intent: <one-sentence purpose> -->`

Write the intent first as the drafting brief — distilled from the user's request — then write prose that fulfills it. The comment ships with the prose; it is part of the draft, not scaffolding.

Example (LaTeX):

```
% intent: establish that the puzzle survives the standard risk-based explanation.
Standard risk-based stories predict ...
```

## Workflow coupling

Whole-section drafts are multi-task work — route through `planning-workflow` (`PLAN.md` + `RESULTS.md`). Paragraph-scale drafts (an abstract from the body, a paragraph from notes) terminate at edit + commit.

## Match the author's tone

When the new prose joins a document the author is already writing, read enough of the surrounding text to absorb the author's tone before drafting. Match contractions, sentence-length variance, technical register, and hedging style — your prose should not be visibly LLM-flavored next to the author's. If the document has no surrounding text yet (greenfield draft), the author's instructions and any sample text they provide define the tone.
