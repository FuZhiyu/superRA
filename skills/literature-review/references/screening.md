# Screening Agent Protocol

Implementer reference. Load when a dispatch asks you to screen candidate-paper records for inclusion.

Your job is to decide membership for assigned candidates and record the rationale. You may verify facts needed for the decision; do not launch a new search frontier inline.

## Screening Scope

Screen only the candidate records assigned in the dispatch. Use metadata, abstract, and introduction for routine inclusion/exclusion. Read deeper only when all hold:

1. the paper is central;
2. it is clearly included or strongly ambiguous;
3. its related-work / citation discussion affects promotion, expansion priority, or the screening decision.

Record deeper reading as `read_depth` plus a one-line reason. Keep OCR for extraction of included central papers.

## Decision Record

For each candidate, update its task-shaped record with:

- `decision: included`, `excluded`, or `escalate`;
- one-line reason;
- failed inclusion gate when excluded;
- outlet tier and identification strategy when applicable (see [econ-corpus.md](econ-corpus.md));
- promotion recommendation;
- any retrieval trace updates found during targeted verification.

When the dispatch authorizes promotion and inclusion is clear, create the promoted paper card by copying the candidate folder into `superRA/<review>/papers/<paper-key>/`. Do not change the body schema during promotion.

## Targeted Verification

You may search narrowly to support the candidate's own decision:

- resolve DOI or published version;
- locate abstract, introduction, landing page, or PDF;
- check whether two records are the same paper;
- verify metadata needed for the inclusion gate.

If screening surfaces a relevant new paper:

- **Direct add to candidate store** when it is a specific paper needed to judge the current candidate, has a clear handle, and is within scope. Record provenance and stop there.
- **Discovery lead** when it suggests a cluster, author trail, method family, or adjacent literature. Add it under `## Discovery Leads` in the screening task or review root for the main agent to prioritize.
- **Promote immediately** only when the dispatch authorizes promotion and the paper is clearly included and central.

Screening may add individual candidate records. Screening may not launch broad search from those records.

## Batch Synthesis

End every screening task with:

```markdown
## Batch Synthesis

### Included themes

### Main exclusion reasons

### Ambiguous cases

### Promotion recommendations

### Discovery Leads
```
