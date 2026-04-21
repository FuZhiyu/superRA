# superRA Codex Compatibility Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all `PLAN.md` / `RESULTS.md` editing. Use `superRA:codex-superra-setup` when changing named Codex agent installation mechanics. For skill-description guidance, follow the contributor rules in `CLAUDE.md` and the upstream Superpowers docs.

**Objective:** Add coherent Codex support to superRA without regressing any Claude-facing workflow behavior.

**Methodology:** Use an additive compatibility layer: keep canonical behavior in root `skills/` and `agents/`, package shared skills through Codex plugin surfaces, install named Codex agents through `.codex/agents/` or `~/.codex/agents/`, and isolate harness-specific instructions in adapter references rather than duplicating workflow logic.

**Data Inventory:** N/A — plugin / workflow implementation task, no empirical dataset.

**Conventions:** Preserve one source of truth per concern. Canonical workflow content stays in root `skills/` and `agents/`; Codex-facing surfaces are manifests, symlinks, generated artifacts, and install docs layered around that canonical content.

**Output:** `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.agents/skills/`, `.codex/agents/`, `skills/codex-superra-setup/`, updated Codex docs, updated shared harness references, and updated structural tests.

**Expected Results / Hypotheses:** Codex can discover superRA skills from the repo and from a local plugin install, named agents `superra_implementer` and `superra_reviewer` can be installed globally or project-scoped, and Claude behavior remains unchanged.

**Sensitivity Analysis:** Validate SKILL frontmatter compatibility, generated-agent sync, local plugin metadata, and structural invariants so Codex-specific breakage is caught before merge.

**Pipeline:** `python3 skills/codex-superra-setup/scripts/test_sync_codex_agents.py`; `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check`; `bash tests/structural-invariants.sh`

---

## Project Conventions

Walked at planning time (2026-04-17). Re-walk on-demand only.

### Repo root

- `/CLAUDE.md` (HEAD in current worktree): preserve the four workflow principles, keep one source of truth per concern, do not weaken Claude behavior while adding Codex support, and keep public docs in sync when the plugin surface changes.
- `/AGENTS.md` and `/AGENT.md`: symlink aliases to `/CLAUDE.md`; contributor guidance stays canonical in one file.
- `/README.md`: public-facing skill inventory and install guidance must match the actual repository surface.

### Module-level docs walked

- `skills/using-superRA/SKILL.md`: harness-specific behavior belongs in adapter references rather than in forked workflow copies; skill descriptions stay concise trigger metadata rather than workflow summaries.
- `tests/structural-invariants.sh`: when a new plugin surface or metadata rule becomes load-bearing, encode it as an invariant so regressions fail fast.

### Not walked (not needed for this retroactive handoff)

- `docs/plans/`, `docs/superpowers/`, and non-structural test fixtures — not needed to reconstruct the current implementation work.

## Decisions

> **User decision (2026-04-17):** Codex support must not affect any Claude Code behavior.
> **Question asked:** Should Codex compatibility be additive, or may it change existing Claude-facing plugin behavior?
> **Rationale (if given):** Do not affect any function of the plugin in Claude Code.

> **User decision (2026-04-17):** Keep the canonical skills shared and use harness-specific references instead of maintaining separate Codex workflow copies.
> **Question asked:** Should Codex compatibility use wrappers everywhere, or should the shared instructions stay canonical with harness-specific adapters?
> **Rationale (if given):** Skills should be harness-neutral where possible, with harness-specific reference files.

> **User decision (2026-04-17):** Support named custom Codex agents and install them through setup rather than relying on plugin-managed agent installation.
> **Question asked:** How should Codex custom agents be delivered for real work across other repos?
> **Rationale (if given):** The setup should support real named agents, not only generic built-in roles.

> **User decision (2026-04-17):** The setup skill is named `codex-superra-setup` and must support both project-scoped and global installation.
> **Question asked:** What should the setup skill be called and where should it install the named agents?
> **Rationale (if given):** Normal use will happen in repos other than this one, but project-scoped setup is still needed for local testing.

