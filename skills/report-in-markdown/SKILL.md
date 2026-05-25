---
name: report-in-markdown
description: Markdown style guide for agents writing task files, status reports, or standalone markdown reports, with optional references for figures, LaTeX math, and tables.
user-invocable: true
---

# Report in Markdown

The markdown style guide for any agent writing markdown. Use the rule below for source-file citations; load references only when the output needs figures, LaTeX math, tables, or final-form results guidance.

## File-reference rule

Cite source files as **markdown links with line anchors**, not backtick-wrapped paths.

| Use case | Form |
|---|---|
| Single line | [file.py:42](file.py#L42) |
| Line range | [file.py:40-50](file.py#L40-L50) |
| Whole file | [file.py](file.py) |

Resolve paths **relative to the markdown file's directory** (use `../` as needed). For files at the worktree root, the relative path equals the project-root path.

## Load map

| Caller | Load |
|---|---|
| Implementer / reviewer writing routine task-block citations only | nothing beyond this file |
| Implementer writing a task `## Results` section with figures / math / tables | `rich-content.md` |
| `integration-workflow` Document doc-writer subagent | `baseline-io.md` + `rich-content.md` + `final-form.md` |
| `integration-workflow` Document doc-reviewer subagent | `final-form.md` |
| Standalone markdown report (any context) | `baseline-io.md` + `rich-content.md` |

The `attachments/` directory is a caller parameter; defaults and fallbacks are in `references/rich-content.md` §Figures.

## References

- `references/baseline-io.md` — frontmatter spec, filename convention, output-path resolution. Permanent artifacts only.
- `references/rich-content.md` — figure handling (PDF→PNG, relative-path embedding), LaTeX math, markdown tables.
- `references/final-form.md` — final results consolidation: fact-check checklist, task-indexed → reader-facing restructure, figure materialization, relocation.
