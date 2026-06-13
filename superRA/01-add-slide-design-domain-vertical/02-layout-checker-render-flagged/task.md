---
title: "Layout Checker: uv Script Header and Flagged-Page Rendering"
status: approved
depends_on: []
tags: [retrospective]
script: skills/slide-design/scripts/check_slide_layout.py
created: 2026-06-11
updated: 2026-06-11
---

## Objective

Make `scripts/check_slide_layout.py` directly runnable and close the gap between its nonvisual triage (steps 1–4 of the layout-check process) and the visual-inspection step 5.

- The script carries the repo's PEP 723 convention: `#!/usr/bin/env -S uv run --script` shebang plus an inline `/// script` metadata block, so `uv run --script` works without environment setup.
- A `--render-flagged DIR` option renders each flagged page to a PNG via `pdftoppm` so the inspecting agent can read the images directly; a missing `pdftoppm` produces an error finding, not a crash.
- `references/layout-checks.md` documents the `uv run --script` invocation, the `--render-flagged` option, and the manual `pdftoppm` command for step 5.

Validation: the script runs end to end on a real deck and produces PNGs for flagged pages.

## Results

### Key Findings

- Replaced the `python3` shebang with `#!/usr/bin/env -S uv run --script` and added the PEP 723 block (`requires-python = ">=3.10"`, no dependencies — stdlib only).
- Added `render_flagged_pages()`: collects the distinct flagged page numbers, renders each with `pdftoppm -png -r 100 -f N -l N`, and appends `rendered-page` info findings (or `render-failed` / `missing-tool` errors) to the report.
- `--render-flagged` runs after bbox-based detection and renders every finding that carries a page number. In practice that is the bbox heuristics (`possible-wrap`, `near-boundary`): `parse_log` findings (overfull boxes, missing assets, LaTeX errors) carry `page=None`, so log-flagged pages are not rendered — a known coverage limitation.
- `references/layout-checks.md` step 5 now names the concrete render command; the process section shows the `uv run --script` invocation with `--render-flagged DIR`.

### Verification

- `uv run --script skills/slide-design/scripts/check_slide_layout.py <template> --no-fail --render-flagged /tmp/flagged-pages` rendered `beamer-starter-template-flagged-06.png` and `-07.png` for the two flagged pages and reported `rendered-page` findings for both.
