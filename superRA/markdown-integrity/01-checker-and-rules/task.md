---
title: "Render-Integrity Checker + Rules + Self-Diagnose CLI (report-in-markdown)"
status: not-started
depends_on:  []
tags: []
created: 2026-06-08
---

## Objective

Build the render-integrity checker, ship it as a self-diagnose CLI under `report-in-markdown`, and document the authoring rules it enforces. This is the single home of the detection logic; `02-hook-integration` calls it from the PostToolUse hook.

**1. Checker module** — `skills/report-in-markdown/scripts/md_integrity.py`, stdlib-only, importable. Expose a pure function, e.g. `check(text: str) -> list[Issue]`, where each issue carries a line number (1-based), a short rule id, and a human-readable message with the fix. Detect:

- **`display-math-not-separated`** — a `$$` display fence line that is directly adjacent (no intervening blank line) to a non-blank, non-`$$` text line above or below it. This is the pattern that makes `markdown-it-texmath` (`dollars`) swallow the block as paragraph text. Report the offending `$$` line and state the fix (blank line above/below the block, none inside).
- **`unbalanced-display-math`** — an odd number of standalone `$$` fence lines in the file (a likely unclosed display block).
- **`tex-only-macro`** — use of a KaTeX-undefined operator macro inside math. Cover at least `\diag \cov \var \corr \Cov \Var \E \plim \argmin \argmax \sgn \tr \rank`, and design the macro list as a single named set that is trivial to extend. Report each occurrence and give the `\operatorname{...}` replacement.

Be **fence-aware**: ignore content inside fenced code blocks (```` ``` ````) and inline code spans so documentation examples (including this task's own examples) are not flagged. Prefer simple line/regex scanning over a real parser — speed and zero dependencies are constraints from the parent objective.

**2. Self-diagnose CLI** — `skills/report-in-markdown/scripts/check_markdown.py`, a PEP 723 `uv run --script` entry (stdlib-only, declares no third-party deps, `python3` fallback works) that takes one or more file paths, runs `md_integrity.check` on each, and prints a concise human-readable report (`path:line  [rule]  message`). Exit 0 always (it is a diagnostic, not a gate) — distinguish "issues found" from "clean" in the printed output, not the exit code, so it composes with the warn-only philosophy.

**3. Rules in the skill** — add the two authoring rules to `report-in-markdown` so the rule and its enforcement share one home: (a) display `$$` blocks must have a blank line above and below (none inside); (b) the `\diag`/`\cov`/`\var`/… class of TeX-only operators must be written `\operatorname{...}` because KaTeX does not define them. Put them where they belong under `## Math` in `SKILL.md` (or a short new reference if the SKILL body would bloat — your call per skill-authoring discipline), and point to the self-diagnose CLI as the way to check a file. Keep additions minimal and behavior-shaping per the CLAUDE.md two-test gate.

**4. Verify against the real renderer.** Confirm the blank-line rule reflects the dashboard's actual behavior, not an assumption: drive a sample with an adjacent `$$` block and a blank-line-separated `$$` block through the dashboard's `dollars` texmath config and confirm the adjacent one fails to produce block math while the separated one renders. The config is at [base.html:1649](../../../skills/task-system/scripts/templates/base.html#L1649). Record what you ran and observed in `## Results`.

**Tests** — unit tests for `md_integrity.check`: a clean file (no issues), an adjacent-`$$` file (flagged with correct line), a properly-separated `$$` file (clean), each TeX-only macro flagged with its `\operatorname` fix, a macro inside a code fence **not** flagged, and an odd-`$$`-count file flagged. Mirror how `skills/task-system/scripts` tests are laid out and run.

**Done when:** `check_markdown.py` run on a file with an adjacent `$$` block and a `\diag` reports both with correct line numbers and fixes; run on a clean file prints a clean result; the unit tests pass; the rules are documented in `report-in-markdown`; and `## Results` records the dashboard live-render verification.

## Planner Guidance

- Model the CLI invocation/doc convention on an existing bundled-script skill — `skills/zotero-paper-reader/SKILL.md` and `skills/mistral-pdf-to-markdown/SKILL.md` both document `uv run --script <skill-dir>/scripts/...`.
- `task_hook.py` is the reference for a stdlib-only, zero-dependency PEP 723 script in this repo.
- For the live-render check, the standalone dashboard export inlines the texmath/KaTeX assets; a minimal Node or browser harness using the same `delimiters: 'dollars'` call is enough — you do not need the full server. If a full render harness is impractical, at minimum cite the rule registration in the bundled `markdown-it-texmath` (block rule registered without `alt`, so `$$` cannot interrupt a paragraph) as the grounding evidence, and say so in Results.
- Keep `Issue` a plain dataclass/namedtuple; no class hierarchy.

## Results

