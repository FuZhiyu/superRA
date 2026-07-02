---
name: slide-design
description: Research slide communication. Use when creating, revising, polishing, or reviewing Beamer, PowerPoint, Keynote, or browser slide decks.
user-invocable: true
---

# Slide Design

Domain skill for research slide communication. Beamer is the first-class implementation target; principles apply across deck formats.

## Stage-Scoped References

Load per stage; do not load them all at every dispatch:

| Reference | Load when |
|---|---|
| `references/planning.md` | PLAN phase - audience-context inventory, deck objective, structure, and main-vs-backup policy. |
| `references/beamer-techniques.md` | IMPLEMENT when creating or refactoring Beamer source, frame structure, columns, figures, tables, equations, navigation, or reusable commands. |
| `references/beamer-overlays.md` | IMPLEMENT when writing Beamer overlays, incremental reveal, alerts, backup links, or stable multi-step technical slides. |
| `references/layout-checks.md` | IMPLEMENT or review when editing Beamer, checking line wraps, overflow, figures, overlays, or final PDF layout. |
| `references/integration.md` | INTEGRATE / final polish - deck-wide consistency, buildability, backup-slide hygiene, and communication review. |

For bundled scripts and assets, `<skill-dir>` is the directory containing this `SKILL.md`; substitute the real path before running commands or copying files.

**Non-Beamer decks (PowerPoint, Keynote, browser slides):** the Core Principle, Audience Context Discipline, Techniques, and the non-Beamer-specific checklist items apply. The Beamer references, starter template, and `check_slide_layout.py` do not apply. Read the build/layout `[BLOCKING]` item as "the deck renders or exports without overflow or unresolved placeholders, verified in the target tool."

## Core Principle

Slides are live communication artifacts. A slide succeeds when the audience can recover the intended point in real time, with imperfect attention and uneven background knowledge.

When rigor and live comprehension compete, preserve the truth of the claim but prioritize the version the audience can understand now. Move derivations, robustness, caveats, and expert objections to oral narration, notes, backup slides, appendix slides, or linked material when they would overload the main path.

**Never use `\resizebox` on text or equations.** `\resizebox` mechanically shrinks content to fit a box rather than making a deliberate design choice; it sacrifices visual consistency and signals that the slide is trying to say too much. When content overflows a slide, simplify the content, split the slide, or move material to backup. Exception: `\resizebox` is acceptable for standalone figures or diagrams where mechanical scaling does not hide information. Font-size commands (`\small`, `\footnotesize`, etc.) are fine as intentional design choices — for example, de-emphasizing source citations or secondary labels.

## Audience Context Discipline

The hard part is judging what the audience knows at each moment. Run an audience-context pass before optimizing wording or visual style:

- Pick a representative audience member for this talk, not an ideal reader of the paper.
- For every section and dense slide, state what the audience already knows, what they do not know yet, and what they may wrongly infer from familiar terms.
- For each visible line, ask: "What thought should this line trigger?" Then ask whether the audience has enough context to think that thought.
- If multiple fields would interpret the same phrase differently, add framing before the phrase or replace it with the intended interpretation.
- Reintroduce unusual notation, model objects, samples, and objectives when they return after a gap.

## Techniques

### Context Engineering

- Lead with the takeaway before evidence when the evidence has many plausible interpretations.
- Use section openers and roadmap returns to tell the audience what question the next block answers.
- Put the slide's purpose in the title or first line when the slide is not self-evident.
- Split main slides and backup slides by audience need: typical-audience context stays on the main path; expert completeness goes to backup.

### Attention Management

- Every visible element competes for attention. Remove, delay, gray out, shrink, or move detail that is not part of the current point.
- Use overlays when early material must remain visible for later steps; use multiple lighter slides when later steps do not need the earlier material on screen.
- Use alerts, boldface, color, and size to identify the current point and connect related text/equation pieces.
- De-emphasize sources, caveats, and secondary notes instead of letting them compete visually with the main claim.
- Design for recovery after distraction: a distracted audience member should be able to skim the slide and rejoin the talk.
- For Beamer overlay mechanics, load `references/beamer-overlays.md` and reuse `<skill-dir>/assets/beamer-starter-template.tex`.

### Simplification

- Prefer one sharp line over a formally complete sentence.
- Keep bullets short; one-line bullets are a strong default, not an absolute rule.
- Avoid three nested itemize levels on main slides.
- For equations, show the minimum expression needed for the live point; move full derivations or general forms to backup unless the derivation itself is the point.
- For tables, show only columns and rows needed for the claim; use visual emphasis for the comparison the audience should make.

## Quick Checklist

Shared checklist walked by the implementer (before DONE) and by the reviewer (as verification). `[BLOCKING]` items must be fixed for APPROVE; `[ADVISORY]` items may be reported as MINOR.

- `[BLOCKING]` Audience context is established before major claims, unusual notation, nonstandard samples, or field-specific terms. When the work runs inside a superRA task tree, verify against the audience-context inventory recorded at planning time (`references/planning.md §Audience-Context Inventory`); when no inventory exists (standalone invocation), state the assumed representative audience member in the review notes and judge against that.
- `[BLOCKING]` Each main-path slide has a clear communication role: setup, takeaway, evidence, mechanism, transition, or recovery/roadmap.
- `[BLOCKING]` Dense slides use overlays, visual cues, simplification, or a backup split to control attention.
- `[BLOCKING]` Technical rigor is not lost: omitted details are either unnecessary for the live point or available through oral narration, notes, backup slides, appendix slides, or links.
- `[BLOCKING]` No `\resizebox` on text or equations (see Core Principle).
- `[BLOCKING]` Beamer/PDF output builds when the task edits source, and no known overflow or missing-asset warnings are ignored.
- `[ADVISORY]` Main-slide bullets are mostly one line; wrapped bullets are intentionally retained only when the extra words materially help communication.
- `[ADVISORY]` Titles and first lines state the takeaway or slide purpose rather than only naming the topic.
- `[ADVISORY]` Navigation aids, slide numbers, and backup-slide numbering help the audience orient without drawing attention away from content.
- `[ADVISORY]` New visual styling stays within the deck's existing color and command vocabulary instead of introducing ad-hoc colors or one-off styling.

## Layout Triage

For Beamer decks, use `uv run --script <skill-dir>/scripts/check_slide_layout.py` when a cheap nonvisual pass is enough to catch likely line wraps, overfull boxes, missing figures, or text near slide boundaries. Load `references/layout-checks.md` for triage evidence interpretation and layout guidance.

## Beamer Implementation

Start new decks from `<skill-dir>/assets/beamer-starter-template.tex` — it carries the house design language (theme, palette, frame/title templates, list markers, semantic commands) and an overlay command reference. Do not rebuild a preamble from scratch when the template applies.
