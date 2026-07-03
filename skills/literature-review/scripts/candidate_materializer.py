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
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


def fail(message: str, code: int = 1) -> int:
    print(f"error: {message}", file=sys.stderr)
    return code


def emit(payload: object) -> None:
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class StoreLock:
    def __init__(self, store: Path):
        self.store = store
        self.file = None

    def __enter__(self):
        self.store.mkdir(parents=True, exist_ok=True)
        self.file = open(self.store / ".candidate-materializer.lock", "a+", encoding="utf-8")
        fcntl.flock(self.file, fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.file is not None:
            fcntl.flock(self.file, fcntl.LOCK_UN)
            self.file.close()


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


def nested_get(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = record.get(key)
        if value:
            return value
    return ""


def zotero_value(record: dict[str, Any], *keys: str) -> str:
    zotero = record.get("zotero") if isinstance(record.get("zotero"), dict) else {}
    for key in keys:
        value = zotero.get(key) or record.get(key)
        if value:
            return str(value)
    return ""


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


def read_status(task_path: Path) -> str | None:
    text = task_path.read_text(encoding="utf-8")
    match = re.search(r"(?m)^status:\s*(\S+)\s*$", text)
    return match.group(1) if match else None


def write_text_atomic(path: Path, text: str) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            tmp.write(text)
        os.replace(tmp_name, path)
    except OSError:
        with suppress_unlink(tmp_name):
            pass
        raise


class suppress_unlink:
    def __init__(self, path: str):
        self.path = path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            os.unlink(self.path)
        except OSError:
            pass


def set_status(text: str, status: str) -> str:
    if not re.search(r"(?m)^status:\s*\S+\s*$", text):
        raise ValueError("task.md has no status frontmatter field")
    return re.sub(r"(?m)^status:\s*\S+\s*$", f"status: {status}", text, count=1)


def ensure_section(text: str, heading: str, body: list[str]) -> str:
    if f"\n{heading}\n" in text or text.startswith(f"{heading}\n"):
        return text
    block = "\n".join(["", heading, "", *body, ""])
    return text.rstrip() + block + "\n"


def update_claim_section(text: str, claimant: str, claimed_at: str, lease_hours: float) -> str:
    body = [
        f"- Claimed by: {claimant}",
        f"- Claimed at: {claimed_at}",
        f"- Lease hours: {lease_hours:g}",
    ]
    block = "\n".join(["## Claim", "", *body, ""])
    pattern = r"(?ms)^## Claim\n.*?(?=^## |\Z)"
    if re.search(pattern, text):
        return re.sub(pattern, block, text, count=1)
    return text.rstrip() + "\n\n" + block


def append_provenance(task_path: Path, provenance: str | None) -> bool:
    if not provenance:
        return False
    text = task_path.read_text(encoding="utf-8")
    line = f"- Additional provenance: {provenance}"
    if line in text or f"- Discovered via: {provenance}" in text:
        return False
    marker = "## Screening Decision"
    if marker not in text:
        return False
    text = text.replace(f"\n{marker}", f"\n{line}\n\n{marker}", 1)
    write_text_atomic(task_path, text)
    return True


def candidate_task(record: dict[str, Any], key: str, provenance: str | None) -> str:
    ids = identity(record)
    title = str(record.get("title") or "Untitled")
    authors = record.get("authors") or []
    author_text = ", ".join(a.get("name") or a.get("family") or str(a) for a in authors) if authors else ""
    abstract = str(record.get("abstract") or "").strip()
    url = nested_get(record, "url", "landing_url")
    source = provenance or record.get("discovered_via") or ""
    corpus_id = record.get("id", {}).get("corpus_id") if isinstance(record.get("id"), dict) else ""
    corpus_id = corpus_id or record.get("corpus_id") or record.get("external_ids", {}).get("CorpusId", "")
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
        f"- Corpus ID: {corpus_id}",
        f"- Title-year: {ids.get('title_year', '')}",
        f"- Metadata source: {record.get('source') or ''}",
        f"- Version of record: {record.get('version_of_record') if record.get('version_of_record') is not None else ''}",
        f"- JEL codes: {record.get('jel_codes') or ''}",
        "",
        "## Abstract",
        "",
        abstract or "Not recorded.",
        "",
        "## Discovery Provenance",
        "",
        f"- Discovered via: {source}",
        "- Source paper: ",
        "- Citation context: Not recorded.",
        "- Depth: Not recorded.",
        "- Lens: Not recorded.",
        "- Priority: Not recorded.",
        "- Local reason: Not recorded.",
        "",
        "## Screening Decision",
        "",
        "- Decision: pending",
        "- Reason: ",
        "- Failed gate: ",
        "- Read depth: ",
        "- Promotion recommendation: ",
        "",
        "## Quality",
        "",
        "- Outlet tier: ",
        "- Identification strategy: ",
        "- Quality notes: ",
        "",
        "## Retrieval Trace",
        "",
        f"- Zotero item: {zotero_value(record, 'item_uri', 'zotero_item', 'zotero_item_uri')}",
        f"- Zotero attachment: {zotero_value(record, 'attachment_uri', 'zotero_attachment', 'zotero_attachment_uri')}",
        f"- Landing URL: {url}",
        f"- PDF URL: {record.get('pdf_url') or ''}",
        f"- PDF path: {record.get('pdf_path') or ''}",
        f"- Markdown path: {record.get('md_path') or record.get('markdown_path') or ''}",
        f"- Access: {record.get('access') or ''}",
        f"- Fetched at: {record.get('fetched_at') or ''}",
        f"- Version divergence: {record.get('version_divergence') or ''}",
        "",
        "## Extraction",
        "",
        "- Status: not-started",
        "- Fields: ",
        "- Notes: ",
        "",
    ]
    return "\n".join(lines)


def materialize_one(store: Path, record: dict[str, Any], provenance: str | None) -> dict[str, Any]:
    ident = identity(record)
    existing = find_existing(store, ident)
    if existing:
        updated = append_provenance(existing / "task.md", provenance)
        return {
            "action": "matched-existing",
            "key": existing.name,
            "path": str(existing / "task.md"),
            "status": read_status(existing / "task.md"),
            "updated_provenance": updated,
        }

    base = key_for(record)
    target = store / base
    if target.exists():
        target = store / f"{base}-{short_hash(record)}"
    target.mkdir(parents=True, exist_ok=False)
    write_text_atomic(target / "task.md", candidate_task(record, target.name, provenance))
    return {"action": "created", "key": target.name, "path": str(target / "task.md"), "status": "not-started"}


def resolve_candidate(store: Path, candidate: str) -> Path:
    path = Path(candidate)
    if path.name == "task.md":
        path = path.parent
    if path.exists():
        return path
    path = store / candidate
    if path.exists():
        return path
    raise FileNotFoundError(f"candidate not found: {candidate}")


def claim_one(store: Path, candidate: str, claimant: str, lease_hours: float, force: bool = False) -> dict[str, Any]:
    folder = resolve_candidate(store, candidate)
    task_path = folder / "task.md"
    text = task_path.read_text(encoding="utf-8")
    status = read_status(task_path)
    if status != "not-started" and not force:
        return {
            "won": False,
            "key": folder.name,
            "path": str(task_path),
            "status": status,
        }
    claimed_at = utc_now()
    text = set_status(text, "in-progress")
    text = update_claim_section(text, claimant, claimed_at, lease_hours)
    write_text_atomic(task_path, text)
    return {
        "won": True,
        "key": folder.name,
        "path": str(task_path),
        "status": "in-progress",
        "claimed_by": claimant,
        "claimed_at": claimed_at,
        "lease_hours": lease_hours,
    }


def rewrite_links(root: Path, old_path: Path, new_path: Path) -> dict[str, Any]:
    updated: list[str] = []
    unresolved: list[str] = []
    old_abs = old_path.resolve()
    for task_path in root.glob("*/task.md"):
        if task_path.resolve() == (new_path / "task.md").resolve():
            continue
        text = task_path.read_text(encoding="utf-8")
        candidates = {
            str(old_path),
            str(old_path / "task.md"),
            old_path.name,
            f"{old_path.name}/task.md",
        }
        next_text = text
        for raw in sorted(candidates, key=len, reverse=True):
            if raw in next_text:
                replacement = os.path.relpath(new_path / "task.md", start=task_path.parent)
                next_text = next_text.replace(raw, replacement)
        if next_text != text:
            write_text_atomic(task_path, next_text)
            updated.append(str(task_path))
        elif str(old_abs) in text:
            unresolved.append(str(task_path))
    return {"updated_links": updated, "unresolved_links": unresolved}


def promote_one(store: Path, candidate: str, destination: Path) -> dict[str, Any]:
    source = resolve_candidate(store, candidate)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(f"destination already exists: {destination}")
    old_path = source
    shutil.move(str(source), str(destination))
    link_report = rewrite_links(store, old_path, destination)
    return {
        "action": "promoted",
        "key": destination.name,
        "old_path": str(old_path),
        "path": str(destination / "task.md"),
        **link_report,
    }


def cmd_key(args: argparse.Namespace) -> int:
    records = unwrap_records(read_json(args.record_file))
    emit([{"key": key_for(record), "identity": identity(record)} for record in records])
    return 0


def cmd_materialize(args: argparse.Namespace) -> int:
    records = unwrap_records(read_json(args.record_file))
    store = Path(args.store)
    with StoreLock(store):
        results = [materialize_one(store, record, args.provenance) for record in records]
    emit({"store": str(store), "count": len(results), "results": results})
    return 0


def cmd_claim(args: argparse.Namespace) -> int:
    store = Path(args.store)
    with StoreLock(store):
        result = claim_one(store, args.candidate, args.by, args.lease_hours, args.force)
    emit({"store": str(store), **result})
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    store = Path(args.store)
    with StoreLock(store):
        result = promote_one(store, args.candidate, Path(args.destination))
    emit({"store": str(store), **result})
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

    claim = sub.add_parser("claim", help="atomically claim a candidate for substantive reading")
    claim.add_argument("candidate", help="candidate key or path")
    claim.add_argument("--store", required=True, help="candidate-paper store directory")
    claim.add_argument("--by", required=True, help="dispatch or agent label")
    claim.add_argument("--lease-hours", type=float, default=12.0, help="claim lease length for diagnostics")
    claim.add_argument("--force", action="store_true", help="override a stale/non-not-started claim")
    claim.set_defaults(func=cmd_claim)

    promote = sub.add_parser("promote", help="move a candidate folder into a permanent-record destination")
    promote.add_argument("candidate", help="candidate key or path")
    promote.add_argument("--store", required=True, help="candidate-paper store directory")
    promote.add_argument("--destination", required=True, help="destination folder for the permanent record")
    promote.set_defaults(func=cmd_promote)
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
