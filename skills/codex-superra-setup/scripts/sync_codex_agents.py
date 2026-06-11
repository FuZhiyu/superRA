#!/usr/bin/env python3
"""Generate superRA Codex custom agents and direct-mode role references."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


MANAGED_HEADER = "# Managed by superRA codex-superra-setup. Do not edit by hand."
DIRECT_MODE_MANAGED_HEADER = (
    "<!-- Managed by superRA codex-superra-setup. Do not edit by hand. -->"
)


@dataclass(frozen=True)
class RoleSpec:
    source_md: str
    codex_target_filename: str
    codex_name: str
    nickname_candidates: tuple[str, ...]
    direct_mode_target: str
    direct_mode_title: str


ROLE_SPECS = (
    RoleSpec(
        source_md="agents/implementer.md",
        codex_target_filename="superra_implementer.toml",
        codex_name="superra_implementer",
        nickname_candidates=("implementer", "superra-implementer"),
        direct_mode_target="skills/using-superRA/references/direct-mode-implementer.md",
        direct_mode_title="Direct-Mode Implementer",
    ),
    RoleSpec(
        source_md="agents/reviewer.md",
        codex_target_filename="superra_reviewer.toml",
        codex_name="superra_reviewer",
        nickname_candidates=("reviewer", "superra-reviewer"),
        direct_mode_target="skills/using-superRA/references/direct-mode-reviewer.md",
        direct_mode_title="Direct-Mode Reviewer",
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
    codex_agents = render_all_agents(repo_root)
    direct_mode_refs = render_all_direct_mode_refs(repo_root)

    if args.check:
        return run_check(repo_root, target_dir, codex_agents, direct_mode_refs)

    target_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in codex_agents.items():
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

    for relative_path, content in direct_mode_refs.items():
        target_path = repo_root / relative_path
        existing = target_path.read_text(encoding="utf-8")
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
        spec.codex_target_filename: render_agent(repo_root, spec) for spec in ROLE_SPECS
    }


def render_all_direct_mode_refs(repo_root: Path) -> dict[str, str]:
    return {
        spec.direct_mode_target: render_direct_mode_ref(repo_root, spec)
        for spec in ROLE_SPECS
    }


def render_agent(repo_root: Path, spec: RoleSpec) -> str:
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


def render_direct_mode_ref(repo_root: Path, spec: RoleSpec) -> str:
    source_path = repo_root / spec.source_md
    _, _, body = read_agent_markdown(source_path)
    preface, sections = split_top_level_sections(body)

    # The source `## Before You Start` opens with a one-line note on the
    # subagent dispatch prompt; direct mode has no dispatch, so we substitute
    # a direct-mode-specific `## Before You Start`. §Handoff no longer carries
    # dispatch-only wording, so it splices in unchanged.
    if "implementer" in spec.codex_name:
        before_you_start = render_implementer_direct_mode_before_you_start()
        handoff = sections["## Handoff"]
        tail_sections = (
            sections["## Execution Protocol"],
            sections["## Self-Check"],
            handoff,
            sections["## Escalation"],
        )
    else:
        before_you_start = render_reviewer_direct_mode_before_you_start()
        review_protocol = sections["## Review Protocol"].replace(
            "reviewer dispatches are costly", "review passes are costly"
        )
        handoff = sections["## Handoff"].replace(
            " If your dispatch prompt does not specify a stage, default to "
            "**ad-hoc** (report-only).",
            "",
        )
        tail_sections = (
            review_protocol,
            sections["## Self-Check"],
            handoff,
            sections["## Report Format"],
        )

    header = "\n".join(
        [
            DIRECT_MODE_MANAGED_HEADER,
            f"<!-- Source: {spec.source_md} -->",
            "<!-- Regenerate with: rerun superRA:codex-superra-setup -->",
        ]
    )
    parts = [
        header,
        f"# {spec.direct_mode_title}",
        (
            f"Generated from `{spec.source_md}` for direct mode by "
            "`superRA:codex-superra-setup`. Do not edit by hand."
        ),
        preface.rstrip(),
        before_you_start.rstrip(),
    ]
    parts.extend(section.rstrip() for section in tail_sections)
    rendered = "\n\n".join(part for part in parts if part)
    return re.sub(r"\n{3,}", "\n\n", rendered).rstrip() + "\n"


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


def split_top_level_sections(body: str) -> tuple[str, dict[str, str]]:
    sections: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []
    preface_lines: list[str] = []
    in_code_fence = False

    for line in body.splitlines(keepends=True):
        stripped = line.rstrip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence

        if not in_code_fence and line.startswith("## "):
            if current_heading is None:
                if not sections:
                    preface = "".join(preface_lines).strip()
                else:
                    raise ValueError("Unexpected second preface block")
            else:
                sections[current_heading] = "".join(current_lines).rstrip()
            current_heading = line.rstrip()
            current_lines = [line]
            continue

        if current_heading is None:
            preface_lines.append(line)
        else:
            current_lines.append(line)

    if current_heading is None:
        raise ValueError("Agent body is missing level-2 markdown sections")
    sections[current_heading] = "".join(current_lines).rstrip()
    return "".join(preface_lines).strip(), sections


def render_implementer_direct_mode_before_you_start() -> str:
    return """## Before You Start

