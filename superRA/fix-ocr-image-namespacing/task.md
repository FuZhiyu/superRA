---
title: "Fix per-paper image namespacing in mistral-pdf-to-markdown"
status: approved
depends_on: []
---

## Objective
Fix a filename-collision bug in `skills/mistral-pdf-to-markdown`. `save_images()` writes every conversion's extracted figures into a single shared `<output_dir>/images/` directory, numbering from `img-0` each run. When multiple papers are converted into the **same output folder** — the normal case for a paper collection — later conversions silently overwrite the earlier papers' identically-named `img-N.jpeg` files, and the in-markdown reference `](images/img-N` is ambiguous across papers. Only the embedded figure images are affected; each paper's OCR'd text/equations live in its own `.md` and are intact.

Namespace extracted images **per paper, keyed on the output markdown filename stem**, so concurrent papers in one folder never collide.

### Deliverables
1. **`scripts/convert_pdf_to_markdown.py`** — write images to `<output_dir>/images/<md-stem>/img-N.jpeg` (subfolder = output `.md` stem), and rewrite the in-markdown image paths to the matching `](images/<md-stem>/img-N` form. The current flat `](img- → ](images/img-` rewrite (line ~226) and the fixed `images/` dir in `save_images()` (lines ~158–160, ~176) are the two sites to change.
2. **`SKILL.md`** — document the per-paper image subfolder layout.
3. **Regression test** — converting two papers into the **same output directory** produces disjoint image sets under separate `images/<stem>/` subfolders with zero overwrite, and each `.md`'s image references resolve to its own subfolder. Runs **offline** against a mocked OCR response — no Mistral key, no network.

### Validation criteria
- Two papers → same output dir → no image is overwritten; each `.md` references only its own `images/<stem>/` subfolder.
- The in-markdown image-path rewrite matches the on-disk per-paper layout (no dangling references).
- Single-paper conversion still works; the layout change is documented in `SKILL.md`.
- The regression test runs with no network and no API key (mock the OCR response object).
- No secret leakage; key still read from env / shared config / `Notes/.env` only.

### Context
Skill-creation work in the **public** superRA repo — the test must use synthetic/mocked OCR data, never real paper titles, counts, or library data. Load `skill-creator` before editing `SKILL.md`. The bug root cause is `save_images()` deriving `images_dir` from `output_path.parent` alone and numbering `image_count` from 0 per call, with no per-paper key.

The damaged research collection (already-converted papers whose figures collided) lives in the researcher's **separate** project, not this repo. Remediation there — re-running the fixed skill on the affected PDFs (a shell loop over the per-file command) — is a researcher-run action outside this task tree; this task ships only the durable fix.

## Planner Guidance
Subfolder-by-stem (`images/<stem>/img-N.jpeg`) is the chosen scheme over a flat filename prefix — it keeps one paper's figures in one directory and reads cleanly. Keep the change surgical: the two edit sites in `convert_pdf_to_markdown.py` plus the path-rewrite string.

## Results

The collision bug is fixed by namespacing every conversion's figures under a per-paper subfolder keyed on the output `.md` filename stem. All three deliverables land.

**1 — Per-paper image layout ([convert_pdf_to_markdown.py](../../skills/mistral-pdf-to-markdown/scripts/convert_pdf_to_markdown.py)).** Two edit sites, as scoped:
- `save_images()` ([scripts/convert_pdf_to_markdown.py:162-166](../../skills/mistral-pdf-to-markdown/scripts/convert_pdf_to_markdown.py#L162-L166)) now writes to `output_path.parent / "images" / output_path.stem` instead of the shared `output_dir / "images"`. The `img-N` numbering is unchanged — it is now safe because each paper's counter lives in its own directory.
- The in-markdown rewrite ([scripts/convert_pdf_to_markdown.py:231-234](../../skills/mistral-pdf-to-markdown/scripts/convert_pdf_to_markdown.py#L231-L234)) changed from the flat `](img- → ](images/img-` to `](img- → ](images/<stem>/img-`, so references match the on-disk layout.

**2 — Documentation ([SKILL.md](../../skills/mistral-pdf-to-markdown/SKILL.md)).** Output Structure now shows the `images/<md-stem>/` tree with two example papers side by side; Key Features, Notes, and Quick Start updated to the per-paper path form.

**3 — Offline regression test ([scripts/test_image_namespacing.py](../../skills/mistral-pdf-to-markdown/scripts/test_image_namespacing.py)).** Converts two synthetic papers (`paper_alpha`, 2 figures; `paper_beta`, 3 figures) into one output directory and asserts: each paper's images land under its own `images/<stem>/` subfolder; nothing lands in a flat `images/*.jpeg`; the full image paths are disjoint across papers even though filenames overlap (`img-0.jpeg` in both); each `.md` references only its own subfolder with no surviving `](img-` flat reference; every referenced path resolves to a file on disk. It stubs `mistralai`, `pypdf`, and `dotenv` in `sys.modules` before import and monkeypatches `load_api_key`/`extract_pages`/`process_with_mistral`, so it runs with no Mistral key, no network, and no third-party deps. Uses synthetic OCR data only (a 1x1 JPEG, placeholder stems) — no real library data.

**Verification.** `python3 test_image_namespacing.py` exits 0: `OK: per-paper image namespacing holds; no overwrite, no dangling refs`. `python3 -m py_compile` passes on both scripts.

**Notes / caveats.**
- `skill-creator` is named in the task Context but is not installed in this environment, so it could not be loaded before the `SKILL.md` edit. The edit is a minimal documentation update following the repo's skill-authoring discipline (`CLAUDE.md`); flagging for the reviewer in case the skill is expected to be present.
- The single-conversion path is unchanged in shape (same `img-N` numbering, same rewrite mechanism) — only the directory prefix moved — so existing single-paper usage still works; the test's per-file conversions exercise that path.
- Secret handling is untouched: the key is still read only from env / shared config / `Notes/.env` via `load_api_key()`.
