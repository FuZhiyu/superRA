# PLAN: User-Facing Doc Polish + Initial Release Prep

## Objective

Turn the committed crude draft of `README.md` + `CLAUDE.md` (commit `3970828` on `jzf/readme-doc-polishing-v2`) into a careful, shippable documentation pair and sweep adjacent user-facing docs (`plugin.json`, `marketplace.json`, `RELEASE-NOTES.md`, `skills/CATEGORIES.md`, `AGENTS.md`, `GEMINI.md`, installation instructions) so the plugin is ready for an initial public release.

**Content split the user has already committed and wants preserved:**

- `README.md` — **user-facing.** What superRA is, the researcher pain it solves, the three-phase workflow, the skill offering (workflow / domain / utility), installation, licensing. No internal design principles, no DRY ownership map, no full Mermaid architecture diagram.
- `CLAUDE.md` — **developer / contributor-facing.** Design principles, DRY / composability rules, skill-design patterns, architectural discipline, extension roadmap. The audience is anyone modifying superRA itself.

## Methodology

Treat the crude draft as authoritative direction, not prose. Keep the section structure and tone the user set; rewrite paragraphs for clarity; add what's genuinely missing (e.g., utility-skill inventory, installation remote, rendered Mermaid diagram); remove HTML comment TODOs by resolving them. Apply `skill-creator` principles to every description field (concise, trigger-oriented, one purpose per skill).

Every commit stays atomic and scoped to one task block below. Commits land on `jzf/readme-doc-polishing-v2`.

## Project Conventions (walk date: 2026-04-20)

- **Repo-root `/CLAUDE.md`** — already the post-draft version. Carries design principles the user wants developer-only. Preserve its spirit; any content I move *out of* README lands *into* CLAUDE.md in a coherent place.
- **`skills/CATEGORIES.md`** — authoritative grouping index (Workflow / Domain / Utility / Meta). README skill tables must mirror it.
- **`using-superRA` §Skill Inventory + §Skill-Load Manifest** — runtime-facing master map. README should point at it, not duplicate it.
- **`RELEASE-NOTES.md`** — currently has three `Unreleased` sections accumulated during the Phase A–D / unified-integration / session-start-hook work. An initial release cuts a version header and consolidates.
- **`skill-creator` discipline (loaded)** — frontmatter descriptions must carry both *what* and *when-to-use*; avoid duplication between description and body; keep references one level deep.

## Expected Results

- `README.md` reads top-to-bottom as a user onboarding doc. New user can decide whether to install within 60 seconds of scanning.
- `CLAUDE.md` is the single entry point for anyone modifying superRA. Covers workflow principles, DRY, skill-design patterns, extension path.
- `plugin.json` + `marketplace.json` descriptions are user-facing, accurate, and match the README tagline.
- `RELEASE-NOTES.md` has a dated `0.1.0` (or user-chosen version) section consolidating the three pending `Unreleased` blocks.
- All skill inventories (README, `skills/CATEGORIES.md`, `using-superRA`) agree on skill names, categories, and one-liners.
- No stale cross-references (`§Changing Plans` → `§User Feedback and Changing Plans`, Stage → Phase vocabulary, removed `merge-workflow`, etc.).

## Pipeline

Single artifact: the documentation itself. No code pipeline. Verification = `rg` sweeps for stale strings + a human read-through after each task.

## Workflow Status

- [x] Plan approved
- [ ] Task 1a — Mermaid workflow diagram (awaiting re-review)
- [ ] Task 1b — README prose rewrite (awaiting re-review)
- [ ] Task 2 — CLAUDE.md consolidation
- [ ] Task 3 — plugin.json + marketplace.json descriptions
- [ ] Task 4 — installation instructions verified
- [ ] Task 5 — cross-reference + terminology sweep
- [ ] Task 6 — final human read-through and release tag decision
- [ ] Refactored (integration-workflow — N/A, docs-only branch)
- [ ] Docs finalized
- [ ] Merged

---

## Decisions

**2026-04-20 — Scope reduction before dispatch.** User dropped two tasks from the original 8-task plan and deleted the artifact feeding one of them:

