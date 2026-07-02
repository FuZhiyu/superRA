---
title: "Fix per-conversion image namespacing in mistral-pdf-to-markdown"
status: approved
depends_on: []
---

## Objective
Fix a filename-collision and portability bug in `skills/mistral-pdf-to-markdown`. The converter originally wrote every conversion's extracted figures into one shared `<output_dir>/images/` directory, numbering from `img-0` each run. Converting multiple papers into the same collection folder could silently overwrite earlier `img-N.jpeg` files, and keeping markdown files separate from their images made single-paper moves fragile.

Write each conversion as a self-contained folder keyed on the requested output markdown stem:

```
<collection>/
└── <paper-stem>/
    ├── <paper-stem>.md
    └── images/
        ├── img-0.jpeg
        └── ...
```

The markdown should reference `images/img-N.jpeg`, so the paper folder can be moved or later subdivided without breaking image paths.

### Deliverables
1. **`scripts/convert_pdf_to_markdown.py`** - resolve the user-supplied output target to a conversion directory, write markdown inside that directory, write images to the directory's `images/` subfolder, and rewrite in-markdown image paths to `](images/img-N...)`.
2. **`SKILL.md`** - document the per-conversion folder layout and output-path behavior.
3. **Regression test** - converting two papers under the same collection output directory produces separate conversion folders with no overwrite, no shared collection-level images directory, and resolvable markdown image references. Runs offline against a mocked OCR response.

### Validation criteria
- Two papers -> same collection dir -> no image is overwritten; each conversion folder contains its own markdown and `images/` folder.
- The in-markdown image-path rewrite matches the on-disk conversion-local layout.
- A requested `output.md` path creates `output/output.md`; an already-foldered `output/output.md` path is not nested again.
- The regression test runs with no network and no API key.
- No secret leakage; key still read from env / shared config / `Notes/.env` only.

### Context
Skill-creation work in the public superRA repo - the test must use synthetic/mocked OCR data, never real paper titles, counts, or library data. Load `skill-creator` before editing `SKILL.md`.

The damaged research collection lives in the researcher's separate project, not this repo. Remediation there - re-running the fixed skill on the affected PDFs - is outside this task tree.

## Planner Guidance
The original `images/<stem>/img-N.jpeg` design fixed collisions but left each markdown file outside its asset boundary. The revised design makes the paper folder the artifact boundary, which is easier to move and can support later section-level subdivision.

## Results

Implemented and integration-reviewed the per-conversion folder layout. A requested markdown target such as `Output/paper.md` now writes a self-contained artifact at `Output/paper/paper.md`, with images under `Output/paper/images/` and markdown references rewritten to `images/img-N.jpeg`; already-foldered markdown paths and directory targets are resolved explicitly in [convert_pdf_to_markdown.py](../../skills/mistral-pdf-to-markdown/scripts/convert_pdf_to_markdown.py).

The skill documentation now describes the self-contained output contract in [SKILL.md](../../skills/mistral-pdf-to-markdown/SKILL.md), and the offline regression in [test_image_namespacing.py](../../skills/mistral-pdf-to-markdown/scripts/test_image_namespacing.py) covers two papers converted under one collection directory, path-resolution variants, absence of a shared collection-level `images/` directory, and image references resolving relative to each paper's markdown file.

**Validation.**
- `uv run --with pytest python -m pytest skills/mistral-pdf-to-markdown/scripts/test_image_namespacing.py`
- `python3 -m py_compile skills/mistral-pdf-to-markdown/scripts/convert_pdf_to_markdown.py skills/mistral-pdf-to-markdown/scripts/test_image_namespacing.py`
- `uv run --script skills/mistral-pdf-to-markdown/scripts/convert_pdf_to_markdown.py --help`
- `git diff --check -- skills/mistral-pdf-to-markdown/SKILL.md skills/mistral-pdf-to-markdown/scripts/convert_pdf_to_markdown.py skills/mistral-pdf-to-markdown/scripts/test_image_namespacing.py superRA/fix-ocr-image-namespacing/task.md`

**Final diff self-check:** `git diff origin/main..HEAD`; surviving hunks are the converter output-path/layout change, matching skill documentation, an offline regression test, and this task record. The only review cleanup was aligning the CLI usage/help text with the documented output target behavior. No unrelated hunks are included in the scoped branch diff.