> **User decision (2026-04-17):** Add `AGENT.md` as a symlink alias to `CLAUDE.md` in this repo and record the Codex design there as well.
> **Question asked:** Should the repo expose a Codex-facing `AGENT.md` alias in addition to the existing `AGENTS.md` symlink?
> **Rationale (if given):** Yes.

> **User decision (2026-04-17):** Create `PLAN.md` and `RESULTS.md` retroactively for the Codex compatibility work already completed in this session.
> **Question asked:** Should the current implementation work be backfilled into handoff docs after the fact?
> **Rationale (if given):** Yes.

> **User decision (2026-04-17):** Proceed from the approved execution work into `integration-workflow`.
> **Question asked:** After the implementation review, should this branch move into pre-merge integration?
> **Rationale (if given):** "integration workflow then"

> **User decision (2026-04-17):** Protect this branch with a new Claude/Codex compatibility check script, not only the Codex-specific structural assertions.
> **Question asked:** Which drift guards should protect the Codex compatibility work during integration?
> **Rationale (if given):** "we need to create a compatibility check script to make sure the changes are compatible to both codex and claude code"

> **User decision (2026-04-19):** Update `codex-adaption` from `main` with a semantic merge, not a rebase, and fold the outstanding Task 3 cleanup into the same pass.
> **Question asked:** What history shape and integration scope should the branch update use?
> **Rationale (if given):** Merge `main` and leave the branch current and merge-ready afterward.

> **User decision (2026-04-19):** Dispose of `PLAN.md` by moving it alongside the mature results record under `docs/plans/`.
> **Question asked:** How should the Codex compatibility plan be archived after the final handoff cleanup?
> **Rationale (if given):** Keep the prescriptive handoff record beside `docs/plans/2026-04-17-codex-compatibility-results.md`.

> **User decision (2026-04-20):** Minimum-net-diff integration policy for harness-specific content. Short harness-specific comments stay inline in the main file; new harness-specific reference files are created only when the instructions are particularly long. Claude-specific tool names may be used inline as long as other harnesses can understand them; avoid hard-coded tool-call signatures.
> **Question asked:** How aggressively should harness-specific content be extracted into separate adapter references during this Round 3 integration sync?
> **Rationale (if given):** Take main verbatim wherever it does not collide with Codex-essential additions; do not over-extract harness-neutral surfaces.

