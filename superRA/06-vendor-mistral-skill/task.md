---
title: "Vendor mistral-pdf-to-markdown as In-Repo PDF->Markdown Skill"
status: revise
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

### Constraints

Faithful migration, not a rewrite — copy `SKILL.md`, `references/reference.md`, and the PEP 723 converter plus its config loader without changing conversion behavior. Apply the same harness-neutral path fix used across this branch: replace the Claude-only `${CLAUDE_SKILL_DIR}` with the `<skill-dir>` placeholder in every command example so the commands work under Codex/superRA as well as Claude. Exclude `__pycache__` (gitignored). Register only in inventory/discovery surfaces (`README.md`, `skills/CATEGORIES.md`, `skills/using-superRA/SKILL.md`) — do not touch the Skill-Load Manifest or workflow choreography, since this is a user-invocable standalone skill not loaded by workflow agents.

## Results

### What was done

Migrated `mistral-pdf-to-markdown` into `skills/mistral-pdf-to-markdown/` as the canonical PDF->Markdown home behind `zotero-paper-reader` ([feat commit](#) `de57aac5`, harness-neutral path fix `772e6457`):

- **Skill files** — `SKILL.md`, `references/reference.md`, and `scripts/convert_pdf_to_markdown.py` + `scripts/_config_loader.py` (PEP 723) copied faithfully from the external plugin. The OCR conversion behavior (Mistral OCR API, image extraction, `--pages` selection) is unchanged.
- **Harness-neutral invocation** — every command example uses the `<skill-dir>` placeholder instead of `${CLAUDE_SKILL_DIR}`, matching the convention applied to `zotero_tool.py` on this branch so the skill is install-location- and harness-independent.
- **Discovery surfaces** — added a Utility row in [README.md](../../README.md), [skills/CATEGORIES.md](../../skills/CATEGORIES.md), and the [using-superRA Skill Inventory](../../skills/using-superRA/SKILL.md), each describing it as a user-invocable standalone skill (needs `MISTRAL_API_KEY`), the conversion step behind `zotero-paper-reader`, and explicitly **not** loaded by workflow agents or the Manifest. Manifest and generated agent files untouched.
- **Wiring** — `zotero-paper-reader`'s Step 6 note now points at the bundled in-repo skill rather than an external plugin path, closing the conversion dead end (see [03-paper-reading-workflow](../03-paper-reading-workflow/task.md)).

### Verification

[tests/test-mistral-skill-text.sh](../../tests/test-mistral-skill-text.sh) — a credential-free text-regression suite locking the migration: it confirms the `<skill-dir>` invocation (no Claude-only `${CLAUDE_SKILL_DIR}`), the PEP 723 script header and converter integrity, and the presence of the skill files. Run with `bash tests/test-mistral-skill-text.sh` from the repo root.

## Review Notes

1. **MAJOR** — Documented run command does not execute a PEP 723 script, recreating the conversion dead-end this task closes. [skills/mistral-pdf-to-markdown/SKILL.md:24](../../skills/mistral-pdf-to-markdown/SKILL.md#L24) (and lines 27, 28, 88, 96, 105) tell agents to run `uv run python <skill-dir>/scripts/convert_pdf_to_markdown.py ...`; [references/reference.md:101](../../skills/mistral-pdf-to-markdown/references/reference.md#L101) uses `subprocess.run(["python", ...])` and lines 247/260/270 use bare `python <skill-dir>/scripts/...`. The converter is a PEP 723 inline-metadata script ([scripts/convert_pdf_to_markdown.py:1](../../skills/mistral-pdf-to-markdown/scripts/convert_pdf_to_markdown.py#L1)), but `uv run python <script>` and bare `python <script>` both **ignore** PEP 723 inline dependencies — verified empirically: `uv run python` on a PEP 723 script raises `ModuleNotFoundError` for the inline deps, while `uv run --script` installs them. So a fresh user with no ambient `mistralai`/`pypdf`/`python-dotenv`/`pyyaml` hits `ModuleNotFoundError: No module named 'mistralai'` at the conversion step — the exact dead-end the Objective sets out to close ("a superRA user without that plugin hit a dead end at conversion"). The shebang `#!/usr/bin/env -S uv run --script` works only when the script is executed directly, but no command example documents that form. The "faithful migration, do not change conversion behavior" constraint covers OCR behavior, not propagating a broken invocation form — and this branch already established `uv run --script` as the correct PEP 723 convention for `zotero_tool.py`. Fix: change every documented invocation to `uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py ...` (and the `subprocess.run` list to `["uv", "run", "--script", "<skill-dir>/scripts/convert_pdf_to_markdown.py", ...]`), then add a `tests/test-mistral-skill-text.sh` guard asserting the documented invocation uses `--script` and that no `uv run python <skill-dir>` / bare `python <skill-dir>/scripts` form survives (the current suite's "PEP 723 script came over intact" claim does not guard the invocation form).
   → implemented: every documented invocation switched to `uv run --script` — SKILL.md (6 command examples + the `subprocess.run` list now `"uv", "run", "--script"`) and reference.md (the `subprocess.run(["python", ...])` list and the three bare `python <skill-dir>/scripts/...` examples). Verified no `uv run python <skill-dir>` or bare `python <skill-dir>/scripts` form survives. Added four guards to `tests/test-mistral-skill-text.sh` (now 9 checks): absence of `uv run python <skill-dir>`, bare `python <skill-dir>/scripts`, and the `"uv", "run", "python"` subprocess list, plus presence of `uv run --script <skill-dir>/scripts/convert_pdf_to_markdown.py` in SKILL.md. Suite passes 9/0.
