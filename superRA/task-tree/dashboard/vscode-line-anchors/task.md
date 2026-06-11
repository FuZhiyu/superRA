---
title: "VS Code line anchors in file links"
status: approved
depends_on:  []
tags: []
created: 2026-06-01
---

## Objective

Markdown file-link citations in task bodies carry GitHub-style line anchors — e.g. `[base.html](../../skills/.../base.html#L890)` or `Code/03.py#L42` — but clicking them in the dashboard opens the file in VS Code **at the top, not at the cited line**. The `renderMarkdown` link rewrite (`skills/task-tree/scripts/templates/base.html`, the `a[href]` loop, the non-task `else` branch) builds `vscode://file/' + PROJECT_ROOT + '/' + pathPrefix + href`, leaving any `#L890` as a URL fragment. VS Code's `vscode://file` handler ignores `#L...`; it expects the line in the path as `:<line>` (`vscode://file/<abs-path>:<line>:<col>`). So the line is silently dropped.

Fix the `else` (vscode) branch to translate a trailing GitHub-style line anchor on the href into VS Code's `:line[:col]` form before building the URI:
- `#L42` → `:42`
- `#L42C5` (GitHub column form) → `:42:5`
- `#L42-L50` (range) → `:42` (jump to the start line; VS Code's basic file URI targets a single position)

Strip the matched anchor from the path portion and append the `:line[:col]` suffix to the final `vscode://file/...` path. Only treat a trailing `#L<digits>...` as a line anchor; leave hrefs without such an anchor exactly as they are today (whole-file open). This is the genuine-file-link branch only — in-tree task references already strip `#fragment` and route to internal navigation in the sibling `[internal-task-links](../internal-task-links/task.md)` branch, so they are unaffected.

Note: task slugs and paths contain no characters that need URL-encoding for VS Code, and the existing branch already concatenates the path raw; keep that behavior, only appending the line suffix.

Validation: a task-body link like `[base.html](<rel-path>/base.html#L890)` rewrites to a `vscode://file/<abs>/base.html:890` href (verify by inspecting the rendered anchor's `href` in the served dashboard); a plain file link with no anchor is unchanged; `#L42-L50` and `#L42C5` forms produce `:42` and `:42:5` respectively. Add a focused test or node-harness check over the anchor-translation logic. Run `uv run pytest skills/task-tree/scripts/test_task_tree.py skills/task-tree/scripts/test_dashboard.py`.

## Results

File-link citations with GitHub-style line anchors now open VS Code at the cited line. The fix is in the `renderMarkdown` `a[href]` loop's genuine-file-link `else` branch in [base.html](../../../../skills/task-tree/scripts/templates/base.html): before building the `vscode://file/...` URI, a trailing `#L<line>[C<col>][-L<line2>]` anchor is matched, stripped from the path, and re-appended as VS Code's `:<line>[:<col>]` suffix. In-tree task links are unaffected (they take the internal-navigation branch, which strips fragments).

### Translation cases (verified via node harness over the exact logic)

| Anchor in href | Resulting vscode path suffix |
|---|---|
| `#L890` | `:890` |
| `#L42C5` | `:42:5` |
| `#L42-L50` | `:42` (start line) |
| none | unchanged (whole-file open) |
| `#heading` (non-`L`) | left as-is (VS Code opens whole file, as before) |

`..` segments in the relative path are passed through unchanged (VS Code resolves them); this matches the pre-existing behavior — only the line suffix is new.

### Verification

- Node harness over the extracted regex/translation confirmed all rows above.
- `test_vscode_file_links_translate_line_anchors` (source-presence guard against the logic being dropped) added to the dashboard suite.
- Full suite green (see commit). The live `serve` template auto-reloads, so a dashboard reload picks up the fix; clicking a `#L<n>` citation opens VS Code at that line.

## Review Notes

*(Retrospective audit, 2026-06-10 — MINOR item only; status stays `approved`.)*

1. **MINOR** — the committed coverage is the disclosed source-presence guard only; the node harness that actually exercised the anchor-translation rows was not committed, and the logic now lives inline in `renderMarkdown`'s file-link branch ([base.html:1801](../../../../skills/task-tree/scripts/templates/base.html#L1801)) where no JS runtime executes it in the suite. Commit the harness alongside the existing extracted-function node tests so the translation table stays executable, not just greppable.

