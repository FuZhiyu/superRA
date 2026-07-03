#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Materialize literature-review candidate papers as task-shaped folders.

The candidate store is non-git workflow state. JSON is accepted only as tool I/O
from citation/search clients; authoritative candidate state is the generated
``task.md`` file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


def fail(message: str, code: int = 1) -> int:
    print(f"error: {message}", file=sys.stderr)
    return code


def emit(payload: object) -> None:
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    doi = value.strip().lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi or None


def slugify(value: object, max_len: int = 48) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return (text[:max_len].strip("-") or "unknown")


def short_hash(payload: object, n: int = 8) -> str:
    data = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha1(data).hexdigest()[:n]


def read_json(path: str | None) -> Any:
    raw = sys.stdin.read() if path in (None, "-") else Path(path).read_text(encoding="utf-8")
    return json.loads(raw)


def unwrap_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("records"), list):
            return [r for r in payload["records"] if isinstance(r, dict)]
        if isinstance(payload.get("record"), dict):
            return [payload["record"]]
        return [payload]
    raise ValueError("input must be a record, {record}, {records}, or an array")


def first_author(record: dict[str, Any]) -> str:
    authors = record.get("authors") or []
    if authors and isinstance(authors[0], dict):
        return authors[0].get("family") or authors[0].get("name") or "unknown"
    if authors:
        return str(authors[0])
    return "unknown"


def venue_label(record: dict[str, Any]) -> str:
    venue = record.get("venue") or record.get("container_title") or record.get("container-title")
    if venue:
        return str(venue)
    source = str(record.get("source") or "").lower()
    if "ssrn" in source:
        return "ssrn"
    if "nber" in source:
        return "nber"
    if record.get("id", {}).get("arxiv") or record.get("arxiv"):
        return "arxiv"
    return "wp"


def identity(record: dict[str, Any]) -> dict[str, str]:
    ids = record.get("id") if isinstance(record.get("id"), dict) else {}
    ext = record.get("external_ids") if isinstance(record.get("external_ids"), dict) else {}
    doi = normalize_doi(ids.get("doi") or record.get("doi") or ext.get("DOI"))
    arxiv = ids.get("arxiv") or record.get("arxiv") or ext.get("ArXiv")
    s2 = ids.get("s2") or record.get("s2") or ext.get("CorpusId") or ids.get("corpus_id")
    title = record.get("title") or ""
    year = str(record.get("year") or "")
    out: dict[str, str] = {}
    if doi:
        out["doi"] = doi
    if arxiv:
        out["arxiv"] = str(arxiv).strip()
    if s2:
        out["s2"] = str(s2).strip()
    if title and year:
        out["title_year"] = f"{slugify(title, 96)}::{year}"
    return out


def key_for(record: dict[str, Any]) -> str:
    author = slugify(first_author(record), 24)
    venue = slugify(venue_label(record), 28)
    year = slugify(record.get("year") or "nd", 8)
    title = slugify(record.get("title") or "untitled", 48)
    return f"{author}-{venue}-{year}-{title}"


def parse_existing_identity(task_path: Path) -> dict[str, str]:
    text = task_path.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    doi = re.search(r"(?im)^\s*-\s*DOI:\s*(.+?)\s*$", text)
    arxiv = re.search(r"(?im)^\s*-\s*arXiv:\s*(.+?)\s*$", text)
    s2 = re.search(r"(?im)^\s*-\s*S2:\s*(.+?)\s*$", text)
    title_year = re.search(r"(?im)^\s*-\s*Title-year:\s*(.+?)\s*$", text)
    if doi:
        out["doi"] = normalize_doi(doi.group(1)) or ""
    if arxiv:
        out["arxiv"] = arxiv.group(1).strip()
    if s2:
        out["s2"] = s2.group(1).strip()
    if title_year:
        out["title_year"] = title_year.group(1).strip()
    return {k: v for k, v in out.items() if v}


