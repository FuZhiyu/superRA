---
title: "No-Knowledge-Lost Coverage Audit"
status: approved
depends_on:
  - 01-core-in-using-superra
  - 02-task-system-slim
  - 03-role-spec-slim
  - 04-doc-sync
tags: []
created: 2026-06-01
---

## Objective

Prove that the restructure (tasks 01–04) lost **no knowledge for any agent**: every distinct piece of guidance that existed before is still present somewhere after, and still **reachable by every role that needs it** through that role's actual load path. Runs last; depends on all four prior tasks.

**The invariant.** Removing a *duplicate* is not knowledge loss — as long as the single surviving copy remains reachable by every role that previously relied on it. Removing or stranding the *only* copy is loss. Relocating content counts as preserved only if the consuming role's load path still reaches the new home. The audit confirms preservation under that definition; it does not re-litigate the design.

**Known deferred item — do NOT flag as a regression.** Task 02 relocated the mutation command surface into the new `skills/task-system/references/commands.md` but, per researcher instruction, deliberately left `skills/task-system/references/planning.md §Hierarchy Management Commands` untouched. So the create/rename/link command surface intentionally co-exists in both `commands.md` and `planning.md` right now. The `planning.md` dedup is owned by a separate researcher worktree, out of scope here. Treat this temporary duplicate as expected: it is the opposite of knowledge loss (content over-present, not lost), so do not report it as a `[BLOCKING]` finding or a "single owner" violation. `planning.md` itself was not modified by this restructure; confirm it is unchanged and move on.

**Method (evidence-based, not prose review):**

1. **Snapshot the pre-restructure surfaces** from git at the commit before task 01 landed: `skills/task-system/SKILL.md`, `skills/task-system/references/planning.md`, `skills/task-system/references/internals.md`, `agents/implementer.md`, `agents/reviewer.md`, and the two generated `direct-mode-*` references. Use `git show <pre-sha>:<path>`.

2. **Enumerate every distinct unit of guidance** in those snapshots (a command, a discipline rule, a field/section definition, an ownership statement, a concept, a migration step). Build a coverage table: `unit → pre-restructure location(s) → post-restructure home → reachable by which roles`.

3. **Map each unit to its post-restructure home** and classify:
   - **Preserved-in-place** — unchanged location.
   - **Relocated** — moved to a new owner (e.g. universal interface → `using-superRA §Task Interface`; command surface → `references/...`; mental model → `task-system §Core Concepts`). Confirm the new home exists and contains it.
   - **Deduplicated** — one of multiple copies removed. Confirm ≥1 authoritative copy remains.
   - **Intentionally dropped** — content the design deliberately retired. Must be justified; flag any that wasn't an explicit decision.
   - **LOST** — no post-restructure home found. Every LOST unit is a `[BLOCKING]` finding.

4. **Per-role reachability check.** For each role, confirm its load path still reaches everything it needs:
   - **Implementer / reviewer (execution):** load path = `using-superRA` (frontmatter preload) + Stage manifest + on-demand. Verify the read/edit interface, status enum, body-section vocabulary, editing principles, ownership boundary, and their own role-specific protocol are all reachable **without** loading `task-system`.
   - **Orchestrator / planner (main agent):** `using-superRA` + `agent-orchestration` + `task-system` on demand + `planning.md`. Verify tree concepts, query/frontier/DAG, the full command/structure surface, results-shape, stale-content, placement, and migration are all reachable.
   - **Contributor:** `task-system` + `internals.md`. Verify data-layer/hooks/migration internals are reachable.
   - **Direct-mode main agent:** verify the generated `direct-mode-*` references plus `using-superRA` cover what subagents get.

5. **Resolve dangling pointers.** Grep for references to sections that moved or were renamed (`§How to Read`, `§How to Edit`, `§Ownership Model`, `§Command Surface`, `§Handoff Docs`, the old "self-contained" claim) across `skills/`, `agents/`, `README.md`, `CLAUDE.md`. Any pointer to a now-nonexistent anchor is a `[BLOCKING]` finding.

