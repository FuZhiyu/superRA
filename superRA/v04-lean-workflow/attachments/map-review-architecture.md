# Map: Current Review Architecture (v0.3.3 baseline)

Hand-authored from a read-only exploration agent dispatch, 2026-08-01, against this worktree at commit `ec5a4897`. Line numbers refer to that baseline and drift as files change; section anchors are the durable reference.

## 1. Role specs and plumbing

**`agents/implementer.md`** (130 lines): frontmatter `tools:` + `skills: [superRA:using-superra, superRA:report-in-markdown]` autoload pair; §Before You Start; §Execution Protocol; §Self-Check (5 gates); §Handoff (§What You Own :62-71 — `## Results`, status up to `implemented`, `→ implemented:` annotations; at `Stage: integration` only, authoring new `## Review Notes` from a self-review first pass :69); §How You Fix Review Items on a REVISE Round :73-95 (worked example uses `[MAJOR]`/`[MINOR]`); §Commit; §Report Format :108-116 (`DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT` + SHA only); §Escalation.

**`agents/reviewer.md`** (121 lines): frontmatter description :4-6 encodes protocol + "Adversarial by design" (copied verbatim into Codex TOML). Adversarial preamble :11-13; §Review Protocol :22-52 (severities :32-42 — CRITICAL invalidates result / MAJOR likely problem, evidence gap, deviation, other failed `[BLOCKING]` / MINOR incomplete compliance, `[ADVISORY]` items; verdict :44-52 — APPROVE sets `approved` + removes `## Revision Notes`; REVISE on CRITICAL/MAJOR or failed `[BLOCKING]`); §Self-Check; §Handoff (re-review mechanics :90-103, narrow re-review scope :101, "CRITICAL cannot be silently overridden" :103); §Report Format :115-121 (Assessment + SHA).

**Codex generation**: `skills/codex-superra-setup/scripts/sync_codex_agents.py` consumes both role specs (`ROLE_SPECS` :23-36, frontmatter name/description + full body) → produces `.codex/agents/superra_implementer.toml` / `superra_reviewer.toml` (or global `~/.codex/agents/`), `developer_instructions` wraps the body; `--check` drift detection; tests in `test_sync_codex_agents.py`. Removing a role touches: `ROLE_SPECS`, `codex-superra-setup/SKILL.md` (:8,15-16,61-62,70,76), `CLAUDE.md:147`, `codex-instructions.md` (routing table + tool map :77-79), the generator tests.

**Canonical-role resolution** (main-filled seats): `using-superra/references/canonical-role.md` → `scripts/resolve_role.py` (choices hardcoded `implementer|reviewer` :12, resolves `<repo>/agents/<role>.md` :18) + `test_resolve_role.py`.

## 2. Review choreography in superimplement

`skills/superimplement/SKILL.md` §Task Execution Steps :71-77 — the unconditional mandate:

- :73 seat structure via `agent-orchestration`; :74 execute implementer seat.
- :76 "Once DONE or DONE_WITH_CONCERNS: execute the reviewer seat for one comprehensive task-local pass per assigned task. On REVISE, adjudicate... and iterate until APPROVE."
- :77 "a generic APPROVE with no file/line citations is a red flag — rerun the reviewer seat"; per-task `status: approved` required in bundles.

No conditional exists in subagent mode. Frontier gating (:69): `task frontier` lists leaves whose deps are all `approved` — review is structurally the gate on downstream dispatch (same at `main-agent.md:16`).

Step 3 verification gate :97-117 includes :113 "Deferred MINORs resolved?" — resurrects non-blocking MINORs at phase end (pedantry amplifier). :149 workflow-specific review scope; :159 "Blocking reviewer findings are not a stop point — adjudicate and fix through the REVISE loop without asking the user."

**Existing flexibility**: §Execution Modes :12-14 (subagent default, interactive opt-in); :90 interactive routes to `superplan/references/interactive-mode.md`; seat assignment lets the main agent fill either seat (no main/main row); `agent-orchestration:118` inline-approve escape hatch for tiny fixes.

