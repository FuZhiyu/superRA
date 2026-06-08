---
title: "Document and Package BibTeX/Citation Commands"
status: approved
depends_on:
  - 07-bibtex-export
  - 08-cite-and-bibliography
tags: [docs, packaging, skill-creation]
input:
  - skills/zotero-paper-reader/SKILL.md
  - skills/zotero-paper-reader/scripts/zotero_tool.py
output:
  - skills/zotero-paper-reader/SKILL.md
  - skills/zotero-paper-reader/references/bibtex-citations.md
  - skills/CATEGORIES.md
  - README.md
  - skills/using-superRA/SKILL.md
created: 2026-06-08
---

## Objective

Surface the new `bibtex`, `cite`, and `bibliography` commands to users and register the expanded capability across the repo's inventory surfaces. Load `skill-creator` before editing `SKILL.md` (repo guideline for any `skills/*/SKILL.md` change).

### Skill Documentation

Follow skill-creator's progressive-disclosure model: metadata (frontmatter `description`) → a lean `SKILL.md` body that routes → on-demand reference for depth. The existing `SKILL.md` is ~60 lines and already routes to `paper-reading.md` / `access-modes.md`; keep that profile. Detail belongs in the reference, not the body — do not duplicate the reference's content into `SKILL.md`.

- **`SKILL.md` (routing surface):** add the three commands to the command-surface table with one-line purposes, plus a single short "Citations & BibTeX" note stating the key model in one or two sentences (BBT keys by default; built-in translator fallback with a key-mismatch warning; BBT keys require local Zotero + Better BibTeX) and a pointer to the new reference for examples and flags. Do not inline the full flag list, fallback semantics, or troubleshooting here. Update the frontmatter `description` so bibtex export, citation insertion, and `.bib` sync are explicit triggers.
- **`references/bibtex-citations.md` (depth):** the full surface — command examples for `bibtex` / `cite` / `bibliography`, every flag (`--bib` / `--tex` / `--markdown` / `--marker` / `--library`), the BBT-vs-built-in key explanation, fallback/warning semantics, group-library targeting, and troubleshooting (BBT not installed, Zotero closed). Add it to the skill's Resources list with a clear load condition. One reference level deep; if it exceeds ~300 lines, give it a short table of contents.

### Packaging Surfaces

Update the one-line capability descriptions so they reflect bib/citation support, keeping the skill a **standalone Utility skill that is NOT loaded by the Skill-Load Manifest**:

- `skills/CATEGORIES.md`
- `README.md`
- `skills/using-superRA/SKILL.md` (the `zotero-paper-reader` inventory row's one-line purpose)

### Validation

- The text-regression suite (task 10) asserts `SKILL.md` and the new reference mention the new commands and the key model.
- Inventory one-liners across `CATEGORIES.md`, `README.md`, and `using-superRA/SKILL.md` stay mutually consistent and none claim the skill is Manifest-loaded.

## Planner Guidance

- Mirror the existing doc structure: `SKILL.md` routes to references; deep examples live in `references/bibtex-citations.md` alongside the existing `paper-reading.md` and `access-modes.md`.
- This is a Tier-2 bundle (one agent, shared `skill-creator` load) — docs and the three inventory edits travel together.

## Results

**Maintenance note (from 2026-06-08 sync with `origin/main`):** this skill's frontmatter `description` is a **single-quoted** YAML scalar, synthesized when incoming `010a5c1e`'s valid-YAML fix met our citation triggers. The single quotes are load-bearing — the literal `` `\cite` `` backslash makes a double-quoted scalar an invalid escape — so do not "normalize" it to double quotes.

Surfaced the `bibtex` / `cite` / `bibliography` commands following skill-creator's progressive-disclosure model: `SKILL.md` is a lean routing surface, the full depth lives in a new on-demand reference, and the three inventory surfaces now reflect citation support while keeping the skill a standalone Utility (not Manifest-loaded). Tasks 07/08 had each added a detailed `SKILL.md` section and a Better BibTeX block in `access-modes.md` as minimal command surfaces; per the dispatch steering I **consolidated and routed** rather than duplicating — the deep content now has one home in the new reference, and the older surfaces point to it.

### `SKILL.md` — lean routing ([SKILL.md](../../skills/zotero-paper-reader/SKILL.md))

- Collapsed the two task-07/08 sections (`## BibTeX Export`, `## Cite and Bibliography`, ~14 lines of prose) into a single 5-line `## Citations & BibTeX` note: the key model in two sentences (BBT citekeys by default; built-in fallback with a key-mismatch warning) plus a pointer to the new reference. The body is back to a ~60-line routing profile (69 lines total).
- Kept the three command-table rows and the `--library` targeting line (the discoverable command surface), and added the new reference to the Resources list with a clear load condition.
- Updated the frontmatter `description` so BibTeX export, `\cite`/`[@key]` insertion, master-`.bib` sync, and bibliography rendering are explicit triggers.

### `references/bibtex-citations.md` (new, depth) ([references/bibtex-citations.md](../../skills/zotero-paper-reader/references/bibtex-citations.md))

The full surface, one level deep with a table of contents: the BBT-default / built-in-fallback key model and the BBT JSON-RPC method table; the shared `--item-key` / `--query` / `--doi` selection flags; per-command sections for `bibtex` / `cite` / `bibliography` with runnable examples and every flag (`--bib` / `--tex` / `--markdown` / `--marker` / `--style`); group-library targeting and the BBT `libraryID` numbering; master-`.bib` dedup-append semantics (including the brace-balancing entry parser and its one known quoted-field limitation); a JSON-field table; and troubleshooting (BBT not installed, Zotero closed, Web-API mode, citekey-not-itemkey, missing marker). 151 lines.

To avoid duplication, the detailed Better BibTeX block tasks 07/08 had placed in `access-modes.md` was reduced to a short pointer to the new reference, with the access-mode capability-matrix rows for the citation commands left in place (those belong to access-modes' local-vs-web boundary). The new reference is now the single authority for the key model.

### Inventory surfaces (mutually consistent, none claims Manifest-loading)

- [skills/CATEGORIES.md](../../skills/CATEGORIES.md) — Utility row now lists BibTeX export, `\cite`/`[@key]` insertion, master-`.bib` sync, and bibliography rendering (Better BibTeX citekeys by default); "User-invocable standalone; not loaded by workflow agents" retained.
- [README.md](../../README.md) — skill table row extended with the citation tooling clause.
- [skills/using-superRA/SKILL.md](../../skills/using-superRA/SKILL.md) — the `zotero-paper-reader` §Skill Inventory row extended with citation tooling; still states "Not loaded by workflow agents or the Manifest". Verified the skill does **not** appear in the Skill-Load Manifest table.

### Verification

- `bash tests/test-zotero-skill-text.sh` — 16/16 pass (existing text-regression suite; the new-command/key-model assertions on `references/bibtex-citations.md` are owned by task 10).
- Cross-reference sweep: `SKILL.md`, `access-modes.md`, and `bibtex-citations.md` link consistently and one level deep; the stale `access-modes.md` BBT-key-model pointer from the old `SKILL.md` section is removed and access-modes now points to the new reference as the authority — no circular or dead links.
- Inventory consistency: confirmed all three surfaces describe the same citation capability and none claims Manifest-loading; `awk` scan of the Skill-Load Manifest section finds no `zotero` row.
