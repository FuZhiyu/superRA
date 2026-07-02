---
title: "Slide Design Domain Vertical"
status: approved
depends_on: []
---

## Objective

Own the slide-design domain vertical. `skills/slide-design/` teaches research slide communication — audience-context discipline, attention management, simplification, and the communication-vs-rigor tradeoff — with Beamer implementation support one level down in stage and technique references, a reusable starter template, and a nonvisual layout-triage script. The vertical is wired into the skill discovery surfaces (`skills/using-superra/SKILL.md`, the `skills/superplan/SKILL.md` Phase 2 verticals table, `skills/CATEGORIES.md`, `README.md`) and the skill-triggering tests.

## Results

The `skills/slide-design/` domain vertical is complete and landed on `main` via PR #35. `SKILL.md` carries the trigger metadata, the communication principles, and the shared quick-checklist walk; depth lives in `references/planning.md`, `references/integration.md`, `references/layout-checks.md`, `references/beamer-techniques.md`, and `references/beamer-overlays.md`, with a stated fallback path for non-Beamer decks.

Reusable Beamer assets: `assets/beamer-starter-template.tex` (house Mondrian chrome with `highlight` folded into the semantic palette, roadmap-frame reuse, overlay commands, backup links, `\includeonlyframes` fast iteration) and `scripts/check_slide_layout.py` (uv script) for cheap nonvisual triage — compile errors, missing assets including `\includeifexists` placeholders, overfull boxes, likely wrapped bullets, text near slide boundaries, and rendering of flagged pages for visual follow-up.

Discovery wiring is registered in `skills/using-superra/SKILL.md`, the `skills/superplan/SKILL.md` Phase 2 verticals table, `skills/CATEGORIES.md`, and `README.md`, and protected by the skill-trigger prompt `tests/skill-triggering/prompts/slide-design.txt` wired into `tests/skill-triggering/run-all.sh`. Nine refinement rounds — starter-template adoption, layout-checker upgrades, reference dedup, Mondrian chrome and palette folds, the shared checklist walk, resizebox scope reconciliation, and the non-Beamer fallback — are folded into these shipped surfaces.
