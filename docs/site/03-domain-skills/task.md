---
title: "Domain Skills"
status: not-started
depends_on:  []
tags: []
created: 2026-06-17
---

## Objective

A domain skill gives the agent the methodology for your kind of research and gives the reviewer the standard to hold the work to. With a data task loaded, the agent describes the panel before it builds a variable, and the reviewer checks that it did; with a theory task, it defines its symbols before it manipulates them, and the reviewer checks that too. The discipline is the one you would apply by hand — superRA makes it run on every task and survive an adversarial second read.

## Data analysis — econ-data-analysis

You get an agent that always knows what it is holding before it changes it. The discipline at the center is the **Iron Law: describe the data before you transform it** — shapes, keys, distributions, missingness, balancedness come first, so the agent can't quietly drop half the sample on a bad merge and report that everything looked fine. Reach for it for any work on economic, financial, or panel data — importing, cleaning, merging, building variables, aggregating, running regressions, making figures — and especially when you hand the agent a data file whose structure it has not seen. The law sits inside a describe–analyze–validate loop, with pitfall catalogs for the operations that bite hardest: merges, time series, aggregations. It runs in Python, Julia, R, or Stata. See [`econ-data-analysis`](skills/econ-data-analysis/SKILL.md).

## Theory and modeling — theory-modeling

You get derivations a referee can audit line by line: every symbol defined, every assumption interpretable, every step justified. The discipline is **four gates, walked in the order your trust depends on: Objects & Notation → Assumptions → Derivations → Verification & Rendering.** You can't judge an assumption built on an undefined symbol, or a derivation without its active assumptions, so the agent defines objects, fixes assumptions, and only then manipulates equations. Reach for it when a task derives, solves, verifies, or proves something mathematical — stating assumptions, writing first-order conditions, solving an equilibrium, running comparative statics, checking a proof, or producing renderable model notes. It guards against the characteristic failure of machine-generated math: plausible algebra resting on a symbol that quietly means two things or an assumption back-filled after the fact.  See [`theory-modeling`](skills/theory-modeling/SKILL.md).

## Writing — writing

You get an editor that improves how your prose reads without touching what it argues. The discipline is one principle in three modes: **preserve substance, polish prose.** Your argument, structure, claims, and intent are sovereign; wording, flow, and mechanics are the editing target — if an edit would change substance, the agent stops and asks. The three modes — **Review** (find issues), **Polish** (edit within a fixed scope), **Draft** (write new prose) — share that principle and a set of consistency checks. Reach for it to draft, polish, proofread, or review prose a human will read — a manuscript section, an abstract, a response letter — in LaTeX, Markdown, Quarto, or plain text. This is the domain skill you'll most often invoke directly on your own manuscript, standalone, outside any task tree: point it at a section and ask it to review or polish. See [`writing`](skills/writing/SKILL.md).

## On the roadmap