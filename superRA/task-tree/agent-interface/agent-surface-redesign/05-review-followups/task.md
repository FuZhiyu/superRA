---
title: "Clean Up DRY Echoes and Meta-Commentary in Lean Task-Interface Surfaces"
status: approved
depends_on:
  - 02-task-tree-slim
  - 03-role-spec-slim
tags: []
created: 2026-06-01
---

## Objective

Apply the `CLAUDE.md` DRY/Necessity gate to the lean task-interface surfaces produced by tasks 02 and 03, fixing the violations a researcher review surfaced. The authoritative read/edit/format home is `using-superRA/SKILL.md §Task Interface`; `task-tree/SKILL.md` is a load-on-demand router for orchestrators/planners/contributors; `agents/implementer.md` and `agents/reviewer.md` carry only role-specific protocol. Every line removed below either restates content one of those owners already carries (DRY) or narrates what a file does/omits instead of shaping behavior (the banned meta-commentary / wrapper anti-pattern). Do not remove any line that shapes non-default behavior, states a safety invariant, or enforces an ordering constraint. Load `skill-creator` before editing any `SKILL.md`, per `CLAUDE.md §Skill Authoring`.

**Scope A — `skills/task-tree/SKILL.md`.** A researcher has partially cleaned this file in the working tree (uncommitted); treat their edits as a head-start, finish per the findings below, and do not revert them.

1. **Collapse two routing surfaces into one.** The "Role-scoped references" bullet list (currently near the top, ~lines 18-21) and the "Routing — operate on the tree" table (~lines 89-99) both map to `references/commands.md` / `references/planning.md` / `references/internals.md` / §Task Interface. Drop the bullet list; keep the table as the single routing surface. If the list names any destination the table lacks, add that row to the table before deleting the list.
2. **One pointer to §Task Interface, not three.** §Task Interface is pointed to from the frontmatter, the "Reading the Tree" paragraph (~line 53), and the routing table. Keep exactly one canonical pointer (the routing-table row); reduce the others to nothing or a bare cross-reference that does not re-describe what §Task Interface contains.
3. **Delete meta-commentary.** Remove "this skill does not duplicate it" (~line 53) and the frontmatter clause "executing agents read/edit their own task via §Task Interface and do not need this skill"; replace the frontmatter with the positive form only ("Load on demand by orchestrators, planners, and contributors"), which already implies executing agents do not load it.
4. **De-duplicate the Task File Format example (~lines 55-87).** The inline status-enum comment duplicates §Task Interface's status enum, the body-section names duplicate its body-section vocabulary, and the frontmatter fields duplicate `references/planning.md`'s field anatomy (already pointed to at ~line 87). Keep a short orienting skeleton if it earns its place, but remove the inline enum comment and let §Task Interface + planning.md own the enum / section / field definitions. The status enum must not be written in two files.
5. **Trim the move paragraph (~line 100).** It explains the `mv` mechanic in full, then points to `references/commands.md` "for detail." Keep only the non-obvious safety fact (a cross-boundary `mv` strands a sibling `depends_on`, which validation flags) and make the rest a one-line pointer.
6. **Drop the line-16 one-liner** ("A directory-tree task tree where the filesystem hierarchy is the task hierarchy") — Core Concepts states it more precisely.

**Scope B — `agents/implementer.md` and `agents/reviewer.md` §Editing Etiquette.**

7. **Replace the four-name principle echo with a bare pointer.** Each spec's `### Editing Etiquette` re-enumerates all four shared principles ("inline-edit / latest-state-not-a-log, remove-superseded-content, markdown-link citations, doc-before-report") that §Task Interface already lists in full; §Task Interface is always loaded, so the echo saves no file load and fails the DRY test. Replace with — implementer: "Apply the shared editing principles in `superRA:using-superra` §Task Interface, plus this implementer-specific rule:"; reviewer: the same opener ending "…plus these reviewer-specific rules:". Keep every role-specific line that follows unchanged.
8. **Strip the researcher's inline `<!-- -->` comments** added in commit 78e1a25e — three in `agents/implementer.md`, one in `agents/reviewer.md` (the malformed nested comment disappears with fix 7).

