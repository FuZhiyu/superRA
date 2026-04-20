# RESULTS: User-Facing Doc Polish + Initial Release Prep

**Objective.** Turn the committed crude draft of `README.md` + `CLAUDE.md` into shippable documentation and prepare adjacent user-facing docs for an initial release.

**Status.** Plan approved; execution in progress.

---

## Task 1a: Mermaid workflow diagram for README

**Status:** IMPLEMENTED — awaiting re-review.

**Artifact:** [`docs/drafts/workflow-diagram.mmd`](docs/drafts/workflow-diagram.mmd) — self-contained Mermaid diagram ready for Task 1b to embed verbatim in README §Plan-Implement-Integrate Workflow.

**Layout change (2026-04-20 revision).** The prior draft used a two-subgraph layout with `direction LR` inside IMPLEMENT, which pushed the implementer/reviewer nodes sideways and broke the linear PLAN → IMPLEMENT → INTEGRATE reading order the user wants. The revised diagram keeps both subgraphs in the default TB direction so every node stacks inside the main vertical column. The structurally important change is the back-arrow encoding: the old `IMPLEMENT -.-> PLAN` / `INTEGRATE -.-> PLAN` directed dotted arrows forced dagre's rank solver to place PLAN below IMPLEMENT and INTEGRATE, destroying the column. Replacing those with undirected dotted edges `PLAN -. scope change .- IMPLEMENT` and `PLAN -. scope change .- INTEGRATE` keeps the edges out of the rank solver entirely, so PLAN stays at the top of the column while the edges render as dotted curves along the left and right sides — exactly the "routed along the side, not through the column" brief.

**Design choices:**

- `flowchart TB` with two subgraphs in default TB direction. IMPLEMENT holds the implementer ⇄ reviewer loop with APPROVE/REVISE labels; INTEGRATE holds the A → B → C → D chain with one-line labels.
- Shows only what the Task 1a constraints require: the three phases, the implementer/reviewer loop, Phases A–D, two dotted `scope change` connections between PLAN and each of IMPLEMENT / INTEGRATE, and a `merged` terminal node off Phase D. Explicitly excludes: skill-load manifest detail, cross-cutting skills rail, stage → reference mapping (those live in `using-superRA`).
- Density unchanged from the prior draft: seven phase nodes + terminal, ~1/3 the ink of the pre-rewrite README Workflow Map.

**Validation:** Rendered via `npx @mermaid-js/mermaid-cli -i src.mmd -o out.png -b white` and visually inspected through the Read tool on the PNG. Confirmed against the layout brief: PLAN at top, IMPLEMENT and INTEGRATE stacked below it in a single vertical column, `merged` at the bottom, scope-change edges as dotted curves along the left and right sides of the column, implementer ⇄ reviewer loop and A → B → C → D chain both readable inside their subgraphs. GitHub Mermaid uses a compatible feature subset — no mermaid-cli-only syntax used (standard `classDef` / `subgraph` / undirected `-. .-` edges only).

## Task 1b: Rewrite README.md as a careful user-facing doc

**Status:** IMPLEMENTED — awaiting re-review (diagram re-embed only).

**Summary.** Rewrote every README section outside the APPROVED `## Installation` block. Header tagline tightened to three offering bullets (workflow / domain skills / utility skills). "Why superRA?" bullets polished, trailing ellipsis dropped, resolution paragraph rewritten to surface the three-part structure (implementer-reviewer pair / domain skills / integration phase). "The Plan-Implement-Integrate Workflow" now embeds the Task 1a Mermaid diagram verbatim from `docs/drafts/workflow-diagram.mmd` (validated with a byte-level diff) and drops the `<!-- -->` TODO comments. "Key principles" polished across all five bullets; principle 3's TODO resolved with explicit definitions of integration (refactor + dovetail with existing codebase, mature docs) and semantic merge (intent-based conflict classification with escalation for research impact). "Domain Skills" replaced with a table row for `econ-data-analysis` plus a flagged-as-hooks roadmap list for theory / lit review / simulation / writing. "Utility Skills" replaced with a table covering `handoff-doc`, `report-in-markdown`, `refactor-and-integrate`, `semantic-merge`, `worktree-data-sync`, each row carrying both *what* and *when to use* per `skill-creator` discipline. The separate downstream "Skills / Workflow / Domain / Utility / Meta" inventory from the pre-draft README was folded into the new Domain + Utility tables; a single pointer to `using-superRA` §Skill-Load Manifest (agent-facing) and `skills/CATEGORIES.md` (contributor-facing) replaces the duplicate surface. Hooks table verified against `hooks/hooks.json` (three entries: `merge-guard`, `ask-user-question-logger`, `exit-plan-mode`). Removed the crude draft's placeholder "Plugin Design Philosophy" section; replaced with a one-paragraph "Contributing" block pointing at `CLAUDE.md`. Restored the "Upstream" paragraph crediting Jesse Vincent / Superpowers that the crude draft deleted.

