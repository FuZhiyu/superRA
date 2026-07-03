---
title: "Task-Tree-Native Review Orchestration"
status: not-started
depends_on:
  - layout-and-coherence-refactor
---

## Objective

Revise the shipped literature-review skill and supporting tooling so reviews run as **superRA task-tree-native, paper-card-centered workflows**. The researcher-facing dashboard is the review root task plus promoted paper cards; pre-screen candidates are stored outside git as task-shaped candidate-paper folders and promoted into `superRA/` only after inclusion or explicit escalation.

### Required design

Implement the design now recorded on the parent `literature-review` task:

- The review root task is the live progress page: research question, criteria/schema, counts, active discovery/screening/extraction frontier, dedup conflicts, saturation evidence, and links to promoted paper cards.
- Discovery writes surfaced candidates into a project-convention, non-git candidate-paper store, not into `superRA/` as one task per candidate.
- Each candidate folder has a `task.md` with the same paper-card body template used after promotion. Promotion copies the folder into `superRA/<review>/papers/<paper-key>/` without schema conversion.
- Authoritative state is Markdown task-shaped records. Do not introduce JSON/JSONL as the candidate ledger or screening queue.
- PDFs and OCR output live in the project's durable paper/artifact store, or Zotero attachments when selected; candidate/paper records link to those artifacts rather than embedding binaries in the task tree.
- A simple materializer CLI creates/updates candidate folders from discovery metadata, computes consistent names, merges clear duplicates by DOI/arXiv/S2/title-year, and surfaces only ambiguous identity conflicts for orchestrator judgment.
- Only included papers, clearly central escalation cases, and final curated papers become promoted `superRA/<review>/papers/<paper-key>/task.md` cards.
- Screening can be batched as a dispatch strategy, but batch/tier labels must not become primary dashboard objects.
- The orchestrator's main decisions are synthesis, review, conflict resolution, saturation judgment, and researcher communication; ordinary dedup and candidate materialization are mechanism-owned.
- A recommended review tree may use `discovery/`, `screening/`, `papers/`, `synthesis/`, and `saturation-audit/` children, but the workflow must treat that as a flexible dashboard convention rather than a required schema.
- Dispatches may include `Recommended depth` and bounds. Depth can mean citation hops, reading depth, or both, as specified by the orchestrator. Agents may stop shallower when locally dry or use the recommended depth when high-signal leads remain, but they report unpursued leads instead of exceeding the bound.
- Discovery agents keep local agency: they return candidate records plus a local map/synthesis of clusters, authors, venues, adjacent literatures, and next leads. They stop on local diminishing returns for their assigned lens/seed, not global saturation.
- Screening agents decide membership and may do targeted verification searches for the candidate in hand. They may add directly relevant individual candidate records with provenance, but they do not launch a new search frontier inline; cluster-level opportunities become `Discovery Leads` for orchestrator prioritization.
- Discovery provenance for citation-based finds includes the source paper link and a quote from the citing/cited context that explains the edge, e.g. `Discovered via: [source paper](...)` plus a short quoted citation context.
- Implementers may create promoted paper tasks when inclusion is clear and the dispatch authorizes promotion. Review should be batched by discovery/screening/extraction packet, not one reviewer per candidate or paper by default.

### Files and stale instructions to update

Load `skill-creator` before editing skill files. Update at least:

- `skills/literature-review/references/workflow.md` — make the task-tree-native executor the main workflow; remove the old standalone executor, subtree-as-ledger alternative, tier language, and orchestrator-owned manual `seen`/admission framing.
- `skills/literature-review/SKILL.md` — revise ledger/schema language so it distinguishes non-git task-shaped candidate records from promoted paper cards; remove the stale "subtree-as-ledger for every considered paper" and standalone folder-ledger framing.
- Split `skills/literature-review/references/search-and-screening.md` if that keeps loader roles clearer. Discovery/search agents and screening agents should not have to read each other's full protocol when dispatched for one role.
- `skills/literature-review/references/citation-client.md` only if the command-surface docs imply JSON/JSONL as authoritative workflow state rather than tool I/O.
- `.agents/skills/literature-review/...` generated or synced copies, if this repository's generation/sync path requires them.

### Validation criteria

- A researcher can open the review root task in the dashboard and see real-time progress without navigating through pre-screen candidate noise.
- Candidate records before screening remain durable and auditable outside git, using the same Markdown `task.md` body template as promoted paper cards.
- Promotion from candidate store to `superRA/<review>/papers/<paper-key>/task.md` is copy/rename work, not schema conversion.
- Ordinary dedup is reproducible through the materializer; only flagged conflicts require orchestrator judgment.
- Search vs. screening responsibilities are separated: search discovers candidate records and local maps; screening decides membership, records batch synthesis, and routes new leads without recursively searching.
- Citation-edge provenance records a source paper link and exact quoted context when a paper is discovered through another paper.
- The workflow explains local stop rules for discovery agents and the screening-to-discovery loop through direct candidate adds vs. discovery leads.
- The reference load map clearly separates main-agent orchestration from discovery-agent, screening-agent, and extraction-agent instructions.
- `rg` over `skills/literature-review` no longer finds stale behavioral instructions for `subtree-as-ledger`, "one subtask per paper considered", `Tier-2`/`Tier-3`, or a standalone folder-ledger executor.
- Markdown checks and relevant skill-trigger / citation-client tests pass.

## Planner Guidance

Keep the implementation focused on the orchestration contract and the smallest tooling needed to materialize task-shaped candidate folders. Do not broaden into a dashboard redesign unless the current dashboard cannot show the review root counts and promoted paper-card links from ordinary task Markdown.