- **Drop old Task 5 (RELEASE-NOTES initial-release cut).** `RELEASE-NOTES.md` is being deleted from the repo; no consolidation needed. Rationale: user prefers to not maintain a separate change log for the initial release.
- **Drop old Task 6 (CATEGORIES + AGENTS.md + GEMINI.md sweep).** Deferred to a later pass; not required for the initial user-facing-docs release.
- **Split Task 1 into 1a (Mermaid diagram, isolated) + 1b (README prose rewrite).** Rationale: the diagram is complex enough to warrant a dedicated agent so the prose rewriter doesn't context-switch.
- **Renumber remaining tasks.** Old Task 7 → new Task 5; old Task 8 → new Task 6.

No downstream per-task `**Review status:**` rollback needed — nothing has been implemented yet.

**2026-04-20 — Version bump for initial release.** User chose 0.1.0 (was 0.0.4.1) to mark this as the first public release. Rationale: README + CLAUDE.md split complete, install flow modernized, workflow diagram added — milestone is meaningful.

**2026-04-20 — Task 1a diagram revision requested.** User inspected the embedded diagram in README and rejected the layout. Required layout:

- **Strict top-to-bottom linear flow:** PLAN → IMPLEMENT → INTEGRATE as a single vertical column. No subgraphs that break the column or push phases sideways.
- The implementer ↔ reviewer loop inside IMPLEMENT and the A → B → C → D chain inside INTEGRATE must still be visible, but simpler than the current draft.
- **Back-arrows for scope-change re-entry must exist** but must NOT disrupt the linear reading order — route as dotted curves along the side of the column, not through it.
- **Render + visually inspect** before claiming done. Syntax-only validation (`npx mermaid-cli` "no errors") is not sufficient — the reviewer must look at the SVG/PNG output and confirm it matches the layout brief.

DAG cascade: Task 1a `**Review status:**` rolled back APPROVED → REVISE. Task 1b's `**Review status:**` also rolled back APPROVED → REVISE because its embedded diagram is now stale; however Task 1b's non-diagram sections (header, Why, Key principles, Domain/Utility tables, Hooks, Contributing, Upstream, License, the Task 4 Installation block) are untouched and do NOT need to be redone — the revision is scoped to re-embedding the new diagram in README §Plan-Implement-Integrate Workflow. No cascade onto Tasks 2, 3, 4.

---

## Task 1a: Mermaid workflow diagram for README

**Depends on:** *(none)*

**Objective.** Design a single Mermaid diagram that the user-facing README embeds in its "Plan-Implement-Integrate Workflow" section. Isolated from the prose rewrite because the diagram demands focused attention on information architecture — what survives, what gets collapsed, what stays implicit.

**Constraints:**

- Renders on GitHub markdown (standard Mermaid syntax; no mermaid-cli-only features).
- User-facing detail level — less dense than the prior README Workflow Map, more narrative than an academic flow chart. Target: a researcher skimming the README understands the phases and the iteration mechanism within ~20 seconds.
- Must show, at minimum:
  - Three top-level phases: **PLAN → IMPLEMENT → INTEGRATE**.
  - Inside IMPLEMENT: the implementer ↔ reviewer loop per task (APPROVE advances, REVISE loops back).
  - Inside INTEGRATE: the four phases A / B / C / D with one-line labels (A drift tests, B review-led sync + refactor, C doc finalization, D merge / PR).
  - An arrow from any of IMPLEMENT / INTEGRATE back to PLAN labeled "scope change (§User Feedback and Changing Plans)".
  - A terminal arrow out of Phase D to a `merged` terminal node.
- Do NOT show: stage-to-skill mapping, `Skill-Load Manifest` detail, cross-cutting skills rail, stage → reference mapping. Those belong in `using-superRA`, not the user README.

