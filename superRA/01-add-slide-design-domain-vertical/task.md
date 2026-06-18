---
title: "Add Slide Design Domain Vertical"
status: approved
depends_on: []
tags: []
script: skills/slide-design/scripts/check_slide_layout.py
input:
  - /Users/zhiyufu/Dropbox/fuzhiyu.me/blogs/slide_design_guide/slide_deck_design.tex
  - inspo/slide-design-guide/slide_deck_design.tex
output:
  - skills/slide-design/
  - tests/skill-triggering/prompts/slide-design.txt
created: 2026-05-26
---

## Objective

- **Step 1: Create the skill surface**
  Add `skills/slide-design/SKILL.md` with trigger metadata, stage-scoped references, audience-context discipline, slide communication principles, techniques, checklist, and Beamer implementation pointers.

- **Step 2: Add stage and technique references**
  Add planning, integration, layout-check, Beamer-technique, and Beamer-overlay references. Keep details one level below `SKILL.md`; point to the template for code examples.

- **Step 3: Add reusable Beamer assets and layout triage**
  Add a minimal Beamer overlay template demonstrating roadmap frame reuse, overlay commands, backup links, and `\includeonlyframes` fast iteration. Add `check_slide_layout.py` for LaTeX log parsing and PDF bounding-box triage.

- **Step 4: Wire skill discovery and docs**
  Update `skills/using-superra/SKILL.md`, `skills/superplan/SKILL.md`, `skills/CATEGORIES.md`, `README.md`, and add/wire `tests/skill-triggering/prompts/slide-design.txt`.

- **Step 5: Verify implementation**
  Run syntax, layout, ignore, and diff checks. Leave any environment-specific tooling limitation recorded.

## Results

**Status:** Completed (Task 1 approved 2026-05-12).

### Key Findings

- Added a new `slide-design` domain skill focused on audience-context discipline, live communication, context engineering, attention management, simplification, and the communication-vs-rigor tradeoff.
- Added Beamer-specific implementation support through `references/beamer-techniques.md`, `references/beamer-overlays.md`, and `assets/beamer-starter-template.tex`.
- Added `scripts/check_slide_layout.py` for cheap nonvisual triage of Beamer/PDF layout issues: compile errors, missing assets, overfull boxes, likely wrapped bullets, and text near slide boundaries.
- Wired the vertical into `using-superra`, `skills/superplan/SKILL.md` (Phase 2 "Currently implemented verticals" table), `skills/CATEGORIES.md`, `README.md`, and the skill-triggering prompt list. On this extraction branch the `superplan` Phase 2 verticals-table row is now actually present (the integration review of the source branch found the original task had claimed this wiring but never added it).

### Files Created

- `skills/slide-design/SKILL.md`
- `skills/slide-design/references/planning.md`
- `skills/slide-design/references/beamer-techniques.md`
- `skills/slide-design/references/beamer-overlays.md`
- `skills/slide-design/references/layout-checks.md`
- `skills/slide-design/references/integration.md`
- `skills/slide-design/assets/beamer-starter-template.tex`
- `skills/slide-design/scripts/check_slide_layout.py`
- `tests/skill-triggering/prompts/slide-design.txt`

### Files Updated

- `README.md`
- `skills/CATEGORIES.md`
- `skills/superplan/SKILL.md`
- `skills/using-superra/SKILL.md`
- `tests/skill-triggering/run-all.sh`

### Verification

- `python3 -m py_compile skills/slide-design/scripts/check_slide_layout.py` passed.
- `skills/slide-design/scripts/check_slide_layout.py --help` passed.
- `uv run --script skills/slide-design/scripts/check_slide_layout.py skills/slide-design/assets/beamer-starter-template.tex --no-fail` ran clean apart from two known info-level possible-wrap false positives.
- Beamer smoke test with a missing `\includeifexists` figure flagged `missing-asset`.
- `bash -n tests/skill-triggering/run-all.sh` passed.
- `git diff --check` passed.
- `git diff main --stat` shows only slide-design surfaces.

### Notes

- Integration protection is script-level rather than result-drift-based: the change adds a skill-trigger prompt, wires it into `run-all.sh`, validates the helper script, and verifies the bundled Beamer template.
- The source guide is copied to ignored `inspo/slide-design-guide/slide_deck_design.tex` on the development environment; it is local reference material, not a packaged skill artifact.
- **Provenance.** This vertical was extracted from branch `superRA-slides-making` (post-sync state, commit `c96f8bcc`) onto `slide-design-vertical`, a fresh branch cut from `main`. The extraction ports the slide-design skill directory, the wiring rows (`using-superra`, `superplan` Phase 2 verticals table, `CATEGORIES.md`, `README.md`, skill-triggering test), and this vertical's task tree, so the branch's diff against `main` contains only slide-design work. The development branch retains the original better-handoff lineage; this branch owns the PR to `main`.
