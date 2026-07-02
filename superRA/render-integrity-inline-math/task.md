---
title: "Render-integrity rule: inline $…$ math split across a line break"
status: approved
depends_on: []
---

## Objective

Add a third render-integrity rule to the checker so it catches inline `$…$` math whose opening and closing `$` land on different lines. This silently fails today: the dashboard renders with `markdown-it-texmath` `delimiters: 'dollars'`, whose inline regex uses `.` without the dotAll flag, so an inline span cannot match across a newline. When prose is hard-wrapped between an opening `$` and its closing `$`, the whole span renders as raw literal text with backslashes — no error. The existing `check()` only covers display-`$$`-not-blank-separated, unbalanced-`$$`, and KaTeX-undefined operator macros; this class is unguarded.

**Deliverables:**

1. **New rule in `md_integrity.py`.** Detect any single line that contains an odd number of unescaped inline `$` delimiters — i.e. an inline `$…$` span opens on that line and does not close on it. Reuse the module's existing fence-awareness and `_strip_inline_code` so content inside fenced code blocks and inline `` `code` `` spans is not flagged. The rule must not misfire on:
   - Display `$$` delimiters (single or standalone-fence `$$`) — count these as display markers, not inline `$`.
   - Escaped literal dollars `\$` (currency in prose).
   - A correct single-line inline span `$r_t$` (even parity → clean).

   Emit an `Issue` with a distinct `rule` name (e.g. `inline-math-line-break`) anchored to the offending line, whose message states that the inline span is unclosed on this line and will not render if it continues on the next line, and points to the fix (keep each inline `$…$` on one line, or escape a literal `$` as `\$`).

2. **Tests in `test_md_integrity.py`.** Cover: a broken span split across a hard wrap is flagged on the opening line; a correct single-line inline span is clean; a `\$…\$` escaped-currency line is clean; a `$$` display block (standalone-fence and inline `$$x$$`) is not flagged by the new rule; the new rule does not fire inside a code fence or inline code span. Follow the existing test style (`rules()` helper, per-rule filtering).

3. **Keep the docs and self-diagnose surface in sync.** The module docstring of `md_integrity.py` enumerates "Two classes of authoring mistake" and `check_markdown.py`'s docstring lists the patterns it reports — extend both to include the new class. Update `skills/report-in-markdown/SKILL.md` §"Two patterns render as broken output" (now three): add the authoring rule "keep each inline `$…$` span on a single line — do not hard-wrap prose between an opening `$` and its closing `$`," phrased as a positive instruction consistent with the two existing bullets.

**Validation:**

- `uv run --with pytest --script skills/report-in-markdown/scripts/test_md_integrity.py` (or `python3 -m pytest skills/report-in-markdown/scripts/test_md_integrity.py`) — all tests green, including the new ones.
- Run the updated `check_markdown.py` across the live task tree and docs to surface any already-broken inline math: `python3 skills/report-in-markdown/scripts/check_markdown.py $(git ls-files 'superRA/**/*.md' 'docs/**/*.md')`. Fix any real `inline-math-line-break` instances found by re-flowing the paragraph so each inline span stays on one line; record the count found (0 is a valid result) in `## Results`.

## Planner Guidance

**Placement.** Top-level task: the checker and its authoring rule are `report-in-markdown` artifacts — a standalone utility skill used across the whole workflow, not owned by any existing top-level concern. The nearest neighbor is `task-tree` (its `dashboard/live-server/math-rendering` child encodes the same `markdown-it-texmath` `dollars` config, and the PostToolUse hook that calls `md_integrity.check()` lives under task-tree), but that subtree owns the *renderer and the hook wiring*, not the report-in-markdown skill this rule belongs to. This mirrors the original (since-consolidated) `markdown-integrity` tree, which was also a top-level sibling of task-tree.

`md_integrity.py` is a hand-written stdlib-only module (not a generated artifact), so edit it directly — the generated-file rule does not apply here. The exact detection mechanism (regex vs. hand scan) is the implementer's call, but it must exclude `$$` runs and `\$` before counting inline parity, and must run per already-stripped line so the fence/inline-code exemptions are inherited rather than reimplemented. This is a diagnostic that always exits 0, so favor a low false-positive rule over an aggressive one; the odd-inline-`$`-parity-per-line signal is the intended approach (it is exactly what the reported bug produces). The checker is loaded by both `check_markdown.py` and the PostToolUse task hook via `md_integrity.check()`, so no call-site changes are needed — the new rule flows to both automatically.

## Results

Shipped the `inline-math-line-break` render-integrity rule — `_inline_dollar_odd` in [md_integrity.py](../../skills/report-in-markdown/scripts/md_integrity.py), test matrix in [test_md_integrity.py](../../skills/report-in-markdown/scripts/test_md_integrity.py) (29 passed), authoring rule in [SKILL.md](../../skills/report-in-markdown/SKILL.md). Flows to both `check_markdown.py` and the PostToolUse hook via `check()` with no call-site changes. Live sweep across the task tree and docs found one real break — four hard-wrapped spans in [docs/plans/2026-04-22-theory-modeling-vertical-results.md](../../docs/plans/2026-04-22-theory-modeling-vertical-results.md), re-flowed onto single lines.
