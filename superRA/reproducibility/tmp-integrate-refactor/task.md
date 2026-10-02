---
title: "TEMPORARY — Integrate Refactoring Pass: Local Builds"
status: implemented
depends_on: []
---

## Objective

Run the Integrate refactoring pass for the 11-local-builds work, against the record matured into this task's siblings. This task is temporary: delete it at Integrate closeout. It carries no durable content.

**Protect decision:** commit `de2376e90f917537f66a1b85401e139806346dd9`, *integrate(protect): reproducibility/11-local-builds — keep all four results; existing tests and docs protect them*. It kept all four results, dropped the 03-state-display screenshots companion, chose documentation plus the existing tests as protection, and folded 11-local-builds into 02-runner, 03-task-interface, 04-dashboard-view, 06-skill, and 07-workflow-integration.

**Governing diff:** `git diff adf5ed6f68437c7254a1267a3a33f7bd2c19f91c..HEAD`, with `BASE_HEAD_SHA` = `adf5ed6f68437c7254a1267a3a33f7bd2c19f91c` (the commit before this work began; not `main`). Recompute it at the start of the pass; the triage below was taken at `a96c2756`.

**Protected record — every surviving hunk traces to one of these:**

- Task results: [02-runner](../02-runner/task.md) §Selection and §No command downloads a file; [03-task-interface](../03-task-interface/task.md); [04-dashboard-view](../04-dashboard-view/task.md) §Cards show reported and own state; [06-skill](../06-skill/task.md); [07-workflow-integration](../07-workflow-integration/task.md); the [parent](../task.md) `## Results`.
- Mechanics docs: [commands.md §Reproduction](../../../skills/task-tree/references/commands.md#reproduction), [internals.md §Dashboard](../../../skills/task-tree/references/internals.md#dashboard-plan_dashboardpy) (**Card channels**, **Graph actions**), [task-file-contract.md](../../../skills/task-tree/references/task-file-contract.md) (readiness line and the records table).
- Skill text: [reproducibility SKILL.md](../../../skills/reproducibility/SKILL.md) and its references, [online-only-files.md](../../../skills/reproducibility/references/online-only-files.md) included; the evidence line in [review-task SKILL.md](../../../skills/review-task/SKILL.md).
- User docs: [RELEASE-NOTES.md](../../../RELEASE-NOTES.md) 0.5.0; the docs-site [reproducibility](../../../docs/site/04-utility-skills/09-reproducibility/task.md) and [dashboard](../../../docs/site/04-utility-skills/01-task-tree/04-dashboard/task.md) pages.
- Protection (support paths that must survive): [test_repro_online.py](../../../skills/task-tree/scripts/test_repro_online.py), [test_repro_upstream.py](../../../skills/task-tree/scripts/test_repro_upstream.py), [tests/test_repro_states_browser.py](../../../skills/task-tree/scripts/tests/test_repro_states_browser.py), and the updated cases in `test_repro_engine.py`, `test_repro_runner.py`, `test_repro_scope.py`, `test_repro_acceptance.py`, `test_repro_builds.py`, `test_task_dependencies.py`, `test_dashboard.py`, and `tests/test_dag_workspace_browser.py`.

### Actions

1. **Triage the recomputed diff hunk by hunk against the survivor set.** At `a96c2756` every hunk traced to a kept result; none was unmatched. A hunk outside the set means something landed later: raise it, never delete it silently.
   - Engine and CLI: `_repro_state.py`, `repro_run.py`, `_repro_acceptance.py`, `_repro_scope.py`, `_repro_provenance.py`, `_repro.py`, `_edit_detect.py`, `_task_snapshot.py`, `task_read.py` — file checks that never download, `unverified`, lock `sizes`, the producer-chain default, `--only`, the download gate, capped output, exit codes 0/1/3.
   - Dashboard: `plan_dashboard.py` (`_file_peek` online-only branch, `_build_args` `only`, `_build_summary` `detail`), `dashboard.js`, `dashboard.css` — the two card channels, the Build menu, and the gate mirror.
   - The docs, skill, and test files named in the protected record.
   - The removal of `11-local-builds/`, its screenshots companion, and the `state-screenshots` lock entry.
2. **De-flake [test_repro_states_browser.py:200](../../../skills/task-tree/scripts/tests/test_repro_states_browser.py#L200).** `test_panel_names_the_own_evidence_the_origin_and_each_online_only_file` times out in `wait_for_selector('#file-peek :text("Online-only here (2.3 MiB)")')` after `online.locator('a').hover()`: 4 of 6 recorded runs failed at `a96c2756` on OlinStudio, some run concurrently. Lead, unconfirmed: `filePeekSchedule` drops the peek when its anchor is replaced during the hover delay ([dashboard.js:2087](../../../skills/task-tree/scripts/templates/dashboard.js#L2087)), and the pointer does not move again. Find the cause first. A product race gets a product fix; a test-only race gets a wait on a settled panel. Keep the assertion on the online-only note.
3. **Reword the frontier's "inputs that are not fresh" family** to "inputs whose producer is `stale`, `missing`, or `failed`", as [task-file-contract.md:103](../../../skills/task-tree/references/task-file-contract.md#L103) and 03-task-interface already say:
   - [main-agent.md:29](../../../skills/using-superra/references/main-agent.md#L29) and [task-tree SKILL.md:33](../../../skills/task-tree/SKILL.md#L33) — `skills/*` lines: apply the [CLAUDE.md](../../../CLAUDE.md) §Teach the Protocol gate;
   - [07-workflow-integration:36](../07-workflow-integration/task.md#L36);
   - [_task_snapshot.py:115](../../../skills/task-tree/scripts/_task_snapshot.py#L115) docstring;
   - docs-site [01-task-tree/task.md:17](../../../docs/site/04-utility-skills/01-task-tree/task.md#L17), [02-cli-commands:17, :21](../../../docs/site/04-utility-skills/01-task-tree/02-cli-commands/task.md#L17), [03-status-and-frontier:36, :47](../../../docs/site/04-utility-skills/01-task-tree/03-status-and-frontier/task.md#L36).
4. **Fix the three advisory record findings, then delete their `## Review Notes`:** [02-runner](../02-runner/task.md) items 1–2 (elided-list command; `--only` exit 3), [04-dashboard-view](../04-dashboard-view/task.md) item 1 (editing-history cues), [07-workflow-integration](../07-workflow-integration/task.md) item 1 (covered by action 3).
5. **Consolidate the stat-then-check online-only probe.** `_edit_detect._dataless` ([_edit_detect.py:181](../../../skills/task-tree/scripts/_edit_detect.py#L181)) and `Resolver._online_only` ([_repro_provenance.py:607](../../../skills/task-tree/scripts/_repro_provenance.py#L607)) each wrap `stat` plus the flag test with an `OSError` guard. Replace both with one helper beside `is_online_only` in `_repro_state.py`. Hoist the function-local `is_online_only` import in `include_closure` ([_repro.py:737](../../../skills/task-tree/scripts/_repro.py#L737)) out of its loop. Keep `plan_dashboard.py`'s `_repro_state.file_flags` attribute access: tests patch it there.
6. **Project Doc Audit walk-up.** No `CLAUDE.md` / `AGENTS.md` / `README.md` sits under the touched directories except `skills/task-tree/scripts/vendor/README.md`, which this diff does not touch. Check the root [README.md](../../../README.md) and [CLAUDE.md](../../../CLAUDE.md) for stale claims only.
7. **Import `OUTPUT_CAP` from `_task_validate`.** The constant landed in `59884a58`. Replace the local copy at [_repro_state.py:60-61](../../../skills/task-tree/scripts/_repro_state.py#L60-L61) with the import, and remove the item from [02-runner](../02-runner/task.md) §Known limits.

**Out of scope.**

- Size and mtime across download and eviction: a live check, not a refactor.
- Sidebar truncation and row order: 04-dashboard-view limits that predate this work.
- Another session's uncommitted edits to `CLAUDE.md` and `skills/task-tree/**` (`commands.md`, `internals.md`, `cli.py`, `task_check.py`, `task_hook.py`, `dashboard.css`, `test_task_tree.py`, `vendor/*`): never stage, revert, or edit them. An action that needs one of those files waits for the researcher.

### Verification

- **Full suite green:** `uv run --with pytest --with playwright --with pyyaml --with fastapi --with jinja2 --with 'uvicorn[standard]' --with watchfiles --with httpx python -m pytest skills/task-tree/scripts`. At `a96c2756` it ran 1123 passed. Investigate any movement in the protection tests; never update an expectation to pass.
- **The de-flaked test passes 20 consecutive runs**, run one at a time.
- `./superRA/superra repro status .` exits 0 with the three showcase steps `fresh`, and `repro-lock.json` is unchanged.
- `./superRA/superra task check` reports 0 errors. The one warning, on `docs-site/11-v05-docs-refresh/03-quickstart`, predates the base.
- `git grep -n "inputs that are not fresh\|reports as not fresh"` outside `docs/plans/` returns nothing.
- `git diff --check` is clean, and each commit body carries the Final Diff Self-Check trail.

## Results

All seven actions are done with no unmatched hunk, and the full suite still passes 1123 tests.

### Triage: every hunk traces to the protected record

`git diff adf5ed6f..HEAD`, recomputed at `b71f03b5`, adds three commits to the `a96c2756` triage: `246cb772` and `b71f03b5` touch only Review Notes, the parent status, and this task; `59884a58` adds `OUTPUT_CAP` to `_task_validate.py` (action 7). Each other file maps to an entry under action 1; none was removed.

### The online-only peek test failed because it hovered before the page settled

The cause is test-only. Both load-time events below are intended dashboard behavior, and a moving pointer recovers from either.

- **The worktree selector's reveal moves the link from under the pointer.** The first `/api/worktrees` answer (about 200 ms after load) shows the selector and shifts the panel. The resulting `pointerout` cancels the peek before its 250 ms delay ends. In every instrumented failure, that `pointerout` followed `populateWorktreeSelector` by about 25 ms.
- **The anchor replacement named as the lead is harmless.** The watcher's catch-up `full-reload` (about 500 ms after load) re-renders the panel. Chrome then fires `pointerover` on the replacement anchor, and the peek shows again; forcing `onFullReload()` mid-hover confirmed this.
- **A third hazard appeared once the selector wait was in place.** `hover()` scrolls the link into view, and the scroll event fires on the next frame, after the pointer has arrived. The dashboard closes the peek on any scroll.

The fix is at [test_repro_states_browser.py:199-206](../../../skills/task-tree/scripts/tests/test_repro_states_browser.py#L199-L206). It awaits `fetchWorktrees()` and `document.fonts.ready`, the same settle as `enter()` in [test_dag_workspace_browser.py:77](../../../skills/task-tree/scripts/tests/test_dag_workspace_browser.py#L77), scrolls the link into view, and waits one animation frame before hovering. The online-only assertion is unchanged.

- **Before the fix:** 1 of 6 runs failed on OlinStudio.
- **After the fix:** 20 of 20 sequential runs passed, as did 15 of 15 module runs with three running in parallel.

### Smaller actions

- **Rewording.** The four files that action 3 lists now say "inputs whose producer is `stale`, `missing`, or `failed`". To satisfy the verification grep, the same wording also replaced the same claim in [RELEASE-NOTES.md:47](../../../RELEASE-NOTES.md#L47) and [v05-design.md:15](../attachments/v05-design.md#L15). Only this task's own text still matches the grep.
- **Review notes.** The [02-runner](../02-runner/task.md) and [04-dashboard-view](../04-dashboard-view/task.md) items are fixed as their notes proposed, the [07-workflow-integration](../07-workflow-integration/task.md) item is resolved by the rewording, and all three `## Review Notes` sections are deleted.
- **Online-only probe.** [`path_online_only`](../../../skills/task-tree/scripts/_repro_state.py#L212) now replaces `_edit_detect._dataless` and `Resolver._online_only`. It also detects a legacy placeholder, which only a regular file can be. `_scan_dir` passes directories only, so `_scan_dir`'s behavior is unchanged. In `include_closure`, the import now runs before the loop. It stays inside the function because `_repro_state` imports `_repro`.
- **`OUTPUT_CAP`.** `_repro_state.py` imports the constant from `_task_validate`, and the known limit is gone from 02-runner.
- **Doc audit.** Neither the root README.md nor CLAUDE.md makes a claim this diff contradicts. CLAUDE.md's pointer to `_task_validate.OUTPUT_CAP` is now accurate.

### Verification

The full suite passes 1123 tests. `repro status .` exits 0 with three `fresh` steps, and `repro-lock.json` is unchanged. `task check` reports 0 errors and the one pre-existing warning, and `git diff --check` is clean.
