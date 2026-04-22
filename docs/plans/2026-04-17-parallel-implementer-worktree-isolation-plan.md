# Parallel-Implementer Worktree Isolation — Plan

> **For agentic workers:** This is a superRA **plugin-engineering** task (prose editing of skill / agent / hook files), not data analysis. No data-analysis domain vertical applies — no Data Inventory gate, no three-concurrent-disciplines, no row counts. Use `superRA:execution-workflow` to execute. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff.

**Objective:** Allow the orchestrator to parallel-dispatch ≥2 implementers without silent file-clobber, by isolating each in its own worktree; and refactor `skills/worktree-data-sync` to own only non-git data sync while worktree lifecycle moves under `skills/agent-orchestration`.

**Methodology:**
1. Establish a branch-name contract `parallel/<analysis-branch>/<slug>` so merge-guard can exempt orchestrator-managed parallel merges and the orchestrator can merge them with plain `git merge` (no `semantic-merge`).
2. Add a new optional `Worktree:` field + canned steering sentence to the implementer dispatch template; teach `agents/implementer.md` the dedicated-worktree commit/handoff branch.
3. Strip worktree creation/cleanup out of `skills/worktree-data-sync`; create `skills/agent-orchestration/references/worktree-harness-fallback.md` to carry the lifecycle fallback (harness tools preferred; raw `git worktree` otherwise).
4. Update consumer workflows (`planning-workflow`, `execution-workflow`, `merge-workflow`, `semantic-merge`) with pointer-level edits only — no duplicated content.

**Output:**
- `skills/agent-orchestration/SKILL.md` — new §Concurrent Writers Require Worktree Isolation; extended §Dispatch Templates.
- `skills/agent-orchestration/references/worktree-harness-fallback.md` — new ~30-line reference.
- `skills/worktree-data-sync/SKILL.md` — lifecycle stripped; scope narrowed to data sync.
- `agents/implementer.md` — worktree-entry step + dedicated-worktree commit branch.
- `hooks/merge-guard` — `^parallel/` exemption.
- `skills/planning-workflow/SKILL.md`, `skills/execution-workflow/SKILL.md`, `skills/merge-workflow/SKILL.md`, `skills/semantic-merge/SKILL.md` — pointer updates.

**Expected Results / Hypotheses:**
- Running `hooks/merge-guard` against synthetic input `git merge parallel/foo/a` emits no additional context; `git merge main` still emits the existing reminder.
- `skills/worktree-data-sync/scripts/test_worktree_data_sync.py` continues to pass after the SKILL.md refactor (CLI logic untouched).
- All cross-references between skill files remain valid (no dangling pointers to removed sections).

**Pipeline:** n/a (no scripts). Verification steps in Task 6.

---

## Workflow Status

- [x] Plan approved
- [x] Execution complete
- [x] Drift tests created *(n/a — plugin engineering; existing regression coverage satisfies: structural-invariants.sh, test_worktree_data_sync.py, merge-guard inline vectors)*
- [x] Refactored
- [x] Docs finalized
- [ ] Merged

---

## Decisions

