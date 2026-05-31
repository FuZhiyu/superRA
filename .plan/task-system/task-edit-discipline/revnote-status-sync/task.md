---
title: "Hook: revision-note ↔ status automation"
status: revise
depends_on:
  - move-hook
tags: []
created: 2026-05-30
updated: 2026-05-30
---

## Objective

Automate the `## Revision Notes` lifecycle inside the PostToolUse hook (`skills/task-system/scripts/task_hook.py`, the `Edit`/`Write` branch built in `move-hook`) so it no longer depends on a reviewer remembering a manual side-duty. Stale revision notes have leaked into approved tasks precisely because their removal was a forgettable secondary reviewer step; moving the lifecycle into the hook makes it deterministic. Two behaviors, both on an `Edit`/`Write` to a `task.md`, both via direct file I/O (best-effort, never block, always exit 0; the hook's own writes do not re-trigger PostToolUse):

### Behavior A — revision note *newly added* on a completed task → flip to `revise`

When an edit *adds* a `## Revision Notes` section to a leaf `task.md` whose status is a *completed* state (`approved` or `implemented`), set its status to `revise` and **preserve the note**. Rationale: a fresh revision note signals the objective changed and the task needs another implementation pass; `revise` routes it back to the implementer (decision 2026-05-30: `revise`, not `not-started`). Guards: never touch a task whose status is already `not-started`, `in-progress`, or `revise` (no-op); only de-approve completed states.

### Behavior B — approve a task whose revision note was *already there* → remove it

When an edit sets a task's status to `approved` and the task *already carried* a `## Revision Notes` section (the note pre-existed in the prior committed body — its rework is now done and the delta signal is spent), remove that entire section. Scope is revision notes only — `## Review Notes` stays owned by the reviewer's own loop and is NOT touched by the hook (decision 2026-05-30: keep the two note types separate, hook handles revision notes only).

### The disambiguation (the crux) — key on the note-presence delta, not the status delta

A stateless post-hoc hook sees an identical end-state — `{status: approved, ## Revision Notes present}` — for two opposite intents: a planner who just *added* a note to reopen a still-`approved` task (wants A), versus a reviewer who just *approved* a task that already carried a note (wants B). Status alone cannot tell these apart, and the dangerous case is real: if an approval lives only in an uncommitted working edit and a planner then adds a note, a status-delta rule would mistake it for an approval transition and **destroy the planner's note**.

So the discriminator is **whether the `## Revision Notes` section is newly added in this edit or pre-existed** — recovered from the prior committed/staged body (`git show :<relpath>` then `HEAD:<relpath>`, parsed via the existing frontmatter/body parser; recover the *body*, not just the status). Rule, applied only when the current body has a revnote and current status ∈ {`approved`, `implemented`}:
- prior body did **not** carry a revnote (note is new this edit) → **Behavior A**: set status `revise`, preserve the note. (This covers the uncommitted-approval case safely — a newly added note is never stripped.)
- prior body **already** carried a revnote and current status == `approved` → **Behavior B**: strip the section.
- prior body already carried a revnote and current status == `implemented` → no-op (note persists until approval).

If the prior committed/staged body cannot be recovered (file not yet committed/staged, not in a git tree, `git` unavailable, unparseable), fall back to the **safe default: do nothing** for the revnote automation (validation/propagation/dashboard still run as before). Never block, never guess destructively — a missed automation self-heals on the next committed edit; a wrong guess could delete a planner's revision note. The same prior-body comparison localizes the section so it is never matched inside a fenced code block (a `## Revision Notes` header quoted inside a ``` block in some other section must not count as present, and must never be stripped).

### Placement and reuse

This logic lives in the `Edit`/`Write` reconcile path only (revision notes are edited via `Edit`/`Write`, not the shell) — do not add it to the `Bash` branch. Run it alongside the existing `_reconcile` (validate → propagate → dashboard); the status change or section removal must happen before propagation so parent rollup reflects the new state. Reuse `_task_io` frontmatter parse/write helpers; do not hand-roll YAML.

## Validation

Extend `TestTaskHook` in `skills/task-system/scripts/test_task_system.py`. Required cases:
- **A:** approved task, edit adds `## Revision Notes`, prior committed status was approved → hook sets `revise`, section preserved.
- **B:** task with `## Revision Notes` present, edit sets status `approved` (prior committed status was `revise` or `implemented`) → hook removes the section, status stays `approved`.
- **Disambiguation:** the same `{approved + revnote}` end-state resolves to A vs B based on the prior committed status (one fixture per branch).
- **No-ops:** `not-started`/`in-progress` task with a revnote → untouched; `approved` with no revnote → untouched; prior-status unrecoverable → no revnote automation (and no crash).
- **Invariants:** always exit 0; the hook's write does not loop; `## Review Notes` is never touched by the hook.

Full task-system suite green (`uv run --with pytest python -m pytest test_task_system.py`). Manual: in a scratch `.plan/`, add a revnote to an approved task.md committed at approved → confirm it flips to revise; separately, approve a task.md that carries a revnote → confirm the section is removed.

## Notes

`agents/reviewer.md` and `planning.md` currently assign revision-note removal to the reviewer; reconciling those instructions to point at this hook (and regenerating the Codex/direct-mode reviewer artifacts) is the sibling `revnote-docs` task, which depends on this one so its docs match shipped behavior. Code + tests only here; no doc or generated-artifact edits.

## Results

Added the revision-note ↔ status automation to the `Edit`/`Write` reconcile path of [task_hook.py](../../../../skills/task-system/scripts/task_hook.py) and 11 tests. Full task-system suite green: **158 passed** (`uv run --with pytest python -m pytest test_task_system.py`), 147 prior + 11 new. Both behaviors confirmed in a scratch git-backed `.plan/`: a revnote added to a committed-approved task flips it to `revise` (note preserved); approving a committed-`revise` task that still carries a revnote removes the section (status stays `approved`).

### `task_hook.py` — revnote lifecycle on the Edit/Write path only

The automation runs in [`_reconcile_revision_notes`](../../../../skills/task-system/scripts/task_hook.py#L254), called from [`_handle_edit_write`](../../../../skills/task-system/scripts/task_hook.py#L322) **before** `_reconcile` so a status flip is visible to parent rollup. It is wrapped in its own best-effort try/except; the hook still always exits 0 and the `Bash` branch is untouched (revision notes are edited via `Edit`/`Write`, not the shell).

Flow inside `_reconcile_revision_notes`:
- **Leaf guard.** If the task directory contains any child `task.md`, return — a branch's status is rolled up from children, not authored, so it is not a target.
- **Gate.** Act only when the current frontmatter status is a completed state (`approved`/`implemented`) AND a `## Revision Notes` header is present. `_body_has_revision_notes` matches the header at line start (leading whitespace tolerated), so an empty-content section still counts as present.
- **Disambiguation.** [`_recover_prior_status`](../../../../skills/task-system/scripts/task_hook.py#L205) recovers the last committed status via `git -C <repo> show :<rel>` (index) then `HEAD:<rel>`, resolving the repo root with `git rev-parse --show-toplevel` and parsing the recovered frontmatter with `_task_io.parse_frontmatter`. The rule from the objective:
  - `status == approved` and `prior != approved` → **Behavior B** (approval transition): strip the `## Revision Notes` section via `_strip_revision_notes`, keep status `approved`.
  - else if `status == prior` (both completed) → **Behavior A**: set status to `revise`, keep the note.
- **Safe fallback.** If `_recover_prior_status` returns `None` (not committed/staged, not in a git tree, `git` unavailable, or unparseable) the function returns without touching the file — a missed automation self-heals on the next committed edit, whereas a wrong guess could delete a planner's note.

Reused `_task_io.parse_frontmatter` / `serialize_frontmatter` (no hand-rolled YAML). Section removal is a local `task_hook.py` concern via `_REVNOTE_SECTION_RE` (header through the next `## ` header or EOF). `## Review Notes` is never matched, so the reviewer's own loop is untouched.

### Tests — `TestRevisionNoteSync`

New class in [test_task_system.py](../../../../skills/task-system/scripts/test_task_system.py). Each case inits a real git repo under `tmp_path`, commits a known prior status, then edits and runs the hook as a subprocess (same harness as `TestTaskHook`). Cases:
- **A:** approved + added revnote (prior approved) → `revise`, note preserved; same for `implemented`.
- **B:** approval transition from prior `revise` and from prior `implemented` → note removed, status `approved`.
- **Disambiguation:** identical `{approved + revnote}` end-state, one fixture with prior `approved` → A, one with prior `revise` → B.
- **No-ops:** `not-started`/`in-progress` with revnote untouched; `approved` with no revnote untouched; prior-status unrecoverable (non-git tmp tree) → no automation, no crash.
- **Invariants:** `## Review Notes` left intact while the revnote is removed; the hook's own write converges (a second run on the now-`revise` file is a no-op, confirming no reconcile loop); all cases exit 0.

### Note on the dashboard step

The dashboard rebuild is best-effort and unrelated to this change; in a minimal environment it logs `No module named 'fastapi'` and is swallowed by its existing try/except (exit 0 preserved), matching prior hook behavior.

## Review Notes

1. **CRITICAL** — [task_hook.py:299](../../../../skills/task-system/scripts/task_hook.py#L299) Behavior B strips a planner's `## Revision Notes` when the approval lived only in an *uncommitted/unstaged* working edit. `_recover_prior_status` reads the last *committed* (or staged) status; when a task is approved in the working tree but that approval was never committed or staged, and the planner then adds a revision note to reopen the still-`approved` task (intent: Behavior A), the recovered prior is the genuinely-last-committed `revise`/`implemented`, so `status == "approved" and prior != "approved"` fires Behavior B and the note is silently deleted. Reproduced: commit a task at `revise`, approve it in the working tree only (no commit/stage), add a revnote with status still `approved` → hook strips the note instead of flipping to `revise`. This is exactly the "wrong guess could delete a planner's revision note" failure the objective's safe-default is meant to prevent; here it is reached because status alone cannot tell "just-approved-uncommitted" from "committed-at-revise." The implementation faithfully follows the objective's stated "last committed version" discriminator, so the gap may be in the discriminator itself — flagging for orchestrator adjudication. Possible fixes: (a) compare the *committed body* for revnote presence (the committed text is already fetched in `_recover_prior_status` but the body is discarded) — only treat it as a genuine approval transition (B) when the prior body also already carried a revnote, otherwise fall to the safe no-op; or (b) when prior status is non-approved, require the staged/committed status to actually equal `approved` before stripping, and treat the uncommitted-approval case as unrecoverable → no-op. Either way, the destructive branch must not be the default when A/B is genuinely ambiguous.
   → orchestrator: accepted — real data-loss path. Fix = reviewer's option (a), the body-aware discriminator now specified in §"The disambiguation": recover the prior committed/staged **body** (not just status) and strip only when the revnote *pre-existed* there; a newly-added note is always Behavior A (preserve + flip to `revise`), and unrecoverable prior body → no-op. The objective's discriminator has been rewritten accordingly — implement to the new rule.

2. **MINOR** — [task_hook.py:197](../../../../skills/task-system/scripts/task_hook.py#L197) `_body_has_revision_notes` matches a `## Revision Notes` line lexically anywhere in the body, including inside a fenced code block (e.g., a `## Results` section that quotes a `## Revision Notes` header while documenting this very feature). Reproduced: a fenced block containing `## Revision Notes` returns `True`, which on an approval edit would invoke `_strip_revision_notes` and could delete content from inside the code block. Low-probability but the gate is purely lexical with no fence awareness. Consider skipping fenced regions, or at minimum note the limitation. (Re-check after item 1 is resolved, since the same body-aware comparison suggested there would also localize this.)
   → orchestrator: accepted — make both `_body_has_revision_notes` and `_strip_revision_notes` code-fence-aware (ignore `## Revision Notes` headers inside ``` fenced blocks), so a header quoted in a Results/objective block is never detected or stripped. The objective's disambiguation section now requires this explicitly.
