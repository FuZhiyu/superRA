# Draft Mode

> Load when the request is to write new prose — "draft the methods section", "write up the results from these notes", "compose the introduction from this outline". Output is new prose, structurally and stylistically self-checked before completion.

## Workflow

1. **Gather inputs.** Notes, outline, results tables, prior section drafts the new prose must connect to, the surrounding sections. Missing critical input (e.g., the results table the section describes): ask before drafting. `## Project Conventions` in the task tree: read its writing-side rows and align to them; rows empty on the first draft pass against the paper: populate them before drafting (per `SKILL.md §Project Conventions in the task tree / CLAUDE.md`).
2. **Build the outline first.** Per `structure.md` (Pyramid Principle): governing idea, MECE support, section-level anatomy for the section type (intro / methods / results / conclusion). The outline runs one level deeper than the headings — every paragraph has a stated purpose before it has prose.
3. **Draft.** One paragraph at a time, topic sentence at the front (or a deliberate exception per `style.md` §Paragraph-level rules), old → new information flow within the paragraph. Place cross-references and citations as the prose is written, not retrofitted.
4. **Self-check** against `style.md` §Gated Checklist (sentence-level) and `structure.md` §Gated Checklist (section anatomy) — a real walk; fix non-compliant prose before completion.
5. **Build.** Compile the document; resolve cross-reference breaks before completion (`refactor-and-compile.md` §Compile).


## Workflow coupling

Whole-section drafts are multi-task work — route through `superplan` (`superRA/` task tree). Paragraph-scale drafts (an abstract from the body, a paragraph from notes) terminate at edit + commit.

## Match the author's tone

New prose joining a document the author is already writing: read enough surrounding text to absorb their tone first. Match contractions, sentence-length variance, technicality, and hedging style — the prose should not read as visibly LLM-flavored next to the author's. Greenfield draft with no surrounding text: the author's instructions and any sample text they provide define the tone.
