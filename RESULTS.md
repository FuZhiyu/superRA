# Parallel-Implementer Worktree Isolation — Results

> Mirrors PLAN.md structure. Updated after each step with key findings.
> New agents: read PLAN.md for what to do, RESULTS.md for what was found.

**Last updated:** 2026-04-17 (Task 6)
**Status:** Complete

---

## Task 1: Worktree lifecycle fallback + §Concurrent Writers subsection

**Status:** Implemented (awaiting review)

### Key changes
- **New:** `skills/agent-orchestration/references/worktree-harness-fallback.md` — ~60 lines covering harness-tool preference, raw-git create/enter/remove, placement priority, and four gotchas.
- **Updated:** `skills/agent-orchestration/SKILL.md` — added §Concurrent Writers Require Worktree Isolation (seven subsections: ownership split, branch naming, plain-merge rationale, worktree lifecycle pointer, data seeding, dispatch, no-PLAN.md-bookkeeping rule). Extended §Dispatch Templates: new optional `Worktree:` field on the implementer template + required canned steering sentence when the field is present.

### Section anchor verification
`grep -n "^## \|^### "` on `agent-orchestration/SKILL.md` confirms the new section sits between §Workload Balancing (line 16) and §Dispatch Templates (line 164). All cross-references in the new content target existing anchors (§Dispatch Templates, `handoff-doc` §Living Plan, `hooks/merge-guard`, `semantic-merge/SKILL.md`, `worktree-data-sync` §Seed).

### Notes
- The canned steering sentence for `Worktree:` is codified as **required**, not additive — the single exception to the existing "additive-only" `Additionally:` rule. Justification in-place: the agent's spawn cwd defaults would otherwise cause silent wrong-copy edits.
- `references/worktree-harness-fallback.md` lives under `agent-orchestration/`, not `worktree-data-sync/` — worktree lifecycle is an orchestration concern. Task 2 points `worktree-data-sync` at this location.

## Task 2: Refactor `worktree-data-sync` to non-git data sync only

**Status:** Implemented (awaiting review)

### Key changes
- **Description frontmatter** narrowed to "syncing non-git-controlled data files between existing worktrees (seeding, diffing, reconciling, teardown). Worktree lifecycle out of scope."
- **Deleted:** §When to Use a Worktree (decision table, ~13 lines) and §Creating a Worktree (6 subsections including Directory Selection, Safety Verification, Create, Seed Data, Verify Accessibility, Report Location — ~80 lines).
- **Renamed §Cleanup → §Data Teardown** — retained the "seeded data disappears with the worktree directory" fact; removed `git worktree remove` prescription and the Option 4 Discard block (branch deletion). Repointed lifecycle operations to `agent-orchestration/references/worktree-harness-fallback.md`.
- **New §See Also** pointing at the lifecycle reference and at `agent-orchestration` §Concurrent Writers.

### Section outline after refactor
Frontmatter → `# Worktree Data Sync Skill` → §When to Use → §Command Surface (with §Endpoints) → §Modes (§`--mode seed` / §`--mode diff` / §`--mode apply`) → §Managed Path Discovery → §Examples → §Data Teardown → §See Also.

### Test verification
`~/.venv/bin/python -m pytest skills/worktree-data-sync/scripts/test_worktree_data_sync.py -x` → **30 passed in 3.37s**. No tests touched deleted SKILL.md sections; CLI logic unchanged.

## Task 3: Implementer dedicated-worktree path

**Status:** Implemented (awaiting review)

### Key changes
- **§Before You Start** — added step 6: when `Worktree:` is present, enter it (harness tool or `cd` + verify `git rev-parse --show-toplevel`), all I/O inside, do not merge/rebase/push/cleanup, report branch + HEAD SHA.
- **§Handoff → Update the Docs and Commit** — split the single "Shared-repo commit discipline" note into (A) shared-worktree path with the existing discipline and (B) dedicated-worktree path on `parallel/<branch>/<slug>`. Atomic-commit block stays shared across both paths.
- **§Report Format** — new bullet: `Worktree return (path B only)` reports branch name and HEAD SHA. Path A omits the field.