**Deliverable.** A ready-to-paste fenced ```` ```mermaid ```` block saved to `docs/drafts/workflow-diagram.mmd` (create the `docs/drafts/` directory if needed). Do NOT edit `README.md` itself in this task — Task 1b does the embedding.

**Steps:**

- [x] Read `README.md` (current state) and the prior Workflow Map diagram (via `git show 3970828^:README.md`) to set the density ceiling — the new diagram sits well below it (no cross-cutting rail, no skill-load manifest detail).
- [x] Draft the diagram as `flowchart TB` with one IMPLEMENT subgraph (implementer ⇄ reviewer loop, default TB) and one INTEGRATE subgraph (A → B → C → D chain); main column is PLAN → IMPLEMENT → INTEGRATE → `merged`; scope-change back-arrows represented as undirected dotted edges (`PLAN -. scope change .- IMPLEMENT` and `PLAN -. scope change .- INTEGRATE`) so dagre routes them along the sides without dragging PLAN off-column.
- [x] Render + visually inspect: `npx @mermaid-js/mermaid-cli -i /tmp/wfdiag/src.mmd -o /tmp/wfdiag/out.png -b white`, viewed output via Read tool. Confirmed: PLAN is at top of a single vertical column, IMPLEMENT stacks below it, INTEGRATE below that, `merged` terminal at the bottom; the two dotted scope-change edges curve along the left (PLAN ↔ IMPLEMENT) and right (PLAN ↔ INTEGRATE) sides of the column; implementer ⇄ reviewer loop readable inside IMPLEMENT; A → B → C → D chain readable inside INTEGRATE.
- [x] Saved to `docs/drafts/workflow-diagram.mmd` with a leading comment noting the target embed location (README §Plan-Implement-Integrate Workflow).
- [x] Commit: `docs(readme): draft workflow diagram for embedding`.

**Expected result.** A self-contained Mermaid file that Task 1b can lift into README without further thought.

> **Reviewer revision — 2026-04-20 (user feedback):** Prior `APPROVE` rolled back. The two-subgraph layout (`flowchart TB` with IMPLEMENT subgraph in `direction LR`) breaks the linear PLAN → IMPLEMENT → INTEGRATE reading order the user wants. Redo per the layout brief in §Decisions (strict vertical column, dotted back-arrows for scope-change routed along the side, render + visually inspect before claiming done).
> → implemented: rewrote `docs/drafts/workflow-diagram.mmd` — dropped the `direction LR` override on IMPLEMENT, kept both subgraphs in default TB, and replaced the directed `IMPLEMENT -.-> PLAN` / `INTEGRATE -.-> PLAN` back-arrows with undirected dotted edges `PLAN -. scope change .- IMPLEMENT` / `PLAN -. scope change .- INTEGRATE`. Undirected edges don't feed dagre's rank solver, so PLAN stays at the top of the column; the edges render as dotted curves along the left and right sides of the main column without disrupting the vertical reading order. Rendered to PNG and visually inspected before handing off (evidence via Read on `/tmp/wfdiag/out.png`).

**Review status:** IMPLEMENTED
**Integration status:** *(N/A)*

---

## Task 1b: Rewrite README.md as a careful user-facing doc

**Depends on:** Task 1a (embeds its diagram)

**Objective.** Turn the crude README draft into a polished user-facing doc that preserves the user's chosen section structure and tone.

**Scope (sections to rewrite, in order):**

1. **Header + tagline.** One sentence that lands what superRA is. Followed by the three-bullet offering the user drafted (workflow / domain skills / utility skills) — tighten wording, keep the list shape.
2. **"Why superRA?"** Keep the bulleted pain-point framing the user chose. Polish grammar; tighten each bullet to one punchy line; drop the trailing "...". Follow with the one-paragraph resolution ("superRA brings discipline...") — rewrite for clarity, make the three-part structure (implementer-reviewer pair / domain skills / integration) explicit.
3. **"The Plan-Implement-Integrate Workflow" section.**
   - Embed the Mermaid diagram produced by Task 1a (copy the contents of `docs/drafts/workflow-diagram.mmd` into a fenced ```` ```mermaid ```` block).
   - Drop the inline `<!-- -->` HTML comments once the diagram resolves them.
   - Keep the prose paragraph above the diagram that motivates iteration.