**Verification.** `rg -n "<!--|TODO|tbd|\.\.\." README.md` returns nothing. Byte-diff of the Mermaid fenced block against `docs/drafts/workflow-diagram.mmd` is empty — diagram embedded verbatim. `## Installation` section (heading through end of `### Other Platforms`) untouched per Task 4 APPROVED scope.

## Task 2: Consolidate CLAUDE.md as the developer / contributor doc

**Status:** APPROVED.

**Summary.** Finished the stash's mid-rewrite of `CLAUDE.md` into a coherent contributor doc. Section-by-section:

- **Top-of-file framing.** Added a dedicated paragraph directing any agent that modifies `skills/*/SKILL.md` to load `skill-creator` alongside the superRA workflow skills, and stating this file's audience (contributor-facing, developer-internal). Removed the stash's dangling trailing sentence after the §Working-in-This-Repo bullets.
- **§Working in This Repo, §Skill Changes.** Unchanged — already coherent.
- **§Design Principles workflow principles 1–4.** Unchanged per scope item 3; verified byte-equal to the pre-edit state.
- **§RA framing.** Unchanged.
- **§Architectural pattern.** Closed the dangling `- ` bullet the stash introduced. Reworded the "Lean agents, rich references" bullet to drop the stash's inline "Agents only load what they need" clause (that belongs in Skill Design Patterns, where it now lives). Added a new middle bullet **"Composable by category"** absorbing two of the crude-draft README's "Plugin Design Philosophy" bullets (Composable / stand-alone). The fourth crude-draft bullet (DRY) already owns its own `### DRY, composability, extensibility` subsection; the "Lean agent" crude-draft bullet was already covered by the existing "Lean agents, rich references" bullet. Preserved the existing "Flat `skills/` layout" bullet.
- **§Skill Design Patterns.** Completed the four-bullet section the user sketched. Bullet 1 (activate `skill-creator`) reworded for clarity. Bullet 2 (positive over negative) kept and given a concrete example ("Describe the data before transforming it" vs the negative form). Bullet 3 (minimum instruction) reformulated so the user's "domain-agnostic" paragraph reads as an explicit "Avoid this anti-pattern" call-out with a one-line "why" after the quoted block. Bullet 4 (new, from scope item 2) added: agents only load what they need, so place new instructions where only the right agents pick them up.
- **§DRY, composability, extensibility; §Domain verticals.** Unchanged.
- **§Roadmap: Extending Beyond Data Analysis.** Restored from `git show 3970828~1:CLAUDE.md` and placed after §Domain verticals (where it lived before). Trimmed scope item 3's "(or under a new vertical heading)" parenthetical since §Domain has a single category heading now.
- **§General.** Removed the stale `RELEASE-NOTES.md` reference (file is deleted on this branch). Sync guidance now points at `README.md`, `skills/CATEGORIES.md`, and the skill inventory in `superRA:using-superRA` — three real, live docs.

**Verification.** `rg -n "TODO|placeholder|tbd" CLAUDE.md` → clean. `rg -n "RELEASE-NOTES" CLAUDE.md` → clean. No dangling bullets. All four workflow principles unchanged (byte-equal to the pre-edit state).

## Task 3: Update plugin.json + marketplace.json descriptions

**Status:** APPROVED.

**Summary.** Updated `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` to reflect the broadened scope of superRA and to mark the first public release.

- **Description** (both files, kept in sync): "Disciplined AI Research Assistant for economists: plan-implement-integrate workflow with implementer–reviewer pair, data-analysis discipline, and drift-test-verified integration."
- **Version bump:** `0.0.4.1` → `0.1.0`. User decision (2026-04-20): README + CLAUDE.md split complete, install flow modernized, workflow diagram added — milestone is meaningful enough to mark as first public release.
- **Keywords added** to `plugin.json`: `research-workflow`, `agent-orchestration` appended after existing entries (`skills`, `economics`, `data-analysis`, `reproducibility`, `research`, `workflows`).

**Verification.** `python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); json.load(open('.claude-plugin/marketplace.json')); print('ok')"` → `ok`.

## Task 4: Verify + modernize installation instructions

**Status:** APPROVED.

