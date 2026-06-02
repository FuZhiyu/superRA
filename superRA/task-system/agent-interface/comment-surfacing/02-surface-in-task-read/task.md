---
title: "Surface Unresolved Comments in task_read.py"
status: not-started
depends_on:
  - 01-block-accessor
tags: []
created: 2026-06-01
---

## Objective

Make `skills/task-system/scripts/task_read.py` surface a task's **unresolved comments with their full anchored block** — the highest-leverage fix, since `task_read` is the canonical read path every dispatched agent runs. Depends on task 01 (the block accessor).

**Human output (`render_human`).** After the body-sections loop and before the Sibling Dependencies block (around `task_read.py:199`), emit an `=== Open Comments ===` section. For each **unresolved** comment: the author/section header, the **full anchored block** (via task 01's accessor), and the comment body. For an **orphaned** comment (accessor returns `None`): fall back to the stored `text_preview` plus an explicit `[ORPHANED — block moved/edited away]` note rather than indexing. Omit the whole section when there are no unresolved comments (no empty header).

**JSON output (`render_json`).** Mirror under an `open_comments` key after `task_data` (around `task_read.py:254`): a list of `{author, section, block, body, orphaned}` with `block` carrying the **full block text, no length cap** (researcher decision: parity with human output). Orphaned entries set `orphaned: true` and `block: null` with the preview preserved.

**Reliability — must work under `python3` (researcher decision).** `task_read.py`/`_task_io.py` are stdlib-only and invoked as `python3 task_read.py`; in this environment bare `python3` has **no `pyyaml`**, but `_comments.py` does `import yaml` at module top (`_comments.py:16`). A naive `from _comments import …` makes `task_read` hard-fail `ModuleNotFoundError: No module named 'yaml'` on the common path, silently killing the feature. Resolve this so comments **reliably** surface under `python3`:
- Read `comments.yaml` without requiring `pyyaml` — e.g. a small stdlib loader for the flat comment sidecar schema (the repo already hand-parses YAML frontmatter without a yaml lib in `_task_io.py` — follow that precedent), or otherwise factor the load path to be stdlib-reachable. Reuse task 01's accessor for block text.
- Do **not** adopt the "optional import, skip if missing" pattern as the final state — under `python3` it would skip every time, which the researcher explicitly rejected. (A defensive guard for a genuinely-malformed/absent sidecar is fine; missing-pyyaml is not an acceptable reason to silently show nothing.)
- Verify: `python3 skills/task-system/scripts/task_read.py --path <a-task-with-comments>` prints the Open Comments section with full blocks, with **no** `uv`/`~/.venv`.

**Coordination — one-clause cross-edit to `using-superRA/SKILL.md §Task Interface`.** That section (authored by `lean-interface/01`, approved) mandates `task_read` as the read path. Add a single clause noting `task_read` also surfaces unresolved comments anchored to the task, so an agent knows to act on them. Keep it to one clause (DRY/Necessity). Flag this added clause in your `## Results` so `lean-interface/05-coverage-audit` accounts for it in its git-snapshot baseline.

**Validation:**
- `python3` invocation surfaces unresolved comments with full blocks; orphaned ones show preview + orphaned note; zero-comment tasks show no section.
- `--json` carries `open_comments` with full block text and the orphaned shape.
- Resolved comments are excluded by default.
- No regression to existing `task_read` output (ancestor context, frontmatter, sections, sibling deps) — diff a no-comment task before/after.
- The one-clause `§Task Interface` cross-edit is present and noted for the coverage audit.

**Output:** `skills/task-system/scripts/task_read.py`; one-clause edit to `skills/using-superRA/SKILL.md`.

## Results
