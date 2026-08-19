#!/usr/bin/env python3
"""Shared parser for Codex apply_patch payloads and Bash Markdown mutation targets.

One grammar for the three shell-invoked consumers (`task_hook.py`,
`hooks/task_approval_gate.py`, `hooks/communicate_gate.py`): `Add/Update/Delete
File` headers, `Move to:` renames, `@@` hunk separators, and context lines that
start with neither `+` nor `-` (the empty string included).
"""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass, field


_FILE_HEADER_RE = re.compile(r"^\*\*\* (?P<kind>Add|Update|Delete) File: (?P<path>.+)$")
_MOVE_TO_RE = re.compile(r"^\*\*\* Move to: (?P<path>.+)$")


@dataclass
class FilePatch:
    """One file section of an apply_patch payload."""

    kind: str  # "add" | "update" | "delete"
    path: str
    move_to: str | None = None
    hunks: list[list[str]] = field(default_factory=list)

    @property
    def target_path(self) -> str:
        """The path the file content lands at after the patch."""
        return self.move_to or self.path

    def added_lines(self) -> list[str]:
        return [line[1:] for hunk in self.hunks for line in hunk if line[:1] == "+"]


def parse_patch(command: str) -> list[FilePatch]:
    """Parse an apply_patch command into per-file patches with raw hunk lines."""
    patches: list[FilePatch] = []
    current: FilePatch | None = None
    hunk: list[str] | None = None

    def close_hunk() -> None:
        nonlocal hunk
        if current is not None and hunk:
            current.hunks.append(hunk)
        hunk = None

    for line in command.splitlines():
        header = _FILE_HEADER_RE.match(line)
        if header:
            close_hunk()
            current = FilePatch(
                kind=header.group("kind").lower(), path=header.group("path").strip()
            )
            patches.append(current)
            continue
        move = _MOVE_TO_RE.match(line)
        if move:
            close_hunk()
            if current is not None:
                current.move_to = move.group("path").strip()
            continue
        if line.startswith("*** "):
            # Begin Patch / End Patch / End of File — structural, never hunk content.
            close_hunk()
            if line.strip() == "*** End Patch":
                current = None
            continue
        if current is None:
            continue
        if line.startswith("@@"):
            close_hunk()
            hunk = []
            continue
        if hunk is None:
            hunk = []
        hunk.append(line)
    close_hunk()
    return patches


def patch_paths(command: str) -> list[str]:
    """Every file path an apply_patch command touches, `Move to:` targets included."""
    paths: list[str] = []
    for patch in parse_patch(command):
        paths.append(patch.path)
        if patch.move_to:
            paths.append(patch.move_to)
    return paths


def apply_to_text(patch: FilePatch, current: str) -> str | None:
    """Reconstruct the file content the patch produces, or None when it cannot.

    A hunk line starting with neither ``+`` nor ``-`` — the empty string
    included — is context; a leading single space is the marker and is
    stripped, a bare line is tolerated verbatim. Each hunk searches for its
    old block from position 0 of the evolving text, so out-of-order hunks
    still reconstruct.
    """
    if patch.kind == "delete":
        return ""
    lines = current.splitlines()
    trailing_newline = current.endswith("\n") or not current
    for hunk in patch.hunks:
        old: list[str] = []
        new: list[str] = []
        for line in hunk:
            marker = line[:1]
            if marker == "+":
                new.append(line[1:])
            elif marker == "-":
                old.append(line[1:])
            else:
                content = line[1:] if marker == " " else line
                old.append(content)
                new.append(content)
        if not old:
            if lines:
                return None
            lines = list(new)
            continue
        found = next(
            (
                i
                for i in range(len(lines) - len(old) + 1)
                if lines[i : i + len(old)] == old
            ),
            None,
        )
        if found is None:
            return None
        lines = lines[:found] + new + lines[found + len(old) :]
    result = "\n".join(lines)
    return result + ("\n" if trailing_newline and result else "")


# Bash mutation-target extraction, shared by the communicate and approval gates.
_REDIRECT_MD_RE = re.compile(
    r"(?:^|[\s;|&])(?:\d*)>>?\s*(['\"]?[^\s;|&'\"]+\.md)['\"]?(?=$|[\s;|&])",
    re.IGNORECASE,
)
_TEE_MD_RE = re.compile(
    r"(?:^|[\s;|&])tee(?:\s+-[a-zA-Z]+)*\s+(['\"]?[^\s;|&'\"]+\.md)['\"]?(?=$|[\s;|&])",
    re.IGNORECASE,
)
# The -i may sit inside a flag cluster (perl -pi -e), so match any flag token
# containing i, not only a standalone -i.
_IN_PLACE_MD_RE = re.compile(
    r"(?:^|[\s;|&])(?:sed|perl)\s+(?:[^;|&]*?\s)?-[a-zA-Z]*i\S*\s+[^;|&]*?(['\"]?[^\s;|&'\"]+\.md)['\"]?(?=$|[\s;|&])",
    re.IGNORECASE,
)


def bash_markdown_mutation_targets(command: str) -> list[str]:
    """Markdown paths a Bash command mutates in place.

    Covers redirects, ``tee``, ``sed``/``perl`` ``-i``, ``touch``, and
    ``cp``/``mv`` destinations. Results are raw path strings; callers resolve
    and filter them.
    """
    paths: list[str] = []
    for pattern in (_REDIRECT_MD_RE, _TEE_MD_RE, _IN_PLACE_MD_RE):
        paths.extend(match.group(1).strip("'\"") for match in pattern.finditer(command))
    for segment in re.split(r"(?:&&|\|\||[;|])", command):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            continue
        if not tokens:
            continue
        executable = tokens[0].rsplit("/", 1)[-1]
        operands = [token for token in tokens[1:] if not token.startswith("-")]
        if executable == "touch":
            paths.extend(token for token in operands if token.lower().endswith(".md"))
        elif executable in ("cp", "mv") and operands:
            destination = operands[-1]
            if destination.lower().endswith(".md"):
                paths.append(destination)
    return paths