**Summary.** Confirmed the canonical remote is `https://github.com/FuZhiyu/superRA` (PUBLIC) — the stale `FuZhiyu/econ-superpowers` name in the crude draft is wrong. Confirmed Claude Code v2.1+ ships a `claude plugin` CLI with `plugin marketplace add <github-repo>` + `plugin install <plugin>@<marketplace>` — direct-from-remote install is supported, and the old clone-plus-`.claude/settings.json` flow is no longer the recommended path. Rewrote README §Installation accordingly: lead with `claude plugin marketplace add FuZhiyu/superRA` + `claude plugin install superRA@superRA-dev`; demote local-clone install to a "development or forking" subsection; add an update snippet (`claude plugin marketplace update superRA-dev && claude plugin update superRA`). Plugin name (`superRA`) and marketplace name (`superRA-dev`) confirmed from `.claude-plugin/marketplace.json`. For "Other Platforms", named the three repo-root entry files explicitly (`AGENTS.md` for Codex / Copilot CLI, `GEMINI.md` + `gemini-extension.json` for Gemini CLI) with direct links instead of pointing users at upstream Superpowers docs to guess. No other README sections were touched — Task 1b owns the rest.

**Verified (locally).** `claude --version` → `2.1.114`. `claude plugin marketplace list` shows `superRA-dev` currently registered from a local directory, confirming the marketplace name + plugin name pair. Install syntax (`claude plugin install superRA@superRA-dev`) matches Claude Code's `plugin@marketplace` convention as documented in `claude plugin install --help`.

**Out of scope, flagged.** `GEMINI.md` still `@`-includes `./skills/using-superpowers/SKILL.md` (upstream name) — the renamed skill in this repo is `using-superRA`. That is a stale import inside an entry file, not an Installation-section issue; deferred to the cross-reference sweep (Task 5) or the later AGENTS.md / GEMINI.md sweep the user dropped from this round.

## Task 5: Cross-reference + terminology sweep across all docs

**Status:** IMPLEMENTED.

**Files touched:** `CLAUDE.md`, `README.md`, `GEMINI.md`, `skills/integration-workflow/SKILL.md`

**Fixes by sweep category:**

- **Sweep 1 — "Changing Plans" residuals:** 0 fixes. All existing hits already read `§User Feedback and Changing Plans` correctly. No changes needed.
- **Sweep 2 — Stage 1/2/3 vocabulary:** 4 fixes in `skills/integration-workflow/SKILL.md`. Replaced "Stage 1 dev-log RESULTS.md" (frontmatter description) with "working RESULTS.md (Phase C)"; "Stage 1 scaffolds" (Phase D paragraph) with "in-progress scaffolds"; "Stage 2 RESULTS.md" (Phase C stop-point bullet, two dispatch task strings) with "Phase C RESULTS.md".
- **Sweep 3 — merge-workflow:** 0 fixes. Clean in README, CLAUDE.md, `skills/CATEGORIES.md`. Only appears in archived `docs/plans/` — expected historical record.
- **Sweep 4 — RELEASE-NOTES:** 0 fixes. Already clean in all scanned files (README, CLAUDE.md, CATEGORIES.md, all SKILL.md files).
- **Sweep 5 — VALIDATE/four-phase:** 1 fix in `CLAUDE.md` line 3: `PLAN → IMPLEMENT → VALIDATE → INTEGRATE` → `PLAN → IMPLEMENT → INTEGRATE`. README was already correct.
- **Extra item 6 — tagline Jupyter notebook:** 1 fix in `README.md` tagline bullet 3: removed "human-friendly Jupyter notebooks" (no standalone notebook skill ships; notebook guidance is buried inside `econ-data-analysis/references/notebook-format.md`) and replaced with "gated integration checklists" (maps to `refactor-and-integrate` in the Utility Skills table). The tagline's four utility-skill callouts now map 1:1 to entries in the Utility Skills table: technical reports in markdown (`report-in-markdown`), gated integration checklists (`refactor-and-integrate`), semantic branch merges (`semantic-merge`), data sync across git worktrees (`worktree-data-sync`).
- **Extra item 7 — GEMINI.md stale @-include:** 2 fixes in `GEMINI.md`: `./skills/using-superpowers/SKILL.md` → `./skills/using-superRA/SKILL.md`; `./skills/using-superpowers/references/gemini-tools.md` → `./skills/using-superRA/references/gemini-tools.md`. Both target paths verified to exist.

**Deferred items:** None — all task-spec items addressed.

## Task 6: Final human read-through + release tag decision

**Status:** Not started
