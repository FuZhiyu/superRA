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