**Out of scope — leave byte-for-byte unchanged:**
- The script-path / `<skill-dir>` placeholder and how `task_read.py` / `task_query.py` are invoked, plus the "load task-tree only for tree tooling" framing. A separate branch repackages the tooling; do not pre-empt it.
- The `→ implemented:` / `→ orchestrator:` annotation protocol and the `status: implemented` enum value — confirmed correct and intentionally informal.
- The role specs' "What You Own / You may NOT edit" sections — authoritative per §Task Interface's delegation; do not restructure.

**Regenerate derived files.** After editing the canonical `agents/*.md`, run `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project` and confirm with `--check`. Generated targets (never hand-edit): `skills/using-superRA/references/direct-mode-implementer.md`, `skills/using-superRA/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml`. The slimmed §Editing Etiquette pointer must propagate into the two direct-mode references.

**Validation (must hold to complete):**
- `task-tree/SKILL.md` has exactly one routing surface and one §Task-Interface pointer; no "this skill does/doesn't …" meta-commentary remains; the status enum is not written in this file.
- The four shared-principle names appear together in exactly one place — §Task Interface. `grep -rn "remove-superseded-content" agents/ skills/using-superRA/references/ .codex/` returns no role-spec or generated echo.
- Both role specs retain every role-specific etiquette / ownership / verdict line (confirm by a heading walk).
- No `<!-- -->` comments remain: `grep -rn "<!--" agents/implementer.md agents/reviewer.md skills/task-tree/SKILL.md` is empty.
- `sync_codex_agents.py --scope project --check` reports all generated files up to date.
- The out-of-scope script-path text and `<skill-dir>` placeholders are unchanged.

**Output:** `skills/task-tree/SKILL.md`, `agents/implementer.md`, `agents/reviewer.md`, and the four regenerated files.

## Results

Done in Direct mode (orchestrator implemented + self-reviewed against the `CLAUDE.md` DRY/Necessity gate), building on the researcher's in-flight `task-tree/SKILL.md` edits.

**Scope A — [`skills/task-tree/SKILL.md`](../../../../../skills/task-tree/SKILL.md):**
1. Dropped the top "Role-scoped references" bullet list; the bottom "Routing — operate on the tree" table is now the single routing surface (it already covered every destination the list named: `commands.md`, `planning.md`, `internals.md`, §Task Interface).
2. §Task-Interface pointers cut from three to two with distinct jobs: the routing-table row (canonical routing) and one bare disambiguating pointer in "Reading the Tree" (so a reader does not reach for `task_query.py` to read a single task). Frontmatter no longer points to it.
3. Removed "this skill does not duplicate it" and the frontmatter "executing agents … do not need this skill" clause — frontmatter now states only the positive "Load on demand by orchestrators, planners, and contributors".
4. Removed the inline status-enum comment (and the `depends_on` sibling-comment) from the format example; the enum/sections/fields are owned by §Task Interface + `planning.md`. The example is no longer a second home for the enum.
5. Trimmed the `mv` paragraph to the non-obvious safety fact (cross-boundary move strands a sibling `depends_on`, flagged by validation) + a one-line pointer to `commands.md`.
6. Dropped the redundant line-16 one-liner (Core Concepts states it).

**Scope B — role specs:** Replaced the four-name editing-principles echo with a bare pointer to §Task Interface in [`agents/implementer.md`](../../../../../agents/implementer.md) (pointer in the `## Handoff` lead) and [`agents/reviewer.md`](../../../../../agents/reviewer.md) (`### Editing Etiquette`); every role-specific line (the `Stay within your assigned task` rule, the reviewer remove-when-empty rule, the flag-unclear-structure line) is retained. Stripped all four `<!-- -->` researcher comments (3 implementer, 1 reviewer); the malformed nested reviewer comment is gone with the rewrite.

**Regenerated** the four derived files via `sync_codex_agents.py --scope project`; `--check` reports all generated agent files and direct-mode references up to date.

**Verification:**
- `grep -rn "<!--" agents/implementer.md agents/reviewer.md skills/task-tree/SKILL.md` → empty.
- `grep -rln "remove-superseded-content" agents/ skills/using-superRA/ .codex/` → empty (the hyphenated token lived only in the deleted echo; §Task Interface still states all four principles in prose at `using-superRA/SKILL.md:55-58`).
- Status enum appears nowhere in `task-tree/SKILL.md`.
- The 5 `<skill-dir>` placeholders and the script-invocation text are unchanged — script-path/packaging is deferred to a separate branch.
