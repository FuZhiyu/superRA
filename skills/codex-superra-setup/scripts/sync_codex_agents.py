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

    # `## Dispatch Inputs` in the source describes the subagent dispatch
    # contract; direct mode has no dispatch, so we drop that section and
    # substitute a direct-mode-specific `## Before You Start`. Other
    # subagent-only fragments (dispatch prompts, re-dispatch deltas,
    # Worktree: fields) leak into the retained sections and are rewritten
    # below by `cleanup_*_handoff` before being spliced in.
    if "implementer" in spec.codex_name:
        before_you_start = render_implementer_direct_mode_before_you_start()
        handoff = cleanup_implementer_handoff(
            sections["## Handoff — Unified Across Stages"]
        )
        tail_sections = (
            sections["## Execution Protocol"],
            handoff,
            sections["## Pre-Commit Self-Check"],
            sections["## Escalation"],
        )
    else:
        before_you_start = render_reviewer_direct_mode_before_you_start()
        review_protocol = sections["## Review Protocol"].replace(
            "reviewer dispatches are costly", "review passes are costly"
        )
        role_section = sections["## Handoff — Unified Across Stages"].replace(
            "\n\nIf your dispatch prompt does not specify a stage, default to "
            "**ad-hoc** (report-only).",
            "",
        )
        role_section = cleanup_reviewer_handoff(role_section)
        role_section = strip_subsection(role_section, "### Report Format")
        tail_sections = (review_protocol, role_section)

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

    for line in body.splitlines(keepends=True):
        if line.startswith("## "):
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

In direct mode there is no dispatch prompt. Task context comes from `PLAN.md`, `RESULTS.md`, the current session, and the current branch state.

1. **Load skills per `superRA:using-superra` §Skill-Load Manifest** for your `Stage:`, and follow each loaded skill's own stage/role load map for implementer references.
2. **Read your task source directly from `PLAN.md`** (the task block plus the relevant header context). If resuming, also read the matching `RESULTS.md` section.
3. **Read `PLAN.md`'s `## Project Conventions` section before editing any file.** If it is missing, empty, stale, or does not cover a convention you need, walk the directories on-demand, apply what you find, and flag the omission in your status return.
4. **Ask questions** before starting if anything is unclear about data sources, methodology, repo conventions, or upstream dependencies.

The handoff-doc editing discipline you will need at the end of the task lives in §Handoff below; read it when you are ready to update `PLAN.md` / `RESULTS.md`."""


def render_reviewer_direct_mode_before_you_start() -> str:
    return """## Before You Start

In direct mode there is no dispatch prompt. Review scope comes from the task block in `PLAN.md`, the matching section in `RESULTS.md`, the current diff, and the current branch state.

1. **Load skills per `superRA:using-superra` §Skill-Load Manifest** for your `Stage:` before opening any code, and follow each loaded skill's own stage/role load map for reviewer references. You walk the same `[BLOCKING]` / `[ADVISORY]` checklist the implementer walked as self-check — one source of truth, two perspectives.
2. **Read your task source directly from `PLAN.md`.** Read the task block, the implementer's step notes, any existing review-notes blockquote (with `→ implemented:` and `→ orchestrator:` annotations), and the corresponding `RESULTS.md` section.
3. **Read `PLAN.md`'s `## Project Conventions` section** as the review standard for codebase-fit findings — code that ignores a documented convention is a MAJOR integration-review finding. If the section is missing, empty, stale, or does not cover a convention you need, walk on-demand starting from every touched directory and flag the omission in your status return.
4. **Read the actual code.** Do not trust summaries, reports, or claims from the implementer. Verify independently.