**Output of the audit:** the coverage table in `## Results`, the per-role reachability verdict, and a list of any LOST units / dangling pointers (which must be fixed — either here or by re-opening the owning task — before this task is approved).

**Validation (must be true to be complete):**
- The coverage table accounts for every distinct unit in the pre-restructure snapshots; none is unclassified.
- Zero units classified LOST; every "intentionally dropped" unit ties to an explicit design decision.
- Each role's reachability verdict is PASS with the load path named.
- Zero dangling pointers to moved/renamed/removed anchors.

## Results

**Verdict: PASS — zero LOST units, zero dangling pointers in live surfaces, all four roles reachable.** The restructure (tasks 01–04, all approved) preserved every distinct unit of pre-restructure guidance. Removals were duplicate-collapses or deliberate relocations with a surviving reachable copy; nothing was stranded.

**Baseline:** pre-restructure SHA `04fa8e2e` (the `05-coverage-audit` planning commit, last commit before task 01's first edit). Snapshots taken with `git show 04fa8e2e:<path>` for all eight surfaces named in the objective. All eight existed at baseline.

### Coverage table

Classification key: **P** = preserved-in-place, **R** = relocated, **D** = deduplicated (≥1 authoritative copy remains), **ID** = intentionally dropped (tied to explicit design decision), **LOST** = no home found.

| # | Unit of guidance | Pre-restructure location | Post-restructure home | Class | Reachable by |
|---|---|---|---|---|---|
| 1 | "Everything is a task / leaf = dir without subtask" concept | task-system SKILL.md §Core Concepts | task-system SKILL.md §Core Concepts ([SKILL.md:30](../../../../skills/task-system/SKILL.md#L30)) | P | orchestrator/planner/contributor |
| 2 | Filesystem hierarchy = task hierarchy (`walk_plan`) | task-system SKILL.md §Core Concepts | task-system SKILL.md §Core Concepts ([SKILL.md:31](../../../../skills/task-system/SKILL.md#L31)) | P | orch/planner/contrib |
| 3 | Dependencies are sibling-only | task-system SKILL.md §Core Concepts | task-system SKILL.md §Core Concepts ([SKILL.md:32](../../../../skills/task-system/SKILL.md#L32)) + using-superRA §Task Interface (implicit via body vocab) | P | all |
| 4 | Parent status rolls up | task-system SKILL.md §Core Concepts | task-system SKILL.md §Core Concepts ([SKILL.md:33](../../../../skills/task-system/SKILL.md#L33)) | P | orch/planner/contrib |
| 5 | DAG-derived ordering vs. display-order prefixes | task-system SKILL.md §Core Concepts | task-system SKILL.md §Core Concepts ([SKILL.md:34](../../../../skills/task-system/SKILL.md#L34)) | P | orch/planner/contrib |
| 6 | How to read a task (`task_read.py`, ancestor context) | task-system SKILL.md §How to Read a Task | using-superRA §Task Interface "Read your task" ([SKILL.md:45](../../../../skills/using-superRA/SKILL.md#L45)) | R | all (preloaded) |
| 7 | Read task.md directly / read ancestor chain | task-system SKILL.md §How to Read a Task | using-superRA §Task Interface ([SKILL.md:45](../../../../skills/using-superRA/SKILL.md#L45)) | R | all |
| 8 | Tree-level views (`task_query.py` tree/frontier/dag/json) | task-system SKILL.md §How to Read a Task | task-system SKILL.md §Reading the Tree ([SKILL.md:36-52](../../../../skills/task-system/SKILL.md#L36)) | R | orch/planner |
| 9 | How to edit a task (direct edit canonical + hook safety net) | task-system SKILL.md §How to Edit a Task | using-superRA §Task Interface "Edit your task" ([SKILL.md:47](../../../../skills/using-superRA/SKILL.md#L47)) | R | all |
| 10 | Frontmatter / body two-part structure | task-system SKILL.md §How to Edit a Task | using-superRA §Task Interface + task-system §Task File Format | R | all |
| 11 | Moving/reorganizing via plain `mv` + cross-boundary caveat | task-system SKILL.md §Moving / reorganizing tasks | commands.md §Rename / move a task ([commands.md:59](../../../../skills/task-system/references/commands.md#L59)); summary in SKILL.md §Routing ([SKILL.md:103](../../../../skills/task-system/SKILL.md#L103)) | R | orch/planner |
| 12 | Frontmatter fields table (title/status/depends_on/tags/script/input/output/created + owners) | task-system SKILL.md §Frontmatter fields | planning.md §Field-by-Field Notes ([planning.md:120](../../../../skills/task-system/references/planning.md#L120)); status enum also in using-superRA §Task Interface ([SKILL.md:49](../../../../skills/using-superRA/SKILL.md#L49)) | R/D | planner (full) / all (enum) |
| 13 | Body-sections table (Objective/Results/Revision Notes/Review Notes + owners) | task-system SKILL.md §Body sections | using-superRA §Task Interface body vocab ([SKILL.md:51](../../../../skills/using-superRA/SKILL.md#L51)) + planning.md §Field-by-Field Notes | R | all (vocab) / planner (full) |
| 14 | Status enum values | task-system SKILL.md (fields table) + internals.md `VALID_STATUSES` | using-superRA §Task Interface ([SKILL.md:49](../../../../skills/using-superRA/SKILL.md#L49)) + internals.md §Enum constants (unchanged) | R/P | all |
| 15 | Ownership model (own body sections + status; not others'/scope-frontmatter/Objective) | task-system SKILL.md §Ownership Model | using-superRA §Task Interface "Ownership boundary" ([SKILL.md:60](../../../../skills/using-superRA/SKILL.md#L60)) → role specs for per-role split | R | all |
| 16 | Task File Format template | task-system SKILL.md §Task File Format | task-system SKILL.md §Task File Format ([SKILL.md:58](../../../../skills/task-system/SKILL.md#L58)) | P | orch/planner |
| 17 | Command surface intro (`<skill-dir>/scripts/`) | task-system SKILL.md §Command Surface | commands.md ([commands.md:5](../../../../skills/task-system/references/commands.md#L5)) | R | orch/planner |
| 18 | Query the tree CLI block | task-system SKILL.md §Command Surface | task-system SKILL.md §Reading the Tree ([SKILL.md:40](../../../../skills/task-system/SKILL.md#L40)) | R | orch/planner |
| 19 | Direct-edit-vs-CLI guidance (single field → direct edit) | task-system SKILL.md §Command Surface (Mutating the tree) | commands.md ([commands.md:7](../../../../skills/task-system/references/commands.md#L7)) | R | orch/planner |
| 20 | `task_create.py` scaffold | task-system SKILL.md + planning.md §Hierarchy Mgmt | commands.md §Scaffold ([commands.md:9](../../../../skills/task-system/references/commands.md#L9)); planning.md §Hierarchy Management Commands (intentional deferred duplicate, see note) | R/D | orch/planner |
| 21 | `task_update.py` bulk status | task-system SKILL.md §Command Surface | commands.md §Bulk status operations ([commands.md:23](../../../../skills/task-system/references/commands.md#L23)) | R | orch/planner |
| 22 | `task_add_result.py` | task-system SKILL.md §Command Surface | commands.md §Append a result ([commands.md:30](../../../../skills/task-system/references/commands.md#L30)) | R | orch/planner |
| 23 | `task_link.py` add/remove deps | task-system SKILL.md + planning.md | commands.md §Manage dependencies ([commands.md:38](../../../../skills/task-system/references/commands.md#L38)); planning.md (deferred duplicate) | R/D | orch/planner |
| 24 | `task_rename.py` | task-system SKILL.md + planning.md | commands.md §Rename / move ([commands.md:52](../../../../skills/task-system/references/commands.md#L52)); planning.md (deferred duplicate) | R/D | orch/planner |
| 25 | Dashboard launch (`.plan/serve`, `uv run … serve`) | task-system SKILL.md §Command Surface (Dashboard) | internals.md §Dashboard ([internals.md:190](../../../../skills/task-system/references/internals.md#L190)); SKILL.md §Routing pointer ([SKILL.md:100](../../../../skills/task-system/SKILL.md#L100)) | R | orch/planner/contrib |
| 26 | `.plan/serve` generation/port/SSE details | task-system SKILL.md §Command Surface (Dashboard) | internals.md §Dashboard ([internals.md:199-201](../../../../skills/task-system/references/internals.md#L199)) | R | orch/planner/contrib |
| 27 | `generate` subcommand deprecated | task-system SKILL.md §Command Surface | internals.md §Dashboard ([internals.md:201](../../../../skills/task-system/references/internals.md#L201)) | R | contrib |
| 28 | Migrate legacy PLAN.md/RESULTS.md CLI | task-system SKILL.md §Command Surface | internals.md §Migration ([internals.md:91-105](../../../../skills/task-system/references/internals.md#L91)) | R | contrib (+ planner via SKILL.md §Routing [SKILL.md:99](../../../../skills/task-system/SKILL.md#L99)) |
| 29 | Preparing a legacy PLAN.md (quick-check, expectations, normalization checklist, manual procedure) | task-system SKILL.md §Preparing a legacy PLAN.md | internals.md §Preparing a legacy PLAN.md for migration ([internals.md:156-180](../../../../skills/task-system/references/internals.md#L156)) | R | contrib |
| 30 | v1→v2 upgrade CLI | task-system SKILL.md §Upgrade | internals.md §Upgrade ([internals.md:182](../../../../skills/task-system/references/internals.md#L182)) | R | contrib |
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

The one known duplicate (mutation command surface co-existing in `commands.md` and `planning.md §Hierarchy Management Commands`, units 20/23/24) is the deferred item flagged in the objective — content is over-present, not lost — and is explicitly out of scope. Confirmed `planning.md` is byte-unchanged from baseline (`git diff 04fa8e2e..HEAD -- skills/task-system/references/planning.md` is empty).

### Per-role reachability verdict

All four PASS.

- **Implementer / reviewer (execution) — PASS.** Load path: `superRA:using-superra` (frontmatter preload) + Stage manifest + on-demand. The read interface (unit 6,7), edit interface + hook safety net (9,10), status enum (14), body-section vocabulary (13), the four shared editing principles (33–36), and the ownership boundary (15) are all in using-superRA §Task Interface — reachable **without** loading `task-system`. Role-specific protocol (the `→ implemented:`/`→ orchestrator:` mechanics, per-role ownership split, verdict protocol, stay-within-your-task rule — units 37,38) stays in `agents/implementer.md` / `agents/reviewer.md`, which are the agent's own spec. Confirmed the role specs' Editing Etiquette sections now point to §Task Interface for the shared principles and retain only role-specific rules, with no broken pointer.
- **Orchestrator / planner (main agent) — PASS.** Load path: `using-superRA` + `agent-orchestration` + `task-system` on demand + `planning.md`. Tree concepts (units 1–5) and query/frontier/DAG (8,18) are in task-system SKILL.md body; the full mutation/command surface (17,19–24) is in `commands.md`; results-shape, stale-content, placement, anatomy, conventions (unit 32) are in `planning.md`; migration (28–30) reachable via SKILL.md §Routing → `internals.md §Migration`. The SKILL.md §Routing table ([SKILL.md:92-101](../../../../skills/task-system/SKILL.md#L92)) names every destination.
- **Contributor — PASS.** Load path: `task-system` + `internals.md`. All data-layer/hooks/migration-parser/dashboard internals (unit 31) preserved in place in `internals.md`, augmented with the relocated dashboard mechanics (25–27) and PLAN.md-prep checklist (29). Cross-ref at [internals.md:179](../../../../skills/task-system/references/internals.md#L179) correctly points to `SKILL.md §Task File Format` (exists).
- **Direct-mode main agent — PASS.** The generated `direct-mode-implementer.md` / `direct-mode-reviewer.md` received the identical Editing-Etiquette edits as their canonical sources (verified by `git diff 04fa8e2e..HEAD`), and `sync_codex_agents.py --scope project --check` exits 0 ("All generated direct-mode role references are up to date" + "All generated agent files are up to date"), proving the direct-mode refs and the `.codex/agents/*.toml` files were regenerated from the canonical specs in task 03, not hand-edited. Direct-mode agents also load `using-superra`, so they reach §Task Interface for the now-relocated shared principles.

### Dangling-pointer sweep

**Zero dangling pointers in live surfaces** (`skills/`, `agents/`, `README.md`, `CLAUDE.md`).

- Grepped for `§How to Read`, `§How to Edit`, `§Ownership Model`, `§Command Surface`, `§Handoff Docs`, the old `using-superra §Handoff Docs` pointer, and the old "self-contained task.md" claim. No live pointer targets a removed anchor.
- The old "a bare `task.md` is self-contained" claim was correctly **inverted** in §Task Interface: using-superRA now states a bare `task.md` is **not** self-contained and you must read through `task_read.py` ([SKILL.md:45](../../../../skills/using-superRA/SKILL.md#L45)). Remaining "self-contained" hits refer to figures/dashboards/drift-tests — unrelated, correct.
- All task-system internal cross-references resolve: `using-superRA/SKILL.md §Task Interface` (exists L41), `planning.md §Field-by-Field Notes` (exists L120), `internals.md §Migration` (exists L91), `internals.md §Dashboard` (exists L190), `SKILL.md §Task File Format` (exists L58). The stale baseline cross-ref `internals.md → "See SKILL.md §Preparing a PLAN.md"` was eliminated when the prep content was consolidated into `internals.md` itself.
- Doc surfaces (CLAUDE.md ownership-boundary table, README.md, CATEGORIES.md) were updated coherently in task 04: CLAUDE.md added a `using-superra (§Task Interface)` row for the universal interface and a tree-tooling row, README/CATEGORIES now describe task-system as load-on-demand tree tooling pointing at `using-superRA §Task Interface` for the executing-agent path.

### Observed, out of scope (not defects of this restructure)

- `superplan/SKILL.md:30` carries a soft pointer "offer migration via `task-system` §Migration". `task-system` SKILL.md has no literal `## Migration` heading (migration lives in `internals.md §Migration`, reachable via the SKILL.md §Routing table). This was already a loose/conceptual pointer at baseline — baseline `task-system` SKILL.md likewise had no `## Migration` heading (it was `### Migrate legacy …` under `## Command Surface`). The restructure did not introduce the looseness, `superplan` was not modified by tasks 01–04, and the migration content remains reachable. Pre-existing, not a regression.
- `.plan/task-system/task-edit-discipline/skill-guidance/task.md:37` contains a historical markdown link `[§How to Edit a Task](…/skills/task-system/SKILL.md#L64)` to a now-removed section. This is a closed/approved planning record from an earlier round, not a live skill cross-reference; the objective scopes the sweep to live surfaces (`skills/`, `agents/`, `README.md`, `CLAUDE.md`), not historical `.plan/` task bodies. Noted for completeness only.

### Verification commands run

- `git show 04fa8e2e:<path>` for all 8 snapshots (all present at baseline).
- `git diff 04fa8e2e..HEAD -- agents/implementer.md agents/reviewer.md skills/using-superRA/references/direct-mode-*.md` — confirms role-spec + direct-mode etiquette edits are identical.
- `git diff 04fa8e2e..HEAD -- skills/task-system/references/planning.md` — empty (planning.md unchanged, as the objective requires).
- `uv run skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` → exit 0, generated artifacts in sync.
- Grep sweeps across `skills/ agents/ README.md CLAUDE.md` for all moved/renamed anchors → zero live dangling pointers.
