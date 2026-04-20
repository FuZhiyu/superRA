# RESULTS: User-Facing Doc Polish + Initial Release Prep

**Objective.** Turn the committed crude draft of `README.md` + `CLAUDE.md` into shippable documentation and prepare adjacent user-facing docs for an initial release.

**Status.** Plan approved; execution in progress.

---

## Task 1a: Mermaid workflow diagram for README

**Status:** APPROVED.

**Artifact:** [`docs/drafts/workflow-diagram.mmd`](docs/drafts/workflow-diagram.mmd) — self-contained Mermaid diagram ready for Task 1b to embed verbatim in README §Plan-Implement-Integrate Workflow.

**Design choices:**

- `flowchart TB` with two subgraphs. IMPLEMENT uses `direction LR` to visually compress the implementer ↔ reviewer loop into a tight horizontal pair. INTEGRATE stays `TB` with Phases A → B → C → D as a vertical chain.
- Shows only what the Task 1a constraints require: the three phases, the implementer/reviewer loop with APPROVE/REVISE labels, Phases A–D with one-line labels, two dotted `scope change (§User Feedback and Changing Plans)` arrows from IMPLEMENT and INTEGRATE back to PLAN, and a `merged` terminal node off Phase D. Explicitly excludes: skill-load manifest detail, cross-cutting skills rail, stage → reference mapping (those live in `using-superRA`).
- Density compared to the prior Workflow Map (archived at `git show 3970828^:README.md`): seven phase nodes vs. eight phase nodes + a cross-cutting rail + per-node skill/reference listings. New diagram is ~1/3 the ink of the old one — user-facing onboarding, not architectural reference.

**Validation:** Rendered cleanly via `npx @mermaid-js/mermaid-cli` to `/tmp/diagram-test.svg` (69 KB SVG, no warnings). GitHub Mermaid uses a compatible feature subset — no mermaid-cli-only syntax used (no `icon:`, no `@{ ... }` shorthand, standard `classDef` / `subgraph` / `direction` only).

## Task 1b: Rewrite README.md as a careful user-facing doc

**Status:** APPROVED.

**Summary.** Rewrote every README section outside the APPROVED `## Installation` block. Header tagline tightened to three offering bullets (workflow / domain skills / utility skills). "Why superRA?" bullets polished, trailing ellipsis dropped, resolution paragraph rewritten to surface the three-part structure (implementer-reviewer pair / domain skills / integration phase). "The Plan-Implement-Integrate Workflow" now embeds the Task 1a Mermaid diagram verbatim from `docs/drafts/workflow-diagram.mmd` (validated with a byte-level diff) and drops the `<!-- -->` TODO comments. "Key principles" polished across all five bullets; principle 3's TODO resolved with explicit definitions of integration (refactor + dovetail with existing codebase, mature docs) and semantic merge (intent-based conflict classification with escalation for research impact). "Domain Skills" replaced with a table row for `econ-data-analysis` plus a flagged-as-hooks roadmap list for theory / lit review / simulation / writing. "Utility Skills" replaced with a table covering `handoff-doc`, `report-in-markdown`, `refactor-and-integrate`, `semantic-merge`, `worktree-data-sync`, each row carrying both *what* and *when to use* per `skill-creator` discipline. The separate downstream "Skills / Workflow / Domain / Utility / Meta" inventory from the pre-draft README was folded into the new Domain + Utility tables; a single pointer to `using-superRA` §Skill-Load Manifest (agent-facing) and `skills/CATEGORIES.md` (contributor-facing) replaces the duplicate surface. Hooks table verified against `hooks/hooks.json` (three entries: `merge-guard`, `ask-user-question-logger`, `exit-plan-mode`). Removed the crude draft's placeholder "Plugin Design Philosophy" section; replaced with a one-paragraph "Contributing" block pointing at `CLAUDE.md`. Restored the "Upstream" paragraph crediting Jesse Vincent / Superpowers that the crude draft deleted.

**Verification.** `rg -n "<!--|TODO|tbd|\.\.\." README.md` returns nothing. Byte-diff of the Mermaid fenced block against `docs/drafts/workflow-diagram.mmd` is empty — diagram embedded verbatim. `## Installation` section (heading through end of `### Other Platforms`) untouched per Task 4 APPROVED scope.

## Task 2: Consolidate CLAUDE.md as the developer / contributor doc

**Status:** Not started

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

**Status:** Not started

## Task 6: Final human read-through + release tag decision

**Status:** Not started
