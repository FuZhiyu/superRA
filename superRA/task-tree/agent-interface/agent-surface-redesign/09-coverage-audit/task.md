---
title: "No-Knowledge-Lost Coverage Audit"
status: approved
depends_on:
  - 01-core-in-using-superra
  - 02-task-tree-slim
  - 03-role-spec-slim
  - 04-doc-sync
  - 05-review-followups
  - 06-restructure-specs
  - 07-coupled-surfaces
  - 08-report-commit-model
tags: []
created: 2026-06-01
---

## Objective

Prove that the full agent-facing-surface redesign lost **no knowledge for any agent**: every distinct piece of guidance that existed before is still present somewhere after, and still **reachable by every role that needs it** through that role's actual load path. This audit covers both rounds of the merged concern — the lean relocation (tasks 01–05) and the role-spec restructure (tasks 06–08) — each audited against its own pre-round baseline, with the combined result anchored on the final state vs the release merge-base `5dfe928b`. Runs last; depends on all prior tasks.

**The invariant.** Removing a *duplicate* is not knowledge loss — as long as the single surviving copy remains reachable by every role that previously relied on it. Removing or stranding the *only* copy is loss. Relocating content counts as preserved only if the consuming role's load path still reaches the new home. The audit confirms preservation under that definition; it does not re-litigate the design.

**Known deferred item — do NOT flag as a regression.** Task 02 relocated the mutation command surface into the new `skills/task-tree/references/commands.md` but, per researcher instruction, deliberately left `skills/task-tree/references/planning.md §Hierarchy Management Commands` untouched. So the create/rename/link command surface intentionally co-exists in both `commands.md` and `planning.md` right now. The `planning.md` dedup is owned by a separate researcher worktree, out of scope here. Treat this temporary duplicate as expected: it is the opposite of knowledge loss (content over-present, not lost), so do not report it as a `[BLOCKING]` finding or a "single owner" violation. `planning.md` itself was not modified by this restructure; confirm it is unchanged and move on.

**Method (evidence-based, not prose review):**

1. **Snapshot the pre-restructure surfaces** from git at the commit before task 01 landed: `skills/task-tree/SKILL.md`, `skills/task-tree/references/planning.md`, `skills/task-tree/references/internals.md`, `agents/implementer.md`, `agents/reviewer.md`, and the two generated `direct-mode-*` references. Use `git show <pre-sha>:<path>`.

2. **Enumerate every distinct unit of guidance** in those snapshots (a command, a discipline rule, a field/section definition, an ownership statement, a concept, a migration step). Build a coverage table: `unit → pre-restructure location(s) → post-restructure home → reachable by which roles`.

3. **Map each unit to its post-restructure home** and classify:
   - **Preserved-in-place** — unchanged location.
   - **Relocated** — moved to a new owner (e.g. universal interface → `using-superRA §Task Interface`; command surface → `references/...`; mental model → `task-tree §Core Concepts`). Confirm the new home exists and contains it.
   - **Deduplicated** — one of multiple copies removed. Confirm ≥1 authoritative copy remains.
   - **Intentionally dropped** — content the design deliberately retired. Must be justified; flag any that wasn't an explicit decision.
   - **LOST** — no post-restructure home found. Every LOST unit is a `[BLOCKING]` finding.

4. **Per-role reachability check.** For each role, confirm its load path still reaches everything it needs:
   - **Implementer / reviewer (execution):** load path = `using-superRA` (frontmatter preload) + Stage manifest + on-demand. Verify the read/edit interface, status enum, body-section vocabulary, editing principles, ownership boundary, and their own role-specific protocol are all reachable **without** loading `task-tree`.
   - **Orchestrator / planner (main agent):** `using-superRA` + `agent-orchestration` + `task-tree` on demand + `planning.md`. Verify tree concepts, query/frontier/DAG, the full command/structure surface, results-shape, stale-content, placement, and migration are all reachable.
   - **Contributor:** `task-tree` + `internals.md`. Verify data-layer/hooks/migration internals are reachable.
   - **Direct-mode main agent:** verify the generated `direct-mode-*` references plus `using-superRA` cover what subagents get.

5. **Resolve dangling pointers.** Grep for references to sections that moved or were renamed (`§How to Read`, `§How to Edit`, `§Ownership Model`, `§Command Surface`, `§Handoff Docs`, the old "self-contained" claim) across `skills/`, `agents/`, `README.md`, `CLAUDE.md`. Any pointer to a now-nonexistent anchor is a `[BLOCKING]` finding.

**Output of the audit:** the coverage table in `## Results`, the per-role reachability verdict, and a list of any LOST units / dangling pointers (which must be fixed — either here or by re-opening the owning task — before this task is approved).

**Validation (must be true to be complete):**
- The coverage table accounts for every distinct unit in the pre-restructure snapshots; none is unclassified.
- Zero units classified LOST; every "intentionally dropped" unit ties to an explicit design decision.
- Each role's reachability verdict is PASS with the load path named.
- Zero dangling pointers to moved/renamed/removed anchors.

## Results

**Combined verdict: PASS.** This audit proves the no-knowledge-lost invariant for the full agent-facing-surface redesign — both the lean relocation (tasks 01–05) and the role-spec restructure (tasks 06–08). In the release diff vs merge-base `5dfe928b` the two rounds collapse into one coherent net delta to six surfaces (`agents/implementer.md`, `agents/reviewer.md`, `using-superRA/SKILL.md`, `task-tree/SKILL.md`, the two `direct-mode-*` refs); every distinct unit of pre-redesign guidance survives in a role-reachable home. Each round was audited against its own pre-round baseline.

