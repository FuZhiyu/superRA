---
title: "Pilot: Register and Build the TreasuryGIV Pipeline"
status: implemented
depends_on: [02-runner, 03-task-interface, 04-dashboard-view, 06-skill]
---

## Objective

Adopt the graph in TreasuryGIV and use it to verify the runner, the dashboard, and the skill against a real pipeline. The durable record of the adoption lives in TreasuryGIV's own task tree; this task records what the pilot taught superRA and lands every fix in the owning task here.

- **Worktree:** branch off `slides/presentation-slidedeck-new-results` in `/Users/zhiyufu/Dropbox/research_projects/TreasuryGIV-code` into `TreasuryGIV-code.worktrees/reproduction-graph` (the project's existing worktree convention), recreate the five share symlinks (`setup_mac.sh` or `worktree-data-sync --mode seed --seed-sync-mode force-symlink`), instantiate Julia, build the sysimage only if absent.
- **Registration:** `superRA/config.yaml` with `OUT` matching `Code/output_paths.jl` routing (sandbox mirror unless `TREASURYGIV_WRITE_CANONICAL=1`), `SANDBOX` for the sandbox-only paths steps 13 and 25 read, a `julia` runner template, env deps `Project.toml` and `Manifest.toml`, code root `Code/`. All 44 `run_all_results.jl` steps become steps in `## Reproduction` sections of their owning durable task; a step with no natural owner goes to `code-infrastructure-change`. Upstream construction (SPF, aggregate factors, TIC/FoF, Stata outputs) and the two commented-out tentative artifacts are external inputs. The four `test/*.jl` scripts register as `check` steps. Steps that share a directory declare per-file outs.
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

The graph is adopted in TreasuryGIV and it works: 49 steps across 21 task files, a full sandbox
build that completes, and make-like reruns — one build after a declaration fix reran 4 steps and
skipped 44 as unchanged. The durable record is
[`code-infrastructure-change/reproduction-graph`](/Users/zhiyufu/Dropbox/research_projects/TreasuryGIV-code.worktrees/reproduction-graph/superRA/code-infrastructure-change/reproduction-graph/task.md)
on branch `reproduction-graph`, which carries the registration, the tier rule, the boundary, and
what the graph found in the pipeline. This section records what the pilot taught superRA.

### Fixes landed in this tree

| Task | Defect | Fix |
|---|---|---|
| [01-section-contract](../01-section-contract/task.md) | The include closure resolved only a string literal and `joinpath(@__DIR__, …)`. TreasuryGIV writes `include(projectdir("Code", "helpers.jl"))` almost everywhere, so 56 of the first 57 findings were unresolved includes — and an unresolved include drops the helper from the step's deps, so editing a helper stopped invalidating the step that reads it. | `projectdir` / `srcdir` / `scriptsdir` anchor at the project root; `joinpath(<variable>, "…")` tries the project root then the including file, keeping whichever is on disk; extraction moved to a balanced-paren scan so a two-level `joinpath(projectdir(), …)` is seen at all. Three tests, each red with its fix reverted. |
| [06-skill](../06-skill/task.md) | Nothing ruled a write stamp out of `outs`, and nothing said a drift pin reads the published root. | Two rules on the `outs` and `check` bullets of `graph-authoring.md`, with both cases recorded as lessons. |
| [02-runner](../02-runner/task.md) | `repro build <step> --force` reads as "rerun that step" and instead reruns every ancestor pulled in with it, fresh or not — here that was five estimation steps and a 40-minute rebuild. | Documented, not changed: scoping the flag needs per-task invalidation rather than pytask's session flag. |

### What the pilot taught the model

**A write stamp is never an out, and this is the single most expensive thing to get wrong.**
TreasuryGIV's `publish_dir` rewrites `provenance.toml` in place with a fresh UTC timestamp, so a
directory out changes on every run whatever the data does. Re-running the baseline estimation on
unchanged inputs reported all seven of its directory outs as changed and restaled 36 downstream
steps — the early cutoff the graph exists for, gone silently. Per-file outs that leave the stamp
undeclared are the v1 answer: 32 directory outs became 293 per-file ones, mechanically, with four
stamp-free directories left as directories. No exclusion mechanism was added to the runner or the
contract.

**A project with an opt-in publish root has two roots, and a check must name the right one.**
Every canonical TreasuryGIV write is mirrored into a per-author, per-branch sandbox unless
`TREASURYGIV_WRITE_CANONICAL=1` is set. Declaring a drift pin's deps as `${OUT}/…` would have had
it compare a rehearsal run against baselines taken from the results of record; the pin's own header
records that failure having happened once already. The four pins declare canonical paths and run
under the opt-in.

**Resolving `${VAR}` must stay cheap.** `${OUT}` and `${SANDBOX}` are `shell:` variables re-resolved
on every `repro status`, and the project's routing lives in Julia. A Julia start-up costs about a
second even with a sysimage, against milliseconds for the stat sweep the cache is designed around,
so the pilot reimplemented the routing in a shell helper and added a check step holding the two in
agreement. A project whose roots are only computable in a slow interpreter would pay that on every
status call.

**Out-of-process steps cost interpreter start-up, per step.** The 44 producers run in-process in
about nine minutes; as 44 Julia processes the first full build took 42 minutes — roughly 30 seconds
per step of package and compile load even with a sysimage. That is the price of step granularity in
an interpreted project, and it is paid once: the graph earns it back by not rebuilding.

**`task check --category reproduction` is the right first move after registering.** It turned 44
producers' worth of guesswork into two residual warnings — one genuinely dynamic
`Base.include(mod, path)`, and one derived task edge contradicting a `depends_on` order — and it
found the include-closure defect above before any build ran.

**A wrong `outs` declaration fails loudly.** The first pass named rolling outputs the run does not
write; pytask reported the three missing files and skipped exactly the three descendants, rather
than recording a step as built.

### Verification

Run in the worktree at
`/Users/zhiyufu/Dropbox/research_projects/TreasuryGIV-code.worktrees/reproduction-graph`, branch
`reproduction-graph`, with the superRA source pinned to this tree via `SUPERRA_REPO_ROOT`. Head
commit `43d9bc33`.

- `repro build --tier canon` completes; the `repro status --tier canon` after it is 45 of 45 fresh,
  exit 0. The one non-fresh step at `--tier all` is the tentative timing pin, `local` and never
  built.
- A no-op helper edit (same bytes, new mtime) leaves status fresh and `--dry-run` skips all 45.
- Editing `Code/run_estimates.jl` schedules 36 of 45 under `--dry-run` — that step plus the 35
  descendants the graph derives, and none of the 9 that read nothing it writes. Restoring the file
  returns status to fresh with no rebuild.
- `git status --porcelain Paper/ Slides/` after the build named one file of 85 tracked exhibits;
  77 were rewritten byte-identical. The remaining difference is 29 bytes in
  `price_decomposition_by_factor_idio.pdf` and is reported as observed, not chased to a verdict.
- The dashboard Reproduction view renders 49 steps, 144 step edges and 31 task edges with per-step
  detail, and a comment on a task's `Reproduction` section round-trips through create, read,
  resolve and delete. Serve it with `./superRA/superra dashboard` from the worktree.

### Notes for whoever runs this next

- **The plugin installed for TreasuryGIV is stale**, so every command here ran with
  `SUPERRA_REPO_ROOT` pointing at this tree. The PostToolUse producer reminder never fired there
  and was not exercised.
- **The base branch moved during the pilot.** `slides/presentation-slidedeck-new-results` advanced
  from `dc8a10c9` to `e53b0813` while the first build ran, because another session was working in
  the main checkout. This worktree stays at the older tip; the four unproduced `_fedpin` deck
  exhibits are exactly what that newer commit addresses, so a rebase will change the rolling
  declarations.
- **Enumerating outs from disk picks up leftovers.** Expanding the directory outs from the sandbox
  captured a `PEN.noncanonical_previous/` backup directory an interrupted earlier run had left, and
  the next build failed on the three files it does not write. Read the producer, or check what an
  enumeration returns against it.
