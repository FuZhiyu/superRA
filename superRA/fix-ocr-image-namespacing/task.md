---
title: "Fix per-paper image namespacing in mistral-pdf-to-markdown"
status: not-started
depends_on: []
---

## Objective
Fix a filename-collision bug in `skills/mistral-pdf-to-markdown`. `save_images()` writes every conversion's extracted figures into a single shared `<output_dir>/images/` directory, numbering from `img-0` each run. When multiple papers are converted into the **same output folder** — the normal case for a paper collection — later conversions silently overwrite the earlier papers' identically-named `img-N.jpeg` files, and the in-markdown reference `](images/img-N` is ambiguous across papers. Only the embedded figure images are affected; each paper's OCR'd text/equations live in its own `.md` and are intact.

Namespace extracted images **per paper, keyed on the output markdown filename stem**, so concurrent papers in one folder never collide.

### Deliverables
1. **`scripts/convert_pdf_to_markdown.py`** — write images to `<output_dir>/images/<md-stem>/img-N.jpeg` (subfolder = output `.md` stem), and rewrite the in-markdown image paths to the matching `](images/<md-stem>/img-N` form. The current flat `](img- → ](images/img-` rewrite (line ~226) and the fixed `images/` dir in `save_images()` (lines ~158–160, ~176) are the two sites to change.
2. **Collision-safe reconvert helper** — a batch/directory mode (e.g. `--reconvert-dir <dir>` or accepting multiple input PDFs) that regenerates figures for already-converted papers under the new per-paper layout, so an existing damaged collection can be repaired by pointing the tool at it. Re-OCR is the only image source, so this re-calls the Mistral API and needs the key — the helper only adds the capability; the researcher runs it on their own PDFs.
3. **`SKILL.md`** — document the per-paper image subfolder layout.
4. **Regression test** — converting two papers into the **same output directory** produces disjoint image sets under separate `images/<stem>/` subfolders with zero overwrite, and each `.md`'s image references resolve to its own subfolder. Runs **offline** against a mocked OCR response — no Mistral key, no network.

### Validation criteria
- Two papers → same output dir → no image is overwritten; each `.md` references only its own `images/<stem>/` subfolder.
- The in-markdown image-path rewrite matches the on-disk per-paper layout (no dangling references).
- Single-paper conversion still works; the layout change is documented in `SKILL.md`.
- The regression test runs with no network and no API key (mock the OCR response object).
- No secret leakage; key still read from env / shared config / `Notes/.env` only.

### Context
Skill-creation work in the **public** superRA repo — the test must use synthetic/mocked OCR data, never real paper titles, counts, or library data. Load `skill-creator` before editing `SKILL.md`. The bug root cause is `save_images()` deriving `images_dir` from `output_path.parent` alone and numbering `image_count` from 0 per call, with no per-paper key.

The damaged research collection (already-converted papers whose figures collided) lives in the researcher's **separate** project, not this repo. Remediation there — re-running the fixed skill on the affected PDFs — is a researcher-run action outside this task tree; this task only ships the durable fix and the reconvert capability.

## Planner Guidance
Subfolder-by-stem (`images/<stem>/img-N.jpeg`) is the chosen scheme over a flat filename prefix — it keeps one paper's figures in one directory and reads cleanly. Keep the change surgical: the two edit sites in `convert_pdf_to_markdown.py` plus the path-rewrite string. The reconvert helper (deliverable 2) is droppable if the researcher decides on a skill-fix-only scope — it is additive and the core collision fix stands without it.
