# Process Issues Observed During the 17-Task Design-Coherence Refactor

Session date: 2026-04-16. Branch: `refactor/workflow-domain-split`. Context: executing PLAN.md's 17 tasks via `execution-workflow`; observed failure modes across dispatch, coordination, and workflow design. This doc is a triage list — each item is a candidate GitHub issue. Format: summary → repro → proposed fix.

---

## 1. Dispatch prompt rule is not strictly followed

**Summary.** The canonical dispatch template (`Stage:` / `Task:` / `Additionally:`, with the prefix "Follow the standard stage-relevant workflow …") is frequently violated by the orchestrator. Typical failures: over-engineered dispatches with 9+ numbered overrides, re-stating protocol the agent already reads from its file, duplicating PLAN.md task content, inlining skill/reference lists the manifest specifies, forgetting the canonical prefix.

**Repro.** First dispatch of this session listed 9 numbered overrides for a single-task implementer, 6 of which duplicated content the agent reads from `agents/implementer.md` + the manifest. User rebuke: "why you fail to follow the basic instruction on not to repeat standard instructions in dispatch though?"

**Proposed fix.** `agent-orchestration` §Dispatch Templates already forbids these things in its "Banned in dispatch prompts" list, but the orchestrator doesn't enforce self-check. Add a pre-dispatch validator: before calling `Agent()`, read the prompt and confirm (a) canonical prefix present, (b) `Additionally:` is ≤ 3 sentences, (c) no PLAN.md content restatement, (d) no manifest re-enumeration. Alternative: hook-based linting of dispatch prompts.

---

## 2. Task tools pressure conflicts with PLAN.md-as-record

**Summary.** The Claude Code system inserts "consider using TaskCreate to track progress" reminders even when the workflow is disciplined to treat PLAN.md as the source of truth. The nags imply TaskCreate tracking is the correct pattern, but superRA's principle #2 says the handoff doc is the record; TaskCreate is ephemeral session-local state. The user experienced the nags as noise and had to explicitly tell the orchestrator to "clean up" stale task-tracker entries from a prior team experiment.

**Repro.** After every tool-use gap of >10 minutes, the harness injects a reminder suggesting TaskCreate. During the session, a prior team's TaskCreate entries persisted and had to be manually deleted with TaskUpdate status=deleted.

**Proposed fix.** Document in `using-superRA` (or CLAUDE.md) that TaskCreate is for team-coordination only; PLAN.md is the authoritative record of work. Optionally suppress the system reminder via hook configuration for superRA sessions. At minimum, add a line to the system that says "When PLAN.md exists, TaskCreate is optional and must not duplicate PLAN.md's task blocks."

---

## 3. Git operations by subagents produce coordination failures

**Summary.** When two implementers run in parallel and both edit overlapping files, the agents race on `git add` / `git commit` / `git stash` operations. Observed failure modes: (a) Agent 1's save-restore dance (cp to /tmp, commit, cp back) overwrote Agent 2's newer working-tree edits; (b) `git add PLAN.md RESULTS.md` indiscriminately swept sibling agent's in-flight PLAN edits; (c) cross-commit attribution (Task 7 edits landed in Task 9's commit, etc.).

**Repro.** Agents 1 and 2 running Tasks 2/7/5/14 and 9/10/11/12 respectively. Agent 1 used `cp /tmp/claude/codebase-integration.md.task9` to restore Agent 2's edits it had saved aside — but the saved copy was stale, clobbering Agent 2's newer work. Agent 2 then saw "its edit disappeared" and almost escalated to `AskUserQuestion` before orchestrator intervened.

**Proposed fix.** Two options: (a) restrict git commit/stash to the orchestrator only; subagents edit files and return a status, orchestrator stages and commits — costs orchestrator-context bloat; (b) teach subagents to use `git stash push -- <specific files>` and `git add -- <specific files>` instead of cp dances, and always run `git status` + `git diff --name-only` before committing. Option (b) is lighter. Orthogonal fix: planning discipline to prevent parallel agents from sharing files.

---

## 4. Integration stop point is a single binary, not a merge-style menu

