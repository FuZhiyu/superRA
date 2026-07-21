---
title: "Discovery & Harness Wiring"
status: approved
depends_on: [skill-core, skill-references]
---

## Objective

Make the literature-review vertical discoverable across the maintained user-facing inventory and harness packaging surfaces.

- Register in `skills/CATEGORIES.md` and `README.md`, and expose the skill through the maintained `.agents/skills/` packaging surface.
- Add the Skill-Load Manifest row only if the skill loads into a generic workflow dispatch.

### Validation criteria
- The skill is discoverable from each surface, with no dangling or omitted entry.
- The cross-harness compatibility check discovers the skill and its packaging link.
- Inventory entries are mutually consistent (CATEGORIES / README / using-superra agree on name, category, and one-line description).

## Planner Guidance

Decide whether `literature-review` is a **Domain-manifest skill** (loaded at a workflow stage — if so, add the manifest row and a `Load when the task…` trigger) or a **standalone Utility skill** like `zotero-paper-reader` (registered in the inventories but not auto-loaded by the Skill-Load Manifest). The two-part workflow is orchestrator-driven and largely standalone, so Utility is the likely fit — confirm against the manifest's stage model. Load `skill-creator`.

## Results

### Categorization decision: Utility (not a Domain-manifest skill)

Confirmed against the current Skill-Load Manifest stage model in [skills/using-superra/SKILL.md](../../../skills/using-superra/SKILL.md#L96-L103). The Domain manifest rows auto-load a domain skill into an implementer/reviewer subagent dispatched *by the generic workflow loop* at a `Stage:` (e.g. an implementer on a data-analysis task at `Stage: implementation` loads `econ-data-analysis`). `literature-review` does not load that way: it is `user-invocable: true`, its Part 1 is a main-agent interactive setup and its Part 2 is a self-contained fan-out driven by the skill's own executor template — the same orchestrator-driven, standalone shape as `zotero-paper-reader`, which is a Utility skill and absent from the manifest. So it "does not genuinely load at a stage" → registered as **Utility**, not added to the Domain manifest.

### Surfaces registered

- **[skills/CATEGORIES.md](../../../skills/CATEGORIES.md#L49)** — added a Utility-table row (styled like the `zotero-paper-reader` / `mistral-pdf-to-markdown` rows, ending "User-invocable standalone; orchestrator-driven, not loaded by workflow agents"). Removed the stale "Literature review — citation integrity" bullet from the Domain "Future verticals (roadmap — not yet implemented)" list ([CATEGORIES.md:31-33](../../../skills/CATEGORIES.md#L31-L33)) and added a one-line note that literature review now ships as a Utility skill rather than a workflow-loaded domain skill. Simulation remains the sole roadmap vertical.
- **[README.md](../../../README.md#L13-L14)** — dropped the now-false "with literature review on the roadmap" clause from the domain-skills line (item 3) and added "building an economics/finance literature review" to the utility-skills line (item 4). The current README carries no skill *tables* (those moved to the docs site), so these two prose lines are its only mention sites.
- **[.agents/skills/literature-review](../../../.agents/skills/literature-review)** — added the missing harness symlink. `tests/check-harness-compatibility.sh` enforces a `.agents/skills/` symlink for every skill under `skills/`, and `literature-review` was the only skill missing one; the `slide-design-vertical` precedent added its symlink in the same registration work.

### Deviations from the literal task surface list

The Objective lists `skills/using-superra/SKILL.md` (skill inventory) and `skills/superplan/SKILL.md` Phase 2 verticals table as edit targets. Neither carries a matching insertion point in current source:

- **using-superra** no longer has a general skill-inventory grouping table — the `slide-design` precedent edited one, but it has since been consolidated into `CATEGORIES.md`; the current file carries only the Stage + Domain auto-load tables of the Skill-Load Manifest, and no Utility skill (`zotero-paper-reader`, `result-protection`, etc.) appears there. A Utility skill correctly gets **no** using-superra entry.
- **superplan** Phase 2 no longer has the "Currently implemented verticals" domain-setup table the precedent edited; the current Phase 2 just instructs "load the matching domain skill" without enumerating them. A Utility skill would get no superplan row regardless.

Both non-edits follow directly from the Utility decision and from architectural drift since this task was written. No dangling or omitted entry results.

### Verification

- **Harness invariant:** [tests/check-harness-compatibility.sh](../../../tests/check-harness-compatibility.sh) requires a `.agents/skills/` entry for every skill under `skills/`; `literature-review` satisfies that maintained packaging contract.
- **Consistency:** CATEGORIES and README agree on name (`literature-review`), category (Utility), and the one-line framing; no stale roadmap reference to literature review remains in README / CATEGORIES / using-superra / superplan.

### Trigger-test retirement

The 0.3.2 upstream-surface cleanup removed the obsolete model-call `tests/skill-triggering/` harness wholesale, including the literature-review prompt and runner entry. The skill's trigger remains owned by its frontmatter description; maintained deterministic coverage now protects inventory consistency and cross-harness packaging rather than pinning model prose/tool events.