**`main-agent.md` §Execution Modes :42-56**: two dials (cadence, seat assignment); subagent mode default; interactive = fused light-plan → execute-yourself → record loop, "asks the researcher whether to dispatch a reviewer rather than dispatching on its own" (:52).

**`superplan/references/interactive-mode.md`** — the elective-review precedent: :3 "review is prompted, not automatic"; :16 role specs not loaded; :19 "Self-review always... Apply every [BLOCKING] item"; :22-24 "Ask before review, with a tool — required... review now / defer / skip. Never dispatch a reviewer on your own read of the situation." Defer/skip leaves the task at `implemented`.

## 3. Review gates elsewhere

### 3a. Planning review (superplan)

- `superplan/SKILL.md` §Agent Review :72-89: dispatched only at thorough depth; :87 REVISE fixed before User Review; :89 skip at quick/standard unless explicitly requested — already conditional.
- `references/planning-review.md`: two modes (handoff-readiness / design-review); :18 planning review never edits `status:`; uses `[BLOCKING]`/`[ADVISORY]` — a second severity vocabulary.
- `references/decomposition.md` §Self-Review :48-62: 9-item planner self-check, "fix inline, no re-review."

### 3b. Integration-stage reviews (superintegrate)

`superintegrate/SKILL.md:51`: any REVISE at any step iterates until APPROVE. Per step: Protect — conditional creator+reviewer dispatch (`protect.md:30`); Sync — generic (non-role-spec) author + reviewer agents, trivial sync skips both (`sync.md:50,79-105`) — proves generic-agent dispatch works; Mature & Consolidate — one reviewer at `Stage: maturation` that also authors the temp refactor task (`mature-consolidate.md:32-53`); Integrate — reviewer at `Stage: integration`, iterate to `approved` (`integrate.md:46-60`); Finish — none.

### 3c. Gated checklist inventory (`[BLOCKING]` counts per file)

| File | Items | Loaded at |
|---|---|---|
| `econ-data-analysis/SKILL.md` | 66 | domain load |
| `econ-data-analysis/references/integration.md` | 14 | integration |
| `theory-modeling/SKILL.md` | 45 | domain load |
| `theory-modeling/references/integration.md` | 25 | integration |
| `refactor-and-integrate/SKILL.md` | 20 (:99-135) | integration |
| `result-protection/SKILL.md` | 3 (+12 in `drift-test-quality.md`) | protection |
| `semantic-merge/SKILL.md` | 22 | sync |
| `slide-design/SKILL.md` | 12 | domain load |
| `writing/references/refactor-and-compile.md` | 19 | polish/draft/review |
| `writing/references/integration.md` | 8 | integration (writing) |
| `writing/references/consistency/*.md` (8 files) | 8–11 each | review/polish lanes |
| `superplan/references/planning-review.md` | 2 | planning-review |
| `CLAUDE.md:48` | 2 (DRY/Necessity meta-gate) | contributor work |

Three severity vocabularies coexist: CRITICAL/MAJOR/MINOR (reviewer.md), `[BLOCKING]`/`[ADVISORY]` (checklists, planning review), mechanical/conventional/authorial (writing review fix tiers).

## 4. Pedantry-driving lines (quoted)

