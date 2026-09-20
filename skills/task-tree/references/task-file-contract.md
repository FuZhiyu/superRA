# Task File Contract

Load for the `task.md` contract: frontmatter, body sections, status/dependency mechanics, inherited context rendering, results shape, stale-content cleanup, figure embedding.

Tree-design judgment — objective writing, splitting, placement, durable homes, update-task lifecycle, context distillation, retroactive tree creation — lives in `skills/superplan/references/task-tree-design.md`.

## Tree Shape

`superRA/` holds top-level tasks as direct subdirectories, each with its own `task.md`. An umbrella `superRA/task.md` is optional — add one only when a shared `## Objective` / `### Context` spans every top-level task, per `task-tree-design.md` §Context Distillation's lowest-ancestor rule. It is an ordinary task, not a privileged one.

"Top-level" describes position (no parent), not scope — such a task may be leaf or branch, narrow or broad, like any nested task.

Files retained in a task directory are not task nodes — placement and the `attachments/` task-discovery exception in `skills/using-superra/references/task-companion-files.md`.

## Task Anatomy

Every `task.md` — top-level, branch, or leaf — uses the same frontmatter and body sections. The tree is recursive: a task frames its own subtree; an umbrella task frames the whole project only because its subtree is everything.

**Binding content goes in `## Objective`; everything else is information and goes in `## Details`.** Binding means a reviewer rejects work that violates it. A descendant inherits ancestor objectives and nothing else (§Context Inheritance), so the same test decides what a subtree sees. Each skill classifies its own artifacts against it.

The frontmatter field set is **closed**: `title`, `status`, `depends_on`. Any other key is discarded the next time a CLI mutation rewrites the file (including ancestor-status rollups) — put custom metadata in a body section.

- **`status`** — task-local validity marker. Values: `not-started`, `in-progress`, `implemented`, `revise`, `approved`, `archived`, `postponed`. Co-owned across the dispatch lifecycle: implementer owns transitions up to `implemented` (including `revise` → `implemented` on fix rounds); reviewer owns `implemented` → `revise`, `implemented` → `approved`, and `approved` → `revise` when integration review surfaces issues in a previously approved task. Independent review is triggered, not scheduled — when none runs, the orchestrating agent sets `implemented` → `approved` on its own verification. Replan transitions — flipping a widened `approved` task to `revise`, resetting downstream dependents — are planner judgment, owned by `superplan/references/task-tree-design.md` §Objective rewrites on scope expansion. `archived` and `postponed` are orchestrator/researcher scope decisions, not dispatch verdicts: `archived` removes the task and its subtree from the active dependency graph, with downstream warnings; `postponed` parks the task off the frontier and blocks its dependents until resumed (set back to `not-started`). Review-only trees (e.g. writing-workflow review lanes) skip the implementer states — tasks go from `not-started` straight to `revise` or `approved` as the reviewer sets them.
- **`depends_on`** — sibling directory names, sibling-only; parent status rolls up from children automatically. Dependent siblings are ordered peers, not inherited context — read a dependency's `## Results` only when the downstream objective needs it.
- **`## Objective`** — planner-owned: the task's goal plus any scoped `### Context` / `### Conventions` / `### Constraints` its subtree inherits. Implementers read it but do not rewrite it.
- **`## Details`** — planner-owned, optional: planning findings, domain surveys, a suggested route. Implementers may deviate when another route satisfies `## Objective`; reviewers flag details only when they mislead, contradict the objective, or would fail to achieve it.
- **`## Results`** — implementer-owned findings record. See §Results Shape.
- **`## Revision Notes`** — temporary update delta: what changed, why, how significant (trivial/mechanical vs. substantive). Planner- or orchestrator-authored on an objective rewrite (`task-tree-design.md` §Objective rewrites on scope expansion); the implementer removes it once incorporated, in the same commit that sets `status: implemented` (`implement-task` §Execution) — whether or not review follows.
- **`## Reproduction`** — implementer-owned build-graph declaration; presence registers the task in the reproduction graph. See §Reproduction Section. When to register a step, and when to opt a task into `required`, is discipline owned by the `reproducibility` skill.
- **`## Review Notes`** — reviewer-owned. Present while any item remains: open `[BLOCKING]` findings at `revise`, or the tier/focus header and any un-actioned `[ADVISORY]` items at `approved`. A task may sit at `revise` with deferred findings while the orchestrator advances dependent work.
- **`## Sync Impact`** — temporary, integration-phase-only. Added by the sync author during `superintegrate` Sync to tasks whose post-sync diff needs task-specific context; removed at Integrate closeout. Format owned by `semantic-merge/references/workflow-sync-author.md`.

