---
title: "Single-Source Slide-Design Reference Content"
status: approved
depends_on: []
tags: [retrospective]
created: 2026-06-11
updated: 2026-06-11
---

## Objective

Apply the CLAUDE.md §Teach the Protocol DRY gate across the slide-design references: every rule stated once in its owning file, pointers elsewhere.

- The `\resizebox`-on-text ban lives only in `SKILL.md §Core Principle`; `beamer-techniques.md` and `layout-checks.md` keep one-line pointers to it instead of restating the rationale.
- Sections that duplicate `SKILL.md` or the starter template are removed rather than maintained as second copies: the `Beamer Fix Patterns` section in `layout-checks.md` (duplicated `SKILL.md §Simplification` and the techniques reference), the `Overlay Companion` section in `beamer-techniques.md` (duplicated the stage-scoped reference table in `SKILL.md`), the cross-pointer sentence and the template bullet list in `beamer-overlays.md`, the "keep prior context visible" design rule in `beamer-overlays.md` (duplicated `SKILL.md §Attention Management`), and the main-vs-backup checklist lines in `integration.md` (duplicated `SKILL.md §Context Engineering`; backup-slide numbering is carried by the template's `appendixnumberbeamer`).

Validation: no behavioral rule is lost — each removed line is either still stated in its owning file or carried by the template.

## Results

### Key Findings

- `beamer-techniques.md` and `layout-checks.md` now reference the `\resizebox` ban as "(see SKILL.md Core Principle)"; the full statement with rationale and the font-size-command exception exists only in `SKILL.md`.
- `layout-checks.md` lost its `Beamer Fix Patterns` section; the fix vocabulary (shorten, split, move to backup) remains in `SKILL.md §Simplification` and in the per-finding guidance under `layout-checks.md §Interpreting Findings`.
- `beamer-overlays.md` lost the itemized template feature list (the template's own comment block is the authoritative example index) and the duplicated design rule about keeping prior context visible.
- `integration.md` lost two checklist lines whose content is owned by `SKILL.md` (main-vs-backup split) and the starter template (`appendixnumberbeamer` slide counting).

### Notes

- This pass deduplicates the restatements introduced when the `\resizebox` ban was added in commit `d81de4bd` across three files at once.