### Round 1 — Lean interface relocation (baseline `04fa8e2e`)

**Verdict: PASS — zero LOST units, zero dangling pointers in live surfaces, all four roles reachable.** The restructure (tasks 01–04, all approved) preserved every distinct unit of pre-restructure guidance. Removals were duplicate-collapses or deliberate relocations with a surviving reachable copy; nothing was stranded.

**Baseline:** pre-restructure SHA `04fa8e2e` (the `05-coverage-audit` planning commit, last commit before task 01's first edit). Snapshots taken with `git show 04fa8e2e:<path>` for all eight surfaces named in the objective. All eight existed at baseline.

### Coverage table

Classification key: **P** = preserved-in-place, **R** = relocated, **D** = deduplicated (≥1 authoritative copy remains), **ID** = intentionally dropped (tied to explicit design decision), **LOST** = no home found.

| # | Unit of guidance | Pre-restructure location | Post-restructure home | Class | Reachable by |
|---|---|---|---|---|---|
| 1 | "Everything is a task / leaf = dir without subtask" concept | task-tree SKILL.md §Core Concepts | task-tree SKILL.md §Core Concepts ([SKILL.md:30](../../../../skills/task-tree/SKILL.md#L30)) | P | orchestrator/planner/contributor |
| 2 | Filesystem hierarchy = task hierarchy (`walk_plan`) | task-tree SKILL.md §Core Concepts | task-tree SKILL.md §Core Concepts ([SKILL.md:31](../../../../skills/task-tree/SKILL.md#L31)) | P | orch/planner/contrib |
| 3 | Dependencies are sibling-only | task-tree SKILL.md §Core Concepts | task-tree SKILL.md §Core Concepts ([SKILL.md:32](../../../../skills/task-tree/SKILL.md#L32)) + using-superRA §Task Interface (implicit via body vocab) | P | all |
| 4 | Parent status rolls up | task-tree SKILL.md §Core Concepts | task-tree SKILL.md §Core Concepts ([SKILL.md:33](../../../../skills/task-tree/SKILL.md#L33)) | P | orch/planner/contrib |
| 5 | DAG-derived ordering vs. display-order prefixes | task-tree SKILL.md §Core Concepts | task-tree SKILL.md §Core Concepts ([SKILL.md:34](../../../../skills/task-tree/SKILL.md#L34)) | P | orch/planner/contrib |
| 6 | How to read a task (`task_read.py`, ancestor context) | task-tree SKILL.md §How to Read a Task | using-superRA §Task Interface "Read your task" ([SKILL.md:45](../../../../skills/using-superRA/SKILL.md#L45)) | R | all (preloaded) |
| 7 | Read task.md directly / read ancestor chain | task-tree SKILL.md §How to Read a Task | using-superRA §Task Interface ([SKILL.md:45](../../../../skills/using-superRA/SKILL.md#L45)) | R | all |
| 8 | Tree-level views (`task_query.py` tree/frontier/dag/json) | task-tree SKILL.md §How to Read a Task | task-tree SKILL.md §Reading the Tree ([SKILL.md:36-52](../../../../skills/task-tree/SKILL.md#L36)) | R | orch/planner |
| 9 | How to edit a task (direct edit canonical + hook safety net) | task-tree SKILL.md §How to Edit a Task | using-superRA §Task Interface "Edit your task" ([SKILL.md:47](../../../../skills/using-superRA/SKILL.md#L47)) | R | all |
| 10 | Frontmatter / body two-part structure | task-tree SKILL.md §How to Edit a Task | using-superRA §Task Interface + task-tree §Task File Format | R | all |
| 11 | Moving/reorganizing via plain `mv` + cross-boundary caveat | task-tree SKILL.md §Moving / reorganizing tasks | commands.md §Rename / move a task ([commands.md:59](../../../../skills/task-tree/references/commands.md#L59)); summary in SKILL.md §Routing ([SKILL.md:103](../../../../skills/task-tree/SKILL.md#L103)) | R | orch/planner |
| 12 | Frontmatter fields table (title/status/depends_on/tags/script/input/output/created + owners) | task-tree SKILL.md §Frontmatter fields | planning.md §Field-by-Field Notes ([planning.md:120](../../../../skills/task-tree/references/planning.md#L120)); status enum also in using-superRA §Task Interface ([SKILL.md:49](../../../../skills/using-superRA/SKILL.md#L49)) | R/D | planner (full) / all (enum) |
| 13 | Body-sections table (Objective/Results/Revision Notes/Review Notes + owners) | task-tree SKILL.md §Body sections | using-superRA §Task Interface body vocab ([SKILL.md:51](../../../../skills/using-superRA/SKILL.md#L51)) + planning.md §Field-by-Field Notes | R | all (vocab) / planner (full) |
| 14 | Status enum values | task-tree SKILL.md (fields table) + internals.md `VALID_STATUSES` | using-superRA §Task Interface ([SKILL.md:49](../../../../skills/using-superRA/SKILL.md#L49)) + internals.md §Enum constants (unchanged) | R/P | all |
| 15 | Ownership model (own body sections + status; not others'/scope-frontmatter/Objective) | task-tree SKILL.md §Ownership Model | using-superRA §Task Interface "Ownership boundary" ([SKILL.md:60](../../../../skills/using-superRA/SKILL.md#L60)) → role specs for per-role split | R | all |
| 16 | Task File Format template | task-tree SKILL.md §Task File Format | task-tree SKILL.md §Task File Format ([SKILL.md:58](../../../../skills/task-tree/SKILL.md#L58)) | P | orch/planner |
| 17 | Command surface intro (`<skill-dir>/scripts/`) | task-tree SKILL.md §Command Surface | commands.md ([commands.md:5](../../../../skills/task-tree/references/commands.md#L5)) | R | orch/planner |
| 18 | Query the tree CLI block | task-tree SKILL.md §Command Surface | task-tree SKILL.md §Reading the Tree ([SKILL.md:40](../../../../skills/task-tree/SKILL.md#L40)) | R | orch/planner |
| 19 | Direct-edit-vs-CLI guidance (single field → direct edit) | task-tree SKILL.md §Command Surface (Mutating the tree) | commands.md ([commands.md:7](../../../../skills/task-tree/references/commands.md#L7)) | R | orch/planner |
| 20 | `task_create.py` scaffold | task-tree SKILL.md + planning.md §Hierarchy Mgmt | commands.md §Scaffold ([commands.md:9](../../../../skills/task-tree/references/commands.md#L9)); planning.md §Hierarchy Management Commands (intentional deferred duplicate, see note) | R/D | orch/planner |
| 21 | `task_update.py` bulk status | task-tree SKILL.md §Command Surface | commands.md §Bulk status operations ([commands.md:23](../../../../skills/task-tree/references/commands.md#L23)) | R | orch/planner |
| 22 | `task_add_result.py` | task-tree SKILL.md §Command Surface | commands.md §Append a result ([commands.md:30](../../../../skills/task-tree/references/commands.md#L30)) | R | orch/planner |
| 23 | `task_link.py` add/remove deps | task-tree SKILL.md + planning.md | commands.md §Manage dependencies ([commands.md:38](../../../../skills/task-tree/references/commands.md#L38)); planning.md (deferred duplicate) | R/D | orch/planner |
| 24 | `task_rename.py` | task-tree SKILL.md + planning.md | commands.md §Rename / move ([commands.md:52](../../../../skills/task-tree/references/commands.md#L52)); planning.md (deferred duplicate) | R/D | orch/planner |
| 25 | Dashboard launch (`.plan/serve`, `uv run … serve`) | task-tree SKILL.md §Command Surface (Dashboard) | internals.md §Dashboard ([internals.md:190](../../../../skills/task-tree/references/internals.md#L190)); SKILL.md §Routing pointer ([SKILL.md:100](../../../../skills/task-tree/SKILL.md#L100)) | R | orch/planner/contrib |
| 26 | `.plan/serve` generation/port/SSE details | task-tree SKILL.md §Command Surface (Dashboard) | internals.md §Dashboard ([internals.md:199-201](../../../../skills/task-tree/references/internals.md#L199)) | R | orch/planner/contrib |
| 27 | `generate` subcommand deprecated | task-tree SKILL.md §Command Surface | internals.md §Dashboard ([internals.md:201](../../../../skills/task-tree/references/internals.md#L201)) | R | contrib |
| 28 | Migrate legacy PLAN.md/RESULTS.md CLI | task-tree SKILL.md §Command Surface | internals.md §Migration ([internals.md:91-105](../../../../skills/task-tree/references/internals.md#L91)) | R | contrib (+ planner via SKILL.md §Routing [SKILL.md:99](../../../../skills/task-tree/SKILL.md#L99)) |
| 29 | Preparing a legacy PLAN.md (quick-check, expectations, normalization checklist, manual procedure) | task-tree SKILL.md §Preparing a legacy PLAN.md | internals.md §Preparing a legacy PLAN.md for migration ([internals.md:156-180](../../../../skills/task-tree/references/internals.md#L156)) | R | contrib |
| 30 | v1→v2 upgrade CLI | task-tree SKILL.md §Upgrade | internals.md §Upgrade ([internals.md:182](../../../../skills/task-tree/references/internals.md#L182)) | R | contrib |
| 31 | All internals.md content (data layer, hooks, migration parser, dashboard, script inventory) | internals.md (whole) | internals.md (whole, augmented with relocated dashboard/prep detail) | P | contrib |
| 32 | All planning.md content (objectives, splitting, placement, anatomy, results shape, stale-content, conventions, field notes, hierarchy commands) | planning.md (whole) | planning.md (whole, unchanged) | P | planner |
| 33 | Editing etiquette: "latest state not a log" / inline-edit | implementer.md, reviewer.md, both direct-mode refs (×4) | using-superRA §Task Interface editing principles ([SKILL.md:55](../../../../skills/using-superRA/SKILL.md#L55)) | D | all (preloaded) |
| 34 | Editing etiquette: remove-superseded-content | role specs ×4 (generic) | using-superRA §Task Interface ([SKILL.md:56](../../../../skills/using-superRA/SKILL.md#L56)); reviewer keeps a reviewer-specific variant ([reviewer.md:96](../../../../agents/reviewer.md#L96)) | D | all |
| 35 | Editing etiquette: markdown-link citations | role specs ×4 | using-superRA §Task Interface ([SKILL.md:57](../../../../skills/using-superRA/SKILL.md#L57)) | D | all |
| 36 | Editing etiquette: doc-before-report | role specs ×4 | using-superRA §Task Interface ([SKILL.md:58](../../../../skills/using-superRA/SKILL.md#L58)) | D | all |
| 37 | Editing etiquette: "stay within your assigned task" (role-specific) | implementer.md / reviewer.md | retained in each role spec ([implementer.md:67](../../../../agents/implementer.md#L67), [reviewer.md:97](../../../../agents/reviewer.md#L97)) | P | implementer/reviewer |
| 38 | Per-role ownership split (Results vs Review Notes, status transitions, `→ implemented:`/`→ orchestrator:` mechanics, delete authority) | implementer.md / reviewer.md §What You Own | unchanged in role specs; using-superRA §Task Interface points to them ([SKILL.md:60](../../../../skills/using-superRA/SKILL.md#L60)) | P | implementer/reviewer |
| 39 | using-superRA §Handoff Docs (pointer to role-spec etiquette + planning.md) | using-superRA SKILL.md §Handoff Docs | superseded by §Task Interface, which carries the interface inline ([SKILL.md:41](../../../../skills/using-superRA/SKILL.md#L41)) | R | all |

**Every unit is classified; none unclassified. Zero LOST. Zero intentionally-dropped units** (every removal is a dedup or relocation with a surviving reachable copy — there were no deliberate content retirements in this restructure, so the "ID" class is empty and the "every ID ties to an explicit decision" criterion is vacuously satisfied).

The one known duplicate (mutation command surface co-existing in `commands.md` and `planning.md §Hierarchy Management Commands`, units 20/23/24) is the deferred item flagged in the objective — content is over-present, not lost — and is explicitly out of scope. Confirmed `planning.md` is byte-unchanged from baseline (`git diff 04fa8e2e..HEAD -- skills/task-tree/references/planning.md` is empty).

### Per-role reachability verdict

All four PASS.

- **Implementer / reviewer (execution) — PASS.** Load path: `superRA:using-superra` (frontmatter preload) + Stage manifest + on-demand. The read interface (unit 6,7), edit interface + hook safety net (9,10), status enum (14), body-section vocabulary (13), the four shared editing principles (33–36), and the ownership boundary (15) are all in using-superRA §Task Interface — reachable **without** loading `task-tree`. Role-specific protocol (the `→ implemented:`/`→ orchestrator:` mechanics, per-role ownership split, verdict protocol, stay-within-your-task rule — units 37,38) stays in `agents/implementer.md` / `agents/reviewer.md`, which are the agent's own spec. Confirmed the role specs' Editing Etiquette sections now point to §Task Interface for the shared principles and retain only role-specific rules, with no broken pointer.
- **Orchestrator / planner (main agent) — PASS.** Load path: `using-superRA` + `agent-orchestration` + `task-tree` on demand + `planning.md`. Tree concepts (units 1–5) and query/frontier/DAG (8,18) are in task-tree SKILL.md body; the full mutation/command surface (17,19–24) is in `commands.md`; results-shape, stale-content, placement, anatomy, conventions (unit 32) are in `planning.md`; migration (28–30) reachable via SKILL.md §Routing → `internals.md §Migration`. The SKILL.md §Routing table ([SKILL.md:92-101](../../../../skills/task-tree/SKILL.md#L92)) names every destination.
- **Contributor — PASS.** Load path: `task-tree` + `internals.md`. All data-layer/hooks/migration-parser/dashboard internals (unit 31) preserved in place in `internals.md`, augmented with the relocated dashboard mechanics (25–27) and PLAN.md-prep checklist (29). Cross-ref at [internals.md:179](../../../../skills/task-tree/references/internals.md#L179) correctly points to `SKILL.md §Task File Format` (exists).
- **Direct-mode main agent — PASS.** The generated `direct-mode-implementer.md` / `direct-mode-reviewer.md` received the identical Editing-Etiquette edits as their canonical sources (verified by `git diff 04fa8e2e..HEAD`), and `sync_codex_agents.py --scope project --check` exits 0 ("All generated direct-mode role references are up to date" + "All generated agent files are up to date"), proving the direct-mode refs and the `.codex/agents/*.toml` files were regenerated from the canonical specs in task 03, not hand-edited. Direct-mode agents also load `using-superra`, so they reach §Task Interface for the now-relocated shared principles.

### Dangling-pointer sweep

**Zero dangling pointers in live surfaces** (`skills/`, `agents/`, `README.md`, `CLAUDE.md`).

- Grepped for `§How to Read`, `§How to Edit`, `§Ownership Model`, `§Command Surface`, `§Handoff Docs`, the old `using-superra §Handoff Docs` pointer, and the old "self-contained task.md" claim. No live pointer targets a removed anchor.
- The old "a bare `task.md` is self-contained" claim was correctly **inverted** in §Task Interface: using-superRA now states a bare `task.md` is **not** self-contained and you must read through `task_read.py` ([SKILL.md:45](../../../../skills/using-superRA/SKILL.md#L45)). Remaining "self-contained" hits refer to figures/dashboards/drift-tests — unrelated, correct.
- All task-tree internal cross-references resolve: `using-superRA/SKILL.md §Task Interface` (exists L41), `planning.md §Field-by-Field Notes` (exists L120), `internals.md §Migration` (exists L91), `internals.md §Dashboard` (exists L190), `SKILL.md §Task File Format` (exists L58). The stale baseline cross-ref `internals.md → "See SKILL.md §Preparing a PLAN.md"` was eliminated when the prep content was consolidated into `internals.md` itself.
- Doc surfaces (CLAUDE.md ownership-boundary table, README.md, CATEGORIES.md) were updated coherently in task 04: CLAUDE.md added a `using-superra (§Task Interface)` row for the universal interface and a tree-tooling row, README/CATEGORIES now describe task-tree as load-on-demand tree tooling pointing at `using-superRA §Task Interface` for the executing-agent path.

### Observed, out of scope (not defects of this restructure)

- `superplan/SKILL.md:30` carries a soft pointer "offer migration via `task-tree` §Migration". `task-tree` SKILL.md has no literal `## Migration` heading (migration lives in `internals.md §Migration`, reachable via the SKILL.md §Routing table). This was already a loose/conceptual pointer at baseline — baseline `task-tree` SKILL.md likewise had no `## Migration` heading (it was `### Migrate legacy …` under `## Command Surface`). The restructure did not introduce the looseness, `superplan` was not modified by tasks 01–04, and the migration content remains reachable. Pre-existing, not a regression.
- `.plan/task-tree/task-edit-discipline/skill-guidance/task.md:37` contains a historical markdown link `[§How to Edit a Task](…/skills/task-tree/SKILL.md#L64)` to a now-removed section. This is a closed/approved planning record from an earlier round, not a live skill cross-reference; the objective scopes the sweep to live surfaces (`skills/`, `agents/`, `README.md`, `CLAUDE.md`), not historical `.plan/` task bodies. Noted for completeness only.

### Verification commands run

- `git show 04fa8e2e:<path>` for all 8 snapshots (all present at baseline).
- `git diff 04fa8e2e..HEAD -- agents/implementer.md agents/reviewer.md skills/using-superRA/references/direct-mode-*.md` — confirms role-spec + direct-mode etiquette edits are identical.
- `git diff 04fa8e2e..HEAD -- skills/task-tree/references/planning.md` — empty (planning.md unchanged, as the objective requires).
- `uv run skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` → exit 0, generated artifacts in sync.
- Grep sweeps across `skills/ agents/ README.md CLAUDE.md` for all moved/renamed anchors → zero live dangling pointers.

### Round 2 — Role-spec redesign (baseline `72671d50`)

**Verdict: PASS — one knowledge gap found and repaired in-place; zero remaining LOST units, zero dangling pointers, all three blocking gates green.** Every distinct behavior-shaping instruction in the baseline surfaces is accounted for after the redesign and reachable by the role that needs it through that role's real load path. The one genuinely-stranded unit (the reviewer's methodology-deference stance) was the small repair edit this task is authorized to make; all other removals are duplicate-collapses, deliberate relocations with a surviving reachable copy, or the user's own intentional wip trims with reachable substance.

**Baseline:** pre-redesign SHA `72671d50` (last commit before the user's wip redesign edits `2398a188` and this subtree). Snapshots taken with `git show 72671d50:<path>` for all touched surfaces. The new planning-review reference ([planning-review.md](../../../../../skills/superplan/references/planning-review.md)) has no baseline — it is the relocation target for the reviewer's deleted §Planning Review Mode, so it is audited as a destination, not a source.

#### Repair made by this task

The baseline reviewer persona carried a **methodology-deference stance**: *"The researcher chose the methodology — your job is to verify the implementation, not to second-guess the approach."* The redesign's new reviewer persona (which the user broadened with an own-judgment-beyond-checklists paragraph) dropped this line, and it had **no surviving home**: the §Review Protocol guidance-vs-objective framing protects the *implementer's* route choices, not the *researcher's* methodology choice from reviewer second-guessing. This was a stranded only-copy, not a dedup. Re-added one clause to the reviewer persona, worded to coexist with the own-judgment paragraph ([reviewer.md:11](../../../../../agents/reviewer.md#L11)): "The researcher chose the methodology — verify the implementation rather than second-guessing a sound approach you would have chosen differently." Regenerated the two reviewer artifacts ([direct-mode-reviewer.md](../../../../../skills/using-superRA/references/direct-mode-reviewer.md), [superra_reviewer.toml](../../../../../.codex/agents/superra_reviewer.toml)) so the clause propagated; `--check` exits 0.

#### Coverage table

Classification key: **K** = kept-in-place, **R** = relocated (new home reachable by the consuming role), **D** = dedup-survivor (≥1 reachable copy remains), **ID** = intentionally dropped by an explicit decision (the user's wip edit and/or a task spec), with substance still reachable, **RA** = re-added by this task, **LOST** = no home found.

| # | Baseline unit | Baseline location | New home | Reachable-by path | Class |
|---|---|---|---|---|---|
| 1 | Reviewer "be thorough and adversarial / missed real issue worse than flagged non-issue" | reviewer persona | reviewer persona ([reviewer.md:15](../../../../../agents/reviewer.md#L15)) | reviewer (preload) | K |
| 2 | Reviewer methodology-deference ("verify, don't second-guess the approach") | reviewer persona | reviewer persona ([reviewer.md:11](../../../../../agents/reviewer.md#L11)) | reviewer (preload) | RA |
| 3 | Reviewer own-judgment-beyond-checklists paragraph (user-added) | reviewer persona | reviewer persona ([reviewer.md:17](../../../../../agents/reviewer.md#L17)) | reviewer (preload) | K |
| 4 | Implementer evidence-first / "Bad analysis worse than no analysis" stance | implementer persona + §Execution Protocol | §Execution Protocol ([implementer.md:27](../../../../../agents/implementer.md#L27)) | implementer (preload) | K |
| 5 | `## Dispatch Inputs` one-liner (both specs) | §Dispatch Inputs | folded into §Before You Start lead ([implementer.md:15](../../../../../agents/implementer.md#L15), [reviewer.md:21](../../../../../agents/reviewer.md#L21)) | both | R |
| 6 | Load-skills-per-manifest step (both) | §Before You Start #1 | §Before You Start #1 ([implementer.md:17](../../../../../agents/implementer.md#L17), [reviewer.md:23](../../../../../agents/reviewer.md#L23)) | both | K |
| 7 | Load `Additionally:`-named skill (both) | §Before You Start #2 | §Before You Start #2 | both | K |
| 8 | Read task via `task_read.py` + inherited context (both) | §Before You Start #3 | §Before You Start #3 ([implementer.md:19](../../../../../agents/implementer.md#L19), [reviewer.md:25](../../../../../agents/reviewer.md#L25)) | both | K |
| 9 | Implementer "delta is only a pointer / task.md authoritative" | impl §Before You Start #3 tail | dropped by user wip `2398a188`; task 03 spec says "preserve, do not revert." Reviewer retains "Paraphrased summaries are not authoritative" ([reviewer.md:25](../../../../../agents/reviewer.md#L25)) | impl: intentional user trim; substance survives in reviewer copy | ID |
| 10 | Implementer "apply scoped conventions in inherited context before editing" | impl §Before You Start #4 | dropped by user wip `2398a188` | impl: intentional user trim; convention-fit enforcement lives in `refactor-and-integrate` §Project Doc Audit (manifest-loaded at `Stage: integration`) | ID |
| 11 | Reviewer scoped-convention enforcement ("ignoring inherited convention = MAJOR finding", walk subtree READMEs, Project Doc Audit) | rev §Before You Start #4 | dropped by user wip `2398a188`; heavyweight enforcement reachable in `refactor-and-integrate` §Project Doc Audit ([SKILL.md:28](../../../../../skills/refactor-and-integrate/SKILL.md#L28), `[BLOCKING]` at [SKILL.md:91](../../../../../skills/refactor-and-integrate/SKILL.md#L91)) loaded by the integration reviewer | integration reviewer (manifest `integration` row) | ID |
| 12 | Implementer "Ask questions before starting if unclear" | impl §Before You Start #5 | §Escalation "Ask for clarification rather than guessing" ([implementer.md:136](../../../../../agents/implementer.md#L136)) | implementer | R |
| 13 | Reviewer "read the actual code, verify independently" | rev §Before You Start #5 + §Read Code First | §Before You Start #4 + §Read Files First ([reviewer.md:26](../../../../../agents/reviewer.md#L26), [reviewer.md:34](../../../../../agents/reviewer.md#L34)) | reviewer | K |
| 14 | Editing-discipline "read §Handoff at task end, not dispatch" pointer | both §Before You Start tail | dropped by user wip; §Handoff is self-evident on read — no behavior change | both | ID |
| 15 | Implementer evidence-before-claims 5-step gate | §Self-Review Before Reporting | §Self-Check #1 ([implementer.md:33](../../../../../agents/implementer.md#L33)) | implementer | R |
| 16 | Implementer completeness checks (spec done, outputs saved, Results carries summary) | §Self-Review Completeness | §Self-Check #2 ([implementer.md:43](../../../../../agents/implementer.md#L43)) | implementer | R |
| 17 | Implementer Reproducibility sub-block (format convention, re-runnable, relative paths) | §Self-Review Reproducibility | folded into §Self-Check #2 completeness bullet ([implementer.md:48](../../../../../agents/implementer.md#L48)); double-covered by `econ-data-analysis` (`[BLOCKING]` re-run describe, pipeline-file reproducibility, relative-path guidance) and `theory-modeling` Gate 4 Verification & Rendering | implementer + active domain skill | D |
| 18 | Implementer domain-checklist self-walk | §Self-Review Domain walk | §Self-Check #4 ([implementer.md:52](../../../../../agents/implementer.md#L52)) | implementer | R |
| 19 | Implementer pre-commit editing-hygiene checklist (edits inside task.md, no deleted review items, stale-content, figures, doc-before-report) | §Pre-Commit Self-Check | merged into §Self-Check #3 + #5 ([implementer.md:50](../../../../../agents/implementer.md#L50), [implementer.md:54](../../../../../agents/implementer.md#L54)); shared editing principles in `using-superra` §Task Interface | implementer | D |
| 20 | `## Handoff — Unified Across Stages` heading (both) | §Handoff heading | renamed `## Handoff` ([implementer.md:60](../../../../../agents/implementer.md#L60), [reviewer.md:89](../../../../../agents/reviewer.md#L89)); generator updated in lockstep | both | K |
| 21 | Editing Etiquette: shared-principles pointer + role-specific stay-within-task rule (both) | §Editing Etiquette | §Editing Etiquette ([implementer.md:76](../../../../../agents/implementer.md#L76), [reviewer.md:103](../../../../../agents/reviewer.md#L103)) | both | K |
| 22 | "What You Own, What You Don't" → positive framing | §What You Own, What You Don't | §What You Own ([implementer.md:64](../../../../../agents/implementer.md#L64), [reviewer.md:93](../../../../../agents/reviewer.md#L93)); "What You Don't" dropped per task 01 | both | ID |
| 23 | Implementer ownership (Results, status transitions, `→ implemented:`) | §What You Own | §What You Own ([implementer.md:66](../../../../../agents/implementer.md#L66)) | implementer | K |
| 24 | Implementer §How You Fix REVISE-round mechanics (orchestrator-annotation handling, `→ implemented:` append, example block) | §How You Fix | §How You Fix ([implementer.md:78](../../../../../agents/implementer.md#L78)) | implementer | K |
| 25 | Ownership-boundary principle (edit only what you own; raise others' content) | role specs §What You Own + using-superRA §Task Interface | using-superRA §Task Interface ([SKILL.md:47](../../../../../skills/using-superRA/SKILL.md#L47)) + each spec §What You Own | all (preload) | K/D |
| 26 | Reviewer §Review Protocol (Read Files First, Verify Independently, Severity, Verdict) | §Review Protocol | §Review Protocol ([reviewer.md:30](../../../../../agents/reviewer.md#L30)) | reviewer | K |
| 27 | Reviewer Planning Review Mode (handoff-readiness/design-review, task_check, verdict, note ownership, no-status-edit) | reviewer §Planning Review Mode + clauses in §Before You Start / §What You Own / §How You Write | [planning-review.md](../../../../../skills/superplan/references/planning-review.md) (whole) + one-line pointer in reviewer ([reviewer.md:28](../../../../../agents/reviewer.md#L28)) | reviewer via manifest `planning-review` row → reference | R |
| 28 | Severity/verdict defined once, referenced not restated | rev §Severity + §Verdict; §How You Write restated | defined once in §Review Protocol; §How You Write references it ([reviewer.md:107](../../../../../agents/reviewer.md#L107)) | reviewer | D |
| 29 | Reviewer §How You Write (first-review + re-review sequences, orchestrator-override handling, CRITICAL-no-silent-override, re-review scope, integration surviving-diff sweep) | §How You Write a Review | §How You Write a Review ([reviewer.md:105](../../../../../agents/reviewer.md#L105)) | reviewer | K |
| 30 | Commit-message guidance (subject `implement/review task <path>`, body=delta, verdict/status not in subject) | impl §Update and Commit + rev §How You Write commit step | §Commit ([implementer.md:104](../../../../../agents/implementer.md#L104), [reviewer.md:133](../../../../../agents/reviewer.md#L133)); resolves parent §Conventions Commit convention | both | R |
| 31 | Commit-hygiene staging rule (stage by path, no `-A`, `git diff --cached`) | both, inline | both §Commit point to `using-superra` §Commit Hygiene ([implementer.md:106](../../../../../agents/implementer.md#L106), [reviewer.md:135](../../../../../agents/reviewer.md#L135)) | both | D |
| 32 | Parallel-worktree return rule | impl §Update and Commit | §Report Format worktree-return bullet ([implementer.md:121](../../../../../agents/implementer.md#L121)) | implementer | R |
| 33 | Implementer report fields: Summary, Key findings, Concerns, Doc edits | §Report Format (multi-field) | collapsed (task 03): Summary→commit body + `## Results`; Key findings→`## Results`; Doc edits→commit delta; Concerns→`DONE_WITH_CONCERNS` enum + `## Results` caveat ([implementer.md:115](../../../../../agents/implementer.md#L115)) | implementer; orchestrator reads via commit + `## Results` | R/ID |
| 34 | Reviewer report fields: Review Summary, Headline findings, Doc edits | rev §Report Format | collapsed (task 03): content lives in `## Review Notes`; return = Assessment + SHA ([reviewer.md:143](../../../../../agents/reviewer.md#L143)) | reviewer; orchestrator reads `## Review Notes` | R/ID |
| 35 | Reviewer closing `ACTION REQUIRED (REVISE)` trailer | nested in §Handoff | superseded by the collapsed §Report Format (status enum drives re-dispatch); task 01 noted as trailer, task 03 collapsed reporting | reviewer | ID |
| 36 | report-in-markdown file-reference rule (markdown links, relative paths) | §File-reference rule | §File-reference rule ([SKILL.md:13](../../../../../skills/report-in-markdown/SKILL.md#L13)) | all (preload) | K |
| 37 | report-in-markdown Load map (rich-content / baseline-io load conditions, attachments default) | §Load map table | §References bullets each carry their "Load when…" condition ([SKILL.md:25-26](../../../../../skills/report-in-markdown/SKILL.md#L25)); `attachments/` defaults live in `rich-content.md` §Figures, loaded when figures in scope | all | D |
| 38 | using-superRA §Task Interface planner-depth pointer (task anatomy / status lifecycle / objective+results templates → planning.md) | §Task Interface | dropped from §Task Interface by user wip; reachable via `task-tree/SKILL.md` §Routing → `references/planning.md` ([task-tree SKILL.md:84](../../../../../skills/task-tree/SKILL.md#L84)), load-on-demand. Executing agents need only read/edit (in §Task Interface) + status enum + body vocab (in role specs §What You Own); planner-depth is planner-facing | impl/rev via on-demand `task-tree`; planner via manifest | R |
| 39 | using-superRA domain add-on routing table (econ/theory/writing trigger conditions) | §Domain add-ons (topic-driven) table | trigger conditions folded into §Skill Inventory domain rows ([SKILL.md:67-69](../../../../../skills/using-superRA/SKILL.md#L67)); §Domain add-ons now points to those descriptions ([SKILL.md:112](../../../../../skills/using-superRA/SKILL.md#L112)) | all | R |
| 40 | manifest `planning-review` row + "reviewer.md owns its mode" note | §Skill-Load Manifest | row now names `planning-review.md` as required skill + owner ([SKILL.md:99](../../../../../skills/using-superRA/SKILL.md#L99), [SKILL.md:106](../../../../../skills/using-superRA/SKILL.md#L106)) | all | R |
| 41 | thorough-planning §Planning Review reviewer-mechanics prose (verdict, note ownership) | thorough-planning.md §Planning Review | relocated to [planning-review.md](../../../../../skills/superplan/references/planning-review.md); thorough-planning keeps planner-facing dispatch context + pointer ([thorough-planning.md:129](../../../../../skills/superplan/references/thorough-planning.md#L129)) | planner (thorough-planning) / reviewer (reference) | R |
| 42 | sync_codex_agents.py heading-coupled parsing (`## Handoff`, `## Self-Check`, `## Report Format`, etc.) | generator | updated in lockstep to the renamed/restructured headings; `--check` exit 0, 7/7 tests pass | contributor | K |
| 43 | Both `direct-mode-*` refs + both `superra_*.toml` | generated artifacts | regenerated from the redesigned specs; `--check` exit 0 confirms in sync | direct-mode main agent / Codex | K |

**Every baseline unit is classified; none unclassified. One RA (the reviewer methodology-deference stance, repaired here). Zero remaining LOST.** Every ID unit ties to an explicit decision — either the user's wip commit `2398a188` (units 9–11, 14, the §Task Interface and report collapses), task 01's "drop What You Don't" decision (unit 22), or task 03's reporting collapse (units 33–35) — and each ID unit's behavior-shaping substance remains reachable by the role that needs it (convention-fit → `refactor-and-integrate` at integration; paraphrase-authority → reviewer copy; ask-questions → §Escalation).

#### Report-consumer check (task 03 collapse)

No consumer relied on a removed report field. `agent-orchestration` §Review Status Reference ([SKILL.md:196](../../../../../skills/agent-orchestration/SKILL.md#L196)) reads `status:` frontmatter, not report prose. §Handling Implementer Status ([SKILL.md:213](../../../../../skills/agent-orchestration/SKILL.md#L213)) keys off the status enum (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED), all still returned; "read the concerns" for DONE_WITH_CONCERNS now resolves to the commit body + `## Results`, exactly as the new implementer §Report Format states ([implementer.md:123](../../../../../agents/implementer.md#L123)). `superimplement` Step 2 reads `## Results` and the committed diff, not a Summary/Key-findings/Doc-edits field. Grep across `agent-orchestration/` and `superimplement/` for the old field names returns zero hits.

#### Per-role reachability verdict — all PASS

- **Implementer (execution) — PASS.** Load path: `using-superra` + `report-in-markdown` (preload) + Stage manifest + on-demand. Read/edit interface, editing principles, ownership boundary (units 8, 21, 25) in using-superRA §Task Interface; status transitions + Results ownership + REVISE mechanics (23, 24) in its own spec §What You Own / §How You Fix; reproducibility (17) double-covered by spec + domain skill; ask-questions (12) in §Escalation. Planner-depth (38) reachable on-demand via `task-tree`.
- **Reviewer (execution) — PASS.** Severity/verdict defined once (26, 28), planning-review mechanics fully in the manifest-loaded reference (27, 40), convention-fit enforcement reachable at integration via `refactor-and-integrate` (11), methodology-deference restored (2). Report content lives in `## Review Notes` (34).
- **Integration reviewer — PASS.** The heavyweight scoped-convention enforcement the user trimmed from §Before You Start is exactly the `refactor-and-integrate` §Project Doc Audit `[BLOCKING]` gate, loaded by the manifest `integration` row — the baseline line itself named that as its home.
- **Direct-mode main agent / Codex — PASS.** Both `direct-mode-*` refs and both `superra_*.toml` regenerated from the redesigned specs; `--check` exit 0, generator tests 7/7.

#### Dangling-pointer sweep — zero in live surfaces

Grepped `skills/ agents/ README.md CLAUDE.md` for `Handoff — Unified`, `Planning Review Mode`, `§Self-Review Before Reporting`, `Pre-Commit Self-Check`, `What You Own, What You Don't`, `Domain add-ons (topic-driven)`, `## Load map`. Zero live pointers to a removed anchor. The only `Planning Review Mode` hits are in the generator test asserting the heading's **absence** (a positive relocation guard). CLAUDE.md §Ownership table row 68 correctly names `planning-review.md` as the new owner; the superplan and thorough-planning pointers resolve to the still-present `thorough-planning.md §Planning Review`.

#### Verification commands run (all green)

- `git show 72671d50:<path>` for every touched surface (all present at baseline; planning-review.md is a new destination).
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` → exit 0 ("All generated agent files are up to date" + "All generated direct-mode role references are up to date").
- `uv run pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py` → 7 passed.
- `python3 skills/task-tree/scripts/task_check.py --plan-root superRA` → "All checks passed. No issues found."
- Grep sweeps for removed report fields across `agent-orchestration/` and `superimplement/` → zero hits; dangling-anchor sweep across live surfaces → zero hits.
