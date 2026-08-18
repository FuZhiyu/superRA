---
title: "Sweep Stale Pointers and Hook Docs"
status: not-started
depends_on: [gate-hardening]
---

## Objective

No shipped skill or doc points at a path or wiring that no longer exists.

- No file under `skills/` references the deleted `writing/` directory — sweep with `grep -rn 'writing/references\|skills/writing' skills/` and fix every hit.
- The hook inventory in `docs/site/06-hooks/task.md` lists guard-task-approval and agent-model-guard with a count sentence matching the shipped set; `docs/README.codex.md`'s Hook Coverage table adds ensure-communicate and guard-task-approval rows mirroring `hooks-codex.json`, both added to its `/hooks` verification list.
- Docs describe the post-gate-hardening wiring (hence `depends_on`), including that apply_patch now reaches the task hook on Codex.

## Details

Known `writing/` dangles: [refactor-and-compile.md:52](../../../../skills/academic-writing/references/refactor-and-compile.md#L52), [:60](../../../../skills/academic-writing/references/refactor-and-compile.md#L60), [:113](../../../../skills/academic-writing/references/refactor-and-compile.md#L113) → the skill's own `references/consistency/…`; [argument-logic.md:70](../../../../skills/academic-writing/references/consistency/argument-logic.md#L70) → `../style.md`. Doc gaps: [docs/site/06-hooks/task.md:19](../../../../docs/site/06-hooks/task.md#L19) (table plus the "six of the seven" count at line 29); [docs/README.codex.md](../../../../docs/README.codex.md) Hook Coverage table (~lines 62-68) and the claim at line 67 that apply_patch covers direct task edits — true only once gate-hardening fixes the matcher.
