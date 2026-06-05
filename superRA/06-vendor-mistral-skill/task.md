---
title: "Vendor mistral-pdf-to-markdown as In-Repo PDF->Markdown Skill"
status: not-started
depends_on: []
tags: [skill-creation, pdf, markdown, vendoring]
input:
  - skills/zotero-paper-reader/SKILL.md
output:
  - skills/mistral-pdf-to-markdown/SKILL.md
  - skills/mistral-pdf-to-markdown/references/reference.md
  - skills/mistral-pdf-to-markdown/scripts/convert_pdf_to_markdown.py
  - skills/mistral-pdf-to-markdown/scripts/_config_loader.py
  - README.md
  - skills/CATEGORIES.md
  - skills/using-superRA/SKILL.md
  - tests/test-mistral-skill-text.sh
created: 2026-06-04
---

## Objective

Make the `zotero-paper-reader` capability self-contained by giving its PDF-to-Markdown conversion step a canonical home inside this repo. Step 6 of the paper-reading workflow invokes `mistral-pdf-to-markdown` by capability name, but that skill previously shipped only in the external `pdf2markdown-converter` plugin, so a superRA user without that plugin hit a dead end at conversion. Vendor the skill into `skills/mistral-pdf-to-markdown/` as a faithful copy, apply the repo's harness-neutral invocation convention, register it in the discovery surfaces as a standalone Utility skill, and lock the migration with a text-regression test.

Additionally, keep the vendored converter runnable as `mistralai` evolves. The converter's PEP 723 header depends on `mistralai` with no version bound, so `uv run --script` resolves the newest release on every run. `mistralai` 2.0 (released 2026-06-03) removed the top-level `Mistral` export, so the script's `from mistralai import Mistral` now raises `ImportError: cannot import name 'Mistral' from 'mistralai'` and the converter is broken on any fresh invocation. Restore it by migrating the import to the v2 client path (`from mistralai.client import Mistral`) and pinning the PEP 723 dependency to the v2 major (`mistralai>=2,<3`) so a future major release cannot silently break the script the same way again. This is an import-path-and-pin fix only: verified against `mistralai` 2.4.9, the `Mistral(api_key=...)` constructor and the `client.ocr.process(model=..., document=..., include_image_base64=...)` call used here are unchanged from v1, so OCR behavior, image extraction, and `--pages` handling must stay byte-for-byte identical.

Validation: the script imports and constructs the Mistral client under `mistralai` 2.x; `bash tests/test-mistral-skill-text.sh` passes from the repo root; and if `MISTRAL_API_KEY` is available, one real single-page conversion of a small PDF completes end-to-end (text + image extraction) to confirm the v2 path works against the live API.

### Constraints

Faithful migration, not a rewrite — copy `SKILL.md`, `references/reference.md`, and the PEP 723 converter plus its config loader without changing conversion behavior. Apply the same harness-neutral path fix used across this branch: replace the Claude-only `${CLAUDE_SKILL_DIR}` with the `<skill-dir>` placeholder in every command example so the commands work under Codex/superRA as well as Claude. Exclude `__pycache__` (gitignored). Register only in inventory/discovery surfaces (`README.md`, `skills/CATEGORIES.md`, `skills/using-superRA/SKILL.md`) — do not touch the Skill-Load Manifest or workflow choreography, since this is a user-invocable standalone skill not loaded by workflow agents.

For the dependency fix: keep the edit surgical — only the `from mistralai import Mistral` import line, the `mistralai` entry in the PEP 723 dependency block, and the matching assertions in `tests/test-mistral-skill-text.sh`. Do not change the OCR call, the response-parsing code, the API-key loader, or any conversion logic. A v1/v2 dual-path `try/except` import is unnecessary because the `<3` pin fixes the resolved major to v2 — prefer the single v2 import.

## Results

### What was done

Migrated `mistral-pdf-to-markdown` into `skills/mistral-pdf-to-markdown/` as the canonical PDF->Markdown home behind `zotero-paper-reader` ([feat commit](#) `de57aac5`, harness-neutral path fix `772e6457`):

- **Skill files** — `SKILL.md`, `references/reference.md`, and `scripts/convert_pdf_to_markdown.py` + `scripts/_config_loader.py` (PEP 723) copied faithfully from the external plugin. The OCR conversion behavior (Mistral OCR API, image extraction, `--pages` selection) is unchanged.
- **Harness-neutral invocation** — every command example uses the `<skill-dir>` placeholder instead of `${CLAUDE_SKILL_DIR}`, matching the convention applied to `zotero_tool.py` on this branch so the skill is install-location- and harness-independent.
- **Discovery surfaces** — added a Utility row in [README.md](../../README.md), [skills/CATEGORIES.md](../../skills/CATEGORIES.md), and the [using-superRA Skill Inventory](../../skills/using-superRA/SKILL.md), each describing it as a user-invocable standalone skill (needs `MISTRAL_API_KEY`), the conversion step behind `zotero-paper-reader`, and explicitly **not** loaded by workflow agents or the Manifest. Manifest and generated agent files untouched.
- **Wiring** — `zotero-paper-reader`'s Step 6 note now points at the bundled in-repo skill rather than an external plugin path, closing the conversion dead end (see [03-paper-reading-workflow](../03-paper-reading-workflow/task.md)).

The `mistralai` v2 dependency fix is pending re-implementation (see Revision Notes); this Results section will be extended once that increment is approved.

### Verification

[tests/test-mistral-skill-text.sh](../../tests/test-mistral-skill-text.sh) — a credential-free text-regression suite locking the migration: it confirms the `<skill-dir>` invocation (no Claude-only `${CLAUDE_SKILL_DIR}`), the PEP 723 script header and converter integrity, and the presence of the skill files. Run with `bash tests/test-mistral-skill-text.sh` from the repo root.

## Revision Notes

2026-06-05 — Substantive scope addition (researcher request). `mistralai` 2.x (released 2026-06-03) removed the top-level `Mistral` export, breaking the vendored converter's `from mistralai import Mistral` on every fresh `uv run --script`. Added a requirement to migrate the import to the v2 client path (`from mistralai.client import Mistral`), pin the PEP 723 dependency to the v2 major (`mistralai>=2,<3`), and extend `tests/test-mistral-skill-text.sh` to lock both. The original vendoring work (skill files, harness-neutral paths, discovery surfaces, wiring) is unchanged; this increment only touches `scripts/convert_pdf_to_markdown.py` and `tests/test-mistral-skill-text.sh`. Status reset to `not-started` for this increment.
