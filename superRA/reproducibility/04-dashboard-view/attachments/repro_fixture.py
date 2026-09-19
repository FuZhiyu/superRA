#!/usr/bin/env python3
"""Build the fixture project the Reproduction view's manual pass was recorded on.

16 shell steps across 4 owner tasks, laid out as a plausible asset-pricing
pipeline, then driven into a state that puts all five step states plus a check
step on screen at once:

  external  fetch-treasury reads a raw file that is not on disk
  sidecar   lag-returns tracks its out through a companion hash file
  failed    bootstrap-se exits 1
  stale     fm.sh is touched after the build, so fama-macbeth and its
            descendants no longer match the lock
  missing   the 04-figures lane is outside the build targets, so it is never built
  fresh     everything else

Usage:
    python3 repro_fixture.py <dir>          # write the project, build it
    python3 repro_fixture.py <dir> --no-build

Then serve it:
    superra dashboard --root <dir>/superRA --port 8996 --no-open
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

CONFIG = """\
reproduction:
  vars:
    DATA: data
    OUT: build
  runners:
    sh: sh {script}
  env_deps:
    - env.lock
"""

BUILT = ("01-ingest", "02-panel", "03-estimation")  # 04-figures stays never-built

TASKS = {
    "01-ingest": (
        "Ingest Raw Vendor Extracts",
        """\
  - name: fetch-crsp
    runner: sh
    script: code/fetch_crsp.sh
    deps:
      - "${DATA}/crsp_raw.csv"
    outs:
      - "${OUT}/crsp.csv"
  - name: fetch-compustat
    runner: sh
    script: code/fetch_compustat.sh
    deps:
      - "${DATA}/compustat_raw.csv"
    outs:
      - "${OUT}/compustat.csv"
  - name: fetch-treasury
    runner: sh
    script: code/fetch_treasury.sh
    deps:
      - "${DATA}/treasury_raw.csv"
    outs:
      - "${OUT}/treasury.csv"
  - name: check-ingest
    kind: check
    runner: sh
    script: code/check_ingest.sh
    deps:
      - "${OUT}/crsp.csv"
      - "${OUT}/compustat.csv"
""",
    ),
    "02-panel": (
        "Build the Firm-Month Panel",
        """\
  - name: merge-panel
    runner: sh
    script: code/merge_panel.sh
    deps:
      - "${OUT}/crsp.csv"
      - "${OUT}/compustat.csv"
    outs:
      - "${OUT}/panel.csv"
  - name: winsorize
    runner: sh
    script: code/winsorize.sh
    deps:
      - "${OUT}/panel.csv"
    outs:
      - "${OUT}/panel_trimmed.csv"
  - name: lag-returns
    runner: sh
    script: code/lag_returns.sh
    deps:
      - "${OUT}/panel_trimmed.csv"
    outs:
      - path: "${OUT}/panel_lagged.csv"
        sidecar: "${OUT}/panel_lagged.csv.sha256"
  - name: check-panel
    kind: check
    runner: sh
    script: code/check_panel.sh
    deps:
      - "${OUT}/panel_lagged.csv"
""",
    ),
    "03-estimation": (
        "Cross-Sectional Estimation",
        """\
  - name: fama-macbeth
    runner: sh
    script: code/fm.sh
    deps:
      - "${OUT}/panel_lagged.csv"
    outs:
      - "${OUT}/fm_coefs.csv"
  - name: portfolio-sorts
    runner: sh
    script: code/sorts.sh
    deps:
      - "${OUT}/panel_lagged.csv"
    outs:
      - "${OUT}/sorts.csv"
  - name: bootstrap-se
    runner: sh
    script: code/bootstrap.sh
    deps:
      - "${OUT}/fm_coefs.csv"
    outs:
      - "${OUT}/fm_se.csv"
  - name: check-estimation
    kind: check
    runner: sh
    script: code/check_estimation.sh
    deps:
      - "${OUT}/fm_se.csv"
