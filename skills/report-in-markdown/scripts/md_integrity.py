"""Render-integrity checker for markdown that targets the superRA dashboard.

The dashboard renders task markdown with markdown-it + markdown-it-texmath
configured `delimiters: 'dollars'` (single source of truth: base.html, the
`md.use(texmath, { engine: katex, delimiters: 'dollars' })` line). Two classes
of authoring mistake render as broken output with no error:

  1. Display `$$ … $$` blocks not blank-line separated from surrounding text.
     A non-blank text line directly above the opening `$$` leaves a paragraph
     open, and the block is swallowed into that paragraph instead of rendering
     as a standalone display block.
  2. TeX-only operator macros (\\diag, \\cov, \\E, …) that KaTeX does not
     define and renders as an error. They must be written \\operatorname{...}.

This module is stdlib-only and importable. The detection logic lives here and
nowhere else; both the self-diagnose CLI (check_markdown.py) and the PostToolUse
hook call `check()`. It scans line-by-line with regex rather than parsing
markdown, so it is fast on the hook's hot path and carries no dependencies.
"""

from __future__ import annotations

import re
from typing import NamedTuple


class Issue(NamedTuple):
    line: int  # 1-based
    rule: str
    message: str


# KaTeX-undefined operator macros. Each must be written as \operatorname{name}.
# Single named set so the list is trivial to extend.
TEX_ONLY_MACROS = (
    "diag",
    "cov",
    "var",
    "corr",
    "Cov",
    "Var",
    "E",
    "plim",
    "argmin",
    "argmax",
    "sgn",
    "tr",
    "rank",
)

# \macro not already followed by an alphabetic char (so \var does not match
# \variance) and not part of \operatorname. word boundary on the tail.
_MACRO_RE = re.compile(
    r"\\(" + "|".join(re.escape(m) for m in TEX_ONLY_MACROS) + r")(?![A-Za-z])"
)

_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
# A standalone display-math fence line: only `$$` (optionally with surrounding
# whitespace), nothing else on the line.
_STANDALONE_DD_RE = re.compile(r"^\s*\$\$\s*$")


def _strip_inline_code(line: str) -> str:
    """Replace inline `code` spans with spaces of equal length so math inside
    documentation backticks is not flagged, while column counts are preserved."""
    out = []
    i = 0
    n = len(line)
    while i < n:
        if line[i] == "`":
            # Count the run of backticks opening the span.
            j = i
            while j < n and line[j] == "`":
                j += 1
            ticks = line[i:j]
            close = line.find(ticks, j)
            if close == -1:
                # Unterminated span: leave the rest as-is.
                out.append(line[i:])
                i = n
            else:
                span_end = close + len(ticks)
                out.append(" " * (span_end - i))
                i = span_end
        else:
            out.append(line[i])
            i += 1
    return "".join(out)


def check(text: str) -> list[Issue]:
    """Return render-integrity issues for `text` (a whole markdown document).

    Fence-aware: content inside fenced code blocks and inline code spans is
    skipped, so documentation examples are not flagged.
    """
    issues: list[Issue] = []
    lines = text.split("\n")

    # First pass: mark which lines are inside a fenced code block.
    in_fence = False
    fence_marker = ""
    in_code = [False] * len(lines)
    for idx, raw in enumerate(lines):
        m = _FENCE_RE.match(raw)
        if m:
            marker = m.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker[0]  # ` or ~
                in_code[idx] = True
                continue
            # Closing fence must use the same marker char.
            if marker[0] == fence_marker:
                in_fence = False
                in_code[idx] = True
                continue
        in_code[idx] = in_fence

    def is_blank(i: int) -> bool:
        return 0 <= i < len(lines) and lines[i].strip() == ""

    # Second pass: per-line rules + collect standalone `$$` fence lines.
    dd_fence_lines: list[int] = []
    for idx, raw in enumerate(lines):
        if in_code[idx]:
            continue
        scan = _strip_inline_code(raw)

        for m in _MACRO_RE.finditer(scan):
            name = m.group(1)
            issues.append(
                Issue(
                    line=idx + 1,
                    rule="tex-only-macro",
                    message=(
                        f"\\{name} is undefined in KaTeX and renders as an error; "
                        f"write \\operatorname{{{name}}} instead."
                    ),
                )
            )

        if _STANDALONE_DD_RE.match(scan):
            dd_fence_lines.append(idx)

    # display-math-not-separated: a standalone `$$` fence whose adjacent
    # non-fence neighbor (above or below) is a non-blank text line. Pair the
    # fence lines into open/close blocks so we test the outward neighbors.
    flagged: set[int] = set()
    i = 0
    while i + 1 < len(dd_fence_lines):
        open_i = dd_fence_lines[i]
        close_i = dd_fence_lines[i + 1]
        # Line above the opening fence.
        if not is_blank(open_i - 1) and open_i - 1 >= 0:
            flagged.add(open_i)
        # Line below the closing fence.
        if close_i + 1 < len(lines) and not is_blank(close_i + 1):
            flagged.add(close_i)
        i += 2

    for ln in sorted(flagged):
        issues.append(
            Issue(
                line=ln + 1,
                rule="display-math-not-separated",
                message=(
                    "display $$ block touches a text line with no blank line "
                    "between; the block gets swallowed into the paragraph and "
                    "does not render as block math. Put a blank line above and "
                    "below the $$ fence (none inside the block)."
                ),
            )
        )

    # unbalanced-display-math: odd number of standalone `$$` fence lines.
    if len(dd_fence_lines) % 2 == 1:
        issues.append(
            Issue(
                line=dd_fence_lines[-1] + 1,
                rule="unbalanced-display-math",
                message=(
                    "odd number of standalone $$ fence lines; a display block "
                    "is likely unclosed."
                ),
            )
        )

    issues.sort(key=lambda it: (it.line, it.rule))
    return issues