def identities_match(a: dict[str, str], b: dict[str, str]) -> bool:
    for key in ("doi", "arxiv", "s2", "title_year"):
        if a.get(key) and b.get(key) and a[key] == b[key]:
            return True
    return False


def find_existing(store: Path, ident: dict[str, str]) -> Path | None:
    for task_path in store.glob("*/task.md"):
        if identities_match(ident, parse_existing_identity(task_path)):
            return task_path.parent
    return None


def candidate_task(record: dict[str, Any], key: str, provenance: str | None) -> str:
    ids = identity(record)
    title = str(record.get("title") or "Untitled")
    authors = record.get("authors") or []
    author_text = ", ".join(a.get("name") or a.get("family") or str(a) for a in authors) if authors else ""
    abstract = str(record.get("abstract") or "").strip()
    url = record.get("url") or record.get("landing_url") or ""
    source = provenance or record.get("discovered_via") or ""
    lines = [
        "---",
        f'title: "{title.replace(chr(34), chr(39))}"',
        "status: not-started",
        "depends_on: []",
        "---",
        "",
        "## Metadata",
        "",
        f"- Key: {key}",
        f"- Title: {title}",
        f"- Authors: {author_text}",
        f"- Year: {record.get('year') or ''}",
        f"- Venue: {venue_label(record)}",
        f"- DOI: {ids.get('doi', '')}",
        f"- arXiv: {ids.get('arxiv', '')}",
        f"- S2: {ids.get('s2', '')}",
        f"- Title-year: {ids.get('title_year', '')}",
        "",
        "## Abstract",
        "",
        abstract or "Not recorded.",
        "",
        "## Discovery Provenance",
        "",
        f"- Discovered via: {source}",
        "- Citation context: Not recorded.",
        "- Depth: Not recorded.",
        "- Priority: Not recorded.",
        "",
        "## Screening Decision",
        "",
        "Pending.",
        "",
        "## Retrieval Trace",
        "",
        f"- Landing URL: {url}",
        "- PDF URL: ",
        "- PDF path: ",
        "- Markdown path: ",
        "- Fetched at: ",
        "- Version divergence: ",
        "",
        "## Extraction",
        "",
        "Not started.",
        "",
    ]
    return "\n".join(lines)


def materialize_one(store: Path, record: dict[str, Any], provenance: str | None) -> dict[str, Any]:
    store.mkdir(parents=True, exist_ok=True)
    ident = identity(record)
    existing = find_existing(store, ident)
    if existing:
        return {"action": "matched-existing", "key": existing.name, "path": str(existing / "task.md")}

    base = key_for(record)
    target = store / base
    if target.exists():
        target = store / f"{base}-{short_hash(record)}"
    target.mkdir(parents=True, exist_ok=False)
    (target / "task.md").write_text(candidate_task(record, target.name, provenance), encoding="utf-8")
    return {"action": "created", "key": target.name, "path": str(target / "task.md")}


def cmd_key(args: argparse.Namespace) -> int:
    records = unwrap_records(read_json(args.record_file))
    emit([{"key": key_for(record), "identity": identity(record)} for record in records])
    return 0


def cmd_materialize(args: argparse.Namespace) -> int:
    records = unwrap_records(read_json(args.record_file))
    store = Path(args.store)
    results = [materialize_one(store, record, args.provenance) for record in records]
    emit({"store": str(store), "count": len(results), "results": results})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    key = sub.add_parser("key", help="compute candidate keys for record JSON")
    key.add_argument("--record-file", default="-", help="JSON file or '-' for stdin")
    key.set_defaults(func=cmd_key)

    mat = sub.add_parser("materialize", help="create task-shaped candidate folders")
    mat.add_argument("--store", required=True, help="candidate-paper store directory")
    mat.add_argument("--record-file", default="-", help="JSON file or '-' for stdin")
    mat.add_argument("--provenance", help="discovered_via label to record")
    mat.set_defaults(func=cmd_materialize)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return fail(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
