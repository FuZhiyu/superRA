---
title: "Validate Reproduction on Registered Research Projects"
status: not-started
depends_on:
  - 02-runner
  - 03-task-interface
  - 04-dashboard-view
  - 06-skill
  - 07-workflow-integration
---

## Objective

Maintain real-project evidence that the reproduction graph, runner, dashboard, and agent protocol work together. Use the supplied ElasticityBound heterogeneity project for the 0.5 update; TreasuryGIV supplies the historical adoption baseline. Each project's own task tree holds its durable research changes; this task records plugin findings and links their evidence.

- Complete the [0.5 compatibility update](v05-compatibility/task.md) in an isolated worktree seeded under the project's data conventions. Use a current source worktree; historical pilot paths are evidence locations, not an implicit writable target.
- Preserve output routing, upstream-input boundaries, existing result meaning, and selected protection checks. Keep generated results in the branch sandbox; published paper/slide exhibits and the active researcher worktree remain outside the pilot's write scope.
- Keep the existing in-process orchestrator as a fallback and verify its maintained producer coverage against the declared graph where that fallback is still used.
- Land plugin defects in their owning implementation tasks rather than relying on project-specific workarounds. Historical adoption results do not certify the 0.5 behavior.

## Details

- Facts from the 2026-09-02 exploration of TreasuryGIV: full run ~9 min with the sysimage, 68% estimation; `publish_artifact` stamps in place without staging, so presence of `provenance.toml` does not prove a complete output; Dropbox Smart Sync once reverted in-flight writes, so the share must stay "always keep on this device"; the sysimage is machine-specific and must not be a dep.
- Historical TreasuryGIV placement: `code-infrastructure-change` owns its orchestrator and output convention. The current heterogeneity pilot needs placement in its own project's task tree before project edits.
- Reference I/O map per step: the exploration report in this session; re-derive from the scripts, the report is not committed.
- Seeding never-built work from canonical outputs remains out of scope. Reviewed reuse after a successful baseline is covered by the 0.5 compatibility child.

## Results

Follow-up: [2026-09-06 small-pilot design feedback](attachments/2026-09-06-small-pilot-design-feedback.md) records a separate two-step adoption test, measured discovery latency, and proposed skill improvements.

The graph is adopted in TreasuryGIV and it works: 49 steps across 21 task files, a full sandbox
build that completes, and make-like reruns — one `superra repro build --tier all` after a
declaration fix reran 4 steps and skipped 44 as unchanged, the 48 of 49 steps that ever build (the
tentative timing pin never does). The durable record is
[`code-infrastructure-change/reproduction-graph`](/Users/zhiyufu/Dropbox/research_projects/TreasuryGIV-code.worktrees/reproduction-graph/superRA/code-infrastructure-change/reproduction-graph/task.md)
on branch `reproduction-graph`, which carries the registration, the tier rule, the boundary, and
what the graph found in the pipeline. This section records what the pilot taught superRA.

### Fixes landed in this tree

| Task | Defect | Fix |
|---|---|---|
| [01-section-contract](../01-section-contract/task.md) | The include closure resolved only a string literal and `joinpath(@__DIR__, …)`. TreasuryGIV writes `include(projectdir("Code", "helpers.jl"))` almost everywhere, so 56 of the first 57 findings were unresolved includes — and an unresolved include drops the helper from the step's deps, so editing a helper stopped invalidating the step that reads it. | `projectdir` / `srcdir` / `scriptsdir` anchor at the project root, as direct include arguments or as the head of a `joinpath`; `joinpath(<variable>, "…")` tries the project root then the including file, warning when both exist; extraction moved to a balanced-paren scan so a two-level `joinpath(projectdir(), …)` is seen at all. Two red-green tests plus one characterization test that already passed pre-fix. |
| [06-skill](../06-skill/task.md) | Nothing ruled a write stamp out of `outs`, and nothing said a drift pin reads the published root. | Two rules on the `outs` and `check` bullets of `graph-authoring.md`, with both cases recorded as lessons. |
| [02-runner](../02-runner/task.md) | `repro build <step> --force` reads as "rerun that step" and instead reruns every ancestor pulled in with it, fresh or not — here that was five estimation steps and a 40-minute rebuild. | Documented, not changed: scoping the flag needs per-task invalidation rather than pytask's session flag. |

