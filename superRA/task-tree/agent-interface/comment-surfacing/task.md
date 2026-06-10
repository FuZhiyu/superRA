---
title: "Surface Task Comments to the Agent Loop"
status: revise
depends_on: []
tags: []
created: 2026-06-01
---

## Objective

Make the task-tree **comment feature visible to the agent loop**. Today a researcher pins comments to `task.md` blocks via the dashboard, but agents never see them: `task_read.py` (the canonical agent read path) has zero comment handling, no role spec or workflow skill references `task_comment.py`, and the CLI is undocumented. Comments are a dashboard-only human feature. This subtree closes the discovery gap (surface unresolved comments on the read path + document the CLI) and the context-richness gap (show the *full anchored block*, not the ≤60-char preview).

**Design source.** A planning agent verified both gaps and the mechanics against the code (see each child objective for cited `file:line`). Placement is a sibling of `lean-interface` under `task-tree/agent-interface/` (same concern: the agent-facing interface to the task tree).

**Researcher decisions (confirmed, load-bearing):**
- **Reliability:** comment surfacing in `task_read.py` MUST work under the documented `python3 task_read.py` invocation. In this environment bare `python3` has no `pyyaml` (the existing `_comments.py` does `import yaml` at module top and fails under `python3`; it only runs under `uv`/`~/.venv`). A best-effort "optional import, skip if missing" would silently surface nothing on the common path — not acceptable. The read path must not hard-depend on `pyyaml`.
- **Dispatch-injection (rec #2):** dropped to a single pointer line in `agent-orchestration` (folded into `03-document-cli`), not a separate mechanism — because `task_read` (which every dispatched agent runs) now surfaces comments, so a second injection path is redundant.
- **Minor defaults:** surface **unresolved** comments only (matches `task_comment.py list` default); emit the **full block** (no length cap) in both human and `--json` output; **also enrich `task_comment.py list`** to show the full block so the standalone CLI matches `task_read` (the accessor is cheap to reuse).

**Sequencing / coordination with the in-flight `agent-surface-redesign` subtree** (cross-parent, so not expressible via `depends_on` — enforced by orchestrator ordering):
- `01-block-accessor` and `02-surface-in-task-read` touch only `_comments.py` and `task_read.py` — no overlap with `agent-surface-redesign` — and may run as soon as ready.
- `02` adds a one-clause cross-edit to `using-superRA/SKILL.md §Task Interface` (just authored by `agent-surface-redesign/01-core-in-using-superra`, approved) noting `task_read` also surfaces open comments. Coordinate: land it only after `agent-surface-redesign/01-core-in-using-superra` is approved (it is), and flag it for `agent-surface-redesign/09-coverage-audit` so its git-snapshot baseline accounts for the added clause.
- `03-document-cli` documents the comment CLI in `task-tree/SKILL.md` / its references — which `agent-surface-redesign/02-task-tree-slim` redesigned into a lean router. **Run `03` after `agent-surface-redesign/02-task-tree-slim` is approved** so the doc lands in the new structure (a reference, e.g. `references/commands.md`, with a one-line body pointer) instead of being clobbered. Flag the added command surface for `agent-surface-redesign/09-coverage-audit`.

**Contributor gates (every child):** apply the repo `CLAUDE.md` "Teach the Protocol" DRY/Necessity gate to any prose; scope all edits/commits to your assigned worktree (its absolute path is supplied in the dispatch `Worktree:` field — sibling worktrees of this repo exist, do not touch them); `skill-creator` is not registered in this harness, so do not attempt to load it. Run tests with `~/.venv/bin/python` (it has `pyyaml`); the *runtime* read path, however, must not require it.

**Success criterion:** an agent that runs the documented `python3 task_read.py --path <t>` on a task with unresolved comments sees each comment together with the full block it is pinned to (orphaned comments degrade to preview + an orphaned note); the comment read/resolve CLI is discoverable in the docs; and no existing behavior or invocation contract is broken.

## Results

The task-tree comment feature is now visible to the agent loop. Previously a researcher could pin comments to `task.md` blocks via the dashboard, but agents never saw them — `task_read.py` (the canonical read path) had no comment handling and the CLI was undocumented. This subtree closed both the discovery gap and the context-richness gap.

**What an agent sees now.** `task_read` emits an `=== Open Comments ===` section listing each *unresolved* comment together with the **full text of the block it is anchored to** — not a "block N" coordinate or a ≤60-char preview — followed by the comment body. Resolved comments are excluded; orphaned comments (block moved or deleted) degrade to the stored preview plus an `[ORPHANED]` note. `--json` mirrors this under an `open_comments` key. See [02-surface-in-task-read](02-surface-in-task-read/task.md).

**Reliability under bare `python3`.** The read path must work under the documented `python3 task_read.py` invocation, where `pyyaml` is unavailable. The comment sidecar is now written as JSON-in-`.yaml` — a strict YAML subset that is lossless, still valid for the dashboard's YAML reader, and parseable by stdlib `json` with no third-party library. The three pre-existing legacy block-YAML sidecars were migrated losslessly; any stray future legacy file degrades gracefully (visible note, read still exits 0) instead of crashing the whole read. See [02-surface-in-task-read](02-surface-in-task-read/task.md).

**Discoverability.** The read/resolve loop is documented as `superra task comment list/tree/resolve` in [`references/commands.md` §Comments](../../../../skills/task-tree/references/commands.md), the scripts (`_comments.py`, `task_comment.py`) are in the internals Script Inventory, and `agent-orchestration` carries a one-line pointer noting comments surface automatically via `task read`. See [03-document-cli](03-document-cli/task.md).

**Test coverage.** 17 tests in `skills/task-tree/scripts/tests/test_comments.py` cover the block accessor, `task_read` human + `--json` surfacing, the enriched CLI, and the load-bearing no-`pyyaml` reliability path (a `sys.meta_path` finder genuinely disables `import yaml`; mutation-verified to fail if the behavior regresses). The full task-tree suite stays green (534 passed). See [04-tests](04-tests/task.md).

**Format-change decision (load-bearing).** Meeting the no-`pyyaml` requirement required changing the on-disk comment sidecar format from PyYAML block-style to JSON-in-`.yaml`, repo-wide; confirmed with the researcher during integration. The format is lossless and backward-readable, and the alternative — a hand-rolled stdlib YAML parser — was rejected as risking silent corruption of multi-line/unicode comment bodies.

## Review Notes

> 1. [MINOR] The Sequencing section was updated but the "Design source" paragraph ([task.md:13](task.md#L13)) still reads "Placement is a sibling of `lean-interface` under `task-tree/agent-interface/`" — the renamed sibling is `agent-surface-redesign`. Update that paragraph to match.
>    → implemented: updated all `lean-interface` references to `agent-surface-redesign` and `05-coverage-audit` to `09-coverage-audit` in the Sequencing section
