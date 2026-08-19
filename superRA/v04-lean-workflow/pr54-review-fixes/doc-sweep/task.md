---
title: "Sweep Stale Pointers and Hook Docs"
status: approved
depends_on: [gate-hardening]
---

## Objective

No shipped skill or doc points at a path or wiring that no longer exists.

- No file under `skills/` references the deleted `writing/` directory — sweep with `grep -rn 'writing/references\|skills/writing' skills/` and fix every hit.
- The hook inventory in `docs/site/06-hooks/task.md` lists guard-task-approval and agent-model-guard with a count sentence matching the shipped set; `docs/README.codex.md`'s Hook Coverage table adds ensure-communicate and guard-task-approval rows mirroring `hooks-codex.json`, both added to its `/hooks` verification list.
- Docs describe the post-gate-hardening wiring (hence `depends_on`), including that apply_patch now reaches the task hook on Codex.

## Details

Known `writing/` dangles: [refactor-and-compile.md:52](../../../../skills/academic-writing/references/refactor-and-compile.md#L52), [:60](../../../../skills/academic-writing/references/refactor-and-compile.md#L60), [:113](../../../../skills/academic-writing/references/refactor-and-compile.md#L113) → the skill's own `references/consistency/…`; [argument-logic.md:70](../../../../skills/academic-writing/references/consistency/argument-logic.md#L70) → `../style.md`. Doc gaps: [docs/site/06-hooks/task.md:19](../../../../docs/site/06-hooks/task.md#L19) (table plus the "six of the seven" count at line 29); [docs/README.codex.md](../../../../docs/README.codex.md) Hook Coverage table (~lines 62-68) and the claim at line 67 that apply_patch covers direct task edits — true only once gate-hardening fixes the matcher.

## Results

- No shipped skill or doc points at a missing path or pre-hardening wiring; `grep -rn 'writing/references\|skills/writing' skills/` returns nothing.
  - The four `writing/` dangles now use skill-local paths: [refactor-and-compile.md](../../../../skills/academic-writing/references/refactor-and-compile.md) cites `consistency/terminology.md` and `consistency/cross-references.md` (3 hits); [argument-logic.md](../../../../skills/academic-writing/references/consistency/argument-logic.md) cites `../style.md`.
  - [docs/site/06-hooks/task.md](../../../../docs/site/06-hooks/task.md) adds agent-model-guard and guard-task-approval rows, notes the Codex `apply_patch` matchers on ensure-communicate and task-hook, and counts "eight of the nine" hooks for Claude.
  - [docs/README.codex.md](../../../../docs/README.codex.md) Hook Coverage adds guard-task-approval and ensure-communicate rows mirroring `hooks-codex.json` (both added to the `/hooks` verification list) and states the task-tree hook's `Edit|Write|Bash|apply_patch` event — the direct-task-edit claim is now backed by the gate-hardening matcher.
- Remaining `skills/writing*` grep hits live under `docs/plans/` — historical plan records, not shipped pointers; left as archives.

## Review Notes

Tier: thorough. Focus: correctness. Verified the four path fixes resolve, re-counted the hook inventory against `hooks/` and all three registries, and re-ran the `writing/` sweep plus a wider one over `skills/`, `docs/site/`, `README.md`, and `CLAUDE.md`.

1. [ADVISORY] → fixed: the line now names `academic-writing`. One shipped doc still names the retired `writing` skill in prose: [04-slide-design/task.md:17](../../../../docs/site/03-domain-skills/04-slide-design/task.md#L17) — "the same way the writing skill works". The skill was renamed to `academic-writing` in `5cfd69db`, so a reader following the analogy finds nothing. Outside the Objective's enumerated `grep -rn 'writing/references\|skills/writing' skills/` sweep but inside its headline ("no shipped skill or doc points at a path or wiring that no longer exists"). Fix: name `academic-writing`, or drop the comparison.
