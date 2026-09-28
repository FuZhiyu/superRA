# Reproducibility wiring review (skills/reproducibility branch vs main)

Read-only review. Script evidence came from a session-local scratch tree (not retained), run with the live `skills/task-tree/scripts/cli.py`.

## Major

**M1. A planner who follows the seeding instruction breaks the tree.**
- Claim: build-and-review.md:13 says "Seed each producing task's section with the outs it should write, leaving `deps` to its implementer". Two sources contradict it:
  - task-file-contract.md:29 makes `## Reproduction` implementer-owned.
  - The contract's validation rule makes a step with neither `cmd` nor `runner`+`script` an `[ERROR]`.
- Evidence: an outs-only seeded step makes `task check` fail, including under `--category dependency`. That is the planner's own self-review item 8, so item 3 and item 8 can't both pass. `task frontier` and `task create` then refuse with "effective dependency graph is invalid". The same seeded section with `name` + `cmd` + `outs` checks clean, and status reports it as `missing`.
- Fix: seed `name`, `cmd` (the planned script), and `outs`. Note the planner exception in the contract's ownership line.

**M2. The completion gate builds costly steps without asking the researcher.**
- Claim: completion.md:18, integrate.md:9 and finish.md:39 all run `superra repro build <targets> --upstream` before any status or dry-run. That executes every stale producer on the chain. It contradicts the stale rule (rerun-or-accept.md:22: "Potentially significant, costly | Ask the researcher").
- Autonomous mode makes this worse. main-agent.md §Proceeding and Pausing allows exactly "two situations" and neither is the costly-rerun ask, so the orchestrator is told to proceed.
- Scenario (b) then (c): a subagent correctly escalates a stale estimation step. At completion the main agent launches the multi-hour estimation anyway.
- Fix: in protect-and-completion §The completion gate, order the gate as status `--upstream`, then resolve non-fresh steps through the stale rule (`build --dry-run` gives the cost), then build. Add the costly-rerun ask to main-agent's pre-set-gate list as a pointer.

**M3. Trees with no reproduction steps can't pass completion or Integrate.**
- Claim: completion.md and integrate.md have no fallback for trees without steps. Only finish.md:39 has one ("on a tree that declares no `## Reproduction` section, run targeted verification instead").
- Evidence: on a tree with no steps, `repro status .` and `repro build 01-reg --upstream --dry-run` exit 1 with "selects no steps; no result verified". completion.md:22 then forbids the menu ("Never present completion options for unreproducible work").
- This blocks every prose-only, slide, or theory tree without scripts. The no-graph condition is also worded three ways:
  - main-agent.md:10: "tree carrying reproduction config"
  - using-superra:34: "trees without reproduction configuration"
  - finish.md:39: "declares no `## Reproduction` section"
- Fix: define the condition and fallback once, in protect-and-completion §The completion gate. All three call sites point there.

**M4. The main load trigger sits outside the manifest, and the default mode never applies the gates.**
- Claim: implementers load `reproducibility` only through prose in using-superra §Task Interface (:34). The manifest, the Agent Load Surface table in CLAUDE.md, and the load contract don't carry it. The protection row is the only manifest entry.
- The role skills compensate with a Self-Check line (implement-task:50) and a review line (review-task:28). implement-task:47 ("every loaded skill's gates") and review-task:40 already cover the gates, so these lines work as a late load trigger plus a restatement.
- Interactive mode is the default, and its self-review applies "`[BLOCKING]` item[s] from active domain skills" (interactive-mode.md:17). `reproducibility` isn't a domain skill, so its gates are skipped on the most common path. 12-agent-protocol's diagnosis "Role skills are silent … `interactive-mode.md` never mention reproduction" is still true for interactive mode.
- Fix:
  - Add a Domain-table row to the manifest: "produces, changes, or reviews a result from executable code → `reproducibility`".
  - Change interactive-mode step 2 to "every loaded skill".
  - Reduce the role-skill lines to pointers, or delete them.
  - Add a load-contract (LC) entry for the new row.

**M5. The shared execution records collide in parallel dispatch and Sync.**
- Claim: `pytask.lock`, `repro-builds.json` and `repro-acceptance.json` are single committed files at the project root (commands.md). Nothing in the workflow handles that:
  - parallel-dispatch.md:15 still says task boundaries make parallel branches "mechanically disjoint, so they typically merge cleanly". Every branch that builds rewrites these files.
  - Sync loads only `semantic-merge`, which has no guidance on resolving lock or acceptance conflicts, or on re-verifying afterwards.
  - The commit template (implement-task:57, `git add [code files] superRA/<task-path>/task.md`) and using-superra §Commits ("files you edited") omit these tool-written files. Only SKILL.md Loop step 4 says to commit them, and it doesn't name them.
- Fix: add one reproducibility section on merging execution records, pointed to from parallel-dispatch and semantic-merge. Name the three files in Loop step 4, or point to commands.md.

**M6. The release notes contradict the tier-key behavior.**
- Claim: RELEASE-NOTES.md:15 says "`--tier` and `repro tier` are retired with actionable errors … A leftover `tier:` section key is a warning".
- Evidence: `--tier` now gets the generic argparse "unrecognized arguments". A `tier:` key is `[ERROR] unknown key 'tier'`, and that error blocks `task frontier`.
- Impact: existing 0.4 projects with `tier: canon` lose their frontier on upgrade. The README Upgrading section doesn't mention it.
- Fix: either make the key a warning again, or correct the release notes and README Upgrading.

## Minor