- `agents/reviewer.md:13`: "Be thorough and adversarial... When uncertain whether something is a problem, flag it — the orchestrator filters false positives... A missed real issue is far worse than a flagged non-issue."
- `agents/reviewer.md:46` (+ :86): "Walk the gates of every skill you loaded — stage and domain — top to bottom... Never halt on a failure... one comprehensive pass of findings."
- `agents/reviewer.md:24`: "Do not take the implementer's word... agents can report 'success' for partial work."
- `agents/reviewer.md:42`: format check — "note 'not applicable' with reasoning — do not silently skip."
- `agents/reviewer.md:59-60`: every material finding written into `## Review Notes`.
- `superimplement/SKILL.md:77`: rerun reviewer on citation-less APPROVE; `:113`: deferred-MINOR resurrection.
- `agent-orchestration/SKILL.md:40`: adversarial first-pass reviews get higher model tier; `:92`: "high-stakes work where the main context should carry adversarial review."
- `CLAUDE.md:48`: reviewers verify DRY/Necessity "line by line on every pass."
- `refactor-and-integrate/SKILL.md:43`: "Walk the governing diff hunk by hunk"; `:97` missing self-check trail is `[BLOCKING]` "including when no code changed."
- `writing/references/consistency/*.md:3` (8 files): "[BLOCKING] items must be reported."
- Calibrated-downward exception (the one that exists): `econ-data-analysis/SKILL.md:40` "[ADVISORY] — reviewer MAY flag as MINOR; does not block APPROVE" (mirrored in theory-modeling:46, refactor-and-integrate:101, slide-design:73).

## 5. agent-orchestration

`skills/agent-orchestration/SKILL.md` (119 lines; hook-gated load for superimplement/superintegrate). §Workload Balancing :12-40 (3 tiers + model-tier selection); §Dispatch Templates :50-83 (canonical template shape; :56 "never assign a `name:` to a role agent — a named Agent call silently drops the `subagent_type` role spec"; reviewer template adds `Git range:`); §Seat Assignment :85-95 (3 rows, no main/main); §Orchestrator Duties :97-104; §Handling Reviewer Feedback :106-118 (adjudicate before forwarding — accept/reject/escalate; :116 warm-agent steering via SendMessage; :118 inline-approve for tiny fixes). `references/agent-teams.md` is ARCHIVED (do not load).

## 6. Files that change for dynamic review + skill-based roles

**Tier 1 core protocol**: `agents/reviewer.md`, `agents/implementer.md` (→ role skills), `superimplement/SKILL.md` (:12-14, :69-77, :79-86, :88-95, :113, :149, :159, :163), `agent-orchestration/SKILL.md` (:40, :50-83, :85-95, :106-118), `using-superra/references/main-agent.md` (:14-18, :30-39, :42-56), `using-superra/SKILL.md` (§Execution Modes pointer, §Skill-Load Manifest — `subagent_type` no longer encodes role).

**Tier 2 workflow gates**: `superplan/SKILL.md` §Agent Review + `references/planning-review.md`, `interactive-mode.md` (generalization source), `thorough-planning.md:86-88`, `decomposition.md:48-62`; `superintegrate/SKILL.md:47-60` + `references/{protect,sync,mature-consolidate,integrate}.md`.

**Tier 3 checklist severity**: the §3c inventory.

**Tier 4 plumbing**: `sync_codex_agents.py` + tests + `codex-superra-setup/SKILL.md`; `.codex/agents/*.toml`; `resolve_role.py` + tests + `canonical-role.md` + `claude-instructions.md` + `codex-instructions.md` (:12-34, :55-66, :67-81); `task-file-contract.md` (:19 status co-ownership, :24-27 section ownership); `hooks/ensure-agent-orchestration` if the gate changes; `handoff-doc/SKILL.md:10` redirect.

**Tier 5 docs/tests**: `CLAUDE.md` (:35 "Gates are local discipline... enforced" — the principle that directly contradicts optional review; :48; :79-92 ownership table; :96-130 Agent Load Surface; :147 generated artifacts; :164 audit checklist); `README.md:12,20,26,31-32`; `skills/CATEGORIES.md`; `docs/site/**` implement/integrate pages; plugin manifests ("implementer–reviewer pair" descriptions); `tests/harness-instruction-following/` (`load_contract.json` cites role-spec line ranges, `sdk_load_evidence.py:314` `ROLE_SPEC_FILES`, `transcript_assertions.py:363,425-426`, `codex_load_evidence.py:226-227`, smoke + stage/domain live tests + fixtures).

**Key tensions**: `CLAUDE.md:35` must be revised alongside the policy change; `agent-orchestration:56` (named dispatch drops `subagent_type`) makes skill-loaded generic agents the default-safe path, since a generic agent has no `subagent_type` to lose.
