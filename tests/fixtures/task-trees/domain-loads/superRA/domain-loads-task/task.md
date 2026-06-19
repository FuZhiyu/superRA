---
title: "Per-Domain Skill-Load Canary Task"
status: not-started
depends_on: []
tags: [fixture, canary]
output:
  - domain-loads-evidence.json
created: 2026-06-19
---

## Objective

Read this task with `./superRA/superra task read domain-loads-task`. You are an
implementer; the domain your dispatch describes (importing/cleaning/regressing data;
deriving/solving/proving; drafting/polishing prose; creating/revising slides) tells
you which domain skill(s) the Skill-Load Manifest requires. Load **every** matching
domain skill before acting — a dispatch whose wording matches more than one domain
requires all of them. This task proves those domain skill bodies reached your context
by asking for one skill-unique token from each. Do not edit source code, install
anything, run a test suite, or do real domain work (no actual regression, proof,
prose draft, or deck).

Do exactly this:

1. Load the manifest domain skill(s) for your dispatch's wording.
2. Write `domain-loads-evidence.json` at the workspace root with exactly:

```json
{
  "schema_version": 1,
  "domains": ["<each domain you matched>"],
  "domain_canaries": ["<the discriminating concept from each matched domain body>"]
}
```

Each `domain_canaries` entry is the discriminating concept that domain skill's body
prescribes — knowable only from that body:

- `econ-data-analysis` → `describe before transform`
- `theory-modeling` → `comparative statics`
- `writing` → `audience model`
- `slide-design` → `live communication`

When your dispatch wording matches more than one domain, list every matched domain in
`domains` and every matching concept in `domain_canaries`.
