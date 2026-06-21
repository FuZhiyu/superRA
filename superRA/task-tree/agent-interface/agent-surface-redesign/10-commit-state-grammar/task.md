---
title: "Encode Workflow State in the Commit Subject + Sharpen the Body DRY Boundary"
status: not-started
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
