---
title: "Discovery Wiring & Skill-Trigger Test"
status: not-started
depends_on: [skill-core, skill-references]
---

## Objective

Make the literature-review vertical discoverable and protect its trigger, mirroring how `slide-design-vertical` and `zotero-skills` registered their skills.

- Register in the inventory/discovery surfaces: `skills/using-superra/SKILL.md` (skill inventory; and the Domain manifest table **if** the skill loads at a stage), `skills/superplan/SKILL.md` Phase 2 verticals table, `skills/CATEGORIES.md`, and `README.md`.
- Add a skill-triggering prompt `tests/skill-triggering/prompts/literature-review.txt` wired into `tests/skill-triggering/run-all.sh`.

### Validation criteria
- The skill is discoverable from each surface, with no dangling or omitted entry.
- The trigger test passes under `run-all.sh`.
- Inventory entries are mutually consistent (CATEGORIES / README / using-superra agree on name, category, and one-line description).

## Planner Guidance

Decide whether `literature-review` is a **Domain-manifest skill** (loaded at a workflow stage — if so, add the manifest row and a `Load when the task…` trigger) or a **standalone Utility skill** like `zotero-paper-reader` (registered in the inventories but not auto-loaded by the Skill-Load Manifest). The two-part workflow is orchestrator-driven and largely standalone, so Utility is the likely fit — confirm against the manifest's stage model. Load `skill-creator`.
