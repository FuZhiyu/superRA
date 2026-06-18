---
title: "result-protection"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

You get drift or regression tests that pin the numbers your paper depends on and fail loudly when a later change moves them. Reach for it when a result you care about — a coefficient from a regression three weeks ago, a headline spread — could be shifted by a refactor, a re-run on fresh data, or an edit to shared code without anyone noticing until a referee does.

The skill captures the key number and turns a silent regression into a visible test failure. It guards the results you confirm as key, not every intermediate number. See [`result-protection`](skills/result-protection/SKILL.md).