> **2026-04-18 — Post-merge re-entry after semantic-merge of origin/main (commit `5f98599`).** Main moved ahead 63 commits while this branch's 19 commits were implementing parallel-implementer worktree isolation. semantic-merge classified the update as Tier 2; two conflicts resolved (PLAN.md kept ours; `using-superRA/SKILL.md §Commit Hygiene` synthesized). All eight tasks' deliverables verified intact post-merge: §Concurrent Writers lives in `agent-orchestration/SKILL.md:73`, `Worktree:` dispatch field at line 113, `merge-guard` `parallel/*` exemption at lines 39–41, `worktree-harness-fallback.md` reference at ~30 lines, `semantic-merge/SKILL.md` bypass note at line 23. `tests/structural-invariants.sh` exits 0.
>
> **Tasks affected:** all (metadata only, no code changes). Adopt main's new task-block anatomy — add `**Integration status:**` (unset, awaiting integration-workflow), rename `Dependencies:` → `Depends on:` for Tasks 1–6 to match Tasks 7–8 which were authored after main's convention landed. Flip `Review status:` from `IMPLEMENTED` to `APPROVED` on all tasks: Task 6 Step 5's batched `code-quality-reviewer` pass adjudicated to APPROVE after revisions; the subsequent simplify pass (`78183d6`) addressed a further 10 integration-review findings in its own commit. Execution is functionally complete pending integration-workflow.
>
> **Boxes unchecked:** none. The merge did not invalidate any deliverable, and no DAG closure re-opens. Plan approved + Execution complete flip on; Drift tests / Refactored / Docs finalized / Merged remain unchecked and become integration-workflow's job.
>
> **Drift tests disposition.** This is plugin-engineering work (prose editing of skill / agent / hook files). There are no analysis results to guard, so the "Drift tests" box is expected to remain unchecked and be flipped `n/a` by integration-workflow Stage 1 per its domain-exempt path. Mechanical regression coverage already lives in `skills/worktree-data-sync/scripts/test_worktree_data_sync.py` (30 tests, green) and `hooks/merge-guard` inline test vectors (Task 7) — these are not drift tests in the econ-data-analysis sense, but they are the analogous safety net for this vertical.

## Stage 2 Doc Review

**Review status:** APPROVED

Target: [`docs/plans/2026-04-17-parallel-implementer-worktree-isolation-results.md`](docs/plans/2026-04-17-parallel-implementer-worktree-isolation-results.md) at HEAD `76c8c41`. Fact-check walked against merged state. Every spot-check confirmed accurate: `worktree-harness-fallback.md` = 79 lines; merge-guard regex at `hooks/merge-guard:41` matches doc text; `test_worktree_data_sync.py` = 30 passed; §Concurrent Writers at `agent-orchestration/SKILL.md:73`; §Dispatch Templates at line 100 with `Worktree:` at line 113; two subsections §Ownership split / §Worktree lifecycle confirmed; narrowed `worktree-data-sync` section outline matches actual headings; `semantic-merge/SKILL.md:23` Exception paragraph confirmed; merge-guard 4-input regression table reproduces live. Reader-facing structure (Problem / Resolution / Verification / Limitations / Reproducibility) stands on its own without task-order context. Known dogfood limitations preserved with reproduction detail. Prior-round MINOR findings (restructure-description wording, §Limitations speculation phrasing, frontmatter staleness) fixed inline in `76c8c41` and re-verified.

---

## Project Conventions

Walked at planning time (2026-04-17).

### Repo root
- `CLAUDE.md` (feedback/agent-dispatch-fixes HEAD `a5b578a`): superRA contributor guidelines. Load-bearing workflow principles (implementer-reviewer pair; handoff-doc as auditable record; fast-early-strict-before-merge; autonomous with human-in-loop). DRY principle: one source of truth per concern; consumer workflow skills must not duplicate content owned by `agent-orchestration` or domain skills. Flat `skills/` layout (no nesting). Skill changes are behavior-shaping and must be tested on at least one harness.
- `AGENTS.md`: duplicate / symlink of `CLAUDE.md`.
- `README.md`: high-level overview; do not edit procedurally for this plan.

### Module-level docs walked
- `skills/agent-orchestration/SKILL.md` (current HEAD): canonical dispatch-template shape (required-fields-first, `Additionally:` anchor last); §Workload Balancing (Tier 1 inline / Tier 2 bundle / Tier 3 dedicated; parallelize independent tasks); §Handling Reviewer Feedback owns orchestrator adjudication discipline.
- `agents/implementer.md` (current HEAD): standard Before-You-Start; §Handoff editing etiquette; assumes shared-worktree by default; has a "Shared-repo commit discipline" note at line 151.

### Not walked
- `skills/*/references/` files not named above (unaffected by this plan).
- Test fixtures in `skills/worktree-data-sync/scripts/test_worktree_data_sync.py` — spot-check only in Task 2.

