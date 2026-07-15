---
title: "Worktree-Scoped Dashboard Launch URLs"
status: not-started
depends_on:  []
---

## Objective

Emit and open dashboard URLs scoped to the invoking worktree so a repo-shared server never falls back to a different launch worktree.

- Use the dashboard's canonical, URL-encoded worktree selector, including basename-collision disambiguation; do not ask agents to reconstruct the selector from a directory basename.
- Cover fresh launch and repo-scoped reuse, with a regression that launches from one worktree and reuses the server from another.
- Update the owning task-tree and main-agent instructions so the emitted scoped URL is the source of truth for task deep links.
- Preserve foreground serving, doc mode, standalone export, collision-safe one-server-per-repo reuse, and the existing direct-open behavior for PDF links. Inline PDF preview is outside this fix.

### Generated-artifact boundary

This task does not change canonical role specs. Do not edit `skills/using-superra/references/direct-mode-implementer.md`, `skills/using-superra/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, or `.codex/agents/superra_reviewer.toml`; if scope expands into `agents/*`, regenerate and check them with `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`.

## Planner Guidance

The background supervisor currently prints and opens a bare localhost URL on both spawn and reuse. `_worktree_id_for_plan_root()` already owns canonical selector construction, while `resolve_worktree()` intentionally maps an absent selector to the server's launch worktree. The browser-open tests in `skills/task-tree/scripts/test_dashboard.py` currently encode the bare-URL behavior and exercise only one plan root.

## Results