### What the pilot taught the model

**A write stamp is never an out.** A directory out whose producer restamps a file in place restaled
36 downstream steps on an otherwise unchanged rerun, silently defeating the early cutoff the graph
exists for. Landed as the `outs` rule in [06-skill](../06-skill/task.md); no exclusion mechanism was
added to the runner or the contract. Full incident:
[durable record §Lessons for the graph model](/Users/zhiyufu/Dropbox/research_projects/TreasuryGIV-code.worktrees/reproduction-graph/superRA/code-infrastructure-change/reproduction-graph/task.md#lessons-for-the-graph-model).

**A project with an opt-in publish root has two roots, and a check must name the published one.**
A drift pin declared against the rehearsal-build root instead can be silently set from that build's
own output. Landed as the `check`-step rule in [06-skill](../06-skill/task.md). Full incident:
[durable record §Lessons for the graph model](/Users/zhiyufu/Dropbox/research_projects/TreasuryGIV-code.worktrees/reproduction-graph/superRA/code-infrastructure-change/reproduction-graph/task.md#lessons-for-the-graph-model).

**Resolving `${VAR}` must stay cheap.** A project whose roots are only computable in a slow
interpreter pays that cost on every `repro status`; TreasuryGIV worked around it with a shell helper
and a `check` step holding the two in agreement, no runner or contract change. Full incident:
[durable record §The graph](/Users/zhiyufu/Dropbox/research_projects/TreasuryGIV-code.worktrees/reproduction-graph/superRA/code-infrastructure-change/reproduction-graph/task.md#the-graph).

**Out-of-process steps cost interpreter start-up, per step — paid once.** TreasuryGIV's 44 producers
run in-process in about nine minutes; as separate processes the first full build took 42 minutes.
The graph earns that cost back by not rebuilding.

**`task check --category reproduction` is the right first move after registering.** It turned 44
producers' worth of guesswork into two residual warnings — one genuinely dynamic
`Base.include(mod, path)`, and one derived task edge contradicting a `depends_on` order — and it
found the include-closure defect above before any build ran.

**A wrong `outs` declaration fails loudly.** A step naming outputs it does not write blocks exactly
its descendants rather than silently recording itself as built.

**A check step whose owning task owns no canon producer sits outside the default build.** Three of
TreasuryGIV's four drift pins are `local` because tier is per task and their owning tasks own no
deck-closure producer, not because of anything about what they protect — so `repro build --tier
canon` and the completion gate behind it go green while those pins never run. Run pins by name or
with `--tier all` before integration; the tiers stay as registered, since per-task tiering is the v1
rule and this pilot's lean default build was the ask.

### Open questions

- Should a `kind: check` step carry its own tier, independent of its owning task's, so a drift pin
  protecting a canonical result isn't silently excluded by per-task tiering? Unresolved in v1.

### Verification

Verified at commit `43d9bc33` in the durable record's worktree. Every criterion in the Objective
holds: `repro build --tier canon` completes to 45 of 45 fresh, exit 0; a no-op helper edit and
`--dry-run` both leave it there; editing `Code/run_estimates.jl` schedules exactly its 36
descendants under `--dry-run` and restoring the file returns to fresh with no rebuild;
`git status --porcelain Paper/ Slides/` is empty save one 85-tracked-exhibit difference of 29 bytes,
reported as observed and not chased; and the dashboard Reproduction view renders the graph with a
round-tripping comment. Commands and full numbers are in the durable record's
[§Verification](/Users/zhiyufu/Dropbox/research_projects/TreasuryGIV-code.worktrees/reproduction-graph/superRA/code-infrastructure-change/reproduction-graph/task.md#verification).

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
