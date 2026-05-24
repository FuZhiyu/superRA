---
title: "Data Model — Body Section Parsing"
status: approved
review_status: approved
integration_status: ~
depends_on: []
tags: []
script: skills/task-system/scripts/_task_io.py
created: 2026-05-23
updated: 2026-05-24
---

## Objective

Add `parse_body_sections()` helper that splits task body on `## ` headers into `{section_name: content}` pairs. Add `objective`, `results`, `decisions`, `review_notes` fields to the `Task` dataclass. Wire them up in `parse_task()`.

## Results

### Key Findings
- `parse_body_sections()` is 15 lines, splits on `## ` regex, returns `dict[str, str]`
- Four new fields added to `Task` dataclass: `objective`, `results`, `decisions`, `review_notes`
- Fields are read-only views derived from `body` — `write_task()` writes `body` directly, no serialization leakage
- Edge cases verified: empty body, no sections, duplicate names (last-wins), preamble before first header (preserved in `body`)
- All 53 tests pass including `TestParseBodySections` (4 tests)
