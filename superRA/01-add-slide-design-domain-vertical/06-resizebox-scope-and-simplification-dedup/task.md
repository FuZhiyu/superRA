---
title: "Reconcile resizebox Scope Drift and Dedup Simplification Guidance"
status: approved
depends_on:  []
tags: []
output:
  - skills/slide-design/SKILL.md
  - skills/slide-design/references/beamer-techniques.md
  - skills/slide-design/references/layout-checks.md
created: 2026-06-12
---

## Objective

Finish the single-sourcing pass started by `03-reference-dedup` where copies have since drifted or paraphrases remain, per the `CLAUDE.md §Teach the Protocol` DRY gate.

- **`\resizebox` scope drift.** `SKILL.md §Core Principle` becomes the complete authoritative statement: the ban covers text **and equations**, and the standalone-figure/diagram exemption currently stated only in `beamer-techniques.md §Layout Tools` moves into the Core Principle. The one-line pointers in `beamer-techniques.md` and `layout-checks.md` keep no scope qualifiers of their own — a bare "(see SKILL.md Core Principle)" pointer. The Quick Checklist `[BLOCKING]` item shortens to the rule name plus pointer rather than restating the full rationale in the same file.
- **Simplification paraphrase.** `beamer-techniques.md §Figures, Tables, And Equations` keeps only Beamer-specific mechanics (connecting equation parts to text with `\underbrace`/`\alert`/aligned equations, annotation/crop/highlight devices for figures); the lines that paraphrase `SKILL.md §Simplification` (show only needed columns/rows, minimum live expression, derivations/robustness to backup) are removed in favor of a pointer.
- **Stage-table echoes.** `SKILL.md §Layout Triage` and `§Beamer Implementation` drop load-condition sentences already carried by the stage-scoped reference table, keeping only what the table does not carry (the template-first instruction; the triage-evidence framing).

Validation: no behavioral rule is lost — each removed line is stated in its owning file; the `\resizebox` rule's full scope (text + equations ban, figure/diagram exemption, font-size-command exception) appears in exactly one place.

## Results

Three files edited:

**[skills/slide-design/SKILL.md](../../../skills/slide-design/SKILL.md):**
- `§Core Principle`: expanded `\resizebox` ban from "text" to "text or equations"; added the figure/diagram exemption sentence that previously lived only in `beamer-techniques.md`. Full scope (text + equations ban, figure/diagram exemption, font-size-command exception) is now in exactly one place.
- `§Quick Checklist` `[BLOCKING]` resizebox item: shortened to "No `\resizebox` on text or equations (see Core Principle)" — rule name plus pointer, no restatement of rationale.
- `§Layout Triage`: replaced load-condition sentence (already in the stage-scoped reference table) with "triage evidence interpretation and layout guidance" framing that the table does not carry.
- `§Beamer Implementation`: removed "When editing Beamer source, load `references/beamer-techniques.md` first. Load `references/beamer-overlays.md` as the focused companion…" — already covered by the stage-scoped reference table.

**[skills/slide-design/references/beamer-techniques.md](../../../skills/slide-design/references/beamer-techniques.md):**
- `§Layout Tools`: removed scope qualifiers from `\resizebox` line; left bare pointer "(see SKILL.md Core Principle)".
- `§Figures, Tables, And Equations`: removed paraphrase lines (tables/columns/rows, minimum live expression, derivations to backup) in favor of a pointer to `SKILL.md §Simplification`; kept only Beamer-specific mechanics (figure annotation, `\underbrace`/`\alert`).

**[skills/slide-design/references/layout-checks.md](../../../skills/slide-design/references/layout-checks.md):**
- `§Interpreting Findings` overfull-hbox entry: updated from "on text" to "on text or equations" to match the authoritative Core Principle scope.

No behavioral rule is lost: every removed line is stated in its owning file.