> **User decision (2026-04-20):** Inlined harness-compat description-length check uses 1024 chars (Agent Skills spec limit), not the original 500. Reference: https://agentskills.io/specification — `description` max 1024; `compatibility` max 500. The original 500 in `3e9f1c8` confused the two fields.
> **Question asked:** Should the inlined `tests/check-harness-compatibility.sh` length cap stay at 500 (failing on 7 main-side files), drop the cap entirely, or raise to the spec's actual limit?
> **Rationale (if given):** User pointed at the official Agent Skills specification (https://agentskills.io/specification) confirming 1024 is the actual limit; the 500 had no documented basis.

## Integration Intent

> **Main-side change (2026-04-20):** `origin/main` advanced past the last branch sync (`af3eae1`) with three commits — `a635dac` drops `tests/structural-invariants.sh`, `242519e` (PR #12) folds in a large skill-surface simplification (descriptions tightened, `using-superRA` body trimmed of §Universal Principles / §Composable Design / §Harness Adapters / §Tool Discipline / §Semantic Merge / §Instruction Priority, manifest collapses to 4 generic rows, `agents/implementer.md` + `agents/reviewer.md` rewritten to point at the new manifest shape, `skills/planning-workflow` + `skills/integration-workflow` + `skills/handoff-doc` + `skills/agent-orchestration` + `skills/refactor-and-integrate` references all simplified accordingly), and `2431e93` lowercases the master skill `name:` to `using-superra` everywhere it is referenced. Two earlier main-side renames are also still unabsorbed on the branch: `5c8b93a` renames `skills/execution-workflow/` → `skills/implementation-workflow/`, and `f58cb58` deletes `skills/merge-workflow/` (already absorbed). Affects Tasks 1, 2, 3.
> **Adaptation needed:** Re-merge `origin/main` into `codex-adaption` per `superRA:semantic-merge`, taking main verbatim on every shared file that does not collide with a Codex-essential additive surface. Concrete carry-over work: (a) absorb the `execution-workflow` → `implementation-workflow` rename across `skills/`, `.agents/skills/`, `hooks/`, contributor docs, plus the rewritten `skills/implementation-workflow/SKILL.md`; (b) adopt the lowercase `using-superra` skill `name:` and update every `superRA:using-superRA` pointer to `superRA:using-superra` while keeping the directory at `skills/using-superRA/` (main keeps the directory case); (c) replace branch versions of the simplified skill bodies (`using-superRA/SKILL.md`, `agents/implementer.md`, `agents/reviewer.md`, `agent-orchestration/SKILL.md`, `handoff-doc/SKILL.md`, `planning-workflow/SKILL.md`, `integration-workflow/SKILL.md`, `refactor-and-integrate/SKILL.md` + references, `econ-data-analysis/SKILL.md`, `report-in-markdown/SKILL.md` + references, `semantic-merge/SKILL.md`, `worktree-data-sync/SKILL.md`) with main's, then re-thread the Codex-essential additive content (Codex Harness Adapter pointer to `references/codex-tools.md`, `codex-superra-setup` row in the Skill Inventory, the Codex design subsection in `CLAUDE.md`, the harness-compat bullet) — minimum-net-diff per the 2026-04-20 policy, no new adapter-reference files created; (d) drop `tests/structural-invariants.sh` and fold its two Codex-essential checks (frontmatter ≤ 500 chars; `.agents/skills/` symlink coverage) into `tests/check-harness-compatibility.sh` so the harness guard remains the sole runtime check; (e) regenerate `.codex/agents/superra_implementer.toml` and `.codex/agents/superra_reviewer.toml` from the rewritten `agents/*.md` via `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`; (f) refresh the `.agents/skills/execution-workflow` symlink to `.agents/skills/implementation-workflow`. After the merge lands, re-run `bash tests/check-harness-compatibility.sh` end-to-end and update Task 3 Step 3 (mature) to reflect the new HEAD.

### Task 1: Codex Plugin and Named-Agent Surfaces
**Review status:** APPROVED
**Integration status:** IMPLEMENTED

**Files affected:** `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.agents/skills/*`, `.codex/agents/*`, `AGENT.md`, `skills/codex-superra-setup/*`, `skills/using-superRA/SKILL.md`, `skills/using-superRA/references/codex-tools.md`, `skills/using-superRA/references/claude-tools.md`, `.codex/INSTALL.md`, `docs/README.codex.md`, `README.md`, `CLAUDE.md`, `skills/CATEGORIES.md`

**Input:** Existing canonical `skills/` and `agents/`, official Codex plugin/skills/subagents docs, and the user decisions recorded above.

**Output:** Local Codex plugin install surface, repo-scoped skill discovery, named custom agent generation/install path, and updated Codex-facing documentation.

- [x] **Step 1: Add Codex plugin and marketplace surfaces.** Added `.codex-plugin/plugin.json` pointing at `./skills/` and `.agents/plugins/marketplace.json` pointing at the repo root so Codex can install the plugin locally from this checkout.
- [x] **Step 2: Expose canonical skills and contributor instructions to Codex.** Created `.agents/skills/` symlinks back to canonical `skills/*` and added `AGENT.md -> CLAUDE.md` alongside the existing `AGENTS.md` symlink.
- [x] **Step 3: Add named-agent generation and installation.** Added `skills/codex-superra-setup/`, the `sync_codex_agents.py` generator / installer, generated `.codex/agents/superra_implementer.toml` and `.codex/agents/superra_reviewer.toml`, and tests for the install/update path.
- [x] **Step 4: Update shared harness references and install docs.** Reworked Codex docs and `using-superRA` adapter references so Codex uses plugin skills plus named custom agents instead of the older prompt-wrapping workaround.

### Task 2: Codex Metadata Cleanup and Validation
**Review status:** APPROVED
**Integration status:** IMPLEMENTED

**Files affected:** `skills/*/SKILL.md` frontmatter across the skill tree, `tests/structural-invariants.sh`

**Input:** Codex skill-loading validation errors from the local repo test, plus contributor guidance on concise trigger descriptions from `CLAUDE.md` and the upstream Superpowers docs.

**Output:** Codex-compatible skill frontmatter across the entire repo and a regression guard for YAML parseability and description length.

- [x] **Step 1: Fix invalid frontmatter.** Repaired the SKILL metadata issues Codex reported: malformed YAML description lines and the overlong `econ-data-analysis` description.
- [x] **Step 2: Shorten the entire skill surface.** Rewrote skill descriptions to trigger-only metadata instead of mini-specs, following the repo contributor guidance and upstream Superpowers skill-writing guidance.
- [x] **Step 3: Add a structural guard.** Extended `tests/structural-invariants.sh` so every `skills/*/SKILL.md` frontmatter must parse and every description must stay at or below 500 characters.
- [x] **Step 4: Verify the retrofitted surface.** Re-ran the Codex-focused frontmatter check, generated-agent tests, sync check, and full structural invariants suite after the metadata cleanup.

### Task 3: Pre-Merge Integration and Merge Readiness

**Review status:** APPROVED
**Integration status:** IMPLEMENTED

**Files affected:** `PLAN.md`, `docs/plans/2026-04-17-codex-compatibility-results.md`, `tests/check-harness-compatibility.sh`, `CLAUDE.md`, `README.md`, `skills/using-superRA/references/main-agent.md`, and any docs or plugin surfaces flagged by the integration pass

**Input:** Approved Codex compatibility implementation (`3e9f1c8`) plus the approved execution-stage record in `docs/plans/2026-04-17-codex-compatibility-results.md`

**Output:** Confirmed drift-test coverage for the Codex support surface, a top-level Claude/Codex compatibility guard, the accepted doc-audit fixes, an archived Codex compatibility handoff pair under `docs/plans/`, and a branch current with `main`

- [x] **Step 1: Confirm drift-test coverage.** User chose a new top-level compatibility check as the Stage 1 guard: add a Claude/Codex compatibility script that validates both harness surfaces, then keep `tests/structural-invariants.sh`, `skills/codex-superra-setup/scripts/test_sync_codex_agents.py`, and `skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` as the concrete checks it runs.
- [x] **Step 2: Run the integration review / fix loop.** Added `tests/check-harness-compatibility.sh` as the top-level harness guard, then ran an integration pass over the new surface. The only accepted finding was a missing contributor-facing instruction to run the new guard for harness-surface changes, fixed in `CLAUDE.md`. The compatibility script reran cleanly afterward.
- [x] **Step 3: Finalize handoff for merge.** Re-merged `origin/main` into `codex-adaption` (Round 3, minimum-net-diff per the 2026-04-20 §Decisions entry) absorbing main commits `a635dac` (drop `tests/structural-invariants.sh`), `242519e` (PR #12 skill-surface simplification, including `5c8b93a` execution-workflow → implementation-workflow rename), and `2431e93` (lowercase `using-superra`). Took main verbatim on every shared file and surgically re-threaded only the Codex-essential additive surfaces: §Codex design subsection + AGENT.md alias note in `CLAUDE.md` (the harness-compat contributor bullet was intentionally dropped per user manual override of `CLAUDE.md`), the Codex install bullet in `README.md`, the `codex-superra-setup` row + harness adapter pointer in `skills/using-superRA/SKILL.md`, the `execution-workflow` → `implementation-workflow` rename in `skills/using-superRA/references/codex-tools.md`, and the `.agents/skills/execution-workflow` → `.agents/skills/implementation-workflow` symlink refresh. Folded the two Codex-essential checks from the dropped `tests/structural-invariants.sh` (frontmatter parses + ≤500-char description; `.agents/skills/` symlink coverage) inline into `tests/check-harness-compatibility.sh` along with the finding-9 lowercase-`name:` assertion, and removed the now-broken `bash tests/structural-invariants.sh` call. Regenerated `.codex/agents/superra_*.toml` from the rewritten `agents/*.md` via `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`. Archived `docs/plans/2026-04-19-*.md` left untouched per advisory finding 12. The branch is current with `main` and merge-ready pending the integration-reviewer APPROVE.

> **Integration review notes (Round 3, 2026-04-20):**
>
> Scope: `92a685b..eece04c` (branch side, 17 commits) and `92a685b..origin/main` (main side, 70 commits with PR #12 + lowercase rename + structural-invariants drop). The branch's last sync (`af3eae1`) predates main's `a635dac`, `242519e` (PR #12), and `2431e93`. Findings cluster around the carry-over surfaces named in §Integration Intent.
>
> 1. [BLOCKING] **Stale rename on the branch — `execution-workflow` → `implementation-workflow`.** Main commit `5c8b93a` renamed `skills/execution-workflow/` to `skills/implementation-workflow/` and updated every reference across `skills/`, `agents/`, `hooks/`, and contributor docs in one atomic commit. The branch still carries `skills/execution-workflow/SKILL.md` (266 lines net-present in `git diff origin/main..eece04c`) and is missing `skills/implementation-workflow/SKILL.md` (204 lines net-absent). 27 files on the branch still mention `execution-workflow` (SKILL bodies, references, hooks, plans). Adopt main's rename verbatim — `git rm -r skills/execution-workflow/`, take main's `skills/implementation-workflow/SKILL.md`, sweep every `execution-workflow` token in shared content to `implementation-workflow`. The Codex-additive mention in `skills/using-superRA/references/codex-tools.md:52` ("`superRA:execution-workflow` Step 4 Option 4") must be updated to the new name in the same pass.
>    → implemented: absorbed via merge of `origin/main` (commit `5c8b93a` carried into the branch); `skills/execution-workflow/` removed, `skills/implementation-workflow/SKILL.md` taken from main verbatim, all live-content `execution-workflow` references swept including `skills/using-superRA/references/codex-tools.md:55` (`superRA:execution-workflow` → `superRA:implementation-workflow`).
>
> 2. [BLOCKING] **Stale `using-superRA` skill name — main lowercased `name:` to `using-superra` in commit `2431e93`.** The directory stays `skills/using-superRA/` (case preserved on main), but the frontmatter `name:` field and every `superRA:using-superRA` pointer are lowercased to `superRA:using-superra` across `skills/`, `agents/`, `CLAUDE.md`, `README.md`, `GEMINI.md`, and the `docs/plans/` history. The branch still has `name: using-superRA` and 35 files mentioning the mixed-case form. Sweep all shared-content references to `superRA:using-superra`, including the regenerated `.codex/agents/superra_*.toml` (which inherits from `agents/*.md`).
>    → implemented: absorbed via merge of `origin/main` (commit `2431e93`); frontmatter `name:` is `using-superra` (`skills/using-superRA/SKILL.md:2`); all live-content pointers lowercased; `.codex/agents/superra_*.toml` regenerated from the rewritten `agents/*.md` and now carry `superRA:using-superra`.
>
> 3. [BLOCKING] **Replace branch versions of the simplified skill bodies with main verbatim.** PR #12 (`242519e` and predecessors `c0d7a69`, `7e0ba6f`, `a56539f`, `e3f5821`, `bc7a5dc`, `1c25b13`) is a substantive simplification pass: descriptions tightened to triggers; `using-superRA/SKILL.md` body trimmed of §Universal Principles, §Composable Design, §Harness Adapters, §Tool Discipline, §Semantic Merge, §Instruction Priority; manifest collapses to 4 generic stage rows (`implementation`, `drift-test`, `integration`, `documentation`) plus a separate domain-overrides table; `agents/implementer.md` + `agents/reviewer.md` rewritten to reference the new manifest shape (skills only, no per-stage references column); `agent-orchestration/SKILL.md`, `handoff-doc/SKILL.md`, `planning-workflow/SKILL.md`, `integration-workflow/SKILL.md`, `refactor-and-integrate/SKILL.md` + references, `econ-data-analysis/SKILL.md`, `report-in-markdown/SKILL.md` + references, `semantic-merge/SKILL.md`, `worktree-data-sync/SKILL.md` all simplified concurrently to remove duplicated discipline. Take main verbatim on every shared file (no methodology call here — main is the source of truth and the branch is downstream). After the merge, the only branch-side delta on `using-superRA/SKILL.md` should be the Codex-essential additive content: (a) restore the `codex-superra-setup` row in the §Skill Inventory table, (b) restore one-line pointers to the harness adapters (`references/codex-tools.md`, `references/claude-tools.md`) so the §Skill-Load Manifest agents know they exist. No new adapter-reference files (per the 2026-04-20 harness-content policy).
>    → implemented: every shared skill body (`skills/using-superRA/SKILL.md`, `agents/implementer.md`, `agents/reviewer.md`, `skills/agent-orchestration/SKILL.md`, `skills/handoff-doc/SKILL.md`, `skills/planning-workflow/SKILL.md`, `skills/integration-workflow/SKILL.md`, `skills/refactor-and-integrate/SKILL.md` + references, `skills/econ-data-analysis/SKILL.md`, `skills/report-in-markdown/SKILL.md` + references, `skills/semantic-merge/SKILL.md`, `skills/worktree-data-sync/SKILL.md`) taken verbatim from main via the merge; `skills/using-superRA/SKILL.md` re-threaded with the `codex-superra-setup` Utility row (line 51) and the one-line "Harness adapters" pointer to `codex-tools.md` / `claude-tools.md` (line 55) — no new adapter-reference files created.
>
> 4. [BLOCKING] **Drop `tests/structural-invariants.sh` and fold its two Codex-essential checks into `tests/check-harness-compatibility.sh`.** Main commit `a635dac` deleted `tests/structural-invariants.sh` with the rationale "tracked file-level shape rather than behavior; not a real test of skill correctness." The branch still keeps it (646 lines net-present vs main) and `tests/check-harness-compatibility.sh:60` still calls it. Two of the file's invariants are Codex-essential and must survive: §6b (frontmatter parses + `description ≤ 500` chars — Codex's hard validation limit) and §21c (`.agents/skills/*` symlink coverage — Codex's repo-local discovery surface). Remaining invariants (§20 `using-superRA` body shape, §21 stage-table presence, §6 manifest row count, README §Workflow Map check, etc.) are all stale relative to main's simplification — the §Workflow Map test was already failing pre-merge per `af3eae1`'s commit message, and main's manifest is now 4 rows not 6. Inline the two surviving checks directly inside `tests/check-harness-compatibility.sh` (Python or bash, ≤30 lines) and `git rm tests/structural-invariants.sh`. Remove the `bash tests/structural-invariants.sh` call at line 60 of `check-harness-compatibility.sh`. The commit-message rationale should mirror main's — keep only behavior-bearing checks.
>    → implemented: `tests/structural-invariants.sh` deletion absorbed via merge (main commit `a635dac`); the bash call at the old line 60 of `tests/check-harness-compatibility.sh` was removed and replaced with a new "Codex skill packaging invariants" Python section (~50 lines) that inlines (i) frontmatter-parses + `description ≤ 1024` chars across `skills/*/SKILL.md` and (ii) `.agents/skills/` symlink coverage of every `skills/<name>/`.
>    → orchestrator: the original 500 in `3e9f1c8` was a confusion between the Agent Skills spec's `description` limit (1024) and `compatibility` limit (500) — see https://agentskills.io/specification. Threshold raised to 1024; all 7 surfaced descriptions are under 1024 (max is `integration-workflow` at 1009). Decision logged in §Decisions 2026-04-20.
>
> 5. [BLOCKING] **Refresh `.agents/skills/execution-workflow` symlink to `.agents/skills/implementation-workflow`.** The symlink at `.agents/skills/execution-workflow -> ../../skills/execution-workflow` will dangle once Finding 1 lands. Replace with `.agents/skills/implementation-workflow -> ../../skills/implementation-workflow` (`git rm` the old, `ln -s` the new). The new symlink coverage will be verified by the inlined check from Finding 4.
>    → implemented: `.agents/skills/execution-workflow` removed and replaced with `.agents/skills/implementation-workflow -> ../../skills/implementation-workflow`; the new check from finding 4 confirms full symlink coverage of `skills/`.
>
> 6. [BLOCKING] **Regenerate the Codex agent toml files from the rewritten `agents/*.md`.** Main rewrote `agents/implementer.md` (42-line diff) and `agents/reviewer.md` (36-line diff) to thread the new manifest shape and the lowercased `using-superra` references. Once those land via the merge, run `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` so `.codex/agents/superra_implementer.toml` and `.codex/agents/superra_reviewer.toml` reflect the new canonical bodies. Verify with the `--check` mode at the end (already invoked by `check-harness-compatibility.sh`).
>    → implemented: ran `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`; `.codex/agents/superra_implementer.toml` and `.codex/agents/superra_reviewer.toml` regenerated; `--check` mode passes.
>
> 7. [BLOCKING] **Re-thread the Codex-essential additive content in `CLAUDE.md` after taking main's body.** Main's `CLAUDE.md` dropped the `tests/check-harness-compatibility.sh` bullet under §Working in This Repo, the §Codex design subsection under §Design Principles, and the lowercased pointers. Take main's body verbatim, then surgically re-add: (a) the `tests/check-harness-compatibility.sh` bullet (line 14 of branch's current CLAUDE.md) — Codex-essential per the §Decisions log entry of 2026-04-17 ("compatibility check script") — keep wording short and inline; (b) the §Codex design subsection under §Design Principles — keep verbatim from branch HEAD as it documents the Codex split (canonical instructions shared, harness adapters, `.agents/skills/`, named agents in `.codex/agents/`); (c) the `AGENT.md` alias note under §Codex contributor docs. Sweep `using-superRA` → `using-superra` and `execution-workflow` → `implementation-workflow` after the verbatim adoption.
>    → orchestrator: 7a (harness-compat contributor bullet) rejected — user manually re-edited `CLAUDE.md` to omit the bullet, accepted as override.
>    → implemented: 7b §Codex design subsection re-added under §Design Principles between Skill Design Patterns and DRY (`CLAUDE.md:65-73`); 7c AGENT.md alias note included as the last bullet of that subsection (`CLAUDE.md:73`). 7a left absent per orchestrator override above. Lowercase / rename sweeps already present from main's verbatim body.
>
> 8. [BLOCKING] **Re-thread the Codex-essential additive content in `README.md` after taking main's body.** Net diff of `README.md` is `+7` lines (branch) — most of those are Codex install bullets. Take main's body verbatim, then re-add the Codex install pointer (the bullet pointing at `docs/README.codex.md` and `.codex/INSTALL.md`) and the `codex-superra-setup` row in the public skill table. Lowercase / rename sweeps as in Finding 7.
>    → implemented: Codex install bullet re-threaded in `README.md:136` (split out from the prior "Codex / Copilot CLI" combined line) pointing at `codex-superra-setup`, `docs/README.codex.md`, and `.codex/INSTALL.md`. No separate `codex-superra-setup` row was added to the §Utility Skills table on main — kept minimum-net-diff; the install bullet itself names the setup skill so a reader can find it. Lowercase / rename sweeps already present from main's verbatim body.
>
> 9. [BLOCKING] **Update `tests/check-harness-compatibility.sh` shared-adapters check to handle the lowercased skill name.** Currently lines 50–53 assert the existence of `skills/using-superRA/references/claude-tools.md` and `codex-tools.md` — those file paths are still correct (directory case preserved on main) so no change required there. But once `using-superRA/SKILL.md` adopts main's body, also assert that the frontmatter `name:` value is `using-superra` (so the lowercase-rename invariant is locked in by the harness guard, not by the dropped structural-invariants script). One-line Python check inside the existing "Shared harness adapters" section is sufficient.
>    → implemented: added a Python heredoc inside the §Shared harness adapters section of `tests/check-harness-compatibility.sh` that asserts the `using-superRA/SKILL.md` frontmatter `name:` value is `using-superra`; passes.
>
> 10. [BLOCKING] **Update Task 3 Step 3 to describe the new sync round.** After the carry-over lands, Task 3 Step 3 currently reads "semantically merged the latest `main` into `codex-adaption`" — that referred to the `af3eae1` round. Rewrite in place (no "Update:" or "Previously..." framing per the inline-edit rule) to describe the Round 3 sync: which main commits were absorbed (`a635dac`, `242519e`, `2431e93`), which Codex-essential additive surfaces were re-threaded, and the final HEAD SHA after Phase B APPROVE. The `RESULTS.md` Reproducibility line ("Reproduce this state from commit `60f50d009c71714e8dc75acc1025ab57d45f0a65`") also needs the new HEAD SHA in the same task block; flag for the Phase C doc-writer pass — not in scope for this Phase B fix loop.
>     → implemented: Task 3 Step 3 rewritten in place to describe the Round 3 sync, naming the absorbed main commits (`a635dac`, `242519e`, `2431e93`) and the re-threaded Codex-essential additive surfaces. The post-APPROVE HEAD SHA cannot be filled until the integration reviewer APPROVES; left as a Phase C carry-forward (the same RESULTS.md Reproducibility-line update flagged in the finding).
>
> 11. [ADVISORY] **`tests/check-harness-compatibility.sh` line 41 hard-codes `plugin["name"] == "superra"`.** Already correct — the Codex plugin manifest uses lowercase `superra` and the `.claude-plugin/plugin.json` uses mixed-case `superRA` (line 26). The two casings are intentional (Claude marketplace expects mixed-case display name; Codex requires lowercase). No action — flagging only because Finding 2 sweeps `using-superRA` → `using-superra` and a careless sed could touch these too.
>     → implemented: no-op; verified the dual-cased `superra` (Codex) / `superRA` (Claude) plugin manifest names are preserved by `tests/check-harness-compatibility.sh:26` and `:41` per the dispatch advisory.
>
> 12. [ADVISORY] **Non-Codex-essential stale references in archived `docs/plans/` files.** `docs/plans/2026-04-19-*.md` and earlier-dated archives still mention `execution-workflow` / `using-superRA`. These are historical records of completed work, not live skill content; per the inline-edit rule they describe state at their authoring date. Leave untouched. Only sweep live skill content + contributor docs.
>     → implemented: no-op; conflict resolution for the four `docs/plans/2026-04-19-*.md` files took the branch (HEAD) side, leaving the mixed-case `using-superRA` / `execution-workflow` references intact per the advisory.
>
> 13. [ADVISORY] **Pre-existing `## Workflow Map` test failure in `tests/structural-invariants.sh`.** Noted in `af3eae1`'s commit message ("unrelated to this merge"). Becomes moot once Finding 4 lands — the test goes away with the file.
>     → implemented: no-op; moot — the failing test was inside `tests/structural-invariants.sh`, which was deleted by main commit `a635dac` (absorbed via the Round 3 merge).
