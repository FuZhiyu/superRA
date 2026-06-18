---
title: "Vendor mistral-pdf-to-markdown as In-Repo PDF->Markdown Skill"
status: approved
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
  - skills/using-superra/SKILL.md
  - tests/test-mistral-skill-text.sh
created: 2026-06-04
---

## Objective

Make the `zotero-paper-reader` capability self-contained by giving its PDF-to-Markdown conversion step a canonical home inside this repo. Step 6 of the paper-reading workflow invokes `mistral-pdf-to-markdown` by capability name, but that skill previously shipped only in the external `pdf2markdown-converter` plugin, so a superRA user without that plugin hit a dead end at conversion. Vendor the skill into `skills/mistral-pdf-to-markdown/` as a faithful copy, apply the repo's harness-neutral invocation convention, register it in the discovery surfaces as a standalone Utility skill, and lock the migration with a text-regression test.

Additionally, keep the vendored converter runnable as `mistralai` evolves. The converter's PEP 723 header depends on `mistralai` with no version bound, so `uv run --script` resolves the newest release on every run. `mistralai` 2.0 (released 2026-06-03) removed the top-level `Mistral` export, so the script's `from mistralai import Mistral` now raises `ImportError: cannot import name 'Mistral' from 'mistralai'` and the converter is broken on any fresh invocation. Restore it by migrating the import to the v2 client path (`from mistralai.client import Mistral`) and pinning the PEP 723 dependency to the v2 major (`mistralai>=2,<3`) so a future major release cannot silently break the script the same way again. This is an import-path-and-pin fix only: verified against `mistralai` 2.4.9, the `Mistral(api_key=...)` constructor and the `client.ocr.process(model=..., document=..., include_image_base64=...)` call used here are unchanged from v1, so OCR behavior, image extraction, and `--pages` handling must stay byte-for-byte identical.

Validation: the script imports and constructs the Mistral client under `mistralai` 2.x; `bash tests/test-mistral-skill-text.sh` passes from the repo root; and if `MISTRAL_API_KEY` is available, one real single-page conversion of a small PDF completes end-to-end (text + image extraction) to confirm the v2 path works against the live API.

### Constraints

Faithful migration, not a rewrite — copy `SKILL.md`, `references/reference.md`, and the PEP 723 converter plus its config loader without changing conversion behavior. Apply the same harness-neutral path fix used across this branch: replace the Claude-only `${CLAUDE_SKILL_DIR}` with the `<skill-dir>` placeholder in every command example so the commands work under Codex/superRA as well as Claude. Exclude `__pycache__` (gitignored). Register only in inventory/discovery surfaces (`README.md`, `skills/CATEGORIES.md`, `skills/using-superra/SKILL.md`) — do not touch the Skill-Load Manifest or workflow choreography, since this is a user-invocable standalone skill not loaded by workflow agents.

For the dependency fix: keep the edit surgical — only the `from mistralai import Mistral` import line, the `mistralai` entry in the PEP 723 dependency block, and the matching assertions in `tests/test-mistral-skill-text.sh`. Do not change the OCR call, the response-parsing code, the API-key loader, or any conversion logic. A v1/v2 dual-path `try/except` import is unnecessary because the `<3` pin fixes the resolved major to v2 — prefer the single v2 import.

## Results

### What was done

Migrated `mistral-pdf-to-markdown` into `skills/mistral-pdf-to-markdown/` as the canonical PDF->Markdown home behind `zotero-paper-reader` ([feat commit](#) `de57aac5`, harness-neutral path fix `772e6457`):

- **Skill files** — `SKILL.md`, `references/reference.md`, and `scripts/convert_pdf_to_markdown.py` + `scripts/_config_loader.py` (PEP 723) copied faithfully from the external plugin. The OCR conversion behavior (Mistral OCR API, image extraction, `--pages` selection) is unchanged.
- **Harness-neutral invocation** — every command example uses the `<skill-dir>` placeholder instead of `${CLAUDE_SKILL_DIR}`, matching the convention applied to `zotero_tool.py` on this branch so the skill is install-location- and harness-independent.
- **Discovery surfaces** — added a Utility row in [README.md](../../README.md), [skills/CATEGORIES.md](../../skills/CATEGORIES.md), and the [using-superra Skill Inventory](../../skills/using-superra/SKILL.md), each describing it as a user-invocable standalone skill (needs `MISTRAL_API_KEY`), the conversion step behind `zotero-paper-reader`, and explicitly **not** loaded by workflow agents or the Manifest. Manifest and generated agent files untouched.
- **Wiring** — `zotero-paper-reader`'s Step 6 note now points at the bundled in-repo skill rather than an external plugin path, closing the conversion dead end (see [03-paper-reading-workflow](../03-paper-reading-workflow/task.md)).

**mistralai v2 dependency fix (2026-06-05 increment).** `mistralai` 2.0 (2026-06-03) dropped the top-level `Mistral` export, so the unpinned converter broke with `ImportError: cannot import name 'Mistral' from 'mistralai'` on every fresh `uv run --script`. Fixed import-and-pin only, OCR behavior untouched:

- **PEP 723 pin** — `convert_pdf_to_markdown.py` now declares `"mistralai>=2,<3"` (was unpinned), so `uv run --script` resolves a v2 release and a future major cannot silently break it again.
- **v2 client import** — `from mistralai import Mistral` → `from mistralai.client import Mistral`, with a one-line comment recording why. Verified against `mistralai` 2.4.9: `Mistral(api_key=...)` and `client.ocr.process(model=..., document=..., include_image_base64=...)` are unchanged from v1, so conversion logic, image extraction, and `--pages` handling are byte-for-byte identical.
- **Doc example** — the v1 `from mistralai import Mistral` snippet in `references/reference.md` (API-key smoke test) updated to the v2 client path.
- **Regression lock** — `tests/test-mistral-skill-text.sh` now asserts the `"mistralai>=2,<3"` pin and the `from mistralai.client import Mistral` line are present, and that the broken top-level form is absent anywhere under the skill dir.

### Verification

[tests/test-mistral-skill-text.sh](../../tests/test-mistral-skill-text.sh) — a credential-free text-regression suite locking the migration: it confirms the `<skill-dir>` invocation (no Claude-only `${CLAUDE_SKILL_DIR}`), the PEP 723 script header and converter integrity, and (since the v2 fix) the `mistralai>=2,<3` pin and v2 client import. Run with `bash tests/test-mistral-skill-text.sh` from the repo root — passes 11/11.

mistralai v2 fix verified live: `uv run --script .../convert_pdf_to_markdown.py --help` resolves the isolated PEP 723 env, installs `mistralai` 2.4.9, and runs all top-level imports (including `from mistralai.client import Mistral`) before printing help — confirmed to stay isolated even with `~/.venv` (mistralai 1.9.11) active, since `uv run --script` ignores the ambient venv. The live-OCR conversion path was not exercised in this session (`MISTRAL_API_KEY` not set); the OCR call signature is unchanged from the working v1 code, so conversion output is preserved by construction.