### Key cross-refs to preserve
- `merge-workflow/SKILL.md` lines 192, 239: currently point at `worktree-data-sync §Cleanup`. Split: lifecycle → new reference; data teardown → stays in `worktree-data-sync`.
- `planning-workflow/SKILL.md` line ~82: currently loads `worktree-data-sync` for worktree setup. Drop entirely — worktree setup is an orchestration-time concern, not a planning-time concern.
- `execution-workflow/SKILL.md` line ~185 (Option 4 Discard): currently points at `worktree-data-sync §Cleanup`. Repoint at new fallback reference.
- `semantic-merge/SKILL.md`: add parallel/* bypass note.

---

## Task 1: Add worktree lifecycle fallback + §Concurrent Writers subsection

**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:**
- `skills/agent-orchestration/references/worktree-harness-fallback.md` (NEW)
- `skills/agent-orchestration/SKILL.md` (extend)

**Inputs:** Current `skills/agent-orchestration/SKILL.md` (read at execution time).

**Outputs:** New reference file + extended SKILL.md.

**Depends on:** *(none)*

- [x] **Step 1: Create `skills/agent-orchestration/references/worktree-harness-fallback.md`** (~30 lines).

  Structure:
  - Short opener: "This reference is loaded by the orchestrator when it needs to create, enter, or remove a worktree and no harness-provided worktree tool is available. Worktree lifecycle is an orchestration concern — see SKILL.md §Concurrent Writers Require Worktree Isolation for when worktrees are required."
  - §Prefer harness tools: list signals (`EnterWorktree`, `ExitWorktree`, IDE worktree integration). Use them when available.
  - §Raw-git fallback: `git worktree add <path> -b <branch> <base-ref>`; `git worktree remove <path>`; `git branch -D <branch>` (only after merge or discard).
  - §Placement: default `./.worktrees/<branch-name>` at repo root; defer to project-level `CLAUDE.md` / `AGENTS.md` if it names a directory; add the chosen directory to `.gitignore` before first use if not already ignored.
  - §Gotchas: verify `git status` clean before `worktree remove`; `remove` refuses dirty worktrees unless `--force` is passed — never `--force` without checking.

- [x] **Step 2: Extend `skills/agent-orchestration/SKILL.md`** in three places.

  **(a) Add new subsection after §Workload Balancing (before §Dispatch Templates):**

  ```markdown
  ## Concurrent Writers Require Worktree Isolation

  When a parallel dispatch batch contains **≥2 implementers**, each runs in
  its own git worktree. Two implementers sharing a worktree race on
  `PLAN.md` / `RESULTS.md` at the filesystem layer — `Edit` reads, sibling
  `Edit` reads, first writes, second writes, first's edits are silently
  lost. Worktree isolation is the only safe concurrency model for parallel
  writes in this plugin.

  **Ownership split:**

  | Direction | Owner | When | How |
  |---|---|---|---|
  | Seed-in (inputs → worktree) | Orchestrator | Before dispatch | `worktree-data-sync` §Seed with `--seed-sync-mode force-symlink` |
  | Inside worktree (task execution) | Subagent | During dispatch | Normal file I/O on the `parallel/…` branch |
  | Harvest-out (merge back) | Orchestrator | After all siblings return | Plain `git merge --no-ff parallel/<branch>/<slug>` |
  | Cleanup | Orchestrator | After merge | Harness worktree tool or `git worktree remove`; `git branch -D` |

  **Branch naming:** `parallel/<analysis-branch>/<slug>` where `<slug>` is
  an orchestrator-chosen short identifier (e.g., `a`, `b`, `alpha`). A single
  implementer may own multiple PLAN.md tasks in one dispatch, so the branch
  is per *parallel slot*, not per task.

  **Plain `git merge`, not semantic-merge.** Task boundaries are set
  ex-ante in `PLAN.md` before parallel dispatch, so `parallel/…` branches
  are mechanically disjoint by construction. Merges are auto-resolving; if
  a conflict surfaces, use discretion — trivial adjacent edits can be
  resolved inline, but material or ambiguous conflicts indicate the
  task-boundary contract was violated and should escalate to the
  researcher. The merge-guard hook exempts `parallel/*` source branches
  for this reason.

  **Worktree lifecycle** (creation, entry, removal): prefer harness
  worktree tools; fall back to raw git per
  `references/worktree-harness-fallback.md`.

  **Data seeding:** force-symlink mode is safe here because parallel tasks
  have disjoint write paths by construction — symlinks point at the source
  worktree's data and no task mutates shared inputs.

  **Dispatch:** implementers in a parallel batch receive a `Worktree:`
  field and a canned steering sentence (see §Dispatch Templates below).

  **Not persisted in PLAN.md.** Branch names, HEAD SHAs, and worktree
  paths are transient orchestration state. Git (`git worktree list`, `git
  branch`) is the source of truth. PLAN.md records the committed state of
  tasks, not in-flight dispatch bookkeeping.
  ```

  **(b) Extend §Dispatch Templates** — add `Worktree:` as a new optional field between required fields and the `Additionally:` tail in the **implementer** template. Show it in the template snippet. Add a short paragraph below:

  > **`Worktree:` field.** Present only when the orchestrator provisioned a
  > dedicated worktree for this parallel slot (see §Concurrent Writers).
  > Value is the absolute path. When present, the dispatch prompt MUST
  > include this canned steering sentence in the `Additionally:` tail:
  > *"Work inside the worktree at `<path>` for the entirety of this task.
  > Enter it using the harness-provided worktree tool if available (e.g.,
  > `EnterWorktree`); otherwise `cd` to that path and verify with `git
  > rev-parse --show-toplevel`. Do not edit files outside this worktree.
  > Do not merge or push — the orchestrator owns merge-back."* This is
  > not optional steering — it's required context the agent cannot derive
  > from PLAN.md alone, because the agent's spawn cwd would otherwise
  > default to the main worktree and silently edit the wrong copy.

- [x] **Step 3: Verify and commit.** Section anchor listing confirmed: new §Concurrent Writers Require Worktree Isolation sits between §Workload Balancing and §Dispatch Templates with the expected subsections (Ownership split, Branch naming, Plain `git merge`, Worktree lifecycle, Data seeding, Dispatch, Not persisted in PLAN.md).

---

## Task 2: Refactor `worktree-data-sync` to non-git data sync only

**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:**
- `skills/worktree-data-sync/SKILL.md`
- `skills/worktree-data-sync/scripts/test_worktree_data_sync.py` (verify only; edit if tests exercise removed SKILL.md-level behavior)

**Inputs:** current `skills/worktree-data-sync/SKILL.md`; the new `agent-orchestration/references/worktree-harness-fallback.md` from Task 1.

**Outputs:** slimmed `SKILL.md`; test file verified green.

**Depends on:** Task 1 (fallback reference must exist before we point at it).

- [x] **Step 1: Rewrite the YAML description and opening paragraphs of `SKILL.md`.**
  - Narrow the `description:` frontmatter to "syncing non-git-controlled data files between existing worktrees (seeding, diffing, reconciling after parallel work, data teardown)." Remove triggers about worktree creation (`set up a worktree for this`, `isolate this analysis`, `I'll run two analyses in parallel`, etc.) — those now live in `agent-orchestration`.
  - Rewrite the opening paragraph under `# Worktree Data Sync Skill`: "Non-git data sync between existing worktrees. Seed, diff, apply, and data teardown. Worktree lifecycle (create / enter / remove) is an orchestration concern — see `skills/agent-orchestration/references/worktree-harness-fallback.md`."

- [x] **Step 2: Delete §Creating a Worktree (lines 37–87 at current HEAD) and the §When to Use a Worktree decision table (lines 11–23).**
  - Keep §When to Use (non-git data sync only) — that's scope-appropriate.
  - Announce-at-start line moves to the top of §When to Use (non-git data sync only) or gets dropped if no longer needed.

- [x] **Step 3: Trim §Cleanup (lines 247–268).** Renamed to §Data Teardown; retained the "seeded data disappears with the worktree directory" fact and repointed lifecycle to the fallback reference.
  - Delete the `git worktree remove` invocation and the "teardown is removal" prose about `git worktree remove` implicit-data-cleanup. Keep the paragraph clarifying that seeded symlinks disappear when the worktree directory is removed (as a cross-reference: "For worktree lifecycle mechanics including removal, see `agent-orchestration/references/worktree-harness-fallback.md`; seeded data lives inside the worktree directory and is removed with it.").
  - Delete the Option 4 Discard block (it prescribes `git checkout; git branch -D; git worktree remove`) — lifecycle lives in the new reference.

- [x] **Step 4: Add §See Also** at the bottom of `SKILL.md`.

- [x] **Step 5: Verify tests still pass.** `~/.venv/bin/python -m pytest skills/worktree-data-sync/scripts/test_worktree_data_sync.py -x` → 30 passed in 3.37s. No test touched SKILL.md-level worktree-creation behavior; no test changes needed.

- [x] **Step 6: Commit.**

---

## Task 3: Teach the implementer the dedicated-worktree path

**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:** `agents/implementer.md`

**Inputs:** current `agents/implementer.md`; the `Worktree:` field definition from Task 1.

**Outputs:** implementer agent file updated with (A) shared / (B) dedicated commit-discipline branch.

**Depends on:** Task 1.

- [x] **Step 1: Extend §Before You Start.** Add a new step (numbered appropriately; current list ends at 5):
  > **6. If the dispatch prompt includes a `Worktree:` field, enter that worktree before any file I/O.** Use the harness-provided worktree-entry tool if available (e.g., `EnterWorktree`); otherwise `cd` to the path and verify with `git rev-parse --show-toplevel`. All reads, edits, and commits for this task happen inside the worktree. Do not touch files outside it. The orchestrator owns merge-back and cleanup — you commit on the `parallel/…` branch and report HEAD SHA back.

  Cross-reference: "See `superRA:agent-orchestration` §Concurrent Writers Require Worktree Isolation for the full protocol."

- [x] **Step 2: Split §Handoff → Update the Docs and Commit** into two paths.

  Replace the current single "Shared-repo commit discipline" line (line 151 at current HEAD) with a branched paragraph:

  ```markdown
  **Commit discipline depends on your dispatch's worktree context:**

  **(A) Shared-worktree path (no `Worktree:` field in dispatch):** Follow `superRA:using-superRA` §Shared-Repo Commit Discipline — stage by exact path, never `git add -A/./-u`, diff-cached before commit. Single atomic commit on the current branch.

  **(B) Dedicated-worktree path (`Worktree:` field present):** You are operating inside a `parallel/<branch>/<slug>` branch provisioned by the orchestrator. Commit code + PLAN.md task block + RESULTS.md task section atomically on that branch. **Do not** merge, rebase, push, or touch worktree lifecycle — the orchestrator owns harvest-out. After your commit, report the branch name and HEAD SHA in your status return alongside the usual fields.
  ```

  Leave the `Single atomic commit` example block (`git add [code files] PLAN.md RESULTS.md results_attachments/`) intact — it applies to both paths.

- [x] **Step 3: Extend §Report Format** — add one bullet:
  > - **Worktree return (path B only):** branch name (`parallel/<branch>/<slug>`) and HEAD SHA. Omit in path A.

- [x] **Step 4: Commit.**

---

## Task 4: Exempt `parallel/*` from merge-guard

**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:** `hooks/merge-guard`

**Inputs:** current `hooks/merge-guard`.

**Outputs:** hook updated with `^parallel/` exemption.

**Depends on:** Task 1 (branch naming convention documented).

- [x] **Step 1: Add the exemption in `hooks/merge-guard`.**

  Between the existing abort/continue/skip/quit exit (around line 28) and the "Detect actual merge" regex (line 32), insert:

  ```bash
  # Exempt orchestrator-managed parallel-task merges.
  # Branch-name convention established in superRA:agent-orchestration
  # §Concurrent Writers Require Worktree Isolation — parallel/<branch>/<slug>
  # branches are disjoint by construction and merge with plain git merge.
  if echo "$command" | grep -qE 'git (merge|rebase|cherry-pick)(\s+--\S+)*\s+parallel/'; then
    printf '{}\n'
    exit 0
  fi
  ```

  Keep the exemption to source refs that start with `parallel/`. Do not match mid-argument occurrences of "parallel/" to avoid spurious exemptions from flags or paths. Test patterns in Step 2.

- [x] **Step 2: Synthetic-input verification.** All 4 cases as expected — parallel/foo/a and --no-ff parallel/feat/b emit `{}`; git merge main emits the STOP reminder; --abort emits `{}`. Run the hook against four inputs and read each stdout:

  ```bash
  # Should emit empty {} (exempt)
  echo '{"tool_input":{"command":"git merge parallel/foo/a"}}' | ./hooks/merge-guard

  # Should emit empty {} (exempt, with --no-ff flag)
  echo '{"tool_input":{"command":"git merge --no-ff parallel/feat/b"}}' | ./hooks/merge-guard

  # Should emit the reminder (not exempt)
  echo '{"tool_input":{"command":"git merge main"}}' | ./hooks/merge-guard

  # Should emit empty {} (abort, not a new merge)
  echo '{"tool_input":{"command":"git merge --abort"}}' | ./hooks/merge-guard
  ```

  Expected: tests 1, 2, 4 emit `{}`; test 3 emits a JSON payload with the `STOP. You are about to run a bare git merge` context.

- [x] **Step 3: Commit.**

---

## Task 5: Update consumer workflow skills (pointer-level only)

**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:**
- `skills/planning-workflow/SKILL.md`
- `skills/execution-workflow/SKILL.md`
- `skills/merge-workflow/SKILL.md`
- `skills/semantic-merge/SKILL.md`

**Inputs:** Tasks 1 and 2 (canonical pointers now exist).

**Outputs:** each consumer skill's references redirected to the correct owner.

**Depends on:** Task 1, Task 2.

- [x] **Step 1: `skills/planning-workflow/SKILL.md`.** Paragraph deleted. Locate the paragraph (around line 82 at current HEAD) that instructs the planner to load `superRA:worktree-data-sync` for worktree setup at planning time. Remove it entirely — worktree setup is not a planning-time concern. Do not replace with a pointer; the first touchpoint is `agent-orchestration` §Concurrent Writers at dispatch time, and planning-workflow does not need to reference it.

- [x] **Step 2: `skills/execution-workflow/SKILL.md`.** Option 4 Discard retargeted to fallback reference; also updated Red Flags entry about parallel implementers (was absolute prohibition; now points at §Concurrent Writers for the worktree-isolated protocol) and the §Integration list (deduplicated the two worktree-data-sync entries; added agent-orchestration pointer). Locate the post-completion Option 4 Discard reference (around line 185) to `worktree-data-sync §Cleanup`. Repoint to `superRA:agent-orchestration/references/worktree-harness-fallback.md`. Do not add parallel-dispatch prose here — parallel dispatch is owned by `agent-orchestration` §Concurrent Writers and consumers reference that section transitively via the existing §Workload Balancing pointer.

- [x] **Step 3: `skills/merge-workflow/SKILL.md`.** Locate the two references to `worktree-data-sync §Cleanup` (around lines 192, 239 at current HEAD). Split each: keep `worktree-data-sync` references for non-git data teardown; point `agent-orchestration/references/worktree-harness-fallback.md` for worktree-lifecycle removal.

- [x] **Step 4: `skills/semantic-merge/SKILL.md`.** Add a short note near the top of §When to Use:
  > **Exception:** Orchestrator-managed parallel merges — branches matching `parallel/*` under `agent-orchestration` §Concurrent Writers Require Worktree Isolation — bypass this skill. Task boundaries are set ex-ante in PLAN.md, so plain `git merge` is sufficient. See `agent-orchestration` §Concurrent Writers.

- [x] **Step 5: Verify no dangling references remain.** Two additional dangling references found and fixed beyond the planned four files: `skills/using-superRA/references/codex-tools.md:86` (pointed at `worktree-data-sync §Creating a Worktree`) and `skills/agent-orchestration/references/agent-teams.md:101` (same). Both repointed at the new fallback reference and, in agent-teams, to the §Concurrent Writers protocol. Final audit: zero `§Creating a Worktree` or `worktree-data-sync §Cleanup` hits. Grep:
  ```bash
  grep -rn "worktree-data-sync.*Cleanup\|worktree-data-sync.*§Creating" skills/
  grep -rn "worktree-data-sync/scripts/sync_worktree_data" skills/   # only in worktree-data-sync itself
  grep -rn "Creating a Worktree" skills/                             # no more cross-refs
  ```

  Every hit must be inside `skills/worktree-data-sync/SKILL.md` itself or the new `worktree-harness-fallback.md`. Any other hit is a dangling cross-reference — fix it.

- [x] **Step 6: Commit.**

---

## Task 6: End-to-end verification + batched-review revisions

**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:** none (verification only).

**Inputs:** All prior tasks merged on this branch.

**Outputs:** Verification log in RESULTS.md Task 6 section.

**Depends on:** Tasks 1–5.

- [x] **Step 1: Merge-guard regression.** All four synthetic inputs pass (same expectations as Task 4 Step 2). Re-run the four synthetic inputs from Task 4 Step 2. Confirm pre-existing behavior (main / abort) still works and new exemption works.

- [x] **Step 2: Data-sync test regression.** `~/.venv/bin/python -m pytest skills/worktree-data-sync/scripts/test_worktree_data_sync.py -x` → 30 passed in 3.58s. Run `python3 skills/worktree-data-sync/scripts/test_worktree_data_sync.py`. Paste exit code + pass/fail summary into RESULTS.md.

- [x] **Step 3: Cross-reference audit.** Zero dangling `§Creating a Worktree` / `worktree-data-sync.*§Cleanup` hits; new fallback reference resolves at 4 call sites; §Concurrent Writers referenced in 7 files (spec-expected). Run:
  ```bash
  grep -rn "§Creating a Worktree" skills/ agents/
  grep -rn "worktree-data-sync/references/worktree-harness-fallback" skills/ agents/   # should be zero
  grep -rn "agent-orchestration/references/worktree-harness-fallback" skills/ agents/  # should match expected call sites
  grep -rn "§Concurrent Writers" skills/ agents/
  grep -rn "parallel/<" skills/ agents/ hooks/
  ```
  Record the matches in RESULTS.md. No dangling references (§Creating a Worktree cross-refs outside worktree-data-sync itself, or fallback paths under the wrong parent skill).

- [x] **Step 4: SKILL.md structural sanity.** All edited SKILL.md files retain frontmatter + top-level heading; `agent-orchestration/SKILL.md` has 7 subsections under §Concurrent Writers. Open each edited SKILL.md and confirm it still has a YAML frontmatter with `name:` and `description:`, a top-level `#` heading matching the skill name, and no broken internal anchors (`§Foo` references to a section that no longer exists).

- [x] **Step 5: Batched adversarial review + revisions.** Dispatched `code-quality-reviewer` agent against the full `889f53c^..HEAD` diff. Verdict: REVISE. Adjudication:
  - **MAJOR M1 — ACCEPTED.** `§Seed` anchor in `worktree-data-sync/SKILL.md` doesn't exist (actual heading is `### \`--mode seed\``). Fixed 2 of 3 reviewer-cited call sites (the third — `agent-teams.md:101` — was already using the correct `§\`--mode seed\`` anchor; reviewer miscited).
  - **MINOR m1 — ACCEPTED.** Updated stale skill-inventory descriptions in `README.md`, `skills/CATEGORIES.md`, `skills/using-superRA/SKILL.md` to reflect narrowed scope. Also added a RELEASE-NOTES.md entry for this refactor per the `CLAUDE.md` sync-when-renaming rule.
  - **MINOR m2–m5 — ADVISORY, no action.** Regex verified safe; path A/B terminology acceptable; canned-steering justification self-defending; worktree-data-sync standalone post-cut.
- [x] **Step 6: Commit verification log + revisions.**

---

## Execution Notes

- **Domain:** plugin-engineering prose. No data-first discipline applies. Implementer subagent's default Stage loads (`econ-data-analysis` under `Stage: implementation`) aren't a good fit; inline execution by the orchestrator with an adversarial review pass (e.g., `code-quality-reviewer` agent reading the diff) is the cleaner shape.
- **Commits:** one per task (six total). No squashing — each task is a reviewable unit.
- **Parallelization:** The feature being built here is what *enables* safe parallel implementers. Tasks 1–6 serialized because the feature did not self-host yet. Tasks 7–8 (below) are the self-hosting dogfood test.

---

## Task 7: Dogfood — document merge-guard test vectors (parallel slot α)

**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:** `hooks/merge-guard`

**Inputs:** Task 4 synthetic test cases (already in RESULTS.md Task 4 section).

**Outputs:** `hooks/merge-guard` gains an inline comment block enumerating the four synthetic test inputs + expected outputs, so future edits can self-regress.

**Depends on:** none (file-disjoint from Task 8).

**Worktree:** orchestrator will provision `.worktrees/parallel/feedback-agent-dispatch-fixes/alpha` on branch `parallel/feedback-agent-dispatch-fixes/alpha`.

- [x] **Step 1: Add a `# Test vectors` comment block to `hooks/merge-guard`** just above the `exit 0` at the end (or immediately after the shebang — agent's choice). Include the four cases from RESULTS.md Task 4: `git merge parallel/foo/a` → `{}`, `git merge --no-ff parallel/feat/b` → `{}`, `git merge main` → STOP reminder, `git merge --abort` → `{}`.
- [x] **Step 2: Commit** on the dedicated branch. Stage `hooks/merge-guard` and `PLAN.md` (this task block only) and `RESULTS.md` (new Task 7 section only). Do not touch Task 8's files.

---

## Task 8: Dogfood — add orchestrator invocation example (parallel slot β)

**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:** `skills/agent-orchestration/references/worktree-harness-fallback.md`

**Inputs:** the existing Create/Enter/Remove sections of the fallback reference.

**Outputs:** a new `## Example Orchestrator Invocation` section appended at the end showing a complete bash sequence for a single-slot parallel dispatch (create → seed symlink → wait for subagent → merge → remove).

**Depends on:** none (file-disjoint from Task 7).

**Worktree:** orchestrator will provision `.worktrees/parallel/feedback-agent-dispatch-fixes/beta` on branch `parallel/feedback-agent-dispatch-fixes/beta`.

- [x] **Step 1: Append `## Example Orchestrator Invocation`** to `worktree-harness-fallback.md`. Show a concrete bash snippet: `git worktree add .worktrees/parallel/<branch>/a -b parallel/<branch>/a`, `python3 skills/worktree-data-sync/scripts/sync_worktree_data.py --to ... --mode seed --seed-sync-mode force-symlink`, a placeholder `# dispatch subagent with Worktree: field`, then `git merge --no-ff parallel/<branch>/a` and `git worktree remove`. Keep it under ~20 lines.
- [x] **Step 2: Commit** on the dedicated branch. Stage `skills/agent-orchestration/references/worktree-harness-fallback.md`, `PLAN.md` (this task block only), `RESULTS.md` (new Task 8 section only). Do not touch Task 7's files.
