---
title: "Encode Workflow State in the Commit Subject + Sharpen the Body DRY Boundary"
status: implemented
depends_on:
  - 08-report-commit-model
tags: []
created: 2026-06-21
---

## Objective

Make every commit's **workflow state legible from `git log` at a glance** by giving the commit subject a single, uniform grammar that carries the state the commit just landed, and sharpen the body rule so it stops duplicating `task.md`. Teach this in the smallest possible footprint — one shared invariant plus the per-site example each agent already copies — with **no new lookup doc**.

This supersedes the [08-report-commit-model](../08-report-commit-model/task.md) decision to keep status/verdict out of the subject. The reconciliation is not a reversal of that model: **`status:` frontmatter remains the single source of current truth** (it mutates with the task); the **subject's STATE token records what _this commit_ did at commit time** (immutable history). They answer different questions and do not compete. The status return staying minimal (status enum + SHA) is unchanged.

### Subject grammar (the authoritative spec)

```
<stage>(<scope>): <STATE> — <summary>
```

- **`<stage>`** — the workflow verb (`plan`, `implement`, `review`, `integrate`, `sync`) or a maintenance type for commits outside a task run (`fix` / `feat` / `refactor` / `docs` / `test` / `chore` / `ci`).
- **`<STATE>`** — the verdict/status this commit lands, taken verbatim from the agent's §Report Format so no new vocabulary is introduced:
  - `implement` → `DONE` | `CONCERNS` | `BLOCKED` | `NEEDS-CTX`
  - `review` → `APPROVE` | `REVISE`
- **`integrate` / `plan` are multi-step _phases_, not single-verdict dispatches** — their glanceable state is the **sub-step name, carried in `<scope>`**:
  - `integrate(protect|sync|fit|mature|finish): <summary>` — the five `superintegrate` steps.
  - `plan(add|revise|rollup): <summary>` — tree authoring vs. update-task revision vs. status rollup. A planning-review verdict commit is `plan(review): APPROVE|REVISE — <summary>`.
- **`<scope>`** — the task-path locator already used elsewhere (e.g. `data-preparation/merge`) for run commits; the component for maintenance commits.
- Maintenance commits omit `<STATE>` (they have no workflow state).

### Body rule (sharpen, do not template)

The body stays free-form prose — **do not add a required structure or field template** (that would be the contingency-tree over-specification the repo gate bans). Make exactly one change: sharpen the existing one-line body rule at both role-spec §Commit sites to draw the DRY boundary against `task.md`:

