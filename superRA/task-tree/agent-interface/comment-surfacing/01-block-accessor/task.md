---
title: "Expose Full Anchored Block from _comments.py"
status: approved
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Add one shared accessor to `skills/task-tree/scripts/_comments.py` that returns the **full text of the block a comment is anchored to**, so both `task_read.py` (task 02) and `task_comment.py list` (task 03) resolve the block through a single implementation instead of duplicating the logic.

**Why it's needed.** `resolve_anchors` already re-anchors `anchor.block_index` by calling `split_into_blocks(section_content)` (`_comments.py:297-318`), but it only mutates the index — `blocks` is a local that goes out of scope, so the block *text* is never returned or stored. Callers currently have only the persisted ≤60-char `text_preview`.

**What to add.** A function such as `anchored_block(comment, body) -> str | None` that re-derives the block from the live body — conceptually `split_into_blocks(parse_body_sections(body)[anchor.section])[anchor.block_index]` — reusing the **same** block-splitting and re-anchoring logic `resolve_anchors` uses (do not fork a second split implementation). Contract:
- Returns the full block text for a comment whose anchor resolves (including after the block moved and was re-anchored).
- Returns `None` for an **orphaned** comment (section gone, or preview matched no block — the existing `comment.orphaned` runtime flag at `_comments.py:293-294,317-318`). Callers handle the fallback; this function does not raise on orphaned anchors.
- **No behavior change** to existing callers of `resolve_anchors` / the dashboard.

**Reliability constraint (researcher decision).** The block-resolution path that tasks 02/03 will call must be usable **without `pyyaml`** — the read path is invoked as `python3 task_read.py`. `split_into_blocks` / `parse_body_sections` operate on the task **body string** (already available to `task_read` via `_task_io`, which is stdlib-only), so the accessor itself should not pull in the `yaml`-dependent loading path. If reaching the accessor currently forces importing the `yaml`-importing module top-level, factor the block logic so the body-string path is reachable stdlib-only (e.g. keep `split_into_blocks` / the accessor independent of the `import yaml` at `_comments.py:16`). Confirm `python3 -c "import <the needed symbol>"` succeeds without pyyaml; the *comments.yaml loading* (which legitimately needs yaml today) is a separate concern handled in task 02.

**Validation:**
- Unit-level: in-block comment → full block text; comment whose block moved → re-anchored full block; orphaned → `None`. (Tests authored in task 04; this task may include a quick inline check.)
- Existing comment/dashboard behavior unchanged (run the existing suite with `~/.venv/bin/python`).
- The accessor (and the block-splitting it relies on) is importable without `pyyaml`.

**Output:** `skills/task-tree/scripts/_comments.py`.

## Results

Added the shared accessor `anchored_block(comment, body) -> str | None` to [_comments.py](../../../../../skills/task-tree/scripts/_comments.py) and made the body-string resolution path importable without `pyyaml`. Two coordinated changes:

**1. Single block-resolution implementation (no fork).** Extracted the per-comment re-anchoring logic that lived inline in `resolve_anchors` into a private helper `_reanchor(comment, sections) -> tuple[list[str], int] | None` ([_comments.py:276](../../../../../skills/task-tree/scripts/_comments.py#L276)). It mutates `anchor.block_index` (re-anchoring after a block moves) and `comment.orphaned` exactly as before, and returns `(blocks, block_index)` or `None` when orphaned. Both `resolve_anchors` ([_comments.py:312](../../../../../skills/task-tree/scripts/_comments.py#L312)) and the new `anchored_block` ([_comments.py:330](../../../../../skills/task-tree/scripts/_comments.py#L330)) call it, so there is one block-splitting + re-anchoring path. `anchored_block` returns `blocks[idx]` (the full block text) on resolution and `None` on orphan; it never raises.

**2. No-pyyaml importability.** Removed the module-top `import yaml` ([_comments.py:16](../../../../../skills/task-tree/scripts/_comments.py)) and made it a function-local import inside `load_comments` and `save_comments` — the only two functions that touch `comments.yaml`. The module, `anchored_block`, `resolve_anchors`, and `split_into_blocks` now import under bare `python3` (no pyyaml). The `comments.yaml` loading path still uses yaml; it raises `ModuleNotFoundError` only when *called* without yaml, which is the separate concern task 02 guards on the read path.

**Section-name convention (note for tasks 02/03):** `anchor.section` is stored as the **bare heading name** (`"Objective"`, not `"## Objective"`), matching `parse_body_sections`'s keys ([_task_io.py:134](../../../../../skills/task-tree/scripts/_task_io.py#L134)) and the dashboard/`task_comment.py` callers. `anchored_block` keys into `parse_body_sections(body)` directly, so callers pass the bare section name.

### Verification

- **No-pyyaml import** (the load-bearing constraint): `python3 -c "import yaml"` → `ModuleNotFoundError`, confirming bare `python3` lacks pyyaml in this env; `python3 -c "from _comments import anchored_block, resolve_anchors, split_into_blocks"` → imports OK.
- **Inline functional check under bare `python3`** (no pyyaml): in-block comment → full block text; comment with a stale index whose preview matches a moved block → re-anchored to the correct index and full text returned (`orphaned=False`); orphaned by missing section → `None`/`orphaned=True`; orphaned by no-preview-match → `None`/`orphaned=True`. All passed.
- **No regression:** `~/.venv/bin/python -m pytest skills/task-tree/scripts/test_dashboard.py skills/task-tree/scripts/test_task_tree.py -q` → **264 passed**. `task_comment.py` and the yaml-backed load/save path still import and run under the venv.

## Review Notes

> 1. [MINOR] The degraded-read design assumes "mutation callers run under `uv` (pyyaml present) and never hit it" ([_comments.py:30](../../../../../skills/task-tree/scripts/_comments.py#L30)), but the committed wrapper falls back to bare `python3` when `uv` is absent, so a comment mutation against a legacy block-YAML sidecar raises `LegacyCommentFormatError` uncaught (traceback) instead of degrading. Catch it on the mutation path with the same visible note, or soften the docstring claim.
