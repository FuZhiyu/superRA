---
title: "Render-Integrity Checker + Rules + Self-Diagnose CLI (report-in-markdown)"
status: implemented
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

Shipped the render-integrity checker, the self-diagnose CLI, the documented authoring rules, and unit tests — all under `report-in-markdown`. The detection logic lives in exactly one module so `02-hook-integration` can call it from the hook.

### Deliverables

- **Checker module** — [skills/report-in-markdown/scripts/md_integrity.py](../../../skills/report-in-markdown/scripts/md_integrity.py). Stdlib-only, importable, exposes `check(text: str) -> list[Issue]` where `Issue` is a plain `NamedTuple` `(line, rule, message)`. Detects the three rules (`display-math-not-separated`, `unbalanced-display-math`, `tex-only-macro`). Fence-aware: a first pass marks lines inside fenced code blocks (matching fence char `` ` `` vs `~`), and `_strip_inline_code` blanks out inline-code spans (preserving column width) before the per-line scan, so documentation examples are not flagged. The TeX-only macro set is a single named tuple `TEX_ONLY_MACROS`, trivially extensible; the regex uses a `(?![A-Za-z])` tail guard so `\var` does not match `\variance` nor `\E` match `\Embedding`.
- **Self-diagnose CLI** — [skills/report-in-markdown/scripts/check_markdown.py](../../../skills/report-in-markdown/scripts/check_markdown.py). PEP 723 `uv run --script` entry, `dependencies = []`, `python3` fallback works. Prints `path:line  [rule]  message` per finding, `path: clean` when clean, and a trailing count. Always exits 0 (diagnostic, not a gate).
- **Rules in the skill** — added under `## Math` in [skills/report-in-markdown/SKILL.md](../../../skills/report-in-markdown/SKILL.md): blank-line-separate every display `$$` block, and write KaTeX-undefined operators as `\operatorname{...}`. Each line explains *why* it breaks (open-paragraph swallow; KaTeX has no such macro), and points to the CLI with the `<skill-dir>` placeholder convention (not `${CLAUDE_SKILL_DIR}`). Kept in `SKILL.md` rather than a new reference — the addition is ~10 lines and belongs next to the existing `$…$`/`$$…$$` guidance. Self-applied the CLAUDE.md DRY + Necessity gate: every added line shapes authoring behavior the renderer cannot warn about.
- **Tests** — [skills/report-in-markdown/scripts/test_md_integrity.py](../../../skills/report-in-markdown/scripts/test_md_integrity.py), 22 passing (clean file, adjacent-above, adjacent-below, separated-clean, every macro parametrized with its `\operatorname` fix, macro-in-code-fence skipped, macro-in-inline-code skipped, `$$`-in-code-fence skipped, odd-count flagged, word-boundary false-positive guard).

```
$ uv run --with pytest python -m pytest skills/report-in-markdown/scripts/test_md_integrity.py -q
......................                                                   [100%]
22 passed in 0.04s
```

CLI end-to-end (a file with an adjacent `$$` block and `\diag`/`\Cov`):

```
$ python3 skills/report-in-markdown/scripts/check_markdown.py /tmp/dirty.md
/tmp/dirty.md:2  [display-math-not-separated]  display $$ block touches a text line ... Put a blank line above and below ...
/tmp/dirty.md:3  [tex-only-macro]  \diag is undefined in KaTeX ...; write \operatorname{diag} instead.
/tmp/dirty.md:6  [tex-only-macro]  \Cov is undefined in KaTeX ...; write \operatorname{Cov} instead.

3 render-integrity issue(s) found.
$ python3 skills/report-in-markdown/scripts/check_markdown.py /tmp/clean.md
/tmp/clean.md: clean
```

The checker run on its own SKILL.md and on this task file both report `clean` — the `\diag`-class macros they mention sit in inline-code backticks and are correctly skipped.

### Live-render verification (against the real renderer, not assumption)

Drove samples through the dashboard's exact config — `markdownit({ html:false, linkify:true })` then `md.use(texmath, { engine: katex, delimiters: 'dollars' })`, mirroring [base.html:1649](../../../skills/task-system/scripts/templates/base.html#L1649) — using the repo's own vendored assets ([skills/task-system/scripts/vendor/](../../../skills/task-system/scripts/vendor/): `markdown-it.min.js`, `texmath.min.js`, `katex.min.js`) loaded into a Node `vm` sandbox (Node v25). This is the same markdown-it + texmath + KaTeX stack the standalone dashboard inlines.

**Grounding evidence (code).** In `texmath.min.js` the `dollars` block rules are registered with `e.block.ruler.before("fence", t.name, texmath.block(t))` — **no fourth `{ alt: [...] }` argument**. In markdown-it, a block rule whose `alt` list does not contain `"paragraph"` cannot interrupt an open paragraph. So a `$$` line directly under a text line cannot start a block; the open paragraph absorbs it.

**Empirical result.** The renderer confirms the rule but the precise failure is subtler than "the adjacent block never renders," so recording it exactly:

| Sample | Rendered HTML (math elided) | Block math standalone? |
|---|---|---|
| `intro text` ⏎ `$$…$$` (text directly **above** opening `$$`) | `<p>intro text` ⏎ `<section>…display…</section></p>` | **No** — the `<section>` is nested *inside* the `<p>`; the equation is pulled into the open paragraph rather than rendering as a standalone display block |
| `intro` ⏎ ⏎ `$$…$$` ⏎ ⏎ `after` (blank lines around) | `<p>intro</p>` ⏎ `<section>…display…</section>` ⏎ `<p>after</p>` | **Yes** — `<section>` is a sibling of the paragraphs |

The genuine silent breakage is a **non-blank text line directly above the opening `$$`** (it gets swallowed into the open paragraph). A text line directly *below* the closing `$$` rendered correctly as a standalone block in this texmath version. The checker still flags both above- and below-adjacency because "blank line above **and** below" is the documented authoring convention in `report-in-markdown` and the safe superset — flagging the below case costs an author one blank line and guards against the symmetric paragraph-continuation case; the rule message states the fix for both. This is a deliberate, evidence-grounded choice, not the task's stated premise that the below case also silently breaks in this version.

### Deviation from Planner Guidance

None material. Guidance offered the code-citation grounding as a fallback "if a full render harness is impractical"; the harness was practical via the vendored assets + Node `vm`, so I did both — the live render *and* the rule-registration citation — and the live render surfaced the above-vs-below nuance recorded above.
