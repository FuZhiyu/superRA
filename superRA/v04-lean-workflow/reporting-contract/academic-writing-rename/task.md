---
title: "Rename Writing to Academic Writing"
status: approved
depends_on:
  - communicate
---

## Objective

Rename the academic-prose domain skill from `writing` to `academic-writing` without changing its substantive protocol.

- Move the skill directory and packaging symlink to `academic-writing`; make `superRA:academic-writing` the only active invocation, with no legacy `writing` alias.
- Update active workflow manifests, cross-skill pointers, inventories, user-facing docs and routes, release notes, harness contracts, fixtures, and evaluators. Preserve ordinary uses of “writing” and historical records that describe the former name.
- Preserve concurrent user edits and keep unrelated hunks out of the rename commit.
- Validate both the renamed skill and its discovery/load behavior, then prove the old path and invocation are absent from active surfaces.

## Details

- The user has already changed `skills/writing/SKILL.md` frontmatter to `name: academic-writing`; the same dirty file has a separate intent-comment edit. `skills/communicate/SKILL.md` and `skills/theory-modeling/references/integration.md` also carry user changes. Preserve all three working diffs and stage only rename-owned hunks.
- The active surface includes `using-superra`'s stage/domain manifest, Communicate's composition pointer, `CLAUDE.md`, `skills/CATEGORIES.md`, the current release-note entry, docs-site domain routing, `.agents/skills`, and harness instruction-following contracts. Archived planning docs and older release-note entries remain historical.
- Move the docs-site domain page from the `writing` route to `academic-writing`; update inbound links and page-local skill paths together.

## Results

Renamed the skill, docs route, packaging symlink, active manifests, inventories, release note, and harness contracts to `academic-writing` / `superRA:academic-writing`; no active legacy pointer remains. The deterministic harness suite, skill validation, and task-tree check pass.