## Task 4: Exempt `parallel/*` from merge-guard

**Status:** Implemented (awaiting review)

### Key changes
- **`hooks/merge-guard`** — added a third early-exit branch between the abort/continue/skip/quit skip and the reminder-emitting regex. Pattern: `git (merge|rebase|cherry-pick)(\s+--?\S+)*\s+parallel/` — matches a parallel/-prefixed positional argument while allowing intermediate flags like `--no-ff`.

### Synthetic-input verification
| Input | Expected | Actual |
|---|---|---|
| `git merge parallel/foo/a` | `{}` (exempt) | `{}` ✓ |
| `git merge --no-ff parallel/feat/b` | `{}` (exempt) | `{}` ✓ |
| `git merge main` | STOP reminder | STOP reminder ✓ |
| `git merge --abort` | `{}` (already skipped) | `{}` ✓ |

## Task 5: Consumer workflow pointer updates

**Status:** Implemented (awaiting review)

### Key changes (pointer-level only — no duplicated content)
- **`skills/planning-workflow/SKILL.md`**: deleted the pre-existing paragraph instructing the planner to load `worktree-data-sync` for worktree setup (worktree setup is not a planning-time concern).
- **`skills/execution-workflow/SKILL.md`**: (a) Option 4 Discard retargeted at `agent-orchestration/references/worktree-harness-fallback.md §Remove`; (b) Red Flag about "dispatch multiple implementers in parallel on the same working tree" reworded to point at §Concurrent Writers (isolation enables parallel dispatch, rather than absolute prohibition); (c) §Integration workflow-skill list deduplicated the two `worktree-data-sync` entries and added an `agent-orchestration` entry as the owner of parallel-dispatch discipline.
- **`skills/merge-workflow/SKILL.md`**: Step 5 Cleanup Worktree and §Pairs with list split — lifecycle → `agent-orchestration/references/worktree-harness-fallback.md §Remove`; data teardown → `worktree-data-sync §Data Teardown`.
- **`skills/semantic-merge/SKILL.md`**: §When to Use gained an "Exception" paragraph noting that `parallel/*` branches bypass this skill.

### Additional dangling references fixed beyond the planned four files
Cross-reference audit uncovered two more stale pointers:
- `skills/using-superRA/references/codex-tools.md:86` — was `superRA:worktree-data-sync §Creating a Worktree`; now points at the fallback reference + `worktree-data-sync` for data seeding.
- `skills/agent-orchestration/references/agent-teams.md:101` — was the same stale cross-ref; rewritten to describe the full §Concurrent Writers flow (worktree provisioning + force-symlink seeding + plain-merge harvest).

### Final audit
- `grep -rn "§Creating a Worktree\|worktree-data-sync.*§Cleanup" skills/ agents/ hooks/` → zero hits.
- All `agent-orchestration/references/worktree-harness-fallback` references land at the correct new path.

## Task 6: End-to-end verification + review revisions

**Status:** Complete (APPROVE post-revision)

### Verification results
- **Merge-guard regression:** 4/4 synthetic inputs behave as specified.
- **Data-sync CLI:** 30/30 pytest pass in 3.58s.
- **Cross-reference audit:** zero dangling `§Creating a Worktree` or `worktree-data-sync §Cleanup` hits; 4 call sites correctly point at `agent-orchestration/references/worktree-harness-fallback`.
- **SKILL.md structural sanity:** edited skills retain frontmatter, top-level headings, and intact subsection anchors.