> The body is the **dispatch delta** — what changed this turn and why. It is history scoped to this commit; it is **not** a copy of `## Results` / `## Review Notes` (those are the task's current self-contained state) and not the full task state.

### Where the teaching lives (concise placement — no new doc)

1. **`skills/using-superra/SKILL.md` §Commit Hygiene** — add the **one** cross-stage invariant: the subject grammar above plus the body DRY clause. This is the only genuinely shared rule; state it once here.
2. **`agents/implementer.md` §Commit** — reshape the example line agents copy: `implement(<task-path>): <STATE> — <delta>` with an inline `# STATE = DONE | CONCERNS | BLOCKED` comment pointing at §Report Format; apply the sharpened body clause; **delete** the now-superseded `implementer.md:106` "Keep status out of the subject" sentence.
3. **`agents/reviewer.md` §Commit** — same reshape: `review(<task-path>): <STATE> — <delta>`, `# STATE = APPROVE | REVISE`; sharpened body clause; **delete** the `reviewer.md:112` "Keep the verdict out of the subject" sentence.
4. **`skills/superintegrate/SKILL.md`** — at the five step descriptions (Protect / Sync / Integrate / Mature & Consolidate / Finish), add the `integrate(<step>): …` subject form inline where each step is described. `SKILL.md:26` already says each step's completion is recorded by its commit — this just makes the subject carry the step name. Do not add a separate table.
5. **`skills/superplan/SKILL.md`** — where plan commits are described (e.g. §User Feedback step 5 currently titles the commit `plan: <one-line scope change>`), update to the `plan(<sub-step>): …` form and note the `add|revise|rollup|review` sub-steps inline.

Apply the principle from `CLAUDE.md` (DRY + Necessity gate): point, don't restate. The role specs already carry a §Commit that points to §Commit Hygiene — keep that pointer; the only per-site content is the example line and the one-line body clause.

### Generated artifacts — `[BLOCKING]`

The §Commit text appears in the generated direct-mode role references, so after editing the canonical specs, regenerate via the generator (do not hand-edit the generated files):

```bash
python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project
```

Generated files that must update:
- `skills/using-superra/references/direct-mode-implementer.md`
- `skills/using-superra/references/direct-mode-reviewer.md`
- `.codex/agents/superra_implementer.toml`
- `.codex/agents/superra_reviewer.toml`

If the generator string-matches any now-removed §Commit wording (the deleted "Keep status/verdict out of the subject" sentences), update the matcher in `sync_codex_agents.py` and `test_sync_codex_agents.py` accordingly.

### Verification

- Subject grammar block present in `using-superra` §Commit Hygiene; both role-spec §Commit examples show the `<stage>(<scope>): <STATE> — <delta>` form; both "keep state out of subject" sentences are gone.
- `superintegrate` step descriptions and `superplan` commit-title guidance carry the sub-step subject form.
- `python3 skills/codex-superra-setup/scripts/sync_codex_agents.py --scope project --check` → clean.
- `uv run --with pytest --with pyyaml python -m pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py` → green.
- `python3 skills/task-tree/scripts/task_check.py --plan-root superRA` → clean.
- Self-apply the `CLAUDE.md` DRY + Necessity gate to every added instruction line.

## Planner Guidance

This is a focused, surgical documentation change to one skill section, two role-spec §Commit blocks, and two workflow-skill spots, plus the mechanical generator regen — medium model is fine. Draft the §Commit Hygiene grammar block once and let the two role specs point to it; the per-site content is just the reshaped example line and the one body clause.

Resist scope creep: do **not** retro-rewrite historical commit messages, and do **not** add a body template — the body stays free prose. The grammar-shape decision (conventional-commits `<stage>(<scope>):` short form, scope = task-path locator) is settled per the user's confirmed previews; do not reopen it.

The integrate/plan sub-step names (`protect|sync|fit|mature|finish`, `add|revise|rollup|review`) are the one piece of genuinely new vocabulary — confirm they match the actual step headings in `superintegrate`/`superplan` as you place them, and keep them owned by those skills (do not duplicate the list into `using-superra`).

## Results

The commit-subject grammar now lives as one cross-stage invariant, with each multi-step phase owning its sub-step token list and each role spec carrying only its per-site example.

**Shared invariant — `using-superra` §Commit Hygiene** ([SKILL.md:40-54](../../../../../skills/using-superra/SKILL.md#L40-L54)): added a `### Commit subject grammar` block with the `<stage>(<scope>): <STATE> — <summary>` spec. It enumerates the stage verbs and maintenance types, the `implement`/`review` `<STATE>` vocabulary (verbatim from §Report Format), and the `<scope>` locator. `integrate`/`plan` are named as multi-step phases whose sub-step token is **owned and enumerated by `superintegrate`/`superplan`** — the list is *not* duplicated here (per planner guidance). The block closes by reconciling with task 08: `status:` frontmatter stays the single source of current truth, the subject `<STATE>` records what *this commit* did (immutable history), status return stays minimal. The sharpened body DRY clause lands here once: the body is the dispatch delta, **not** a copy of `## Results` / `## Review Notes`.

**Role-spec §Commit example lines (per-site content only):**
- Implementer ([implementer.md:101-105](../../../../../agents/implementer.md#L101-L105)): example reshaped to `implement(<task-path>): <STATE> — <delta>` with inline `# STATE = DONE | CONCERNS | BLOCKED — per §Report Format`; the superseded "Keep status out of the subject" sentence deleted; body clause sharpened to point at `## Results`.
- Reviewer ([reviewer.md:108-112](../../../../../agents/reviewer.md#L108-L112)): example reshaped to `review(<task-path>): <STATE> — <delta>` with `# STATE = APPROVE | REVISE — per §Report Format`; "Keep the verdict out of the subject" sentence deleted; body clause sharpened to point at `## Review Notes`.

Both specs keep their existing §Commit pointer to `using-superra` §Commit Hygiene (the grammar is not restated there).

**Phase owners — sub-step tokens placed inline where each step is described:**
- `superintegrate` ([SKILL.md:26](../../../../../skills/superintegrate/SKILL.md#L26)): §Stop Points carries the authoritative one-line enumeration `integrate(<step>)` with `protect | sync | fit | mature | finish` (the `fit` token names the "Integrate" refactor-to-fit step, since `integrate(integrate)` would be redundant). Each of the five step descriptions then carries a concise inline subject mention at its commit point (Protect step 6, Sync intro, Integrate close step 6, Mature & Consolidate APPROVE commit, Finish closeout). A dispatched sync (its own `Stage: sync`) commits under the `sync` verb; an inline Direct-mode sync lands as `integrate(sync)`. No separate table added.
- `superplan` ([SKILL.md:199](../../../../../skills/superplan/SKILL.md#L199)): §User Feedback step 5 commit title updated from `plan: …` to `plan(<sub-step>): …` with the `add | revise | rollup | review` set enumerated inline (this update-task path is `plan(revise)`; a planning-review verdict commit is `plan(review): APPROVE|REVISE — …`). Execution Handoff (§Phase 4) tags initial tree authoring as `plan(add): …` and points to the full set.

**Generated artifacts (`[BLOCKING]`)** — regenerated via `sync_codex_agents.py --scope project`; all four updated and verified to carry the new §Commit example lines:
- `skills/using-superra/references/direct-mode-implementer.md`, `direct-mode-reviewer.md`
- `.codex/agents/superra_implementer.toml`, `superra_reviewer.toml`

No generator/test matcher change was needed: the generator splices §Handoff (which contains §Commit) structurally by top-level section and never string-matched the deleted "Keep status/verdict out of the subject" sentences; `grep` confirmed the test file has no such string.

**Verification:**
- `sync_codex_agents.py --scope project --check` → clean (all generated agents + direct-mode refs up to date)
- `uv run --with pytest --with pyyaml python -m pytest skills/codex-superra-setup/scripts/test_sync_codex_agents.py` → 7 passed
- `task_check.py --plan-root superRA` → all checks passed
- `check_markdown.py skills/using-superra/SKILL.md` → clean

**DRY + Necessity self-check:** the grammar block exists once (`using-superra`); the integrate/plan token lists live only in their owning skills; the role specs carry only the example line + a scoped one-line body clause (the per-site content the objective authorizes). No body template was added — the body stays free prose. Historical commit messages were not rewritten.
