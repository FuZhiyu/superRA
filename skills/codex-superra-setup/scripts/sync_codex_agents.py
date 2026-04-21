#!/usr/bin/env python3
"""Generate and install superRA Codex custom agents."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


MANAGED_HEADER = "# Managed by superRA codex-superra-setup. Do not edit by hand."


@dataclass(frozen=True)
class AgentSpec:
    source_md: str
    target_filename: str
    codex_name: str
    nickname_candidates: tuple[str, ...]


AGENT_SPECS = (
    AgentSpec(
        source_md="agents/implementer.md",
        target_filename="superra_implementer.toml",
        codex_name="superra_implementer",
        nickname_candidates=("implementer", "superra-implementer"),
    ),
    AgentSpec(
        source_md="agents/reviewer.md",
        target_filename="superra_reviewer.toml",
        codex_name="superra_reviewer",
        nickname_candidates=("reviewer", "superra-reviewer"),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate and install superRA Codex custom agents."
    )
    parser.add_argument(
        "--scope",
        choices=("project", "global"),
        required=True,
        help="Install into this repo's .codex/agents or into ~/.codex/agents.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Repo root containing agents/ and skills/.",
    )
    parser.add_argument(
        "--home-dir",
        type=Path,
        default=Path.home(),
        help="Home directory to use for global installs and tests.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check that target files match generated output without writing.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite conflicting unmanaged files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    target_dir = resolve_target_dir(args.scope, repo_root, args.home_dir.resolve())
    expected = render_all_agents(repo_root)

    if args.check:
        return run_check(target_dir, expected)

    target_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in expected.items():
        target_path = target_dir / filename
        if target_path.exists():
            existing = target_path.read_text(encoding="utf-8")
            if not is_managed(existing) and existing != content and not args.force:
                print(
                    f"Refusing to overwrite unmanaged file: {target_path}\n"
                    "Re-run with --force only after explicit user approval.",
                    file=sys.stderr,
                )
                return 1
            if existing == content:
                continue
        write_atomically(target_path, content)
        print(f"Wrote {target_path}")

    print(f"superRA Codex agents installed in {target_dir}")
    return 0


def resolve_target_dir(scope: str, repo_root: Path, home_dir: Path) -> Path:
    if scope == "project":
        return repo_root / ".codex" / "agents"
    return home_dir / ".codex" / "agents"


def render_all_agents(repo_root: Path) -> dict[str, str]:
    return {
        spec.target_filename: render_agent(repo_root, spec) for spec in AGENT_SPECS
    }


def render_agent(repo_root: Path, spec: AgentSpec) -> str:
    source_path = repo_root / spec.source_md
    _, description, body = read_agent_markdown(source_path)

    nicknames = ", ".join(f'"{nickname}"' for nickname in spec.nickname_candidates)
    instructions = (
        "This file is generated from superRA's canonical agent definition.\n"
        "It expects the superRA skills to be available in the parent session.\n"
        "If the skills are missing, stop and tell the user to install or enable the superRA plugin.\n\n"
        f"{body.rstrip()}"
    )

    return (
        f"{MANAGED_HEADER}\n"
        f"# Source: {spec.source_md}\n"
        "# Regenerate with: rerun superRA:codex-superra-setup\n\n"
        f'name = "{spec.codex_name}"\n'
        f'description = "{escape_toml_basic_string(description)}"\n'
        f"nickname_candidates = [{nicknames}]\n"
        "developer_instructions = '''\n"
        f"{instructions}\n"
        "'''\n"
    )


def read_agent_markdown(path: Path) -> tuple[str, str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path} is missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path} has unterminated YAML frontmatter")

    frontmatter = text[4:end]
    body = text[end + len("\n---\n") :].lstrip()
    name = parse_frontmatter_scalar(frontmatter, "name")
    description = parse_frontmatter_description(frontmatter)
    return name, description, body


def parse_frontmatter_scalar(frontmatter: str, key: str) -> str:
    prefix = f"{key}:"
    for line in frontmatter.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    raise ValueError(f"Missing {key}: in frontmatter")


def parse_frontmatter_description(frontmatter: str) -> str:
    lines = frontmatter.splitlines()
    capture = False
    parts: list[str] = []
    for line in lines:
        if capture:
            if line.startswith("  "):
                stripped = " ".join(line.strip().split())
                if stripped:
                    parts.append(stripped)
                continue
            break
        if line.startswith("description:"):
            remainder = line.split(":", 1)[1].strip()
            if remainder in {">", "|"}:
                capture = True
            elif remainder:
                parts.append(" ".join(remainder.split()))
                break
    if not parts:
        raise ValueError("Missing description in frontmatter")
    return " ".join(parts)


def escape_toml_basic_string(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def is_managed(text: str) -> bool:
    return text.startswith(MANAGED_HEADER)


def write_atomically(path: Path, content: str) -> None:
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(content, encoding="utf-8")
    temp_path.replace(path)


def run_check(target_dir: Path, expected: dict[str, str]) -> int:
    failures = 0
    for filename, content in expected.items():
        target_path = target_dir / filename
        if not target_path.exists():
            print(f"Missing generated agent file: {target_path}", file=sys.stderr)
            failures += 1
            continue
        existing = target_path.read_text(encoding="utf-8")
        if existing != content:
            print(f"Generated agent drift: {target_path}", file=sys.stderr)
            failures += 1
    if failures:
        return 1
    print(f"All generated agent files are up to date in {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
