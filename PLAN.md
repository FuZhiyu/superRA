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
- [ ] Task 1 — README rewrite
- [ ] Task 2 — CLAUDE.md consolidation
- [ ] Task 3 — plugin.json + marketplace.json descriptions
- [ ] Task 4 — installation instructions verified
- [ ] Task 5 — RELEASE-NOTES initial-release cut
- [ ] Task 6 — skills/CATEGORIES.md + AGENTS.md + GEMINI.md sweep
- [ ] Task 7 — cross-reference + terminology sweep
- [ ] Task 8 — final human read-through and release tag decision
- [ ] Refactored (integration-workflow — N/A, docs-only branch)
- [ ] Docs finalized
- [ ] Merged

---

## Decisions

*(User decisions logged here as they occur. Empty at plan time.)*

---

## Task 1: Rewrite README.md as a careful user-facing doc

**Depends on:** *(none)*

**Objective.** Turn the crude README draft into a polished user-facing doc that preserves the user's chosen section structure and tone.

**Scope (sections to rewrite, in order):**

1. **Header + tagline.** One sentence that lands what superRA is. Followed by the three-bullet offering the user drafted (workflow / domain skills / utility skills) — tighten wording, keep the list shape.
2. **"Why superRA?"** Keep the bulleted pain-point framing the user chose. Polish grammar; tighten each bullet to one punchy line; drop the trailing "...". Follow with the one-paragraph resolution ("superRA brings discipline...") — rewrite for clarity, make the three-part structure (implementer-reviewer pair / domain skills / integration) explicit.
3. **"The Plan-Implement-Integrate Workflow" section.**
   - Replace the ASCII-block-with-TODO-comments with a rendered Mermaid diagram. The diagram shows PLAN → IMPLEMENT → INTEGRATE with: the implementer-reviewer loop inside IMPLEMENT, the 4-phase unfold inside INTEGRATE (A drift tests / B review-led sync + refactor / C doc finalization / D merge), an arrow from any phase back to PLAN labeled "scope change → §User Feedback and Changing Plans", and a terminal arrow from Phase D to "merged". Keep the diagram's information density below the prior full-architecture diagram — this is a user-facing overview, not the Workflow Map.
   - Drop the inline `<!-- -->` HTML comments once the diagram resolves them.
   - Keep the prose paragraph above the diagram that motivates iteration.
