---
title: "Refresh the worktree dropdown on open (no page reload)"
status: approved
depends_on:
  - 03-worktree-url-routing

tags: []
created: 2026-06-07
---

## Objective

Task 03 made switching worktrees a client-side navigation, but the dropdown's **option list** is only fetched once, at page load (`fetchWorktrees()` on init, plus `applyWorktree`/`onFullReload`). A worktree created or removed while the dashboard is open does not appear (or disappear) in the selector until the user manually reloads the whole page. Opening the dropdown should re-fetch the worktree list so it reflects the current set of worktrees without a page refresh.

**File:** `skills/task-tree/scripts/templates/base.html` (worktree selector).

## Results

Implemented in [base.html](skills/task-tree/scripts/templates/base.html).

- `initWorktreeSelectorRefresh()` wires `mousedown` (click that opens the native picker) and `focus` (keyboard) on `#worktree-select` to call `fetchWorktrees()`, so each time the user reaches for the dropdown the list is re-fetched from `/api/worktrees`. Called once from page-load init alongside the initial `fetchWorktrees()`.
- To keep refresh-on-open from rewriting `<option>`s under an already-open native picker (which collapses it), `populateWorktreeSelector` now computes a signature of the option set (each worktree's id + branch + plan_title + agent flag, plus the active id) and short-circuits the innerHTML rebuild when nothing changed. The rebuild — and the visible list change — happens only when the worktree set actually differs.

Because the fetch is async, a brand-new worktree shows up on the dropdown's next open after the one that triggered its discovery; no full page reload is ever required, which is the regression this task closes.

### Validation

- **Dashboard test suite:** 117 passed, 2 skipped (`uv run --project skills/task-tree --with pytest --with httpx python -m pytest skills/task-tree/scripts/test_dashboard.py -q`). `TestWorktreeSelectorLiveRefresh` asserts the refresh-on-open wiring (`mousedown`/`focus` → `fetchWorktrees`) and the signature guard (`signature === _wtSignature` short-circuit in `populateWorktreeSelector`).
- **Real served path:** `initWorktreeSelectorRefresh` is present in the served page (HTTP 200).

## Review Notes

*(Retrospective audit, 2026-06-10 — MINOR items only; status stays `approved`.)*

1. **MINOR** — wiring both `mousedown` *and* `focus` means a single click-to-open can fire `fetchWorktrees()` twice, and each `/api/worktrees` call currently costs a *double* full git discovery (`git worktree list` + `git rev-parse` + one `git log -1` per worktree, run twice — see the parent's [Review Notes item 3](../task.md)). Debounce the two triggers (e.g. skip `focus` within ~200ms of `mousedown`) or add a short server-side discovery cache.
2. **MINOR** — `TestWorktreeSelectorLiveRefresh` asserts wiring strings (`mousedown`/`focus` → `fetchWorktrees`, the `_wtSignature` short-circuit) rather than executing the signature guard; the no-rebuild-under-open-picker behavior the guard exists for is untested. A node-harness run of `populateWorktreeSelector` over an unchanged worktree list (asserting no innerHTML rebuild) would pin it.