### Adversarial review (batched)
Dispatched `code-quality-reviewer` against `889f53c^..HEAD`. Verdict: **REVISE** → fixed → **APPROVE (self-assessed after revisions)**.
- **MAJOR M1 — accepted + fixed.** Three reviewer-cited `§Seed` anchor pointers resolved to nothing; actual heading is `### \`--mode seed\``. Fixed two (`agent-orchestration/SKILL.md` ownership table, `worktree-harness-fallback.md` Create section); the third (`agent-teams.md:101`) was already correct — reviewer miscited.
- **MINOR m1 — accepted + fixed.** Updated skill-inventory blurbs in `README.md`, `skills/CATEGORIES.md`, `skills/using-superRA/SKILL.md` to reflect narrowed scope ("non-git data sync + data teardown; lifecycle in agent-orchestration/references/worktree-harness-fallback.md"). Added a 2-bullet entry to the 2026-04-17 section of `RELEASE-NOTES.md` covering this refactor.
- **MINOR m2–m5 — advisory, no action.** Hook regex verified safe against spoofing vectors (`-m 'parallel/...'`, positional path args, feature-branch names containing "parallel"). Path A/B terminology in implementer agent is coherent. Canned-steering justification is self-defending. Trimmed `worktree-data-sync` still stands on its own.

### Final commit count
7 commits on branch `feedback/agent-dispatch-fixes`:
1. `889f53c` plan bootstrap
2. `1f844f6` agent-orchestration: §Concurrent Writers + fallback reference
3. `4241a8f` worktree-data-sync: narrow scope
4. `3a7b987` implementer: dedicated-worktree commit path
5. `1f69f28` merge-guard: parallel/* exemption
6. `42ecc7b` workflows: redirect worktree lifecycle refs
7. (this commit) verification + review-driven revisions + RELEASE-NOTES entry

## Task 7: Dogfood — merge-guard test vectors documented

**Status:** Implemented (parallel slot α, merged `4224ac3`)

### Key changes
- **New:** `hooks/merge-guard` gains a comment block immediately after the header, documenting the four synthetic test inputs (two exempt cases with parallel/* branches, one semantic-merge reminder case, one skip case) and their expected outputs.

### Test vector documentation
Added shell comments enumerating the four regression cases from Task 4:
- `git merge parallel/foo/a` → emit `{}`
- `git merge --no-ff parallel/feat/b` → emit `{}`
- `git merge main` → emit STOP reminder
- `git merge --abort` → emit `{}`

## Task 8: Dogfood — orchestrator invocation example added

**Status:** Implemented (parallel slot β)

### Key changes
- **New `## Example Orchestrator Invocation` section** appended to `skills/agent-orchestration/references/worktree-harness-fallback.md` — shows a complete ~25-line bash sequence for a single parallel slot: worktree creation, data seeding via force-symlink, placeholder for subagent dispatch, merge, and cleanup. Covers the full orchestrator-side lifecycle from the fallback reference perspective.

## Dogfood findings (Tasks 7–8)

Two issues surfaced from self-hosting the §Concurrent Writers protocol:

1. **Hook regex misfires at harness invocation time.** Direct CLI tests of `hooks/merge-guard` against the exact `git merge --no-ff parallel/feedback/agent-dispatch-fixes/alpha -m "..."` command return `{}` (exempt, as intended). But when Claude Code's Bash tool ran the same command, the PreToolUse hook emitted the STOP reminder instead — fired on both alpha and beta merges. Reminder is advisory-only so the merges proceeded, but the exemption is not load-bearing in practice. Root cause likely a JSON-escaping / command-string difference in how the harness serializes to the hook's stdin. **Follow-up:** harden the hook's input parsing and add an integration test that invokes the hook through a Bash-tool-equivalent JSON wrapper.

2. **Both agents appending to RESULTS.md at EOF caused a real git conflict.** The plan's assumption that "task blocks are line-separated → different hunks = no conflict" held for PLAN.md (different task blocks mid-file, merged cleanly) but broke for RESULTS.md (both agents appended new sections at the end of the file; overlapping line range → conflict). Per §Concurrent Writers' discretion clause, this is a trivial adjacent-edit conflict — resolved inline by concatenating Task 7 then Task 8 sections. **Lesson for the protocol:** the ex-ante task-boundary contract must specify *where* each agent writes in shared files, not just *what* files they touch. For RESULTS.md: either pre-allocate per-task section stubs in the file before dispatch, or route RESULTS.md edits through the orchestrator after agents return.