4. **"Key principles of the workflow"** (renamed from "Design Principles" to match the user's draft tone). Five bullets as the user drafted them — polish grammar and tighten. For principle 3, fill in the user's explicit TODO "Explain what does integration and semantic merge do" with one sentence each.
5. **"Domain Skills" section.** Replace the placeholder ("we ship data analysis skill") with a short table keyed from `skills/CATEGORIES.md` §Domain: one row for `econ-data-analysis` with its flagship-discipline one-liner. End with the roadmap list of planned verticals (theory / lit review / simulation / writing) — one line each, explicitly flagged as hooks, not commitments. This moves the "planned verticals" content back into the README where users expect it (it was deleted in the crude draft along with CLAUDE.md's Roadmap section).
6. **"Utility Skills" section.** Replace the placeholder with a short table: `report-in-markdown`, `refactor-and-integrate`, `worktree-data-sync`, `semantic-merge`, `handoff-doc`. One-line description per skill, keyed from `skills/CATEGORIES.md`. Apply `skill-creator` description discipline — each row says what + when.
7. **"Installation" section.** See Task 4; Task 1b leaves a `<!-- Task 4 -->` anchor here if Task 4 hasn't landed yet, otherwise inline the Task 4 output.
8. **Existing "Skill Inventory" table** (downstream of Installation, currently in main — need to check what survived the crude draft). Fold into the Domain Skills / Utility Skills tables above; do not repeat.
9. **"Hooks" table.** Keep as-is from the crude draft but verify the two rows (`ask-user-question-logger`, `exit-plan-mode`) match current `hooks/hooks.json`.
10. **"Plugin Design Philosophy" section** at the bottom of the crude draft. Move this entirely to CLAUDE.md (Task 2). Replace with a one-paragraph "Contributing" block that points at `CLAUDE.md` for design principles.
11. **"Upstream" + "License"** — restore the "Upstream" paragraph (credits Jesse Vincent / Superpowers) that the crude draft deleted. The License section should stay.

**Steps:**

- [x] Read current `README.md` end-to-end; list every surviving stale reference in a scratchpad
- [x] Read `docs/drafts/workflow-diagram.mmd` (Task 1a output) to have the diagram ready for embedding
- [x] Rewrite sections 1–11 in place, one heading at a time
- [x] `rg -n "<!--|TODO|tbd|\.\.\." README.md` to confirm no placeholders survived
- [x] Commit: `docs(readme): careful rewrite of user-facing README`

**Expected result.** A `README.md` a first-time user can read front-to-back in 5 minutes and know: what this is, when to use it, what skills ship, how to install, and where to read more.

> **Reviewer revision — 2026-04-20 (cascade from Task 1a):** Prior `APPROVE` rolled back because the embedded Mermaid diagram is now stale. Scope of the re-revision: replace the ```mermaid``` fenced block in README §Plan-Implement-Integrate Workflow with the revised `docs/drafts/workflow-diagram.mmd`. Every other section of README stays as-is.
> → implemented: re-embedded the revised diagram — replaced only the ```mermaid ... ``` fenced block in README §Plan-Implement-Integrate Workflow with the body of `docs/drafts/workflow-diagram.mmd` verbatim. All surrounding prose (the paragraph above the diagram, §Key principles, §Domain Skills, §Utility Skills, §Installation, §Hooks, §Contributing, §Upstream, §License) is byte-identical to the APPROVED state in commit `9825529`.

**Review status:** IMPLEMENTED
**Integration status:** *(docs-only; N/A)*

---

## Task 2: Consolidate CLAUDE.md as the developer / contributor doc

**Depends on:** Task 1b (so we know what moved out of README)

**Objective.** Finish the stash's CLAUDE.md edits into a coherent contributor doc. The stash left the file mid-rewrite (partial "Skill Design Patterns" section, orphan blank lines, removed Roadmap that needs reinstating).

**Scope:**

1. **Top-of-file framing paragraph.** Keep the user's added sentence ("Treat the domain as 'Skill-creation' and load `skill-creator` skill…") but reword it for a developer reader: any agent modifying skills in this repo should load `skill-creator` alongside the superRA workflow skills.
2. **"Skill Design Patterns" subsection** the user sketched. Complete it:
   - Bullet 1 (activate `skill-creator`) — keep, reword.
   - Bullet 2 (positive over negative instructions) — keep, add a one-line example.
   - Bullet 3 (minimal instruction, no design-reasoning spill) — keep the user's example verbatim as an "anti-pattern" call-out; add a one-line "why" that makes the point stick.
   - Add a 4th bullet from the user's CLAUDE.md edit on the architectural pattern: "Agents only load what they need; when adding new instructions, think carefully where it should be so only relevant agents learn about it."
3. **Workflow principles.** Keep unchanged — the stash didn't touch principles 1–4. Verify the §Architectural pattern sub-bullets the user edited read coherently now (the stashed edit introduced a dangling `- ` bullet).
4. **Reinstate "Roadmap: Extending Beyond Data Analysis" section** that the crude draft deleted. Rationale: developers adding a new vertical need this checklist, and the README will only carry the user-facing roadmap bullets. Keep the README version short; keep the CLAUDE.md version as the actionable developer checklist.
5. **Absorb the README crude draft's "Plugin Design Philosophy" bullets** (Composable / stand-alone / lean agent / DRY) into the existing §Design Principles section in CLAUDE.md. These are contributor-facing, not user-facing.
6. **General house-keeping section at the bottom** — verify still accurate.

**Steps:**

- [x] Read current `CLAUDE.md` end-to-end
- [x] Complete the "Skill Design Patterns" subsection per scope item 2
- [x] Restore Roadmap section (copy from prior `main` version + trim redundant prose)
- [x] Absorb Plugin Design Philosophy bullets into §Design Principles (folded "Composable / stand-alone" into §Architectural pattern as a new "Composable by category" bullet; "Lean agent" was already covered; "DRY" already owns its own subsection)
- [x] Sweep §General — removed stale `RELEASE-NOTES.md` reference, pointed instead at `superRA:using-superRA` skill inventory
- [x] `rg -n "TODO|placeholder|tbd" CLAUDE.md` → clean
- [x] Commit: `docs(claude-md): consolidate developer-facing design doc`

**Review status:** APPROVED
**Integration status:** *(N/A)*

---

## Task 3: Update plugin.json + marketplace.json descriptions

**Depends on:** Task 1b (README tagline is the source of truth for the plugin description)

**Objective.** Make the one-liner descriptions in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` match the README tagline and communicate what a user gets.

**Current state.** `plugin.json` description = "Super Research Assistant: data-first discipline, analysis planning, reproducibility, and rigorous data validation for economic research". This is accurate but data-analysis-centric; the repo has broadened to a domain-agnostic workflow + data-analysis flagship.

**Steps:**

- [x] Draft the new one-liner: something like "Disciplined AI research assistant for economists: plan-implement-integrate workflow with implementer–reviewer pair, domain-aware data-analysis discipline, and semantic merges." Validate against the README tagline for consistency.
- [x] Update `plugin.json` `description` + `keywords` (consider adding `research-workflow`, `agent-orchestration`)
- [x] Update `marketplace.json` `description` to match
- [x] Decide version: keep `0.0.4.1` (in-flight docs) or bump to `0.1.0` (first public release) — **this is a user decision, log via `AskUserQuestion` and record in §Decisions before editing**
- [x] Commit: `plugin: user-facing description + version bump for initial release`

**Review status:** APPROVED
**Integration status:** *(N/A)*

---

## Task 4: Verify + modernize installation instructions

**Depends on:** *(none)* — can run in parallel with Tasks 1a / 1b

**Objective.** The crude draft left an inline TODO: "need to be updated. https://github.com/FuZhiyu/superRA. and we can directly install from the remote I think. research on the updated guide on how to install for claude code". Resolve it.

**Steps:**

- [x] Verified canonical remote URL via `git remote -v` + `gh repo view FuZhiyu/superRA`: `https://github.com/FuZhiyu/superRA` (PUBLIC). The `econ-superpowers` name in the old crude-draft clone URL is stale.
- [x] Researched current Claude Code plugin install flow. Claude Code v2.1+ ships a `claude plugin` CLI: `claude plugin marketplace add <github-repo>` registers a GitHub repo as a marketplace, and `claude plugin install <plugin>@<marketplace>` installs from it. Local-clone install is supported by passing a directory path to `marketplace add`. The old `.claude/settings.json` flow is no longer the recommended path.
- [x] Rewrote README §Installation: lead with the direct `claude plugin marketplace add FuZhiyu/superRA` + `claude plugin install superRA@superRA-dev` flow; demoted local-clone flow to a "development or forking" subsection; added an update snippet. Marketplace name `superRA-dev` and plugin name `superRA` confirmed from `.claude-plugin/marketplace.json`.
- [x] Verified "Other Platforms" entry files exist at repo root (`AGENTS.md`, `GEMINI.md`, `gemini-extension.json`) and named them explicitly in the subsection with direct links. Users no longer have to guess what the upstream Superpowers docs refer to.
- [x] Commit: `docs(readme): modernize installation instructions`

**Review status:** APPROVED
**Integration status:** *(N/A)*

---

## Task 5: Cross-reference + terminology sweep across all docs

**Depends on:** Tasks 1b, 2, 3, 4

**Objective.** Catch any stale cross-references that survived the individual rewrites.

**Steps:**

- [x] `rg -n "Changing Plans" -- '!docs/plans/'` — every hit reads `User Feedback and Changing Plans`. All hits were already correct; no changes needed.
- [x] `rg -n "Stage 1|Stage 2|Stage 3" skills/integration-workflow/ README.md CLAUDE.md` — fixed 4 stale "Stage 1" / "Stage 2" references in `skills/integration-workflow/SKILL.md` (frontmatter description, Phase C stop-point bullet, two dispatch task strings, and Phase D disposition paragraph).
- [x] `rg -n "merge-workflow"` — clean in README, CLAUDE.md, `skills/CATEGORIES.md`. Only appears in archived `docs/plans/` (expected historical record).
- [x] `rg -n "RELEASE-NOTES"` — clean in README, CLAUDE.md, `skills/CATEGORIES.md`, and all `skills/*/SKILL.md` files. No active cross-references remain.
- [x] `rg -n "VALIDATE|four-phase"` — fixed `CLAUDE.md` line 3: `PLAN → IMPLEMENT → VALIDATE → INTEGRATE` → `PLAN → IMPLEMENT → INTEGRATE`. README already correct.
- [x] `rg -n "\[.*\]\(.*\.md\)"` markdown links spot-check: README links to `AGENTS.md`, `GEMINI.md`, `gemini-extension.json`, `CLAUDE.md` — all exist at repo root. No broken links found.
- [x] Extra item 6 (tagline bullet 3): fixed README tagline bullet 3 — replaced "human-friendly Jupyter notebooks" (no standalone notebook skill) with "gated integration checklists" (maps to `refactor-and-integrate`). Utility Skills table is now 1:1 consistent with the tagline.
- [x] Extra item 7 (GEMINI.md stale @-include): updated `GEMINI.md` — `./skills/using-superpowers/SKILL.md` → `./skills/using-superRA/SKILL.md`; `./skills/using-superpowers/references/gemini-tools.md` → `./skills/using-superRA/references/gemini-tools.md`. Verified both targets exist.
- [x] Commit: `docs: cross-reference + terminology sweep`

**Review status:** IMPLEMENTED
**Integration status:** *(N/A)*

---

## Task 6: Final human read-through + release tag decision

**Depends on:** Tasks 1a–5

**Objective.** Before tagging a release, present the final doc set to the user for read-through. Get explicit approval on: README clarity for a first-time user, CLAUDE.md clarity for a contributor, version number, release tag timing.

**Steps:**

- [ ] Render README.md in GitHub preview (or `gh`-based preview) to confirm Mermaid diagram renders
- [ ] Summarize diffs across the commits for the user
- [ ] Ask via `AskUserQuestion`: version number confirmed? ready to merge `jzf/readme-doc-polishing-v2` → `main`? tag release?
- [ ] Log the answer in §Decisions
- [ ] (If tagging) `git tag v0.1.0 && git push origin v0.1.0`

**Review status:** not started
**Integration status:** *(N/A)*

---

## Review Instructions (for the reviewer agent)

This plan produces no analysis output — every task produces prose. The reviewer's focus is:

1. **Tone fit.** README sections read as user-facing; CLAUDE.md sections read as contributor-facing. No developer-internal detail leaks into README; no user-onboarding prose leaks into CLAUDE.md.
2. **Accuracy.** Every claim about the workflow matches the current `skills/` implementation. Every skill name referenced is a real skill.
3. **skill-creator discipline.** Skill descriptions carry both *what* and *when-to-use*. No duplication between frontmatter descriptions and body.
4. **Cross-reference integrity.** No dead links, no stale terminology, no references to removed skills/sections.
5. **DRY.** Skill inventories agree across README, `skills/CATEGORIES.md`, and `using-superRA`. One source of truth per concern.
