#!/usr/bin/env python3
"""Resolve a canonical superRA role spec from the installed plugin package."""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("role", choices=("implementer", "reviewer"))
    return parser.parse_args()


def resolve_role_path(role: str, *, script_path: Path = Path(__file__)) -> Path:
    repo_root = script_path.resolve().parents[3]
    role_path = (repo_root / "agents" / f"{role}.md").resolve()
    if not role_path.is_file():
        raise FileNotFoundError(f"Missing canonical role spec: {role_path}")
    return role_path


def main() -> int:
    print(resolve_role_path(parse_args().role))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
