---
title: "Layout Checker: Detect includeifexists Placeholders and Document Heuristic Calibration"
status: approved
depends_on:  []
tags: []
script: skills/slide-design/scripts/check_slide_layout.py
output:
  - skills/slide-design/scripts/check_slide_layout.py
  - skills/slide-design/references/layout-checks.md
created: 2026-06-12
---

## Objective

The house template's `\includeifexists` deliberately swallows missing figures, so they never produce the "LaTeX Warning: File ... not found" line that `parse_log` matches — a draft full of placeholder boxes passes the missing-asset check clean, yet `references/integration.md`'s gate ("missing figures fixed or explicitly justified") leans on this checker. Separately, the wrap/boundary heuristics carry calibration constants tuned to the house template without saying so.

- **Placeholder detection.** The bbox pass flags any page whose extracted text contains the placeholder marker rendered by `\includeifexists` ("Figure not available:") as a `missing-asset` finding (warning severity, page-numbered), making the integration gate enforceable by the checker for house decks.
- **Calibration notes.** The heuristic constants (7–22pt line-gap window, 8pt continuation indent, 0.97/0.96 boundary fractions, the heading regex) get a source comment stating they are calibrated to the house template (10pt metropolis, `\onehalfspacing`) and may misfire on other themes or font sizes; `references/layout-checks.md §Interpreting Findings` gets one line setting the same expectation so agents do not read false negatives on foreign decks as evidence of health.

Validation: a smoke deck using `\includeifexists` with a nonexistent figure path is flagged as `missing-asset`; the unmodified starter template stays clean (no new error/warning findings; the known info-level `possible-wrap` false positives recorded in `01-beamer-starter-template` are unchanged).

## Results

Two files edited:

**[skills/slide-design/scripts/check_slide_layout.py](../../../skills/slide-design/scripts/check_slide_layout.py):**
- Added `detect_placeholder_pages(bbox_path)` function that reconstructs page text from bbox word data and flags any page containing "Figure not available:" as a `missing-asset` finding (warning severity, page-numbered). Called first inside `detect_layout_issues`.
- Added calibration comments on the heuristic constants: the 7–22pt line-gap window, 8pt continuation indent, 0.97/0.96 boundary fractions are annotated as "calibrated to the house template (10pt metropolis, `\onehalfspacing`)."
- Added a top-level comment to `detect_layout_issues` warning that the heuristics may misfire on other themes or font sizes.

**[skills/slide-design/references/layout-checks.md](../../../skills/slide-design/references/layout-checks.md):**
- `§Interpreting Findings`: added a paragraph at the top of the section stating the heuristics are calibrated to the house template and may produce false negatives/positives on other themes or font sizes.
- `missing-asset` entry: added note that `\includeifexists` placeholder boxes are also flagged as `missing-asset` warnings by the bbox pass.

**Validation output:**

Smoke deck (missing `\includeifexists` figure path):
```
[warning] missing-asset page 1: Placeholder box detected (figure not available) on page 1
[warning] near-boundary page 1: Text appears close to a slide boundary
exit code 1
```
Placeholder correctly flagged as `missing-asset` warning at page 1.

Unmodified starter template:
```
[info] possible-wrap page 6: ...
[info] possible-wrap page 7: ...
```
No new error/warning findings; only the two known info-level `possible-wrap` false positives from `01-beamer-starter-template` are present.

### Notes

- Integration protection (researcher decision, 2026-06-12): script-level per the vertical's convention — verification commands recorded above, independently re-run by reviewer and orchestrator; no drift-test files added for the placeholder detection.
