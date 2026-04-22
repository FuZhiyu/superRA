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

### Task 1: Codex Plugin and Named-Agent Surfaces
**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:** `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `.agents/skills/*`, `.codex/agents/*`, `AGENT.md`, `skills/codex-superra-setup/*`, `skills/using-superRA/SKILL.md`, `skills/using-superRA/references/codex-tools.md`, `skills/using-superRA/references/claude-tools.md`, `.codex/INSTALL.md`, `docs/README.codex.md`, `README.md`, `CLAUDE.md`, `skills/CATEGORIES.md`

**Input:** Existing canonical `skills/` and `agents/`, official Codex plugin/skills/subagents docs, and the user decisions recorded above.

**Output:** Local Codex plugin install surface, repo-scoped skill discovery, named custom agent generation/install path, and updated Codex-facing documentation.

- [x] **Step 1: Add Codex plugin and marketplace surfaces.** Added `.codex-plugin/plugin.json` pointing at `./skills/` and `.agents/plugins/marketplace.json` pointing at the repo root so Codex can install the plugin locally from this checkout.
- [x] **Step 2: Expose canonical skills and contributor instructions to Codex.** Created `.agents/skills/` symlinks back to canonical `skills/*` and added `AGENT.md -> CLAUDE.md` alongside the existing `AGENTS.md` symlink.
- [x] **Step 3: Add named-agent generation and installation.** Added `skills/codex-superra-setup/`, the `sync_codex_agents.py` generator / installer, generated `.codex/agents/superra_implementer.toml` and `.codex/agents/superra_reviewer.toml`, and tests for the install/update path.
- [x] **Step 4: Update shared harness references and install docs.** Reworked Codex docs and `using-superRA` adapter references so Codex uses plugin skills plus named custom agents instead of the older prompt-wrapping workaround.

### Task 2: Codex Metadata Cleanup and Validation
**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:** `skills/*/SKILL.md` frontmatter across the skill tree, `tests/structural-invariants.sh`

**Input:** Codex skill-loading validation errors from the local repo test, plus contributor guidance on concise trigger descriptions from `CLAUDE.md` and the upstream Superpowers docs.

**Output:** Codex-compatible skill frontmatter across the entire repo and a regression guard for YAML parseability and description length.

- [x] **Step 1: Fix invalid frontmatter.** Repaired the SKILL metadata issues Codex reported: malformed YAML description lines and the overlong `econ-data-analysis` description.
- [x] **Step 2: Shorten the entire skill surface.** Rewrote skill descriptions to trigger-only metadata instead of mini-specs, following the repo contributor guidance and upstream Superpowers skill-writing guidance.
- [x] **Step 3: Add a structural guard.** Extended `tests/structural-invariants.sh` so every `skills/*/SKILL.md` frontmatter must parse and every description must stay at or below 500 characters.
- [x] **Step 4: Verify the retrofitted surface.** Re-ran the Codex-focused frontmatter check, generated-agent tests, sync check, and full structural invariants suite after the metadata cleanup.

### Task 3: Pre-Merge Integration and Merge Readiness

**Review status:** APPROVED
**Integration status:** APPROVED

**Files affected:** `PLAN.md`, `docs/plans/2026-04-17-codex-compatibility-results.md`, `tests/check-harness-compatibility.sh`, `CLAUDE.md`, `README.md`, `skills/using-superRA/references/main-agent.md`, and any docs or plugin surfaces flagged by the integration pass

**Input:** Approved Codex compatibility implementation (`3e9f1c8`) plus the approved execution-stage record in `docs/plans/2026-04-17-codex-compatibility-results.md`

**Output:** Confirmed drift-test coverage for the Codex support surface, a top-level Claude/Codex compatibility guard, the accepted doc-audit fixes, an archived Codex compatibility handoff pair under `docs/plans/`, and a branch current with `main`

- [x] **Step 1: Confirm drift-test coverage.** User chose a new top-level compatibility check as the Stage 1 guard: add a Claude/Codex compatibility script that validates both harness surfaces, then keep `tests/structural-invariants.sh`, `skills/codex-superra-setup/scripts/test_sync_codex_agents.py`, and `skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` as the concrete checks it runs.
- [x] **Step 2: Run the integration review / fix loop.** Added `tests/check-harness-compatibility.sh` as the top-level harness guard, then ran an integration pass over the new surface. The only accepted finding was a missing contributor-facing instruction to run the new guard for harness-surface changes, fixed in `CLAUDE.md`. The compatibility script reran cleanly afterward.
- [x] **Step 3: Finalize handoff for merge.** Re-merged `origin/main` into `codex-adaption` (Round 3, minimum-net-diff per the 2026-04-20 §Decisions entry) absorbing main commits `a635dac` (drop `tests/structural-invariants.sh`), `242519e` (PR #12 skill-surface simplification, including `5c8b93a` execution-workflow → implementation-workflow rename), and `2431e93` (lowercase `using-superra`). Took main verbatim on every shared file and surgically re-threaded only the Codex-essential additive surfaces: §Codex design subsection + AGENT.md alias note in `CLAUDE.md` (the harness-compat contributor bullet was intentionally dropped per user manual override of `CLAUDE.md`), the Codex install bullet in `README.md`, the `codex-superra-setup` row + harness adapter pointer in `skills/using-superRA/SKILL.md`, the `execution-workflow` → `implementation-workflow` rename in `skills/using-superRA/references/codex-tools.md`, and the `.agents/skills/execution-workflow` → `.agents/skills/implementation-workflow` symlink refresh. Folded the two Codex-essential checks from the dropped `tests/structural-invariants.sh` (frontmatter parses + ≤1024-char description; `.agents/skills/` symlink coverage) inline into `tests/check-harness-compatibility.sh` along with the finding-9 lowercase-`name:` assertion, and removed the now-broken `bash tests/structural-invariants.sh` call. Regenerated `.codex/agents/superra_*.toml` from the rewritten `agents/*.md` via `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project`. Archived `docs/plans/2026-04-19-*.md` left untouched per advisory finding 12.
