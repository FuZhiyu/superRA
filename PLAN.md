# Markdown Style Guide Plan

> **For agentic workers:** REQUIRED DISCIPLINE: Use `superRA:handoff-doc` for all PLAN.md / RESULTS.md editing. This is a contributor-discipline change (skills + agent files) under the rules in repo-root `CLAUDE.md`. Steps use checkbox (`- [ ]`) syntax for tracking and cross-session handoff. **Generated artifacts:** changes to `agents/*.md` require regeneration of `skills/using-superRA/references/direct-mode-{implementer,reviewer}.md` and `.codex/agents/superra_{implementer,reviewer}.toml` via `skills/codex-superra-setup/scripts/sync_codex_agents.py`. Do not hand-edit those files.

**Objective:** Teach every superRA agent to cite source files using markdown links with line anchors (e.g. `[file.py:42](file.py#L42)`) instead of bare backtick paths, by re-scoping `report-in-markdown` to be the always-loaded markdown style guide.

**Methodology:** Trim `report-in-markdown/SKILL.md` to a small always-loaded body that carries always-applicable rules (file-link citation discipline) and the existing load map; keep heavy content (figures, math, tables, Stage 2 fact-check) in references loaded on demand. Add `report-in-markdown` to every Stage row in the Skill-Load Manifest. Propagate the new citation format to canonical examples in `agents/implementer.md`, `agents/reviewer.md`, and `handoff-doc/references/plan-anatomy.md`. Sweep for stale backtick-path examples. Regenerate Codex artifacts.

**Conventions:** See `## Project Conventions` below.

**Output:**
- `skills/report-in-markdown/SKILL.md` (rewritten)
- `skills/report-in-markdown/references/rich-content.md` (extended §File references)
- `skills/using-superRA/SKILL.md` (Skill-Load Manifest updated)
- `agents/implementer.md`, `agents/reviewer.md` (canonical examples + conditional-load text updated)
- `skills/handoff-doc/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md` (pointer + examples updated)
- Generated artifacts: `skills/using-superRA/references/direct-mode-{implementer,reviewer}.md` and `.codex/agents/superra_{implementer,reviewer}.toml` (regenerated, not hand-edited)

**Expected Results / Hypotheses:** After the change, an implementer or reviewer dispatched at any Stage will load `report-in-markdown` and have the file-link rule visible in its always-loaded skill body. Routine review-item citations in PLAN.md and RESULTS.md task sections will use markdown links matching the canonical agent-body example. Stage 2 RESULTS.md fact-check (already enforced via `final-form.md`) will continue to pass with no regression. Total instruction-line growth in always-loaded surface is < 25 lines.

**Sensitivity Analysis:** Verify the trimmed `report-in-markdown/SKILL.md` body remains useful as a standalone style guide (a researcher invoking it directly should see the rules without further reads). Verify the `using-superra` Skill-Load Manifest change does not bloat any single Stage's load list beyond what is already justified (each Stage already loads ≤ 3 skills; adding `report-in-markdown` makes some 1 → 2 or 2 → 3).

**Pipeline:** `python skills/codex-superra-setup/scripts/sync_codex_agents.py` (regenerates Codex named-agent artifacts after `agents/*.md` edits). No code-execution pipeline; this is a doc/skill edit.

---

## Workflow Status

- [x] **Plan approved** — researcher signed off on Option 5 in plan-mode session 2026-04-27 (no domain vertical applies)
- [ ] **Execution complete** — all tasks `APPROVED`, regeneration script run clean
- [ ] **Drift tests created** — n/a for skill-text edits (no numerical results to protect)
- [ ] **Integrated** — integration reviewer `APPROVED` after Sync
- [ ] **Docs finalized** — RESULTS.md matured (likely minimal: this work *is* docs), project docs audited
- [ ] **Finished** — branch landed locally or PR opened

---

## Project Conventions

Walked at planning time (2026-04-27). Re-walk on-demand only.