## Context Inheritance

`superra task read <path>` renders the task with its ancestor chain, including each ancestor's full `## Objective` and nested `### Context` / `### Conventions` / `### Constraints` — that is how a scoped subsection reaches every descendant's agent. What a subsection carries, and when to point rather than distill: `skills/superplan/references/task-tree-design.md` §Context Distillation.

## Hierarchy Management Commands

The mutation command surface — `task create`, `task rename`, `task dep add/remove`, bulk status ops, the move/rename cascade rules — lives in `references/commands.md`. Single-field edits, including `status`, go through direct edit per `using-superra/SKILL.md` §Task Interface.

## Stale Content Checklist

Common stale content to replace in place (never strike through or append "Update:"):

- Task objectives describing an approach abandoned after seeing the data.
- Results sections now incorporated into the current approach.
- Review items confirmed fixed on re-review.
- Sibling task objectives that assume an earlier approach which has since changed.
- Task `## Objective` or `## Results` descriptions superseded by a later task — rewrite in place to the latest shape; see `## Revision Notes` above for when to add one.
- Dated decision ledgers — a "Decisions" section, or a "per user decision `<date>`" note on a rule. A researcher decision enters a task file by rewriting the owning objective or constraint to its current state; date and deliberation stay in git.

## Results Shape

Each task's `## Results` matures through two stages.

### Two-Stage Lifecycle

- **Stage 1 — Dev log (IMPLEMENT phase).** `## Results` is the live, agent-facing findings record. A line belongs only if a future reader needs it to use, reproduce, or trust the result — the inclusion test mirrors the objective's rejection test in `task-tree-design.md` §Writing Objectives and Details. Detail that clears the test sits low in the pyramid or behind a link; anything a linked artifact, commit, or upstream task already carries is pointed at, not restated (`communicate`). Re-implementation replaces a task's results; it never appends history.
- **Stage 2 — Permanent record (INTEGRATE Mature & Consolidate).** After Protect selects results, documentation homes, consolidation dispositions, and protection mechanisms: create the user-facing documentation and result files first, then distil each touched task's `## Results` to a disposition below and apply the structural fold owned by `skills/superplan/references/consolidation.md`. Ordering and record verification: `superintegrate/references/mature-consolidate.md`.

### Maturation Disposition Menu

Stage-2 distillation picks one disposition:

- **Mature** — default for key or substantive results. Synthesize the findings into the agreed user-facing document or result file at its project-appropriate durable home, then leave a concise reader-facing account in the durable task linking the permanent artifact and any retained task-local evidence. A short retained subsection suffices when a full narrative would overstate minor work.
- **Trim-to-pointer** — the task's own output *is* a document (report, rendered note, manuscript section): reduce `## Results` to a one-line pointer, so the document stays the single source of truth rather than a summary that duplicates it and drifts.
- **Drop** — Protect selected the result for omission, or the task is a minor fix not worth surfacing as an outcome: trim heavily or drop `## Results`.

When the consolidation fold removes a task's directory (Merge or Flatten), its distilled results move into the **target** task's `## Results` at the chosen level — a one-line note, a short subsection, or folded into the target's narrative. Nothing is left behind in the deleted directory.

**Guardrail:** results selected to keep at Protect are never dropped. Permanent documentation, result files, and matured task results form the protected record; selected automated checks supplement it.

### Subsection menu

Most results are a few lines under `## Results` with no subsections. Add one only when it carries a takeaway the inclusion test keeps — the default for every entry below is to omit it.

| Subsection | Add when |
|---|---|
| `### Key Findings` | more than one finding a researcher would quote or act on needs separating from the surrounding narrative |
| `### Row Counts / Sample` | a downstream task or reviewer must reconcile against the sample the work produced |
| `### Figures and Tables` | the task produced a figure or table a reader needs to see — embed as `![caption](attachments/fig_name.png)` |
| `### Notes` | a caveat, data quirk, or decision changes how the result is read |
| `### Notation & Assumptions Ledger` | theory-modeling tasks — required by `theory-modeling/SKILL.md`; tasks introducing nothing record "None." |

`superra task result add --finding` is the exception: it appends under a `### Key Findings` heading, creating it when absent, since it needs a fixed insertion anchor rather than parsing hand-written prose. Results assembled by direct edit — the usual path — follow the menu.

