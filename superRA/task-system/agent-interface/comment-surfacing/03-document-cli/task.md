---
title: "Document the Comment CLI + Dispatch Pointer"
status: implemented
depends_on:
  - 01-block-accessor
tags: []
created: 2026-06-01
---

## Objective

Make the comment read/resolve loop **discoverable** in the docs, enrich the standalone CLI for parity, and add the single dispatch pointer. Depends on task 01 (the accessor, reused by the CLI). **Sequenced after `lean-interface/02`** (which redesigns `task-system/SKILL.md` into a lean router with references) — see Coordination.

**Enrich `task_comment.py list`.** Reuse task 01's accessor so `list` prints the **full anchored block** (not just the ≤60-char `text_preview` at `task_comment.py:107-120`), matching what `task_read` now shows. Orphaned comments keep the `[ORPHANED]` rendering with the preview. Keep `--json` parity (full block).

**Document the CLI.**
- Add `task_comment.py` and `_comments.py` to the Script Inventory in `references/internals.md` (they are currently absent, `internals.md:174-188`).
- Add a short "Comments" subsection covering the read/resolve loop: `task_comment.py list <task>`, `list-tree`, `resolve <task> <id>`, the unresolved/resolved lifecycle, and that comments also surface via `task_read` (task 02). This lands in the **new structure** `lean-interface/02` produces — into `references/commands.md` if that reference is created, else `references/internals.md` — with at most a one-line pointer from the slimmed `task-system/SKILL.md` body. Do not document it in the old SKILL.md layout.

**Dispatch pointer (rec #2, reduced — researcher decision).** Add a **single pointer line** to `agent-orchestration` (dispatch-template area or orchestrator duties) noting that open comments surface to the agent automatically via `task_read`, and the orchestrator can additionally run `task_comment.py list <path>` to fold them into steering when useful. Do **not** build an injection mechanism — `task_read` already covers the common path.

**Coordination.** Run this task only after `lean-interface/02` is approved so the doc home (`references/commands.md` vs `references/internals.md`) is settled and the body pointer fits the new router. Flag in `## Results` that a new documented command surface (the comment CLI) was added, for `lean-interface/05-coverage-audit`'s baseline. Apply the `CLAUDE.md` DRY/Necessity gate to all added prose; `skill-creator` is unavailable in this harness.

**Validation:**
- `task_comment.py list` shows the full block; `--json` parity holds; orphaned rendering intact.
- `task_comment.py` and `_comments.py` appear in the Script Inventory; the Comments subsection exists in the reference and is reachable from the slimmed SKILL.md via one pointer.
- Exactly one pointer line added to `agent-orchestration`; no injection mechanism.
- No duplication with `task-system/SKILL.md` (single owner per command, per the lean-router design).

**Output:** `skills/task-system/scripts/task_comment.py`; `skills/task-system/references/internals.md` and/or `references/commands.md`; `skills/task-system/SKILL.md` (one-line pointer); `skills/agent-orchestration/SKILL.md` (one pointer line).

## Results

The comment read/resolve loop is now documented in the lean-router structure, the standalone CLI reaches full `--json` parity with `task_read`, and a single dispatch pointer was added.

### CLI enrichment — `task_comment.py --json` parity

The human `list` output already rendered the full anchored block (task 02 wired `anchored_block`); only the `--json` path lagged, emitting just `text_preview`. Fixed `_comment_to_json` to re-anchor against the live body and emit the full `block` (or `null` when orphaned), plus a live-computed `orphaned` flag, matching the JSON shape `task_read.py` exposes ([scripts/task_comment.py](../../../../../skills/task-system/scripts/task_comment.py)). The stored `text_preview` is retained under `anchor` for orphaned consumers. Human and `--json` output now both carry the full block; orphaned comments render `[ORPHANED]` + preview (human) and `orphaned: true` / `block: null` (JSON) — both verified against scratch tasks (live + orphaned anchor).

### Documentation home (lean-router structure)

- **`references/commands.md` §Comments** — new subsection documenting `superra task comment list <task>` (with `--all`), `tree`, `resolve <task> <id>`, the unresolved/resolved lifecycle, orphaned rendering, and `--json`. Uses the packaged `superra task comment …` form because the loop is wired into the `superra` CLI dispatcher ([cli.py:537-565](../../../../../skills/task-system/scripts/cli.py#L537-L565)) — consistent with the rest of `commands.md`. The subsection opens by noting unresolved comments already surface on the read path, so the standalone commands are framed as the explicit read/resolve loop, not a duplicate discovery path.
- **`references/internals.md` Script Inventory** — added `_comments.py` (sidecar data layer) and `task_comment.py` (`list` / `list-tree` / `resolve`); also updated the `task_read.py` row to mention unresolved comments.
- **`SKILL.md` Routing table** — one pointer row to `references/commands.md §Comments`.

### Dispatch pointer (`agent-orchestration`)

Extended the existing `superra task read` sentence in §Dispatch Templates (one line) to note that `task read` injects unresolved comments with their full blocks, and the orchestrator may additionally run `superra task comment list <task-path>` to fold them into `Additionally:` steering. No injection mechanism was built — `task read` already covers the common path.

### Coordination flag for `lean-interface/05-coverage-audit`

A new documented command surface — the comment read/resolve loop (`superra task comment list/tree/resolve`) — was added to `references/commands.md`, `references/internals.md`, and `SKILL.md`. The coverage audit's baseline should account for it. (Per dispatch steering, the `lean-interface` subtree is already approved/merged on the base branch, so this is recorded for completeness rather than as an active blocker.)

### Verification

- `~/.venv/bin/python -m pytest skills/task-system/scripts/test_task_system.py -q` → **285 passed**.
- `task_comment.py list` and `list --json` exercised on scratch tasks for both live-anchor (full block, `orphaned: false`) and orphaned-anchor (`[ORPHANED]` + preview, `block: null`) cases.

### Deviation from guidance

The objective's commands referenced the bare-script form (`task_comment.py list <task>`, `list-tree`, `resolve`). The loop is in fact wired into the packaged `superra` CLI as `superra task comment list/tree/resolve` ([cli.py:537-565](../../../../../skills/task-system/scripts/cli.py#L537-L565)), and `commands.md` documents every other command in the packaged `superra task …` form. I documented the packaged form for consistency with the surrounding reference; the underlying script is still named in the internals Script Inventory. This satisfies the objective (discoverable read/resolve loop, single owner per command) while fitting the lean-router convention.
