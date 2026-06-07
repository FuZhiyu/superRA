---
title: "Surface Unresolved Comments in task_read.py"
status: implemented
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

`task_read.py` now surfaces a task's unresolved comments with their full anchored block on every read path, and the surfacing works reliably under bare `python3` (no `pyyaml`).

**What changed**

- [`task_read.py`](../../../../../skills/task-system/scripts/task_read.py): added a shared `_open_comments(target_task)` helper that loads the sidecar, keeps only unresolved comments, and resolves each one's full block via task 01's `anchored_block` accessor (block `None` ⇒ orphaned). `render_human` emits an `=== Open Comments ===` section after the body-sections loop and before Sibling Dependencies; each entry shows `[author] on ## section`, the full block (indented) or the stored preview + `[ORPHANED — block moved/edited away]`, then the comment body. The section is omitted entirely when there are no unresolved comments. `render_json` mirrors this under an `open_comments` key placed after `task` and before `dependencies`, as `{author, section, block, preview, body, orphaned}` with the full block text (no length cap) and `block: null` + preserved `preview` for orphans.
- [`_comments.py`](../../../../../skills/task-system/scripts/_comments.py): resolved the `pyyaml` hard-dependency at the source. `save_comments` now writes the sidecar as **JSON** (`json.dumps`, stdlib) — JSON is a strict subset of YAML, so the file stays a valid `comments.yaml` for every existing reader (dashboard `yaml.safe_load`, tests) while becoming parseable with no third-party library. `load_comments` parses with stdlib `json.loads` first (the reliable `python3` path), and only falls back to `yaml.safe_load` for legacy block-style YAML files written before this switch. The fallback under bare `python3` (legacy file + no `pyyaml`) raises a loud `RuntimeError` telling the user to re-save, rather than silently returning `[]` — honoring the researcher decision that missing-pyyaml must never silently show nothing. The first comment mutation upgrades a legacy file to JSON. (The three existing in-repo `comments.yaml` files are all fully-resolved, so they never surface as open comments regardless.)
- [`task_comment.py`](../../../../../skills/task-system/scripts/task_comment.py): enriched `list` to show the **full anchored block** (parity with `task_read`) instead of the ≤60-char preview, using the same `anchored_block` accessor; orphaned comments fall back to the stored preview + orphaned note. This is the researcher's "also enrich the standalone CLI" minor default.

**Reliability design choice (deviation note).** The Planner Guidance suggested "a small stdlib loader for the flat comment sidecar schema … (follow the `_task_io.py` frontmatter precedent)." I did not hand-roll a block-YAML parser. PyYAML's real on-disk output for this schema uses single-quoted block folding and double-quoted escape sequences (`—`, line-continuation) for multi-line/unicode comment bodies and previews — a hand parser would risk silently corrupting comment text. Instead I made the *writer* emit JSON (a strict YAML subset, so nothing downstream breaks) and the *reader* use stdlib `json.loads`. This satisfies the objective's stated alternative ("or otherwise factor the load path to be stdlib-reachable") and is lossless for all unicode/multiline content, which a bespoke YAML parser would not guarantee.

**Coordination — cross-edit for `lean-interface/05-coverage-audit`.** Added one clause to [`skills/using-superRA/SKILL.md §Task Interface`](../../../../../skills/using-superRA/SKILL.md) line 45 (the `task_read` read-path mandate authored by `lean-interface/01`): it now ends "… and surfaces any unresolved comments anchored to the task so you act on them." `lean-interface/05-coverage-audit` should account for this added clause in its git-snapshot baseline. The clause lives only in the source `SKILL.md`; no generated role reference duplicates it.

**Verification (all run fresh this session)**

- Bare `python3 task_read.py --path <task-with-comments>` (confirmed no `pyyaml` importable): prints the `=== Open Comments ===` section with the full block for an unresolved comment, shows an orphaned comment as preview + `[ORPHANED …]`, and excludes a resolved comment. Exit 0.
- `--json`: carries `open_comments` (after `task`, before `dependencies`) with full `block` text, `block: null` + preserved `preview` for the orphan, `orphaned` flag, and resolved comments excluded.
- A no-comment task emits no Open Comments section (no empty header) and is otherwise unchanged — context, frontmatter, sections, sibling deps intact.
- `task_comment.py list` under `python3` shows full blocks with the orphaned fallback.
- Legacy block-YAML sidecar: loads via fallback under `~/.venv` (pyyaml present); raises the loud `RuntimeError` under bare `python3` rather than silently skipping.
- Full suite green: `test_task_system.py` + `test_cli.py` = 303 passed; `test_dashboard.py` = 113 passed (JSON-format sidecar is transparent to the dashboard's YAML reader).
