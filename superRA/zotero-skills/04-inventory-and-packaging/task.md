---
title: "Update Skill Inventory and Packaging Surfaces"
status: approved
depends_on:
  - 03-paper-reading-workflow
tags: [docs, packaging, skill-creation]
input:
  - skills/zotero-paper-reader/SKILL.md
output:
  - README.md
  - skills/CATEGORIES.md
  - skills/using-superRA/SKILL.md
created: 2026-06-04
---

## Objective

Register the Zotero skill in the repo surfaces that control discovery and contributor navigation. Add it as a utility skill unless implementation discovers a better owner. Update README skill tables, `skills/CATEGORIES.md`, and `skills/using-superRA/SKILL.md` without changing workflow choreography or the Skill-Load Manifest.

### Constraints

Do not add Codex-only behavior. The plugin manifests already package `skills/`, so packaging changes should be limited to inventory/docs unless implementation discovers a concrete distribution gap. Leave generated agent files untouched because this plan does not change canonical agent specs.

## Planner Guidance

Keep descriptions trigger-focused: reading, searching, retrieving, converting, and analyzing papers from Zotero libraries. Mention local-first and web fallback only where it changes agent behavior.

## Results

### Placement decision

`zotero-paper-reader` is user-invocable standalone and not loaded by any workflow stage or the Skill-Load Manifest. The `using-superra` Skill Inventory already contains a standalone-invocable entry (`codex-superra-setup`) so including `zotero-paper-reader` there is consistent and keeps it discoverable to agents that might suggest it to users. The entry explicitly states it is not loaded by workflow agents, so no Manifest change is needed and no workflow choreography is touched.

### Changes

Three inventory surfaces updated; Manifest and generated agent files are untouched.

- [skills/using-superRA/SKILL.md:65](../../skills/using-superRA/SKILL.md#L65) — added `zotero-paper-reader` row to the Skill Inventory table under Utility, with an explicit "not loaded by workflow agents or the Manifest" note.
- [skills/CATEGORIES.md:47](../../skills/CATEGORIES.md#L47) — added `zotero-paper-reader` row to the Utility table with a trigger-focused description matching the skill's frontmatter.
- [README.md:89](../../README.md#L89) — added `zotero-paper-reader` row to the Utility Skills table; description covers trigger conditions (reading, finding, summarizing, analyzing by title/author/DOI/topic) and lists library query capabilities, consistent with the skill's frontmatter.

### mistral-pdf-to-markdown rows

When the conversion step behind `zotero-paper-reader` was vendored in-repo (see [06-vendor-mistral-skill](../06-vendor-mistral-skill/task.md)), a matching Utility row was added to the same three surfaces, each describing it as a user-invocable standalone skill needing `MISTRAL_API_KEY`, the conversion step behind `zotero-paper-reader`, and not loaded by workflow agents or the Manifest:

- [skills/using-superRA/SKILL.md:66](../../skills/using-superRA/SKILL.md#L66)
- [skills/CATEGORIES.md:48](../../skills/CATEGORIES.md#L48)
- [README.md:90](../../README.md#L90)

### Verification

All entries confirmed present via grep. Skill-Load Manifest (Generic and Domain add-on tables in `using-superra`) is unchanged.

