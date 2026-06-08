---
title: "Markdown Render-Integrity Check: Hook + Self-Diagnose Tool"
status: approved
depends_on: []
tags: []
created: 2026-06-08
---

## Objective

Ship a fast, warn-only markdown **render-integrity** check that catches the markdown patterns that silently fail to render in the superRA dashboard, and surface it two ways: (a) automatically, via the existing PostToolUse hook, after any agent Edit/Writes a markdown file under a task root; and (b) on demand, as a self-diagnose CLI an agent can run on any markdown file before committing. The same checker logic backs both surfaces.

**Why this exists.** The dashboard renders task markdown with `markdown-it` + `markdown-it-texmath` configured `delimiters: 'dollars'` (the single source of truth is [base.html:1649](../../skills/task-system/scripts/templates/base.html#L1649)). Two classes of authoring mistake render as broken output with no error:

1. **Display-math not blank-line separated.** In the `dollars` ruleset, a `$$ … $$` display block cannot interrupt an open paragraph. When a `$$` line directly touches the text line above it (no blank line between), `markdown-it` has already opened a paragraph and swallows the whole `$$ … $$` as literal paragraph text — it never renders as block math. Every display equation must have a blank line above and below the `$$` fence lines (no blank lines inserted *inside* the block).
2. **TeX-only macros KaTeX does not define.** Operators like `\diag`, `\cov`, `\var`, `\corr`, `\plim`, `\argmin`, `\argmax`, `\Cov`, `\Var`, `\E` work in a LaTeX `.tex` document but are undefined in KaTeX and render as an error. They must be written with `\operatorname{...}` (e.g. `\operatorname{diag}`, `\operatorname{Cov}`).

**Deliverables (split across the two subtasks):**

- A single stdlib-only checker module + a self-diagnose CLI under `skills/report-in-markdown/scripts/`, plus the authoring rules documented in `report-in-markdown` so the rule and its enforcement share one home.
- Integration of that checker into the existing PostToolUse path so it runs automatically — non-blocking, warn-only — on any `.md` edited under a task root, for both the Claude (Edit/Write) and Codex (apply_patch) edit paths.

**Done when:** editing a task `.md` with an adjacent `$$` block or a `\diag`-class macro produces a non-blocking hook warning naming the file and line; a clean file produces no output; the same CLI run by an agent on an arbitrary markdown file reports the same findings; and the blank-line rule is verified against the dashboard's actual `dollars` texmath config rather than assumed.

### Constraints

- **Warn-only, never block, never auto-fix.** Both surfaces only report. The hook always exits 0 and emits findings as model-visible context; it does not rewrite the file. (superRA automation warns on ambiguous state rather than mutating author content.)
- **Fast on the hot path.** The PostToolUse hook fires on every Edit/Write. The check must early-exit cheaply for non-`.md` files and files outside a task root, and use regex/line scanning — no full markdown parse, no third-party parser. The checker stays stdlib-only so it runs under both `uv run --script` and a bare `python3` fallback, matching `task_hook.py` (which declares no dependencies).
- **One checker, two callers.** The detection logic lives in exactly one module; the hook and the CLI both call it. No duplicated rule logic.
- **Fence-aware.** Skip content inside fenced code blocks (```` ``` ````) and inline code spans (`` ` ``) so example math in documentation is not flagged.

### Context

- The dashboard texmath config is authoritative for what "renders" means: `md.use(texmath, { engine: katex, delimiters: 'dollars' })` at [base.html:1649](../../skills/task-system/scripts/templates/base.html#L1649). `dollars` = inline `$…$`, display `$$…$$`. Ground the blank-line rule in this, not in assumption — see the live-render verification in `01-checker-and-rules`.
- The existing PostToolUse hook entry is [skills/task-system/scripts/task_hook.py](../../skills/task-system/scripts/task_hook.py). It already fires on Edit/Write/Bash/apply_patch for both harnesses, already emits non-blocking `additionalContext` feedback JSON via `_feedback_json`, and declares no dependencies. The hook integration extends this file — it does not add a new hook registration.
- `report-in-markdown` currently ships no scripts; its `## Math` section documents `$…$`/`$$…$$` but not the blank-line or KaTeX-macro rules. This work adds both the rules and the first bundled script to that skill.

### Conventions

- **This is superRA-internal tooling, not a research vertical** (no `econ-data-analysis` / `theory-modeling` / `writing` domain skill applies). It is governed by the repo `CLAUDE.md` contributor rules. Editing `skills/report-in-markdown/SKILL.md` (or adding a reference) is skill authoring: load `skill-creator` first, and self-apply the CLAUDE.md "Teach the Protocol, Don't Prescribe Each Action" two-test gate (DRY + Necessity) on every instruction line added.
- Bundled-script invocation follows the established placeholder convention: `uv run --script <skill-dir>/scripts/<name>.py …`, where `<skill-dir>` is the directory containing the skill's `SKILL.md` (substitute the real path). Do **not** use `${CLAUDE_SKILL_DIR}` — it is Claude-only and unset under Codex.
- Do not hand-edit generated files. The `hooks/task-hook` shell shim is generated from `wrapper_resolver.py`; this work changes only `task_hook.py` (which the shim already invokes), so the shim needs no regeneration and no hook-manifest (`hooks/hooks*.json`) change.
- Run the test suite with deps supplied per the repo `CLAUDE.md`, e.g. `uv run --with pytest --with pyyaml python -m pytest skills/...`.

## Results

Shipped a warn-only markdown render-integrity check on both surfaces, backed by a single checker. Verified end-to-end against the dashboard's real `markdown-it-texmath` `dollars` renderer and the live PostToolUse hook; 347 tests pass across the two subtasks.

**What it catches** — the two patterns that render silently-broken in the dashboard, both grounded in the real renderer (not assumed):
- *Display `$$` not blank-line separated* — a `$$` block touching the text line above it is swallowed into the open paragraph and never renders as block math. The live render confirmed the genuine break is the text-above case; the checker flags both above- and below-adjacency as the safe superset matching the documented "blank line above and below" convention.
- *TeX-only operator macros* — `\diag`, `\cov`, `\var`, `\Cov`, `\E`, … are undefined in KaTeX and render as errors; the fix is `\operatorname{...}`. The macro set is one extensible named list.

**Two surfaces, one checker** ([01-checker-and-rules](01-checker-and-rules/task.md)):
- `skills/report-in-markdown/scripts/md_integrity.py` — stdlib-only, fence-aware `check(text) -> list[Issue]`, the single home of the detection logic.
- `skills/report-in-markdown/scripts/check_markdown.py` — self-diagnose CLI (`uv run --script … <file>`, `python3` fallback, always exit 0) for an agent to check any markdown before committing.
- The `$$`/`\operatorname` rules are documented under `## Math` in `report-in-markdown`.

**Auto-enforcement** ([02-hook-integration](02-hook-integration/task.md)): the existing `task_hook.py` PostToolUse path now runs the same `check()` on any `.md` edited under a task root — both the Claude Edit/Write and Codex apply_patch paths — merging findings into the existing non-blocking `additionalContext` feedback channel. No new hook registration and no generated-shim edit were needed; the checker is imported relative to `task_hook.py` so it resolves across all install layouts. A cheap `.md`-under-task-root gate keeps the hot path fast; clean and non-markdown edits stay silent.
