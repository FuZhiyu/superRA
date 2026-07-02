#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest"]
# ///
"""Tests for the render-integrity checker (md_integrity.check)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from md_integrity import TEX_ONLY_MACROS, check


def rules(text):
    return [i.rule for i in check(text)]


def test_clean_file_no_issues():
    text = (
        "# Title\n\nSome prose with inline math $r_t$.\n\n"
        "$$\nx = y + z\n$$\n\nMore prose.\n"
    )
    assert check(text) == []


def test_adjacent_dollar_flagged_with_line():
    # text line directly above the opening $$ (line 2 is the $$ fence).
    text = "intro text\n$$\nx = y + z\n$$\n\nafter\n"
    issues = [i for i in check(text) if i.rule == "display-math-not-separated"]
    assert len(issues) == 1
    assert issues[0].line == 2  # the opening $$ fence


def test_adjacent_below_flagged():
    # text line directly below the closing $$.
    text = "intro\n\n$$\nx = 1\n$$\nafter\n"
    issues = [i for i in check(text) if i.rule == "display-math-not-separated"]
    assert len(issues) == 1
    assert issues[0].line == 5  # the closing $$ fence


def test_separated_dollar_clean():
    text = "intro text\n\n$$\nx = y + z\n$$\n\nafter\n"
    assert [i for i in check(text) if i.rule == "display-math-not-separated"] == []


@pytest.mark.parametrize("macro", TEX_ONLY_MACROS)
def test_each_tex_only_macro_flagged(macro):
    text = f"The estimator is $\\{macro}(X)$ here.\n"
    issues = [i for i in check(text) if i.rule == "tex-only-macro"]
    assert len(issues) == 1
    assert issues[0].line == 1
    assert f"\\operatorname{{{macro}}}" in issues[0].message


def test_macro_inside_code_fence_not_flagged():
    text = "```\n$\\diag(X)$\n```\n"
    assert [i for i in check(text) if i.rule == "tex-only-macro"] == []


def test_macro_inside_inline_code_not_flagged():
    text = "Write `\\diag` as operatorname.\n"
    assert [i for i in check(text) if i.rule == "tex-only-macro"] == []


def test_dollar_fence_inside_code_not_flagged():
    # a $$ block inside a code fence is documentation, not real display math.
    text = "```\nintro\n$$\nx=1\n$$\n```\n"
    assert check(text) == []


def test_odd_dollar_count_flagged():
    text = "intro\n\n$$\nx = 1\n\nmore prose without a close.\n"
    issues = [i for i in check(text) if i.rule == "unbalanced-display-math"]
    assert len(issues) == 1


def test_macro_word_boundary_no_false_positive():
    # \variance should not match \var; \Embedding should not match \E.
    text = "$\\variance$ and $\\Embedding$\n"
    assert [i for i in check(text) if i.rule == "tex-only-macro"] == []


def test_inline_span_split_across_wrap_flagged():
    # opening $ on line 1, prose hard-wraps, closing $ on line 2. Both lines
    # carry an odd, unclosed $ — the opening line is flagged (as are any other
    # broken lines), pointing the author at each end of the split span.
    text = "The return $r_t = p_t -\np_{t-1}$ is defined here.\n"
    lines = [i.line for i in check(text) if i.rule == "inline-math-line-break"]
    assert 1 in lines


def test_inline_span_single_line_clean():
    text = "The return $r_t$ is defined here.\n"
    assert [i for i in check(text) if i.rule == "inline-math-line-break"] == []


def test_escaped_currency_clean():
    text = "It costs \\$5 today and \\$10 tomorrow.\n"
    assert [i for i in check(text) if i.rule == "inline-math-line-break"] == []


def test_display_fence_not_flagged_as_inline():
    text = "intro\n\n$$\nx = y + z\n$$\n\nafter\n"
    assert [i for i in check(text) if i.rule == "inline-math-line-break"] == []


def test_inline_display_dollars_not_flagged_as_inline():
    text = "The identity $$x = y$$ holds.\n"
    assert [i for i in check(text) if i.rule == "inline-math-line-break"] == []


def test_inline_break_inside_code_fence_not_flagged():
    text = "```\nThe return $r_t = p_t -\np_{t-1}$ here.\n```\n"
    assert [i for i in check(text) if i.rule == "inline-math-line-break"] == []


def test_inline_break_inside_inline_code_not_flagged():
    text = "Write `$r_t` and close it later.\n"
    assert [i for i in check(text) if i.rule == "inline-math-line-break"] == []


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
