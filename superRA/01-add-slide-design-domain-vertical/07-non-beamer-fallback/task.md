---
title: "State the Non-Beamer Fallback Path"
status: approved
depends_on:  []
tags: []
output:
  - skills/slide-design/SKILL.md
created: 2026-06-12
---

## Objective

The skill description triggers on PowerPoint, Keynote, and browser slides, but every IMPLEMENT-stage reference, the starter template, the layout checker, and the checklist's build gate are Beamer-only — an agent dispatched on a non-Beamer deck has no stated load set. Add an explicit fallback so the trigger surface matches what the skill delivers.

- One short note in `SKILL.md` (adjacent to the stage-scoped reference table): for non-Beamer decks, the Core Principle, Audience Context Discipline, Techniques, and the non-Beamer-specific checklist items apply; the Beamer references, starter template, and `check_slide_layout.py` do not; the build/layout `[BLOCKING]` item is read as "the deck renders or exports without overflow or unresolved placeholders, verified in the target tool."
- Principles-only by design — no new references, no non-Beamer tooling.

Validation: passes the `CLAUDE.md §Teach the Protocol` DRY and Necessity tests; an agent dispatched on a PowerPoint task can determine its applicable references and gates from `SKILL.md` alone.

## Results

One edit to [skills/slide-design/SKILL.md](../../../skills/slide-design/SKILL.md): added a bolded non-Beamer note directly after the stage-scoped reference table (before `§Core Principle`). The note states:

- Core Principle, Audience Context Discipline, Techniques, and non-Beamer-specific checklist items apply to non-Beamer decks.
- Beamer references, starter template, and `check_slide_layout.py` do not apply.
- The build/layout `[BLOCKING]` item is reinterpreted as "renders or exports without overflow or unresolved placeholders, verified in the target tool."

DRY/Necessity check: this is new behavior-shaping content (an agent dispatched on a PowerPoint task had no way to determine its applicable references from SKILL.md before this note). No new references or tooling added — principles-only as specified.
