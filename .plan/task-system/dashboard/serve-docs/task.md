---
title: "Dashboard serve documentation clarity"
status: implemented
review_status: approved
integration_status: ~
depends_on: 
  - serve-shortcut

tags: []
created: 2026-05-26
updated: 2026-05-26
---

## Objective

Fix documentation so agents find the dashboard serve command without probing, and so users know about `.plan/serve`.

**Specific changes:**

1. **`skills/task-system/references/internals.md`** §Dashboard Generation (lines 168–179) — the section still shows the old static `generate` command (`python3 <skill-dir>/scripts/plan_dashboard.py --plan-root .plan`) and describes generating a static HTML file. Rewrite to reflect the live `serve` subcommand as primary, mention that `generate` is deprecated. Keep it concise — the authoritative CLI docs are in `SKILL.md` §Dashboard; `internals.md` should cross-reference, not duplicate.

2. **`skills/task-system/SKILL.md`** §Dashboard (line 196–204) — add a note about `.plan/serve` as the user shortcut: "If `.plan/serve` exists (generated at plan creation time), users can launch with `bash .plan/serve`." Keep the `uv run <skill-dir>/...` command as the canonical agent-facing form.

3. **`README.md`** — add a brief mention of the dashboard under the workflow overview, something like: "Each `.plan/` includes a `serve` script — run `bash .plan/serve` to open the live dashboard." This is the first place users look.

**Do not** add dashboard serve instructions to workflow skills (`planning-workflow`, `implementation-workflow`) or `main-agent.md` — those are agent-internal and the task-system skill is the owner. The `.plan/serve` script itself is the discoverability mechanism for users.

## Results

Three documentation files updated to surface the live dashboard and `.plan/serve` shortcut:

1. **`internals.md` §Dashboard** ([internals.md:168](skills/task-system/references/internals.md#L168)) — rewrote from static-generation description to live-server description; cross-references SKILL.md §Dashboard as authoritative; updated Script Inventory entry for `plan_dashboard.py` to mention `serve` and deprecated `generate`.
2. **`SKILL.md` §Dashboard** — already updated by the serve-shortcut implementer with `.plan/serve` as primary command, `uv run` as agent-facing form, and explanation of the shortcut script. No further changes needed.
3. **`README.md`** ([README.md:52](README.md#L52)) — added one-line dashboard mention in the workflow overview, between the invocation keywords and key principles sections.