### Section Ownership

Implementer and reviewer duties on `## Results` live in the role skills (`superRA:implement-task`, `superRA:review-task`); orchestrator parent-rollup and disposition duties in `superimplement` and `superintegrate/references/mature-consolidate.md`. Beyond those: the planner creates `task.md` with an empty or placeholder `## Results`; a standalone author owns everything.

Any `## Results` riding higher than the task that produced a finding — a parent rollup, a monitoring summary, the matured narrative — links down to the owning task rather than copying the finding up the tree. A rollup is strictly shorter than the children it covers.

### Figure Embedding

Commit figures to `attachments/` beside the task's `task.md` and embed relative to the task file — `![caption](attachments/fig_name.png)` — so moving a task moves its figures and the dashboard resolves them via `pathPrefix`. Full mechanics — PDF-to-PNG conversion, caption discipline, file-reference conventions — in `skills/communicate/references/markdown.md` §Figures.

## Effective Dependencies

**Author only logical prerequisites in `depends_on`.** The effective graph combines them with consumed-output edges inferred from reproduction steps, retaining both reasons when they coincide. Tasks without steps remain graph nodes. Removing a logical declaration leaves any inferred dependency intact.

**Validate at every task boundary.** Nodes are direct child task groups and the containing task's individual steps. Edges inside one collapsed child stay internal; crossing edges order its sibling groups. Reject cycles in the step graph or any boundary graph, including cycles created only by grouping or combining logical and inferred edges. A parent's setup step → child task → parent's report step remains valid; adding a child preserves existing step identities and hashes.

**Use effective prerequisites for development readiness.** Active prerequisite groups at `implemented`, `approved`, or `revise` satisfy the gate; `not-started`, `in-progress`, or `postponed` block. A group's prerequisites apply to its descendants. Internal parent/child prerequisites use actual producer-step freshness, avoiding a wait on the containing parent's child-status rollup. The frontier includes actionable parent-owned steps as `kind: own-work`, with their owner path and step names; this is derived context, not another persisted task status.

**Exclude archived tasks and their subtrees from the active graph.** Keep declarations for direct/transitive downstream warnings. Their consumed artifacts become boundary inputs: available files remain usable, missing files still block execution. Archival itself does not create a blocking dependency or cycle.

**Reject incomplete or cyclic graphs before dispatch or build selection.** Task/step target selection cannot bypass global validation. Structural `task tree` remains available without resolving shell configuration; `task read`, frontier, DAG, dependency checks, and mutation preflight resolve one shared snapshot. Invalid declarations stay readable with their findings.

## Reproduction Section

