---
title: "Pilot: Register and Build the TreasuryGIV Pipeline"
status: not-started
depends_on: [02-runner, 03-task-interface, 04-dashboard-view, 06-skill]
---

## Objective

Adopt the graph in TreasuryGIV and use it to verify the runner, the dashboard, and the skill against a real pipeline. The durable record of the adoption lives in TreasuryGIV's own task tree; this task records what the pilot taught superRA and lands every fix in the owning task here.

- **Worktree:** branch off `slides/presentation-slidedeck-new-results` in `/Users/zhiyufu/Dropbox/research_projects/TreasuryGIV-code` into `TreasuryGIV-code.worktrees/reproduction-graph` (the project's existing worktree convention), recreate the five share symlinks (`setup_mac.sh` or `worktree-data-sync --mode seed --seed-sync-mode force-symlink`), instantiate Julia, build the sysimage only if absent.
- **Registration:** root `superRA/task.md` config with `OUT` matching `Code/output_paths.jl` routing (sandbox mirror unless `TREASURYGIV_WRITE_CANONICAL=1`), `SANDBOX` for the sandbox-only paths steps 13 and 25 read, a `julia` runner template, env deps `Project.toml` and `Manifest.toml`, code root `Code/`. All 44 `run_all_results.jl` steps become steps in `## Reproduction` sections of their owning durable task; a step with no natural owner goes to `code-infrastructure-change`. Upstream construction (SPF, aggregate factors, TIC/FoF, Stata outputs) and the two commented-out tentative artifacts are external inputs. The four `test/*.jl` scripts register as `check` steps. Steps that share a directory declare per-file outs.
- **Tiers:** every task owning a `Paper/` or `Slides/` producer or a canonical estimate is `canon`; everything else `local`.
- **Keep `Code/run_all_results.jl`** as the documented in-process fallback; its `validate_steps()` preflight and the graph must list the same scripts, checked by a `check` step or a test.
- **Verification:** `repro build` in the branch sandbox completes; a second `repro status` is clean; `git status --porcelain Paper/ Slides/` is empty after the build and the exhibit count touched matches the orchestrator's; a no-op edit to one helper reruns nothing downstream; editing `run_estimates.jl` schedules exactly its descendants in `--dry-run`; the dashboard Reproduction view renders the graph and one node comment round-trips.
- **Feedback:** every runner, contract, dashboard, or skill defect found lands as a fix in the owning task of this tree (reopened to `revise` if already approved), not as a workaround in TreasuryGIV. `## Results` here links the TreasuryGIV task and commit and lists the lessons.

## Details

- Facts from the 2026-09-02 exploration of TreasuryGIV: full run ~9 min with the sysimage, 68% estimation; `publish_artifact` stamps in place without staging, so presence of `provenance.toml` does not prove a complete output; Dropbox Smart Sync once reverted in-flight writes, so the share must stay "always keep on this device"; the sysimage is machine-specific and must not be a dep.
- The TreasuryGIV task tree already has `code-infrastructure-change` as the home of the orchestrator and output convention; plan the pilot there through `superplan` in that repo (a child such as `reproduction-graph`) before registering steps.
- Reference I/O map per step: the exploration report in this session; re-derive from the scripts, the report is not committed.
- A seed-from-canonical adoption (`pytask lock accept` after copying canonical outputs) is deliberately out of scope for v1.

## Results
