---
title: "Document the Comment CLI + Dispatch Pointer"
status: not-started
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