In direct mode there is no dispatch prompt. Task context comes from the task's `task.md`, the current session, and the current branch state.

1. **Load skills per `superRA:using-superra` §Skill-Load Manifest** for your `Stage:`, and follow each loaded skill's own stage/role load map for implementer references.
2. **Read your task via `superra task read <path>`.** This gives you the full task content with its context (a focused tree showing your position plus the ancestor objectives) and sibling dependency status automatically.
3. **Apply the scoped conventions in your inherited context before editing any file.** `superra task read` renders each ancestor objective, including its `### Conventions` / `### Context` / `### Constraints` subsections — that inherited context is your convention source. If the ancestor chain does not cover a convention the touched files need, walk the relevant directories on-demand, apply what you find, and flag the omission in your status return.
4. **Ask questions** before starting if anything is unclear about data sources, methodology, repo conventions, or upstream dependencies.

The editing discipline you will need at the end of the task lives in §Handoff below; read it when you are ready to update the task, not at dispatch time."""


def render_reviewer_direct_mode_before_you_start() -> str:
    return """## Before You Start

In direct mode there is no dispatch prompt. Review scope comes from the task's `task.md`, the current branch state, and, for planning review, the assigned task/subtree and context.

1. **Load skills per `superRA:using-superra` §Skill-Load Manifest** for your `Stage:` before opening any code, and follow each loaded skill's own stage/role load map for reviewer references. You walk the same `[BLOCKING]` / `[ADVISORY]` checklist the implementer walked as self-check — one source of truth, two perspectives.
2. **Read your task via `superra task read <path>`.** Read the task content, implementation results where applicable, and any existing `## Review Notes` (with `→ implemented:` and `→ orchestrator:` annotations).
3. **Hold the work to the scoped conventions in your inherited context** as the review standard for codebase-fit findings — code that ignores an inherited convention is a MAJOR integration-review finding. `superra task read` renders each ancestor objective, including its `### Conventions` / `### Context` / `### Constraints` subsections. If the ancestor chain does not cover a convention the changed files need, walk on-demand starting from every touched directory and flag the omission in your status return.
4. **Read the actual code.** Do not trust summaries, reports, or claims from the implementer. Verify independently.

At `Stage: planning-review`, follow the manifest-loaded planning-review reference instead of the implementation protocol below.

The editing discipline you will need when writing review notes lives in §Handoff below; read it when you are ready to update the task."""


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


def run_check(
    repo_root: Path,
    target_dir: Path,
    expected_agents: dict[str, str],
    expected_direct_mode_refs: dict[str, str],
) -> int:
    failures = 0
    for filename, content in expected_agents.items():
        target_path = target_dir / filename
        if not target_path.exists():
            print(f"Missing generated agent file: {target_path}", file=sys.stderr)
            failures += 1
            continue
        existing = target_path.read_text(encoding="utf-8")
        if existing != content:
            print(f"Generated agent drift: {target_path}", file=sys.stderr)
            failures += 1

    for relative_path, content in expected_direct_mode_refs.items():
        target_path = repo_root / relative_path
        existing = target_path.read_text(encoding="utf-8")
        if existing != content:
            print(
                f"Generated direct-mode reference drift: {target_path}",
                file=sys.stderr,
            )
            failures += 1
    if failures:
        return 1
    print(f"All generated agent files are up to date in {target_dir}")
    print("All generated direct-mode role references are up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
