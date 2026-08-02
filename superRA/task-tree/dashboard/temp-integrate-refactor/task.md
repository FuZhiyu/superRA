---
title: "TEMPORARY — Integrate Refactoring Pass: Local Open and Tab Title"
status: not-started
depends_on:  []
---

## Objective

Execute the Integrate refactoring pass for the local-open and tab-title work on branch `dashboard-local-file-open`, against the record matured at [the parent dashboard task](../task.md). This task is temporary: delete it at Integrate closeout. It bounds one pass and carries no durable content.

**Protect decision:** commit `91252c25`, *integrate(protect): keep the dashboard rollup, fold both children, rely on the existing suite*. It selected nothing to drop, named the parent's `## Results` as the durable home plus a `RELEASE-NOTES.md` entry under `Unreleased`, folded and deleted `local-file-open/` and `task-scoped-tab-title/`, kept the dashboard subtree alive for the not-started `nonloopback-host-serve` sibling, and chose existing automated coverage as the entire protection — no new smoke test, by researcher judgment.

**Governing diff:** `git diff 68a09aa431f5dfdbb101d91ef03d59f0d519e961..HEAD`, with `BASE_HEAD_SHA` = `68a09aa431f5dfdbb101d91ef03d59f0d519e961`. Recompute it at the start of the pass; the triage below was taken at `f52f270a`.

**Protected record — the artifacts every surviving hunk must trace to:**