The build unit is a **step**. File-derived edges also contribute task prerequisites under [Effective Dependencies](#effective-dependencies); `depends_on` retains its sibling-slug syntax. Logical prerequisites govern task development and do not add file inputs or pull unrelated scripts into a reproduction build.

**The section body is exactly one fenced `yaml` block.** Prose outside the fence is a contract violation — a note about a step goes in `## Details` or in a YAML comment inside the block.

```yaml
steps:
  - name: build-panel
    cmd: julia --project=. Code/build_panel.jl
    deps:
      - Code/build_panel.jl
      - "${DATA}/crsp_monthly.parquet"
    outs:
      - "${OUT}/panel.parquet"
  - name: check-panel
    kind: check
    cmd: julia --project=. test/check_panel.jl
    deps: ["${OUT}/panel.parquet", test/check_panel.jl]
```

### Step references

Cite a step with `[build-panel](../data/task.md#step-build-panel)`, relative to the citing file; use `[build-panel](#step-build-panel)` within its own task. The fragment's name must match a step declared in the target task. `task check --category links` validates these citations.

Keep the step name stable when reordering or editing its command. Task moves rewrite relative links; a step rename also requires updating its citations. Citations do not create execution dependencies.

The dashboard reveals and selects the step, and rendered step rows expose matching anchors. A shared dashboard link uses `#/<task-path>?step=<name>` with its worktree selector intact. Generic Markdown viewers can open the task file; exact step jumping requires a renderer that emits the anchor.

### Top-level keys

| Key | Value |
|---|---|
| `steps` | List of step mappings. |

### Step keys

| Key | Value |
|---|---|
| `name` | Slug, unique across the active graph. Archived name/output conflicts are diagnostic only and cannot replace an active producer. |
| `cmd` | Shell string, run from the project root. Mutually exclusive with `runner`. |
| `runner` + `script` | Expands a runner template from config; the script is added to `deps` automatically. |
| `deps` | Files or directories the step reads. With `cmd`, list the script here. |
| `outs` | Files or directories the step writes. A directory out owns every file inside it, so a downstream `deps` entry below that directory infers the edge. |
| `kind` | `build` (default) or `check`. A `check` step declares no `outs` and reruns when its deps change. |
| `params` | Flat mapping hashed into the step's state, so changing a value reruns the step. |

Per-out sidecar tracking is a nested block item:

```yaml
outs:
  - "${OUT}/intermediate.arrow"
  - path: "${OUT}/very_large.arrow"
    sidecar: "${OUT}/very_large.arrow.sha256"
```

Within the selected producer chain, the runner hashes the sidecar instead of the out; a hand-edit of the out goes unnoticed until the sidecar is rewritten. Saved-input boundaries additionally track actual bytes. An absent upstream sidecar does not block an existing artifact: the dependency retains an explicit `saved-input:<digest>` baseline until the consumer executes again; newly available metadata alone does not invalidate unchanged bytes. Producer products still require their declared sidecars. Reviewed acceptance checks actual output and saved-input digests; arbitrary unchanged sidecar text cannot establish equality.

### Project config

Project-wide reproduction settings live under the `reproduction:` key of `superRA/config.yaml`. Top-level keys of that file are namespaced by concern, so later configuration moves in beside `reproduction:` rather than into a second file.

```yaml
reproduction:
  vars:
    DATA: Data/derived
    OUT:
      shell: "Code/output_root.sh"
    SCRATCH:
      env: PROJECT_SCRATCH
  runners:
    julia: julia --project=. {script}
  code_roots:
    - Code
```

| Key | Value |
|---|---|
| `vars` | Name → a literal, `env: NAME`, or `shell: "…"`. Evaluated once per invocation. |
| `runners` | Name → command template containing `{script}`. |
| `env_deps` | Optional paths added to every step's deps; changing one invalidates every step. Existing explicit configurations retain this behavior. Default environment-file handling belongs to [reproducibility](../../reproducibility/SKILL.md#environment-changes). Machine-specific files — sysimages, caches — never belong here. |
| `code_roots` | Directories the reminder hook watches for producer edits. |

`${VAR}` interpolation applies to `cmd`, `deps`, `outs`, `script`, and `env_deps`; `code_roots` is read literally. **Every node keeps its variable-form path as its id** alongside the resolved path. Root changes invalidate through changed content or resolved command text; relocation to equal bytes alone preserves freshness.

### The YAML subset

Both the section block and `config.yaml` are read by a stdlib parser over a bounded subset. `pyyaml`, when installed, reads every accepted text to the same values, except for two resolvers the subset drops: a timestamp-shaped scalar (`1994-01-01`) becomes a date under `pyyaml` and a sexagesimal (`12:30`) becomes an integer, where the subset keeps both as strings.

- **Accepted:** block mappings, block lists, inline lists of scalars, plain and quoted scalars, `#` comments.
- **Rejected:** anchors, aliases, tags, multi-line (literal or folded) scalars, inline mappings, duplicate keys, tab indentation.
- **Rejected here, accepted by `pyyaml`:** an unpaired `'` or `"` inside a plain scalar (`cmd: echo don't` — quote the whole scalar); an escaped `\"` inside a double-quoted scalar; any escape outside `\n`, `\t`, `\r`, `\\`, `\/`, `\0`, including `\uXXXX`.

Inline lists are flow context, where YAML reserves `{`, `}`, `[`, `]`, and `,`: quote a `${VAR}` path there (`deps: ["${OUT}/panel.parquet"]`) or use a block list. Both parsers reject the unquoted form.

Julia deps carry their own closure: a `.jl` dep expands to every file it reaches through `include`, so helper edits invalidate the step without being listed. Resolved forms are a string literal; `joinpath(@__DIR__, "…")` or `joinpath` of string literals; DrWatson's `projectdir("…")`, `srcdir("…")`, and `scriptsdir("…")`, also as the head of a `joinpath`; and `joinpath(<variable>, "…")` — a variable root resolves against the project root, then against the including file, keeping whichever is on disk and warning when both exist. An include whose argument is not a static path is reported and left to be declared by hand.

### Validation

Findings come back in the `Finding` shape shared with `task check`, under the `reproduction` or `dependency` category.

**`[ERROR]`**

- **Text:** prose outside the fence; YAML outside the subset, in a section or in `config.yaml`.
- **Names and outs:** a missing or non-slug `name`; a duplicate active step name; two active steps declaring the same out.
- **Step shape:** a step that declares neither `cmd` nor `runner` + `script`; a `kind` other than `build` or `check`; a `check` step with outs; a `deps` or `outs` value that is not a list; an `outs` entry that is neither a path nor `path:` with an optional `sidecar:`; a `params` value that is not a flat mapping.
- **Dependencies:** step cycles, cyclic task-group ordering, unresolved logical prerequisites, or incomplete task parsing.
- **Keys and config:** an unknown section, step, or `reproduction:` key; a `runner` the config does not define; a runner template without `{script}`; an unknown `${VAR}`.

**`[WARNING]`** — a retired `tier:` section key, which is ignored; a dep that neither exists on disk nor is produced by a step; an archived or postponed prerequisite; an `include` that could not be resolved.

**Unregistered results artifact** — an advisory `[WARNING]`, one per file, when a task's `## Results` links a file on disk that looks generated (a data or exhibit extension, or a `.tex` inside a directory some step writes into) and that no active step declares as an out and no step reads as a dep. Not every retained artifact belongs in the graph, so it never blocks. Silent for a tree with no `## Reproduction` section and no `code_roots`, for prose and source links, and for scratch paths.

An out that has never been built is runner state, reported as `missing` by `repro status`, not a check finding — a fresh clone of a correctly declared tree checks clean.

### Acceptance and successful baseline records

The project-root `repro-acceptance.json` is committed separately from `pytask.lock`. Its version-1 object has `version: 1` and a `steps` mapping by stable step name. Each record contains:

| Field | Binding |
| --- | --- |
| `id` | SHA-256 of the canonical JSON record excluding `id` |
| `basis` | `reviewed` for current-state acceptance; absent on legacy unchanged-output acceptance |
| `baseline` | Preceding successful lock and available execution evidence; `lock: null` when the runner has never built the step |
| `boundary_inputs` | Actual saved-input fingerprints at acceptance, including inputs between steps accepted together |
| `state` | Reviewed dependency/specification hashes, engine product hashes, and actual output fingerprints |
| `upstream` | Direct upstream acceptance ids on which this decision relies |
| `reason`, `reviews` | Required overall rationale and optional per-node notes |
| `evidence` | Optional existing evidence-file references mapped to content hashes at review time |
| `recorded_at`, `actor` | Recording time and available local account name |

A reviewed record establishes or replaces the current baseline, including never-built producers and changed outputs. It binds the preceding successful lock if any, reviewed input/product/output state, and selected upstream acceptance identities. Outside producers remain saved-input boundaries. Changes after acceptance invalidate that state. Invalid graphs, missing inputs/products, and unsuccessful executions cannot be covered. Acceptance does not change workflow task statuses, successful lock entries, check stamps, or actual-run metadata. The status vocabulary remains `fresh`, `stale`, `missing`, `failed`, and `external`.

Successful receipts live in gitignored `.superra-repro/baselines/<step>.json`. After engine product verification, the runner records full output digests, the dependency/product state, the resolved step definition, and UTF-8 dependency snapshots of at most 128 KiB each and 1 MiB per step. `execution_scope` names the frozen selected steps; `boundary_inputs` records consumed artifacts from out-of-scope producers, their logical/resolved paths, actual digests, producer identities, and successful-output provenance when available. Dependencies and boundary bytes must remain unchanged through execution. A receipt supports a baseline only when its recorded state matches the successful lock. Accepted records embed the preceding execution identity if any, reviewed state, output digests, and saved-input fingerprints, preserving reuse checks after local cache loss. Raw source snapshots remain local and never enter the committed ledger or status payload; absent historical source text and execution logs remain unavailable.

Build guards compare the selected commands/specifications, resolved paths, and relevant artifact ownership. Unrelated task creation, active status changes, prose, and unused configuration edits do not abort a run. Full graph validation applies at invocation start; changes to the selected contract prevent inconsistent success evidence. Acceptance retains its separate preview/apply consistency guard.

Older normal-output locks supply successful output hashes without source snapshots; older sidecar locks supply only sidecar hashes. A current reviewed baseline hashes the actual outputs even without a successful receipt; it does not claim those bytes were executed. `explain` discloses unavailable source text. Legacy acceptance records without `basis` retain successful-output equality and upstream-freshness requirements. Check acceptance requires its previous successful baseline and unchanged stamp; missing stamps require execution.