""",
    ),
    "04-figures": (
        "Figures and Appendix Tables",
        """\
  - name: fig-coefs
    runner: sh
    script: code/fig_coefs.sh
    deps:
      - "${OUT}/fm_coefs.csv"
    outs:
      - "${OUT}/fig_coefs.pdf"
  - name: fig-sorts
    runner: sh
    script: code/fig_sorts.sh
    deps:
      - "${OUT}/sorts.csv"
    outs:
      - "${OUT}/fig_sorts.pdf"
  - name: table-summary
    runner: sh
    script: code/table_summary.sh
    deps:
      - "${OUT}/panel_lagged.csv"
    outs:
      - "${OUT}/tab_summary.tex"
  - name: assemble-appendix
    runner: sh
    script: code/assemble.sh
    deps:
      - "${OUT}/fig_coefs.pdf"
      - "${OUT}/fig_sorts.pdf"
      - "${OUT}/tab_summary.tex"
    outs:
      - "${OUT}/appendix.pdf"
""",
    ),
}

# script name -> (output it writes, exit code)
SCRIPTS = {
    "fetch_crsp.sh": ("build/crsp.csv", 0),
    "fetch_compustat.sh": ("build/compustat.csv", 0),
    "fetch_treasury.sh": ("build/treasury.csv", 0),
    "check_ingest.sh": (None, 0),
    "merge_panel.sh": ("build/panel.csv", 0),
    "winsorize.sh": ("build/panel_trimmed.csv", 0),
    "lag_returns.sh": ("build/panel_lagged.csv", 0),
    "check_panel.sh": (None, 0),
    "fm.sh": ("build/fm_coefs.csv", 0),
    "sorts.sh": ("build/sorts.csv", 0),
    "bootstrap.sh": ("build/fm_se.csv", 1),
    "check_estimation.sh": (None, 0),
    "fig_coefs.sh": ("build/fig_coefs.pdf", 0),
    "fig_sorts.sh": ("build/fig_sorts.pdf", 0),
    "table_summary.sh": ("build/tab_summary.tex", 0),
    "assemble.sh": ("build/appendix.pdf", 0),
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_project(root: Path) -> None:
    plan_root = root / "superRA"
    write(plan_root / "config.yaml", CONFIG)
    write(
        plan_root / "task.md",
        "---\ntitle: \"Cross-Sectional Anomaly Replication\"\nstatus: in-progress\n"
        "depends_on: []\n---\n\n## Objective\n\nA fixture project for the "
        "Reproduction dashboard view.\n",
    )
    for slug, (title, steps) in TASKS.items():
        body = (
            f"---\ntitle: \"{title}\"\nstatus: in-progress\ndepends_on: []\n---\n\n"
            f"## Objective\n\n{title}.\n\n## Reproduction\n\n```yaml\n"
            f"steps:\n{steps}```\n"
        )
        write(plan_root / slug / "task.md", body)

    for name, (out, code) in SCRIPTS.items():
        lines = ["#!/bin/sh", "set -e"]
        if out:
            lines += [f"mkdir -p $(dirname {out})", f"echo \"$(date +%s%N)\" > {out}"]
        else:
            lines.append(f"echo 'checked {name}'")
        if code:
            lines += ["echo 'bootstrap did not converge: singular covariance' >&2",
                      f"exit {code}"]
        write(root / "code" / name, "\n".join(lines) + "\n")

    # `${DATA}/treasury_raw.csv` is deliberately absent, so fetch-treasury has
    # an external input it cannot satisfy.
    write(root / "data" / "crsp_raw.csv", "permno,date,ret\n10001,199401,0.03\n")
    write(root / "data" / "compustat_raw.csv", "gvkey,datadate,at\n001004,19940131,412.5\n")
    write(root / "env.lock", "sh 5.2\n")


def run(root: Path, cli: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(cli), "--plan-root", str(root / "superRA"), *args],
        cwd=root, capture_output=True, text=True,
        env={**os.environ, "SUPERRA_REPRO_REEXEC": ""},
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--cli", default="", help="path to skills/task-tree/scripts/repro_run.py")
    ap.add_argument("--no-build", action="store_true")
    args = ap.parse_args()

    root = Path(args.dir).resolve()
    build_project(root)
    print(f"fixture project at {root}")
    if args.no_build:
        return

    cli = Path(args.cli).resolve() if args.cli else None
    if cli is None:
        print("pass --cli <path to repro_run.py> to drive the build", file=sys.stderr)
        return
    print(run(root, cli, "build", *BUILT).stdout)
    # Touch one script after the build so its step and descendants read stale.
    time.sleep(1.1)
    (root / "code" / "fm.sh").write_text(
        (root / "code" / "fm.sh").read_text() + "# re-specified with a 60-month window\n"
    )
    print(run(root, cli, "status", ".").stdout)


if __name__ == "__main__":
    main()