### Repo root
- `/CLAUDE.md` (HEAD at 886fda8): contributor guidelines for superRA itself. Treats skill/agent edits as skill creation (load `skill-creator` before editing any `skills/*/SKILL.md`). Two key gates apply here: (a) §"Teach the Protocol, Don't Prescribe" — every instruction line must pass DRY + Necessity tests; one-line echoes are tolerable only when avoiding a redundant file load; (b) §"Codex and Harness Design" — `agents/*.md` is canonical and `direct-mode-*.md` + `.codex/agents/*.toml` are generated via `sync_codex_agents.py`; surface generated files in PLAN.md so dispatched agents do not hand-edit them. Ownership table assigns "Report formatting for figures, math, tables, and final-form markdown" to `report-in-markdown` — this plan extends that ownership to file-link citations as well, which is consistent with the existing `rich-content.md §File references` section.
- `/AGENT.md`, `/AGENTS.md`: identical aliases of `/CLAUDE.md` (verified by `diff`).
- `/README.md` (HEAD at 886fda8): user-facing overview of superRA — plan-implement-integrate workflow, domain skills, utility skills. Not directly authoritative for this contributor-internal change but defines the user-visible surface (e.g., the README skill tables that may need updating if a skill's described purpose shifts).

### Module-level docs walked
- `/skills/CATEGORIES.md` (HEAD at 886fda8): authoritative grouping index. `report-in-markdown` is listed under Utility with description "Format discipline for markdown reports — figures, LaTeX math, tables. Progressive-reveal references by stage." This description is now slightly narrow given the scope shift; row should be updated to reflect "markdown style guide for any agent writing markdown" and remind of the always-loaded status.
- No `CLAUDE.md` / `AGENTS.md` / `README.md` in `skills/report-in-markdown/`, `skills/using-superRA/`, `skills/handoff-doc/`, or `agents/` — the SKILL.md files themselves are authoritative for their skills' behavior.

### Not walked (not reachable from the planned diff)
- `skills/econ-data-analysis/`, `skills/theory-modeling/`, `skills/integration-workflow/`, etc. — domain and other workflow skills are not edited by this plan; they will pick up the new style guide via the Skill-Load Manifest and via `agents/implementer.md` / `agents/reviewer.md` examples without needing per-skill edits.
- `tests/`, `evals/` — out of scope for this plan.

---

## Decisions

> **User decision (2026-04-27):** Option 5 — slim `report-in-markdown/SKILL.md` to ~25 lines (load map + quick rules including markdown-link file-citation syntax), make it always-loaded by every agent via the Skill-Load Manifest, keep heavy content (figures, math, tables, Stage 2 fact-check) in references loaded on demand.
> **Question asked:** Which approach for teaching agents the markdown file-link format — examples-only, pointer + examples, examples + tiny rule line in agent bodies, slim always-loaded skill, or `using-superra` addition?
> **Rationale:** Single source of truth; every agent writes markdown; the existing `report-in-markdown/SKILL.md` is already lightweight enough that always-loading it is acceptable.

---

### Task 1: Re-scope `report-in-markdown` skill body and extend rich-content reference
**Depends on:** *(none)*
**Review status:** APPROVED
**Integration status:** *(set during integration)*

**Script:** `skills/report-in-markdown/SKILL.md` (rewritten body), `skills/report-in-markdown/references/rich-content.md` (§File references extended)
**Input:** Existing `SKILL.md` (~46 lines) and `rich-content.md` §File references (lines 88–97).
**Output:** Trimmed `SKILL.md` (40 lines including frontmatter) that stands as the markdown style guide; `rich-content.md` §File references covering single-line, range, and whole-file citation syntax.

- [x] **Step 1: Update `skills/report-in-markdown/SKILL.md` frontmatter and body**

Rewrite frontmatter `description` to: "Markdown style guide for any agent writing PLAN.md, RESULTS.md, status reports, or standalone reports. Carries always-applicable rules (markdown-link file citations) plus a load map pointing to references for figures, math, tables, and Stage 2 final-form discipline."

Body structure (~25 lines):

```markdown
# Report in Markdown

The markdown style guide. Every agent loads this skill — every agent writes markdown.

Always-applicable rules below. Details for figures / math / tables / Stage 2 maturation live in references; load only the reference your output needs.

## File-reference rule

Cite source files as **markdown links with line anchors**, not backtick paths.

| Use case | Form |
|---|---|
| Single line | `[file.py:42](file.py#L42)` |
| Line range | `[file.py:40-50](file.py#L40-L50)` |
| Whole file | `[file.py](file.py)` |

Resolve paths **relative to the markdown file's directory** (use `../` as needed). For files at the worktree root, relative path = project-root path.

Full discipline (relative-path edge cases, the wrong/correct contrast): `references/rich-content.md` §File references.

## Load map

| Caller | Load |
|---|---|
| Implementer / reviewer writing routine task-block citations only | nothing beyond this file |
| Implementer writing a `RESULTS.md` task section with figures / math / tables | `rich-content.md` |
| `integration-workflow` Document doc-writer subagent (maturing `RESULTS.md`) | `baseline-io.md` + `rich-content.md` + `final-form.md` |
| `integration-workflow` Document doc-reviewer subagent | `final-form.md` |
| Standalone markdown report (any context) | `baseline-io.md` + `rich-content.md` |

The `attachments/` directory is a caller parameter; defaults and fallbacks are in `rich-content.md` §Figures.

## References

- `references/baseline-io.md` — frontmatter spec, filename convention, output-path resolution. Permanent artifacts only.
- `references/rich-content.md` — figure handling, LaTeX math, markdown tables, full file-reference discipline.
- `references/final-form.md` — Stage 2 `RESULTS.md` consolidation: fact-check checklist, restructure, figure materialization, relocation.
```

- [x] **Step 2: Extend `skills/report-in-markdown/references/rich-content.md` §File references with line-anchor syntax**

Replace lines 88–97 with an expanded §File references section that:
- Keeps the existing "always create markdown links with paths resolved relative to the report file's directory" rule and the Wrong/Correct contrast.
- Adds line-anchor syntax: `#L42` for single line, `#L40-L50` for a range.
- Shows the canonical citation form with link text matching the path: `[code/BOP/clean_data.py:42](../code/BOP/clean_data.py#L42)`.
- Explicitly notes that GitHub renders these as clickable line anchors and editors / VS Code preview honor them.

- [x] **Step 3: Validate, commit**

Re-read both files end-to-end. Confirm:
- Trimmed `SKILL.md` < 50 lines (final: 40 lines with frontmatter), stands on its own as a style guide (no required reference load to use the citation rule).
- `rich-content.md` §File references fully covers single-line, range, and whole-file anchors with a wrong/correct contrast.
- `skills/CATEGORIES.md` row for `report-in-markdown` updated to reflect the scope shift.
- `README.md` skill table row updated for consistency.
- No prohibited patterns: no DRY violations, no restating defaults, no wrapper instructions.

---

### Task 2: Make `report-in-markdown` always-loaded in the Skill-Load Manifest
**Depends on:** *(none)*
**Review status:** REVISE
**Integration status:** *(set during integration)*

> **Review notes:**
> 1. [MINOR] [skills/using-superRA/SKILL.md:59](skills/using-superRA/SKILL.md#L59) — the §Skill Inventory row for `report-in-markdown` still reads "Format discipline for markdown reports — figures, LaTeX math, tables." This contradicts the new framing introduced 18 lines below at line 77 ("the two skills every agent already loads ... `report-in-markdown` is always loaded because every agent writes markdown ... always-applicable file-link citation rule"). Task 1 already updated the parallel rows in `skills/CATEGORIES.md:44` and `README.md:82` to "Markdown style guide for any agent writing markdown — always-applicable file-link citation rule plus progressive-reveal references for figures, LaTeX math, tables, and Stage 2 final-form." The using-superRA inventory row should match. Fix: rewrite line 59 to mirror the CATEGORIES/README phrasing (e.g. "Markdown style guide for any agent writing markdown — always-applicable file-link citation rule plus on-demand references for figures, LaTeX math, tables, and Stage 2 final-form."). The dispatch's check (3) explicitly flagged this consistency point. Without this, a fresh agent reading the file top-to-bottom sees two different stories about what the skill is.

**Script:** `skills/using-superRA/SKILL.md` (§Skill-Load Manifest)
**Input:** Current manifest §Generic table (lines 79–89), with `report-in-markdown` only at `Stage: documentation`.
**Output:** Updated manifest where `report-in-markdown` is always loaded (in addition to `using-superra`); each Stage row's "Required skills" column lists it explicitly, or a short "always loaded" note above the table makes the universality clear.

- [x] **Step 1: Update `skills/using-superRA/SKILL.md` §Skill-Load Manifest**

Took **Form A**: extended the explanatory paragraph above the §Generic table to call out `report-in-markdown` as always loaded alongside `using-superra`, with a one-sentence rationale ("every agent writes markdown"). Dropped `report-in-markdown` from the `documentation` Stage row to avoid double-listing — `handoff-doc` remains there.

- [x] **Step 2: Update the §References explanatory paragraph**

Folded the §References paragraph extension into Step 1 — the rewritten paragraph now both names the always-loaded pair and explains why.

- [x] **Step 3: Validate, commit**

Confirmed:
- `Stage: documentation` row no longer double-lists `report-in-markdown`; `handoff-doc` retained.
- Always-loaded note is unambiguous and placed where an agent reading the manifest cannot miss it (right above the table).
- The **Main agents additionally load** sentence below the domain table is unaffected.

---

### Task 3: Update canonical examples and conditional-load text in agent files and handoff-doc references
**Depends on:** Task 1 (must know the new citation form), Task 2 (must know the new always-loaded state)
**Review status:** *(set during execution)*
**Integration status:** *(set during integration)*

> **User decision (2026-04-27):** Add a one-line reminder in `agents/implementer.md` and `agents/reviewer.md` pointing at `report-in-markdown` for the file-link citation rule, even though the manifest update in Task 2 makes it always-loaded. Concise — a single line near the existing handoff/etiquette section in each file is enough.
> **Question asked:** During Task 1 REVISE round, the user asked whether to add a "highlight" sentence in the agent bodies that points at `report-in-markdown` when the agent is editing PLAN.md / RESULTS.md.
> **Rationale:** The manifest load makes the skill available, but a one-liner in the agent body increases the chance an agent actually consults it for the citation rule.

**Script:** `agents/implementer.md`, `agents/reviewer.md`, `skills/handoff-doc/SKILL.md`, `skills/handoff-doc/references/plan-anatomy.md`
**Input:** Existing canonical examples using backtick-path citations and the conditional-load sentence at `agents/implementer.md` line 128.
**Output:** All canonical example blockquotes use markdown-link citations; one-line `report-in-markdown` highlight added to each agent body's Editing Etiquette section; conditional-load sentence reflects always-loaded state of `report-in-markdown`; `handoff-doc/SKILL.md` line 49 pointer extended.

- [ ] **Step 1: Update `agents/implementer.md`**

- Lines 113–120 — rewrite the example blockquote so review items and `→ implemented:` annotations use markdown-link citations:

```markdown
> **Review notes:**
> 1. [MAJOR] Step 2 uses inner join; should be left join. ([Code/03.py:42](Code/03.py#L42))
>    → implemented: switched to left join, row count preserved ([Code/03.py:42](Code/03.py#L42))
> 2. [MINOR] Missing row-count log after merge. ([Code/03.py:45](Code/03.py#L45))
>    → implemented: added `print(f"Rows: {n_before} → {len(df)}")` ([Code/03.py:47](Code/03.py#L47))
> 3. [MAJOR] Use log returns, not arithmetic.
>    → orchestrator: rejected — methodology specifies arithmetic returns per plan header Section 2
```

- Line 128 — drop the conditional `also load` sentence (the skill is now always loaded). Replace with: "If your task section contains figures, LaTeX math, or tables, also load `report-in-markdown/references/rich-content.md` for the format details."

- [ ] **Step 2: Add one-line `report-in-markdown` highlight to both agent bodies**

In each of `agents/implementer.md` and `agents/reviewer.md`, find the Editing Etiquette subsection (the compact handoff-doc etiquette that already lives in each file) and add a single line: "Cite source files as markdown links per `report-in-markdown` §File-reference rule (e.g., `[file.py:42](file.py#L42)`)." Keep it concise — one sentence, no new paragraph.

- [ ] **Step 3: Update `agents/reviewer.md`**

§Review Protocol (around line 126) — the description currently reads "file:line, description, severity, what to fix." Change to: "markdown-link citation (e.g., `[file.py:42](file.py#L42)`), description, severity, what to fix." One-sentence change; no new paragraphs.

- [ ] **Step 4: Update `skills/handoff-doc/SKILL.md` line 49**

Current: `**Figure embedding** — discipline in `report-in-markdown/references/rich-content.md`; Stage 2 materialization in `report-in-markdown/references/final-form.md`.`

New: `**Figure embedding and code-file citations** — discipline in `report-in-markdown/references/rich-content.md`; Stage 2 materialization in `report-in-markdown/references/final-form.md`.`

One-word extension to surface the link-citation rule for handoff-doc readers.

- [ ] **Step 5: Update `skills/handoff-doc/references/plan-anatomy.md`**

Find the example review-notes blockquote (currently around lines 208–212 with `(`Code/03.py:42`)` style). Rewrite to match the agent-body example: markdown-link citations.

- [ ] **Step 6: Validate, commit**

Confirm:
- All four files use markdown-link citations in their canonical examples.
- The `agents/implementer.md` line 128 conditional-load sentence is consistent with `report-in-markdown` being always loaded (no contradictory wording).
- No bare backtick-path citation samples remain in the four files.

Update PLAN.md, RESULTS.md Task 3, commit. Note: do NOT regenerate Codex artifacts in this commit — that happens in Task 5 once all agent edits land.

---

### Task 4: Sweep for stale backtick-path citation samples across the repo
**Depends on:** Task 1, Task 3
**Review status:** *(set during execution)*
**Integration status:** *(set during integration)*

**Script:** repo-wide grep across `skills/`, `agents/`, plus a manual review of any hits.
**Input:** Pattern: `(\`[A-Za-z0-9_/.-]+\.(py|md|sh|jl|R)[:#][0-9]` and similar — any backtick-wrapped path with a `:line` or `#L` suffix that should be a markdown link.
**Output:** A clean codebase where committed examples teach exactly one citation convention.

- [ ] **Step 1: Run the sweep**

```bash
grep -rn "\`[A-Za-z0-9_/.-]\+\.\(py\|md\|sh\|jl\|R\):[0-9]" skills/ agents/ \
  | grep -v "/references/codex-instructions.md"  # adapter-specific, may use different convention
```

Also grep for citation-shaped patterns in fenced code blocks of skill bodies and review-item examples.

- [ ] **Step 2: Triage hits**

For each hit:
- **Canonical example or instructional sample** → rewrite to markdown-link form.
- **Adapter-specific reference (Codex tool name, harness shorthand)** → leave alone; flag in commit message.
- **Genuine code reference inside a code block** (`# %%` cell line numbers, code under a fenced `python` block) → leave alone; these are not citation samples.
- **PLAN.md / RESULTS.md examples in the handoff-doc references** (covered by Task 3) → already updated, ignore on the sweep.

Document the triage decisions in RESULTS.md Task 4 §Notes.

- [ ] **Step 3: Validate, commit**

Re-run the grep after rewrites; confirm only adapter-specific or in-code-block hits remain.

Update PLAN.md, RESULTS.md Task 4, commit.

---

### Task 5: Regenerate Codex named-agent artifacts and verify
**Depends on:** Task 3, Task 4
**Review status:** *(set during execution)*
**Integration status:** *(set during integration)*

**Script:** `python skills/codex-superra-setup/scripts/sync_codex_agents.py`
**Input:** Updated `agents/implementer.md` and `agents/reviewer.md`.
**Output:** Regenerated `skills/using-superRA/references/direct-mode-implementer.md`, `skills/using-superRA/references/direct-mode-reviewer.md`, `.codex/agents/superra_implementer.toml`, `.codex/agents/superra_reviewer.toml` — committed with the same diff content as the canonical agent files.

- [ ] **Step 1: Run the regeneration script**

```bash
python skills/codex-superra-setup/scripts/sync_codex_agents.py
```

- [ ] **Step 2: Verify generated files reflect Task 3 edits**

```bash
grep -n "Code/03.py#L42" skills/using-superRA/references/direct-mode-*.md .codex/agents/*.toml
```

Confirm the new markdown-link example appears in all four generated files. If any file shows the old backtick-path form, the regeneration did not pick it up; investigate `sync_codex_agents.py`.

- [ ] **Step 3: Validate, commit**

Confirm `git diff` of generated files is consistent with the agent-file edits (no unrelated drift). Stage and commit only the four generated files in this task's commit.

Update PLAN.md, RESULTS.md Task 5, commit.

---