The handoff-doc editing discipline you will need when writing the review blockquote lives in §Handoff below; read it when you are ready to update `PLAN.md`."""


def cleanup_implementer_handoff(section: str) -> str:
    """Strip subagent-dispatch-only wording from the implementer handoff section."""
    # Rewrite the §How You Fix Review Items opening paragraph. The source
    # wording references "first dispatch", "re-dispatch prompt", and a
    # one-line delta, none of which exist in direct mode.
    source_opener = (
        "On a first dispatch there is no review-notes blockquote yet; you just "
        "implement the steps, update the docs, and commit. On a REVISE round "
        "the blockquote exists — the reviewer wrote it, and the orchestrator "
        "may have rewritten some steps (for accepted items) or appended "
        "`→ orchestrator: ...` notes to items it is rejecting or flagging for "
        "a second opinion. Your re-dispatch prompt carries a one-line delta "
        "pointing at what changed."
    )
    direct_opener = (
        "On a first pass there is no review-notes blockquote yet; you just "
        "implement the steps, update the docs, and commit. On a REVISE round "
        "the blockquote exists — it was written previously, and items may "
        "carry `→ orchestrator: ...` notes rejecting them or flagging them for "
        "a second opinion."
    )
    if source_opener not in section:
        raise ValueError(
            "cleanup_implementer_handoff: expected dispatch-only opener not found "
            "in implementer §How You Fix Review Items; source may have been reworded."
        )
    section = section.replace(source_opener, direct_opener)

    # Drop the Parallel worktree dispatch paragraph entirely — Worktree: is
    # a subagent dispatch field.
    worktree_block = (
        "\n\n**Parallel worktree dispatch (`Worktree:` field set).** Return the "
        "`<branch>/parallel/<slug>` branch name and HEAD SHA in your status "
        "report. Do not merge, rebase, push, or touch worktree lifecycle — the "
        "orchestrator owns harvest-out."
    )
    if worktree_block not in section:
        raise ValueError(
            "cleanup_implementer_handoff: expected Parallel worktree dispatch "
            "paragraph not found; source may have been reworded."
        )
    section = section.replace(worktree_block, "")
    return section


def cleanup_reviewer_handoff(section: str) -> str:
    """Strip subagent-dispatch-only wording from the reviewer handoff section."""
    source_paragraph = (
        "**The `## Upstream Intent` section in PLAN.md** — reviewer-owned for "
        "the active Phase B round. The orchestrator passes the round context "
        "(`origin/<base-branch>`, `MERGE_BASE_SHA`, reviewed upstream range, "
        "and any special steering) in the dispatch. When the base-side scan "
        "surfaces material overlap, you create or update the section for the "
        "current round using that context. Implementers are hands-off. Keep "
        "the section current while the round is active; the orchestrator "
        "removes it in the Phase B closeout commit."
    )
    direct_paragraph = (
        "**The `## Upstream Intent` section in PLAN.md** — reviewer-owned for "
        "the active Phase B round. Use the current round context "
        "(`origin/<base-branch>`, `MERGE_BASE_SHA`, reviewed upstream range) "
        "from `PLAN.md` and the current session when the base-side scan "
        "surfaces material overlap, and create or update the section for the "
        "current round from that context. Keep the section current while the "
        "round is active; remove it in the Phase B closeout commit."
    )
    if source_paragraph not in section:
        raise ValueError(
            "cleanup_reviewer_handoff: expected Upstream Intent paragraph with "
            "dispatch-only wording not found; source may have been reworded."
        )
    return section.replace(source_paragraph, direct_paragraph)


def strip_subsection(section: str, heading: str) -> str:
    lines = section.splitlines(keepends=True)
    start = find_heading_line(lines, heading)
    if start is None:
        return section

    level = heading_level(heading)
    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith("#") and heading_level(line.rstrip()) <= level:
            end = index
            break

    stripped = "".join(lines[:start] + lines[end:]).rstrip()
    return re.sub(r"\n{3,}", "\n\n", stripped)


def find_heading_line(lines: list[str], heading: str) -> int | None:
    for index, line in enumerate(lines):
        if line.rstrip() == heading:
            return index
    return None


def heading_level(line: str) -> int:
    return len(line) - len(line.lstrip("#"))


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