- [the parent task's `## Results`](../task.md) — §Opening files, and naming the tab plus §Verification, the durable home.
- [RELEASE-NOTES.md](../../../../RELEASE-NOTES.md) `## [Unreleased]` — the two user-visible behaviors.
- [internals.md §Dashboard](../../../../skills/task-tree/references/internals.md#L232) — the contributor-facing bind/mode conditions and `SUPERRA_EDITOR`.
- [docs/site/02-quickstart/task.md:23](../../../../docs/site/02-quickstart/task.md#L23) — the adopter-facing launcher sentence.
- [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py) — `TestLocalOpen`, `TestTabTitle`, `TestTabTitleWiring`, and the updated `TestWorktreeOpenButton` / `TestFileLinkConsistency`; the selected protection.

### Actions

**1. Triage the recomputed governing diff hunk by hunk against the survivor set below.** Anything outside it is a pruning candidate — revert confident junk, raise anything scope-ambiguous rather than deleting it silently. The maturation triage at `f52f270a` found no unmatched hunk, so a new one means something landed after that commit.

Survivor set, by artifact:

- [plan_dashboard.py](../../../../skills/task-tree/scripts/plan_dashboard.py) — `BOUND_HOST` with the `serve()` record-and-restore, `EDITOR_ENV_VAR` / `DEFAULT_EDITOR`, the `local_open=` render kwarg on `GET /`, `_is_loopback_host`, `_is_loopback_authority`, `_local_open_enabled`, `_editor_executable`, `_spawn`, `_open_native_sync`, `_open_editor_sync`, and [`POST /api/open`](../../../../skills/task-tree/scripts/plan_dashboard.py#L1413).
- [base.html](../../../../skills/task-tree/scripts/templates/base.html) — the `window.LOCAL_OPEN` block and the header [`#worktree-open-btn`](../../../../skills/task-tree/scripts/templates/base.html#L70) element.
- [dashboard.css](../../../../skills/task-tree/scripts/templates/dashboard.css) — the `.vscode-btn` → [`.open-btn`](../../../../skills/task-tree/scripts/templates/dashboard.css#L1097-L1122) rename with its three in-file ripple sites (doc-mode hide rule, `pointer: coarse` tap-highlight list, `#worktree-open-btn` margin override), the `--accent-soft` / `--accent` hover, and the [`.open-toast`](../../../../skills/task-tree/scripts/templates/dashboard.css#L1127-L1146) block.
- [dashboard.js](../../../../skills/task-tree/scripts/templates/dashboard.js) — `decodePathHref`; the body-link and attachment `data-open-path` branches in `renderMarkdown`; `taskFileOpenPath`; `showOpenError`; `openLocalPath`; the delegated `[data-open-path]` click handler; the [`EDITOR_ICON` / `OPEN_ICON`](../../../../skills/task-tree/scripts/templates/dashboard.js#L1066-L1077) pair replacing `VSCODE_ICON`; `loadActiveNode`'s open-button build, tab-title set, and both error clears; `loadActiveArtifact`'s title set and clear; `SITE_TITLE` / `setTabTitle` / [`refreshTabTitle`](../../../../skills/task-tree/scripts/templates/dashboard.js#L922-L932); `patchTabTitleWhenReady`; `worktreeLabel` with its `_wtTabLabels` indexing in `fetchWorktrees` and `populateWorktreeSelector`; `updateWorktreeOpenHref` and `setActive`'s call to it.
- [test_dashboard.py](../../../../skills/task-tree/scripts/test_dashboard.py) — the three new classes, the `base_url` parameter on `_client_for` (the `Host`-authority check needs a non-default origin), and the `TestWorktreeOpenButton` / `TestFileLinkConsistency` updates.
- The four documentation artifacts named above.
- Line-anchor re-cuts in seven already-integrated task records: `worktree-scoped-launch-url`, `task-local-artifacts/02-dashboard-artifact-data`, `task-local-artifacts/03-dashboard-artifact-ui`, `interactive-mode`, `interactive-mode/prose-test-cleanup/02-structured-diagnostics`, `interactive-mode/superimplement-mode-default`, `econ-data-efficiency`. Anchor-only, approved at `802b078b` and repaired at `a64c0418` for the RELEASE-NOTES insertion. Keep them; they are what stops those records citing lines that no longer exist.
- The deletion of `local-file-open/` and `task-scoped-tab-title/`, per the Protect decision.

**2. Remove `## Sync Impact` from [the parent task](../task.md).** `task check` flags it and Integrate closeout owns the removal. Nothing in it is a lasting task assumption — maturation absorbed both consequences into §Opening files, and naming the tab — so drop the section outright rather than folding it into `## Objective`.

**3. Run the Project Doc Audit walk-up** over every file in the governing diff. No module-level `CLAUDE.md` / `AGENTS.md` / `README.md` exists under `skills/task-tree/`, so the set is the repo-root [README.md](../../../../README.md) and [CLAUDE.md](../../../../CLAUDE.md) with its `AGENTS.md` / `AGENT.md` aliases. Two specific checks: the README's dashboard bullet defers the launcher story to the Quickstart, which this branch rewrote, so confirm it still reads true; and `CLAUDE.md` §Codex and Harness Design lists the generated artifacts, so confirm no file in the diff requires `sync_codex_agents.py` — nothing under `agents/` is touched, `internals.md` is a reference rather than an instruction body, and `.codex/agents/*.toml` are untouched.

**4. Review the surviving code for host-project fit** — names, utility reuse, local patterns, with a one-line reason at any deliberate deviation. Two places that invite a wrong "consolidation": `_is_loopback_host` is the file's only loopback predicate and the other `127.0.0.1` occurrences are bind defaults and probe targets, not duplicate logic; and `POST /api/open` deliberately mirrors the containment shape of `GET /files/{path}` (join under `project_root` → `resolve()` → `is_relative_to` → `is_file()`), which is the reuse, not a duplication to collapse.

**5. Write the Final Diff Self-Check trail** into this task's `## Results` before returning: the command and range, the protected record, the surviving and removed change classes, and a justification for every suspicious hunk or an explicit "none".

**Out of scope.** Leave the `plan_dashboard.py` extraction alone — the parent record defers it to a future pass and names the background supervisor and the standalone build as the candidates. Leave `skills/task-tree/scripts/vendor/` alone; it is hand-managed and re-fetched per its own `README.md`. Do not touch the background-supervisor or `--host` handling region, which the not-started sibling `nonloopback-host-serve` owns and whose objective depends on the loopback gate remaining a deliberate restriction.

### Verification

Runtime verification was waived for the maturation pass alone. This refactor runs later and must be verified for real: the selected protection has never been executed against the merged tree, so a green suite here is its first run.

- Full task-tree script suite green: `uv run --with pytest --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`. `TestLocalOpen`, `TestTabTitle`, `TestTabTitleWiring`, `TestWorktreeOpenButton`, and `TestFileLinkConsistency` must all pass. Movement in any of them is something to investigate, never an expectation to update.
- If any hunk in `dashboard.js`, `dashboard.css`, or `base.html` is touched: drive a loopback server by hand (`superra dashboard`, restarted so the hour-cached assets are re-served) and confirm all four open surfaces — card-head `Open`, header `VS Code`, a body file link, an attachment link — still reach the route on a plain left-click and still fall through to their own `vscode://` or `/api/artifact` href on a modifier click. The in-browser click path (button hit area, toast rendering) has never been driven in any pass and the suite pins it by source assertion only, so a template refactor cannot lean on the tests here.
- If a template or asset change is meant to be behavior-preserving on the render path, confirm it with a before/after `superra dashboard export` byte comparison.
- `./superRA/superra task check` reports 0 errors and no `sync-impact` warning.
- `git diff --check` clean, and the recomputed governing diff matches the survivor set with the self-check trail recorded.

## Results