4. **"Key principles of the workflow"** (renamed from "Design Principles" to match the user's draft tone). Five bullets as the user drafted them — polish grammar and tighten. For principle 3, fill in the user's explicit TODO "Explain what does integration and semantic merge do" with one sentence each.
5. **"Domain Skills" section.** Replace the placeholder ("we ship data analysis skill") with a short table keyed from `skills/CATEGORIES.md` §Domain: one row for `econ-data-analysis` with its flagship-discipline one-liner. End with the roadmap list of planned verticals (theory / lit review / simulation / writing) — one line each, explicitly flagged as hooks, not commitments. This moves the "planned verticals" content back into the README where users expect it (it was deleted in the crude draft along with CLAUDE.md's Roadmap section).
6. **"Utility Skills" section.** Replace the placeholder with a short table: `report-in-markdown`, `refactor-and-integrate`, `worktree-data-sync`, `semantic-merge`, `handoff-doc`. One-line description per skill, keyed from `skills/CATEGORIES.md`. Apply `skill-creator` description discipline — each row says what + when.
7. **"Installation" section.** See Task 4; Task 1 leaves a `<!-- Task 4 -->` anchor here if Task 4 hasn't landed yet, otherwise inline the Task 4 output.
8. **Existing "Skill Inventory" table** (downstream of Installation, currently in main — need to check what survived the crude draft). Fold into the Domain Skills / Utility Skills tables above; do not repeat.
9. **"Hooks" table.** Keep as-is from the crude draft but verify the two rows (`ask-user-question-logger`, `exit-plan-mode`) match current `hooks/hooks.json`.
10. **"Plugin Design Philosophy" section** at the bottom of the crude draft. Move this entirely to CLAUDE.md (Task 2). Replace with a one-paragraph "Contributing" block that points at `CLAUDE.md` for design principles.
11. **"Upstream" + "License"** — restore the "Upstream" paragraph (credits Jesse Vincent / Superpowers) that the crude draft deleted. The License section should stay.

**Steps:**

- [ ] Read current `README.md` end-to-end; list every surviving stale reference in a scratchpad
- [ ] Draft the Mermaid workflow diagram in a fenced `mermaid` block; test by pasting into GitHub's markdown preview (or the `mermaid` CLI)
- [ ] Rewrite sections 1–11 in place, one heading at a time
- [ ] `rg -n "<!--|TODO|tbd|\.\.\." README.md` to confirm no placeholders survived
- [ ] Commit: `docs(readme): careful rewrite of user-facing README`

**Expected result.** A `README.md` a first-time user can read front-to-back in 5 minutes and know: what this is, when to use it, what skills ship, how to install, and where to read more.

**Review status:** not started
**Integration status:** *(docs-only; N/A)*

---

## Task 2: Consolidate CLAUDE.md as the developer / contributor doc

**Depends on:** Task 1 (so we know what moved out of README)

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

- [ ] Read current `CLAUDE.md` end-to-end
- [ ] Complete the "Skill Design Patterns" subsection per scope item 2
- [ ] Restore Roadmap section (copy from prior `main` version + trim redundant prose)
- [ ] Absorb Plugin Design Philosophy bullets into §Design Principles
- [ ] `rg -n "TODO|placeholder" CLAUDE.md` to confirm clean
- [ ] Commit: `docs(claude-md): consolidate developer-facing design doc`

**Review status:** not started
**Integration status:** *(N/A)*

---

## Task 3: Update plugin.json + marketplace.json descriptions

**Depends on:** Task 1 (README tagline is the source of truth for the plugin description)

**Objective.** Make the one-liner descriptions in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` match the README tagline and communicate what a user gets.

**Current state.** `plugin.json` description = "Super Research Assistant: data-first discipline, analysis planning, reproducibility, and rigorous data validation for economic research". This is accurate but data-analysis-centric; the repo has broadened to a domain-agnostic workflow + data-analysis flagship.

**Steps:**

- [ ] Draft the new one-liner: something like "Disciplined AI research assistant for economists: plan-implement-integrate workflow with implementer–reviewer pair, domain-aware data-analysis discipline, and semantic merges." Validate against the README tagline for consistency.
- [ ] Update `plugin.json` `description` + `keywords` (consider adding `research-workflow`, `agent-orchestration`)
- [ ] Update `marketplace.json` `description` to match
- [ ] Decide version: keep `0.0.4.1` (in-flight docs) or bump to `0.1.0` (first public release) — **this is a user decision, log via `AskUserQuestion` and record in §Decisions before editing**
- [ ] Commit: `plugin: user-facing description + version bump for initial release`

**Review status:** not started
**Integration status:** *(N/A)*

---

## Task 4: Verify + modernize installation instructions

**Depends on:** *(none)* — can run in parallel with Task 1

**Objective.** The crude draft left an inline TODO: "need to be updated. https://github.com/FuZhiyu/superRA. and we can directly install from the remote I think. research on the updated guide on how to install for claude code". Resolve it.

**Steps:**

- [ ] Verify the canonical remote URL — `git remote -v` and `gh repo view` to confirm whether it's `FuZhiyu/superRA` or `FuZhiyu/econ-superpowers`. Update the README clone URL accordingly.
- [ ] Research current Claude Code plugin install flow (as of 2026-04): does `claude-code` support `/plugin install <github-url>` directly, or is local-clone-plus-`.claude/settings.json` still required? Check Claude Code release notes / docs.
- [ ] Update the README Installation section with the current canonical flow. If direct install from remote now works, lead with it and demote the clone-plus-settings flow to "for development / forking".
- [ ] Verify the "Other Platforms" subsection (Copilot CLI, Gemini CLI, Codex) — check whether `AGENTS.md` + `GEMINI.md` + `gemini-extension.json` are still the right entry points
- [ ] Commit: `docs(readme): modernize installation instructions`

**Review status:** not started
**Integration status:** *(N/A)*

---

## Task 5: Cut initial release section in RELEASE-NOTES.md

**Depends on:** Task 3 (version number)

**Objective.** Consolidate the three pending `Unreleased` sections into a dated release header matching the Task 3 version choice.

**Steps:**

- [ ] Read the three `Unreleased` sections end-to-end
- [ ] Replace their three headers with a single dated section: `## YYYY-MM-DD — v0.1.0: initial public release` (or whatever version Task 3 picks)
- [ ] Within that section, reorganize the bullets under subheads by theme: Workflow architecture / Integration refactor / Agent orchestration / Planning & re-entry / Infrastructure. Preserve the full detail — developers reading `RELEASE-NOTES` want the change log.
- [ ] Add a top-of-file "About this release" paragraph (2–3 sentences) framing v0.1.0 as the first public release — what stabilized, what's still experimental.
- [ ] Commit: `docs(release-notes): cut v0.1.0 initial release section`

**Review status:** not started
**Integration status:** *(N/A)*

---

## Task 6: Sync skills/CATEGORIES.md, AGENTS.md, GEMINI.md

**Depends on:** Task 1, Task 2

**Objective.** Keep ancillary entry-point docs aligned with the rewritten README + CLAUDE.md.

**Steps:**

- [ ] `skills/CATEGORIES.md` — verify every skill row still has the right category and one-liner after Task 1's Domain/Utility tables. Any description I tighten in the README, back-port here (or vice-versa — pick one as the source of truth; I lean toward CATEGORIES.md as the source since it's the index).
- [ ] `AGENTS.md` (Copilot CLI entry point) — read current content; update any stale skill names or category references
- [ ] `GEMINI.md` + `gemini-extension.json` — same check for Gemini CLI
- [ ] Commit: `docs: sync CATEGORIES + platform entry points with new README/CLAUDE.md`

**Review status:** not started
**Integration status:** *(N/A)*

---

## Task 7: Cross-reference + terminology sweep across all docs

**Depends on:** Tasks 1, 2, 5, 6

**Objective.** Catch any stale cross-references that survived the individual rewrites.

**Steps:**

- [ ] `rg -n "Changing Plans" -- '!docs/plans/' '!RELEASE-NOTES.md'` — every hit must read `User Feedback and Changing Plans` unless it's a historical release-note line
- [ ] `rg -n "Stage 1|Stage 2|Stage 3" skills/integration-workflow/ README.md CLAUDE.md` — post-unified-integration, the vocabulary is Phases A–D in user-facing docs. Release notes keep their historical wording.
- [ ] `rg -n "merge-workflow"` — must not appear in README, CLAUDE.md, skills/CATEGORIES.md, AGENTS.md, GEMINI.md. It's legitimately in RELEASE-NOTES as a historical removal.
- [ ] `rg -n "VALIDATE|four-phase"` across README + CLAUDE.md — the user's crude draft renames to three-phase (PLAN → IMPLEMENT → INTEGRATE) with VALIDATE folded into IMPLEMENT's reviewer loop. Every phase-list in user-facing docs must match. CLAUDE.md may still say four-phase if it's describing the internal workflow skills' decomposition; pick one framing and use it consistently.
- [ ] `rg -n "\[.*\]\(.*\.md\)"` spot-check markdown links for broken paths after any file renames
- [ ] Commit: `docs: cross-reference + terminology sweep`

**Review status:** not started
**Integration status:** *(N/A)*

---

## Task 8: Final human read-through + release tag decision

**Depends on:** Tasks 1–7

**Objective.** Before tagging a release, present the final doc set to the user for read-through. Get explicit approval on: README clarity for a first-time user, CLAUDE.md clarity for a contributor, version number, release tag timing.

**Steps:**

- [ ] Render README.md in GitHub preview (or `gh`-based preview) to confirm Mermaid diagram renders
- [ ] Summarize diffs across the seven commits for the user
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