**Summary.** `execution-workflow` Step 4 presents a 4-option menu (merge locally / PR / keep / discard) at completion. This conflates two decisions: "proceed to integration-workflow?" (yes/no/discard) and "how to merge?" (local vs PR). The merge question belongs at the end of integration-workflow, not before it. Conflating them forces the researcher to commit to a merge method before integration review has even run — and integration review may turn up issues that change the right merge method.

**Repro.** User asked to "integrate" this session. The 4-option menu doesn't have "just integrate" as a choice. User had to type in "Other" with custom text. Decision had to be logged explicitly as a divergence from the menu.

**Proposed fix.** Split the Step 4 menu into two stops: (1) after execution complete, ask "proceed to integration, keep as-is, or discard?" — 3 options; (2) at end of integration-workflow, ask "merge locally, push PR, or keep on branch?" — 3 options. This matches the actual decision tree and lets integration findings inform the merge choice.

---

## 5. Agent Teams mode caused coordination chaos

**Summary.** Experimented briefly with `TeamCreate` during the session. Failure modes: teammates auto-claimed tasks out of dependency order (Tasks 13 and 8 grabbed before Task 1 APPROVED because `blockedBy` wasn't set at TeamCreate time); reviewer marked "review-T1 task" as completed when verdict was REVISE (status should be REVISE, not completed); duplicate tasks created (#15/#26 both `impl-T13`; #22/#27 both `review-T13`).

**Repro.** Team spawned for 17-task refactor. Tasks created via TaskCreate without `blockedBy` set before teammates started auto-claiming. By the time the orchestrator intervened, 3 teammates were working on tasks out of order. Had to send STOP messages, then shutdown_request, then TeamDelete.

**Proposed fix.** `references/agent-teams.md` already lists one-team-per-session and task-graph-construction rules, but the "Task creation order" rule ("Create the team BEFORE creating tasks") needs stronger enforcement — ideally the TaskCreate tool should refuse to create tasks without blockedBy set when a team exists. Alternatively, add a pre-team-spawn checklist step: "construct the full blocked-by graph in a draft file first, then TeamCreate, then TaskCreate in dependency order."

---

## 6. Cross-commit attribution from concurrent writes to shared docs

**Summary.** Distinct failure mode from #3. Even when two agents don't clobber each other's edits, if both write to PLAN.md and RESULTS.md and one commits with `git add PLAN.md RESULTS.md`, the commit pulls in the sibling's in-flight edits. Task 7's integration-workflow edits rode in Task 9's commit (5807f2d); Task 14's merge-workflow edits rode in Task 11+12's commit (261b712); Task 17's PLAN.md+RESULTS.md edits rode in Task 3's commit (5c9b55a). The record is preserved but attribution is wrong — `git log --follow` attributes each task's changes to a sibling's commit.

**Repro.** Agent 2's git commit in Task 17 staged only the code files (agent-orchestration/SKILL.md, execution-workflow/SKILL.md), not PLAN.md/RESULTS.md — because by the time it committed, Task 3 implementer had already swept its docs into 5c9b55a. Agent 2 returned DONE_WITH_CONCERNS flagging the atomicity split.

**Proposed fix.** Related to #3. Teach implementers to use `git add -p` for PLAN.md and RESULTS.md when parallel work is in-flight, staging only the hunks that belong to the current task. Or: serialize PLAN.md/RESULTS.md edits by file-lock convention when multiple agents run concurrently. Or: the "orchestrator-only commits" proposal from #3 would solve this.

---

## 7. Planning didn't catch duplication with integration-workflow

**Summary.** PLAN.md's Task 16 ("final consistency pass") duplicated what `integration-workflow` Stage 2 already does at merge time — inventory sync, cross-skill consistency checks, CHANGELOG update, grep sweep. The plan went through planning-workflow review without anyone noticing. Execution of Task 16 would have been ~hours of work redundant with the integration-review the workflow runs anyway.

**Repro.** User asked mid-execution: "why do we need task 16 though? It should be built in the integration stage so it's not needed." Orchestrator confirmed — Task 16's 6 steps map 1:1 onto integration-workflow Stage 2 + Step 3 sub-part B. Dropped it and logged the decision in `## Decisions`.

**Proposed fix.** Add a planning-workflow check (in Phase 2 plan drafting or Phase 3 self-review): "for each task, does its work overlap with what integration-workflow Stage 2 or Step 3 will do at merge time? If so, delete from PLAN — integration will do it." Alternatively, `planning-workflow/references/planning.md` could carry a "redundancy check" subsection listing workflow phases whose work should not appear in task blocks.

---

## 8. Plugin development is an unnamed vertical

**Summary.** `integration-workflow`'s "When to Lighten" section enumerates two adaptations — "standalone analysis (no existing codebase)" and "small changes" — but does NOT cover plugin development, even though the superRA repo IS the plugin being developed. The plugin has a drift-test analogue (`tests/structural-invariants.sh`) that no workflow skill points at. The integration review reviewer this session flagged the test file as failing precisely because no task propagated Task 1/3/6 changes into it — but the workflow itself never instructed the implementer to do that.

**Repro.** Stage 2 integration review caught 5 FAILs + 1 silently-stale PASS in `tests/structural-invariants.sh`. Tasks 1, 3, 6 all made structural changes that the tests assert, but no task had the test file in its Files-affected list.

**Proposed fix.** Either: (a) add a "Plugin development" row to `integration-workflow` §When to Lighten with a pointer to `tests/structural-invariants.sh` as the drift-test analogue; (b) create a full `skills/plugin-development/` domain skill in the roadmap; (c) in the meantime, document plugin-dev conventions in the repo-root `CLAUDE.md`. Related: Task 3's §Skill Types heading deletion contradicted a structural-invariants assertion, but no test-update ran.

---

## 9. Reviewer always-fresh rule has an unnamed exception

**Summary.** Task 17 introduced an "Agent reuse vs fresh dispatch" heuristic with a hard rule: **"Reviewers are adversarial by design … review passes always spawn a fresh reviewer agent; never send a review task to the implementer that just produced the work."** But in practice, this session reused the same reviewer via `SendMessage` across 3 review bundles (Tasks 1+8 review, Task 13 narrow re-review, Tasks 4/13/3/17/6 bundle review, Tasks 2/7/5/9/10/11/12/14 bundle). Warm-context reuse saved tokens but the adversarial property is weakened — the reviewer had seen earlier tasks' content and may carry forward unconscious priors.

**Repro.** The reviewer agent `ab3a78a…` was revived 4 times via SendMessage. Each revival brought full prior-session transcript into context. Token budgets for later reviews were far lower than a fresh dispatch would have been — but the reviewer is the same agent-instance across all four rounds.

**Proposed fix.** Decide explicitly. Either: (a) strengthen the rule ("reviewer must be freshly dispatched each review pass, no SendMessage revivals"); (b) soften and document the exception ("reviewer may be SendMessage-revived when reviewing NEW work the reviewer has not seen; must be fresh when re-reviewing its own prior REVISE verdicts"); (c) leave the rule as stated and treat SendMessage revival as a violation. Current ambiguity caused mid-session confusion about what "fresh" means.

---

## 10. Skill loading vs file reading is ambiguous for agents

**Summary.** Observed during mid-session user question: "why do agents read execution-workflow skill? it doesn't seem efficient." The answer was "they're Read-editing the file, not loading the skill" — but the distinction isn't documented. Agents could interpret "my task edits execution-workflow/SKILL.md" as "I need to load execution-workflow as a skill to understand it." That would be wasteful — the manifest specifies what to load for the Stage; the file is an edit target, not a skill to comprehend.

**Repro.** User observed the Task 7 implementer reading `execution-workflow/SKILL.md` multiple times and questioned whether the agent was wastefully full-loading the skill. Investigation confirmed it was just Edit/Read operations, not Skill tool invocations.

**Proposed fix.** Add a one-line clarification to `agents/implementer.md` Before-You-Start and `agents/reviewer.md` Before-You-Start: "Loading a skill (via the Skill tool or via your frontmatter) dumps its full body into your context. Reading a file (via the Read tool) only pulls the requested lines. When your task edits a skill file, `Read` it to see the content — do NOT invoke it as a Skill."

---

## Out of scope for this doc

The 11 REVISE findings from the Stage 2 integration review (committed as `f0b6e12`) are bugs in the refactor content itself, not process issues — they are documented in PLAN.md §Integration Review (Stage 2, post-refactor sweep) and being addressed by the refactorer subagent.
