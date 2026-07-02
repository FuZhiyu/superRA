---
title: "Discovery Wiring & Skill-Trigger Test"
status: implemented
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

## Results

### Categorization decision: Utility (not a Domain-manifest skill)

Confirmed against the current Skill-Load Manifest stage model in [skills/using-superra/SKILL.md](../../../skills/using-superra/SKILL.md#L96-L103). The Domain manifest rows auto-load a domain skill into an implementer/reviewer subagent dispatched *by the generic workflow loop* at a `Stage:` (e.g. an implementer on a data-analysis task at `Stage: implementation` loads `econ-data-analysis`). `literature-review` does not load that way: it is `user-invocable: true`, its Part 1 is a main-agent interactive setup and its Part 2 is a self-contained fan-out driven by the skill's own executor template — the same orchestrator-driven, standalone shape as `zotero-paper-reader`, which is a Utility skill and absent from the manifest. So it "does not genuinely load at a stage" → registered as **Utility**, not added to the Domain manifest.

### Surfaces registered

- **[skills/CATEGORIES.md](../../../skills/CATEGORIES.md#L49)** — added a Utility-table row (styled like the `zotero-paper-reader` / `mistral-pdf-to-markdown` rows, ending "User-invocable standalone; orchestrator-driven, not loaded by workflow agents"). Removed the stale "Literature review — citation integrity" bullet from the Domain "Future verticals (roadmap — not yet implemented)" list ([CATEGORIES.md:31-33](../../../skills/CATEGORIES.md#L31-L33)) and added a one-line note that literature review now ships as a Utility skill rather than a workflow-loaded domain skill. Simulation remains the sole roadmap vertical.
- **[README.md](../../../README.md#L13-L14)** — dropped the now-false "with literature review on the roadmap" clause from the domain-skills line (item 3) and added "building an economics/finance literature review" to the utility-skills line (item 4). The current README carries no skill *tables* (those moved to the docs site), so these two prose lines are its only mention sites.
- **[tests/skill-triggering/prompts/literature-review.txt](../../../tests/skill-triggering/prompts/literature-review.txt)** — a naive prompt (map the heterogeneous-investor asset-pricing literature: find, screen, snowball backward/forward to convergence, organize with per-paper notes; curated deduped collection, not a written survey) that exercises the description's trigger surface without naming the skill and without single-paper `zotero-paper-reader` framing.
- **[tests/skill-triggering/run-all.sh](../../../tests/skill-triggering/run-all.sh#L21)** — added `"literature-review"` to the `SKILLS` array.
- **[.agents/skills/literature-review](../../../.agents/skills/literature-review)** — added the missing harness symlink. `tests/check-harness-compatibility.sh` enforces a `.agents/skills/` symlink for every skill under `skills/`, and `literature-review` was the only skill missing one; the `slide-design-vertical` precedent added its symlink in the same registration work.

### Deviations from the literal task surface list

The Objective lists `skills/using-superra/SKILL.md` (skill inventory) and `skills/superplan/SKILL.md` Phase 2 verticals table as edit targets. Neither carries a matching insertion point in current source:

- **using-superra** no longer has a general skill-inventory grouping table — the `slide-design` precedent edited one, but it has since been consolidated into `CATEGORIES.md`; the current file carries only the Stage + Domain auto-load tables of the Skill-Load Manifest, and no Utility skill (`zotero-paper-reader`, `result-protection`, etc.) appears there. A Utility skill correctly gets **no** using-superra entry.
- **superplan** Phase 2 no longer has the "Currently implemented verticals" domain-setup table the precedent edited; the current Phase 2 just instructs "load the matching domain skill" without enumerating them. A Utility skill would get no superplan row regardless.

Both non-edits follow directly from the Utility decision and from architectural drift since this task was written. No dangling or omitted entry results.

### Verification

- **Trigger:** the live `claude -p` trigger run on the new prompt (plugin-dir = this worktree) invoked `Skill` with `"skill":"superRA:literature-review"`; replicating `run-test.sh`'s exact pass predicate (`grep '"name":"Skill"'` AND `grep -E '"skill":"([^"]*:)?literature-review"'`) against the output returns **PASS**.
- **Harness invariant:** `.agents/skills/` now has a symlink for every skill under `skills/` (`literature-review` was the last one missing).
- **Consistency:** CATEGORIES and README agree on name (`literature-review`), category (Utility), and the one-line framing; no stale roadmap reference to literature review remains in README / CATEGORIES / using-superra / superplan.

### Caveat — `run-all.sh` cannot be run end-to-end in this environment

The committed `run-test.sh` is incompatible with this machine's toolchain for reasons unrelated to this change (they affect every trigger test, e.g. `slide-design`, identically): macOS has no `timeout` binary, and the current `claude` CLI (2.1.198) requires `--verbose` alongside `--output-format stream-json`, which `run-test.sh` omits. Additionally the environment's auto-mode classifier blocks `--dangerously-skip-permissions`. Verification above was therefore done by reproducing the runner's exact pass predicate on a real model run (dropping only the sandbox flag — the predicate matches the `Skill` tool-use event, which is emitted regardless of permission gating). Fixing `run-test.sh` is out of scope for this task; a maintainer on a Linux runner (or with `coreutils`/`gtimeout` and matching CLI flags) can run `run-all.sh` directly.