- **m1. The reviewer has no evidence route.**
  - review-task:28 paraphrases the gates as "registered, built, and — if accepted rather than run — reasoned". The paraphrase drops Gate 3 (stale resolution), which is the DRY drift CLAUDE.md warns about.
  - It names no evidence: no `superra repro status <task> --upstream` (read-only, and not a rerun under review-task:26), and no check that the lock and acceptance records are committed.
  - Replace it with a pointer plus those two evidence checks.
- **m2. DRY across call sites.**
  - The build/status command pair is restated in completion.md:18, integrate.md:9 and finish.md:39, each next to its own link to the owner.
  - The mature-consolidate prompt (:29-32) restates designing-the-graph §Step lifecycle.
  - econ planning.md:77 ("maintained output") and theory planning.md:130 ("kept … output") restate build-and-review:13 with thresholds narrower than using-superra:34 ("Retained code — companion or permanent").
- **m3. Completion targets have no durable home.**
  - They live only in the `integrate(protect)` commit body. A later IMPLEMENT gate "once recorded" means searching git log.
  - For the first cycle, "final deliverable tasks" is undefined (build-and-review:57 only says "terminal task(s)").
  - designing-the-graph §Presenting a graph for review is a second decision point for the same targets, and nothing in the workflow calls it.
- **m4. Protect omits the reproduction decisions where they matter.** The researcher template (protect.md:17-28) and the commit-body list (:30) leave out the three decisions. protect-and-completion.md:11 requires them in the body.
- **m5. A lock is described as value protection.** result-protection:8 calls "a registered `## Reproduction` step with its committed lock" protection, but `build` rewrites the outs and the lock without complaint. Only a `kind: check` step guards values, and protect.md:14's list of options doesn't include it. Suggested wording: "drift tests, registered as check steps".
- **m6. "Ad-hoc REPL" wording conflicts with acceptance.** completion.md:19 ("not ad-hoc REPL state") sits oddly next to acceptance of results that were "Ran interactively" (rerun-or-accept.md:33).
- **m7. The subagent escalation status is ambiguous.** "Escalate through your return" (rerun-or-accept:24) could mean either:
  - implement-task §Escalation's BLOCKED/NEEDS_CONTEXT, which has no commit, or
  - DONE_WITH_CONCERNS, which Gate 3's "report it" allows.
  Name the status.
- **m8. Session-start wording.** main-agent.md:10 routes session-start status "through the stale rule", which implies running cheap builds before the first response. Say "report".
- **m9. Harness contract.**
  - The using-superra anchors in load_contract.json are off by two since 3a548e98:
    - LC002 `L44-L51` misses the integration and maturation rows.
    - LC008 `L48` is the planning-review row.
    - LC011–14 shift the same way.
  - LC008 cites reproducibility/SKILL.md#L12-L18, which is model text, not routing.
  - `ALL_STAGE_SKILLS` now contains `reproducibility`, so a correct conditional load at `Stage: implementation` counts as an over-load.
  - The suite shows 1 failed / 128 passed: `test_bundle_fixture.py::test_task_read_json_carries_comments_and_dependency_status`. The dependency `slug` is now the full path.
  - The reproducibility half of the protection row is still not live-verified.
- **m10. Wrong or missing anchors.** changing-the-tree:42 points to §What earns a step, but moves and removals belong to §Step lifecycle. consolidation.md §Prune has no step-lifecycle pointer.
- **m11. Terminology.**
  - "Boundary input" means an unproduced external input in the skill (designing-the-graph:45), but CLI `boundary_inputs` includes produced, out-of-scope saved inputs (commands.md:116). SKILL.md Loop step 4's "the boundary inputs" is therefore ambiguous.
  - kept / key / retained / maintained / canonical result are used interchangeably. "Canonical" at designing-the-graph:7 and :60 is left over from the tier naming.
  - "final deliverable tasks" and "completion targets" name the same thing.
  - The noun "plan" is not misused.

## Prose

- completion.md's heading "Verify Pipeline and Reproducibility" still says "Pipeline", and econ-data-analysis SKILL:151 cites it.
- integrate.md:9 "on the Protect completion targets among them" is unclear.
- CATEGORIES.md:52 states the trigger as "before a maintained output is produced", narrower than using-superra:34.

## Result-protection vs reproducibility ownership

Ownership is mostly clean:
- **result-protection:** test quality, red-green verification, escalation.
- **reproducibility:** check-step registration (designing-the-graph:9, protect-and-completion:8). The manifest loads both at protection.

There are two blemishes. m5 above is one. The other: designing-the-graph:9 carries a `[BLOCKING]` tag inside a definition bullet rather than in §Gates.

## Stale content in the task tree

- **superRA/reproducibility/task.md:**
  - :60 `--tier canon`
  - :63 `dag | tier`
  - :64 "badges canon tasks"
  - :69 "canon narrowed"
  - :71 "Clear tier names"
  - :56 "Runtime implementation remains queued"
- **07-workflow-integration/task.md:**
  - :31 `--tier canon`
  - :31 cites an implement-task:29 "same commit" line that no longer exists
  - :32 "never drops a canon step"
  - :36 says the trigger is "keyed on a `reproduction:` key in `superRA/config.yaml`"
- **unified-dependency-workflow/task.md:** :20 and :68 link to deleted `graph-authoring.md` and `rerun-model.md`.
- **12-agent-protocol/task.md:** :39, :41 and :44 link to deleted files. Its interactive-mode diagnosis is still unresolved.
- **06-skill/task.md:** :12-13, :32-33, :39 and :60 still describe the old files and `--tier canon`.
