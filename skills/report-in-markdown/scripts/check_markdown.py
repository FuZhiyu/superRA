#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Self-diagnose CLI for markdown render-integrity in the superRA dashboard.

Run on one or more markdown files before committing. It reports the patterns
that silently fail to render in the dashboard (adjacent display $$ blocks,
unbalanced $$, KaTeX-undefined operator macros). Stdlib-only, so it runs under
`uv run --script` and a bare `python3` fallback.

    uv run --script <skill-dir>/scripts/check_markdown.py path/to/file.md ...

It is a diagnostic, not a gate: it always exits 0. "issues found" vs "clean" is
distinguished in the printed output, not the exit code.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from md_integrity import check  # noqa: E402


def main(argv: list[str]) -> int:
    paths = argv[1:]
    if not paths:
        print("usage: check_markdown.py FILE.md [FILE.md ...]", file=sys.stderr)
        return 0

    total = 0
    for p in paths:
        path = Path(p)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            print(f"{p}: cannot read ({e})", file=sys.stderr)
            continue
        issues = check(text)
        if not issues:
            print(f"{p}: clean")
            continue
        total += len(issues)
        for it in issues:
            print(f"{p}:{it.line}  [{it.rule}]  {it.message}")

    if total:
        print(f"\n{total} render-integrity issue(s) found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
