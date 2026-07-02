#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyzotero==1.13.0",
# ]
# ///
"""Unified pyzotero command surface for the zotero-paper-reader skill.

Local-first reads through the Zotero Desktop local API, with the Zotero Web API
as a fallback. Every subcommand emits JSON on stdout for agent consumption.
Credentials are read from the environment or a project-local ``Notes/.env`` and
are never printed to stdout/stderr.

Run from anywhere via the bundled path, e.g.:

    uv run --script <skill-root>/scripts/zotero_tool.py health

See ``references/access-modes.md`` for access-mode rules and configuration.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from pathlib import Path

LOCAL_API_BASE = "http://localhost:23119/api"
# The Zotero desktop connector (separate path from the read-only local /api).
# Writes go through the connector locally; the local /api is read-only.
CONNECTOR_BASE = "http://localhost:23119/connector"
# A non-Mozilla User-Agent (plus the allowed-request header) is required or the
# connector rejects the save; the API-version header pins the connector wire
# protocol. See references/access-modes.md.
CONNECTOR_HEADERS = {
    "Content-Type": "application/json",
    "X-Zotero-Connector-API-Version": "3",
    "User-Agent": "zotero-paper-reader/1.0",
    "zotero-allowed-request": "1",
}
# The local API exposes the desktop's default user library at id 0.
LOCAL_LIBRARY_ID = "0"
PDF_MIN_BYTES = 1024

# Better BibTeX is a local-only Zotero plugin (not the Web API / pyzotero). Its
# JSON-RPC endpoint resolves BBT citekeys and exports BBT-keyed BibTeX.
BBT_RPC_URL = "http://127.0.0.1:23119/better-bibtex/json-rpc"
# Better BibTeX numbers the user library 1; group libraries keep their group id.
BBT_USER_LIBRARY_ID = 1


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def emit(payload: object) -> None:
    """Write a JSON result to stdout."""
    json.dump(payload, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def fail(message: str, code: int = 1) -> "int":
    """Emit a structured error to stderr and return an exit code.

    The message is constructed by the tool, never echoing credential values.
    """
    eprint(f"error: {message}")
    return code


# --------------------------------------------------------------------------- #
# Configuration                                                               #
# --------------------------------------------------------------------------- #


def load_env_file() -> dict[str, str]:
    """Read ``Notes/.env`` from the current working directory if present.

    Returns a mapping of variable name to value. Values are never logged.
    Environment variables already set take precedence over file values.
    """
    env_path = Path("Notes/.env")
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip().strip('"').strip("'")
    return values


def get_config() -> dict[str, str | None]:
    """Resolve Zotero configuration from the environment, then ``Notes/.env``.

    Environment variables win over file values. Returns only what is present;
    no value is printed.
    """
    file_values = load_env_file()

    def resolve(name: str) -> str | None:
        return os.environ.get(name) or file_values.get(name) or None

    return {
        "library_id": resolve("ZOTERO_LIBRARY_ID"),
        "library_type": resolve("ZOTERO_LIBRARY_TYPE") or "user",
        "api_key": resolve("ZOTERO_API_KEY"),
    }


# --------------------------------------------------------------------------- #
# Access-mode detection and client construction                               #
# --------------------------------------------------------------------------- #


def local_api_available() -> bool:
    """Probe the Zotero Desktop local API.

    Returns True only when the local API is enabled and serving requests, not
    merely when the Zotero connector port answers. The connector port responds
    even with the local API disabled, so we check an actual ``/api`` path.
    """
    import urllib.error
    import urllib.request

    url = f"{LOCAL_API_BASE}/users/{LOCAL_LIBRARY_ID}/items?limit=1"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:  # noqa: S310
            return 200 <= resp.status < 300
    except urllib.error.HTTPError:
        # Any HTTP response (e.g. 403 "Local API is not enabled") means the
        # local API path is not usable for our reads.
        return False
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def parse_library(spec: str | None) -> "tuple[str, str | None]":
    """Resolve a ``--library`` spec to ``(library_type, group_id)``.

    ``user`` (or None) -> ``("user", None)``; a bare numeric id or ``group:<id>``
    -> ``("group", "<id>")``. Raises RuntimeError on an unparseable spec.
    """
    if spec is None or spec == "user":
        return "user", None
    gid = spec.split(":", 1)[1] if spec.startswith("group:") else spec
    if not gid.isdigit():
        raise RuntimeError(
            f"invalid --library {spec!r}: use 'user', a numeric group id, "
            "or 'group:<id>' (list ids with the 'libraries' command)"
        )
    return "group", gid


def make_client(prefer: str = "auto", library: str | None = "user"):
    """Construct a pyzotero client, choosing local or web mode and target library.

    ``prefer`` is one of ``auto`` (local if available, else web), ``local``,
    or ``web``. ``library`` is ``user`` (default), a numeric group id, or
    ``group:<id>``. Raises RuntimeError with a credential-free message when the
    requested mode cannot be constructed.
    """
    from pyzotero.zotero import Zotero

    cfg = get_config()
    lib_type, group_id = parse_library(library)

    def build_local() -> "tuple[object, str]":
        # pyzotero 1.13.0 requires library_id + library_type even in local mode.
        # The local API serves the desktop's default user library at id 0 and
        # each group library at its group id.
        if lib_type == "group":
            zot = Zotero(library_id=group_id, library_type="group", local=True)
        else:
            zot = Zotero(library_id=LOCAL_LIBRARY_ID, library_type="user", local=True)
        return zot, "local"

    def build_web() -> "tuple[object, str]":
        if not cfg["api_key"]:
            raise RuntimeError(
                "Web API mode needs ZOTERO_LIBRARY_ID and ZOTERO_API_KEY "
                "(set in the environment or Notes/.env)"
            )
        if lib_type == "group":
            zot = Zotero(
                library_id=group_id, library_type="group", api_key=str(cfg["api_key"])
            )
            return zot, "web"
        if not cfg["library_id"]:
            raise RuntimeError(
                "Web API mode needs ZOTERO_LIBRARY_ID and ZOTERO_API_KEY "
                "(set in the environment or Notes/.env)"
            )
        zot = Zotero(
            library_id=str(cfg["library_id"]),
            library_type=str(cfg["library_type"]),
            api_key=str(cfg["api_key"]),
        )
        return zot, "web"

    if prefer == "local":
        return build_local()
    if prefer == "web":
        return build_web()

    # auto
    if local_api_available():
        return build_local()
    return build_web()


def pyzotero_version() -> str:
    from importlib.metadata import version

    return version("pyzotero")


# --------------------------------------------------------------------------- #
# Better BibTeX client (local-only JSON-RPC) and key resolution               #
# --------------------------------------------------------------------------- #


class BBTError(RuntimeError):
    """Better BibTeX is unreachable or returned an RPC error.

    Callers treat this as the signal to fall back to the built-in translator.
    """


def bbt_library_id(library: str | None) -> int:
    """Map a ``--library`` spec to a Better BibTeX ``libraryID``.

    The user library is BBT ``libraryID`` 1; a group library uses its own
    numeric id. Raises RuntimeError (via parse_library) on an unparseable spec.
    """
    lib_type, group_id = parse_library(library)
    if lib_type == "group" and group_id is not None:
        return int(group_id)
    return BBT_USER_LIBRARY_ID


def bbt_call(method: str, params: list, timeout: float = 15.0):
    """Invoke one Better BibTeX JSON-RPC method, returning its ``result``.

    Raises BBTError when the endpoint is unreachable or the response carries an
    RPC error. BBT item abstracts can contain raw control characters, so the
    response is parsed with ``strict=False``.
    """
    import urllib.error
    import urllib.request

    body = json.dumps(
        {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    ).encode("utf-8")
    req = urllib.request.Request(
        BBT_RPC_URL,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            raw = resp.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise BBTError(f"Better BibTeX endpoint unreachable: {exc}") from exc
    try:
        payload = json.loads(raw, strict=False)
    except json.JSONDecodeError as exc:
        raise BBTError(f"Better BibTeX returned non-JSON: {exc}") from exc
    if payload.get("error"):
        raise BBTError(f"Better BibTeX RPC error: {payload['error']}")
    return payload.get("result")


def bbt_available() -> bool:
    """Report whether the Better BibTeX JSON-RPC endpoint is reachable."""
    try:
        bbt_call("item.citationkey", [[]], timeout=3.0)
        return True
    except BBTError:
        return False


def bbt_citekeys(item_keys: list[str], _library_id: int) -> dict[str, str | None]:
    """Resolve Zotero item keys to Better BibTeX citekeys.

    Returns a ``{item_key: citekey}`` map; an unknown item key maps to ``None``.
    """
    result = bbt_call("item.citationkey", [list(item_keys)])
    return result if isinstance(result, dict) else {}


def bbt_export(citekeys: list[str], library_id: int) -> str:
    """Export BibTeX (with BBT citekeys) for the given citekeys via BBT."""
    result = bbt_call("item.export", [list(citekeys), "better bibtex", library_id])
    if not isinstance(result, str):
        raise BBTError(f"Better BibTeX export returned {type(result).__name__}")
    return result


def bbt_bibliography(citekeys: list[str], style: str) -> list[str]:
    """Render formatted reference entries for citekeys via Better BibTeX.

    Calls ``item.bibliography([citekeys], {id: style, contentType: "text"})``,
    which returns one ``text``-rendered entry per item joined by newlines.
    Returns the list of non-empty entry strings, in citekey order.
    """
    result = bbt_call(
        "item.bibliography", [list(citekeys), {"id": style, "contentType": "text"}]
    )
    if not isinstance(result, str):
        raise BBTError(f"Better BibTeX bibliography returned {type(result).__name__}")
    return [line.strip() for line in result.splitlines() if line.strip()]


def builtin_bibliography(zot, item_keys: list[str], style: str) -> list[str]:
    """Render formatted reference entries via Zotero's built-in CSL (fallback).

    Uses pyzotero's ``include="bib"`` per item, which returns a dict carrying the
    rendered reference under the ``bib`` key. Works in both local and Web mode.
    """
    entries: list[str] = []
    for key in item_keys:
        res = zot.item(key, include="bib", style=style)
        rendered = res.get("bib") if isinstance(res, dict) else None
        if rendered and rendered.strip():
            entries.append(rendered.strip())
    if not entries:
        raise RuntimeError(
            "built-in bibliography rendering produced no entries for the "
            "requested items"
        )
    return entries


def resolve_bibliography(
    zot, item_keys: list[str], library: str | None, style: str
) -> "tuple[bool, list[str]]":
    """Render formatted references, preferring Better BibTeX.

    Returns ``(bbt_used, entries)``. Tries BBT first (item-key -> citekey ->
    ``item.bibliography``); on any BBTError falls back to the built-in CSL
    renderer over the active pyzotero access mode, with ``bbt_used`` False.
    """
    lib_id = bbt_library_id(library)
    try:
        keymap = bbt_citekeys(item_keys, lib_id)
        citekeys = [keymap.get(k) for k in item_keys]
        missing = [k for k, c in zip(item_keys, citekeys) if not c]
        if missing:
            raise BBTError(
                "Better BibTeX has no citekey for: " + ", ".join(missing)
            )
        resolved = [c for c in citekeys if c]
        return True, bbt_bibliography(resolved, style)
    except BBTError:
        return False, builtin_bibliography(zot, item_keys, style)


def resolve_keys(
    zot, item_keys: list[str], library: str | None
) -> "tuple[bool, list[str], str]":
    """Resolve item keys to BibTeX, preferring Better BibTeX citekeys.

    Returns ``(bbt_used, citekeys, bibtex_text)``. Tries BBT first (item-key ->
    citekey -> export); on any BBTError falls back to the built-in translator
    over the active pyzotero access mode, in which case ``bbt_used`` is False
    and ``citekeys`` are read back from the emitted entries. Shared by the
    ``bibtex`` command and the citation features in sibling tasks.
    """
    lib_id = bbt_library_id(library)
    try:
        keymap = bbt_citekeys(item_keys, lib_id)
        citekeys = [keymap.get(k) for k in item_keys]
        missing = [k for k, c in zip(item_keys, citekeys) if not c]
        if missing:
            raise BBTError(
                "Better BibTeX has no citekey for: " + ", ".join(missing)
            )
        resolved = [c for c in citekeys if c]
        text = bbt_export(resolved, lib_id)
        return True, resolved, text
    except BBTError:
        text = builtin_bibtex(zot, item_keys)
        return False, bib_entry_keys(text), text


def builtin_bibtex(zot, item_keys: list[str]) -> str:
    """Export BibTeX via Zotero's built-in translator (BBT fallback).

    Uses pyzotero's ``format="bibtex"`` per item, which returns the raw BibTeX
    body (text/plain) in both local and Web mode. The built-in translator's
    citekeys differ from BBT's; callers must warn on this path.
    """
    chunks: list[str] = []
    for key in item_keys:
        raw = zot.item(key, format="bibtex")
        text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
        text = text.strip()
        if text:
            chunks.append(text)
    if not chunks:
        raise RuntimeError(
            "built-in BibTeX export produced no entries for the requested items"
        )
    return "\n\n".join(chunks) + "\n"


# --------------------------------------------------------------------------- #
# Master-.bib sync (dedup-append, minimal touch)                              #
# --------------------------------------------------------------------------- #

_BIB_ENTRY_RE = re.compile(r"@\s*\w+\s*\{\s*([^,\s]+)\s*,", re.IGNORECASE)


def split_bib_entries(text: str) -> "list[tuple[str, str]]":
    """Split BibTeX text into ``(citekey, entry_text)`` pairs, in order.

    Only true entry starts count: an ``@type{key,`` is an entry opener only at
    the top level (brace depth 0), so a ``@type{...,`` token embedded inside a
    field value — e.g. an ``abstract`` quoting another BibTeX snippet — is part
    of the enclosing entry, never a phantom entry of its own. The scanner tracks
    brace depth so an entry's full body (through its matching closing ``}``) is
    captured intact rather than split mid-field.
    """
    entries: list[tuple[str, str]] = []
    pos = 0
    n = len(text)
    while pos < n:
        m = _BIB_ENTRY_RE.search(text, pos)
        if not m:
            break
        citekey = m.group(1)
        # Walk from the opening brace of this entry, balancing braces to find
        # the entry's matching close; field-internal "@type{...}" tokens sit at
        # depth > 0 and never start a new entry.
        brace = text.index("{", m.start())
        depth = 0
        i = brace
        while i < n:
            ch = text[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    i += 1
                    break
            i += 1
        chunk = text[m.start():i].strip()
        entries.append((citekey, chunk))
        pos = i
    return entries


def bib_entry_keys(text: str) -> list[str]:
    """Return the citekeys of every top-level ``@type{key, ...}`` entry."""
    return [key for key, _ in split_bib_entries(text)]


def sync_bib(bib_path: "Path", text: str) -> "tuple[list[str], list[str]]":
    """Append new BibTeX entries into a master ``.bib``, deduped by citekey.

    Existing entries are never reordered or rewritten (minimal touch); only
    entries whose citekey is absent from the file are appended. Returns
    ``(added, skipped)`` citekey lists. Shared with the citation features in
    sibling tasks.
    """
    existing = set()
    if bib_path.exists():
        existing = set(bib_entry_keys(bib_path.read_text(encoding="utf-8")))
    added: list[str] = []
    skipped: list[str] = []
    to_append: list[str] = []
    seen = set(existing)
    for citekey, entry in split_bib_entries(text):
        if citekey in seen:
            skipped.append(citekey)
            continue
        seen.add(citekey)
        added.append(citekey)
        to_append.append(entry)
    if to_append:
        bib_path.parent.mkdir(parents=True, exist_ok=True)
        prefix = ""
        if bib_path.exists():
            current = bib_path.read_text(encoding="utf-8")
            if current and not current.endswith("\n"):
                prefix = "\n"
            if current.strip():
                prefix += "\n"
        with bib_path.open("a", encoding="utf-8") as fh:
            fh.write(prefix + "\n\n".join(to_append) + "\n")
    return added, skipped


# --------------------------------------------------------------------------- #
# Subcommand handlers                                                          #
# --------------------------------------------------------------------------- #


def cmd_health(args: argparse.Namespace) -> int:
    cfg = get_config()
    local_ok = local_api_available()
    web_configured = bool(cfg["library_id"] and cfg["api_key"])
    if local_ok:
        active = "local"
    elif web_configured:
        active = "web"
    else:
        active = None
    emit(
        {
            "pyzotero_version": pyzotero_version(),
            "local_api_available": local_ok,
            "better_bibtex_available": bbt_available(),
            "web_api_configured": web_configured,
            "library_type": cfg["library_type"],
            "active_mode": active,
            # Booleans only — never the values themselves.
            "config_present": {
                "ZOTERO_LIBRARY_ID": bool(cfg["library_id"]),
                "ZOTERO_API_KEY": bool(cfg["api_key"]),
            },
        }
    )
    sys.stdout.flush()
    if active is None:
        eprint(
            "no usable access mode: enable the Zotero Desktop local API or "
            "configure Web API credentials (see references/access-modes.md)"
        )
        return 1
    return 0


def cmd_libraries(args: argparse.Namespace) -> int:
    """List accessible libraries: the user library plus all group libraries."""
    zot, mode = make_client(prefer=args.mode)
    cfg = get_config()
    user_id = (
        LOCAL_LIBRARY_ID
        if mode == "local"
        else (str(cfg["library_id"]) if cfg["library_id"] else None)
    )
    libraries = [{"library_id": user_id, "library_type": "user", "name": "My Library"}]
    try:
        groups = zot.everything(zot.groups())
    except Exception as exc:  # noqa: BLE001
        return fail(f"could not list group libraries: {exc}")
    for g in groups:
        libraries.append(
            {
                "library_id": str(g.get("id")),
                "library_type": "group",
                "name": g.get("data", {}).get("name"),
            }
        )
    emit({"mode": mode, "count": len(libraries), "libraries": libraries})
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    # Full-text search uses qmode="everything" (matches indexed content); plain
    # search uses qmode="titleCreatorYear". Both qmodes are served by the local
    # API and the Web API, so honor the requested access mode in either case.
    qmode = "everything" if args.fulltext else "titleCreatorYear"
    zot, mode = make_client(prefer=args.mode, library=args.library)
    results = zot.items(q=args.query, qmode=qmode, limit=args.limit)
    emit({"mode": mode, "count": len(results), "items": results})
    return 0


def cmd_item(args: argparse.Namespace) -> int:
    zot, mode = make_client(prefer=args.mode, library=args.library)
    emit({"mode": mode, "item": zot.item(args.item_key)})
    return 0


def cmd_children(args: argparse.Namespace) -> int:
    zot, mode = make_client(prefer=args.mode, library=args.library)
    children = zot.children(args.item_key)
    emit({"mode": mode, "count": len(children), "children": children})
    return 0


def cmd_collections(args: argparse.Namespace) -> int:
    zot, mode = make_client(prefer=args.mode, library=args.library)
    cols = zot.everything(zot.collections())
    emit({"mode": mode, "count": len(cols), "collections": cols})
    return 0


def cmd_tags(args: argparse.Namespace) -> int:
    zot, mode = make_client(prefer=args.mode, library=args.library)
    tags = zot.everything(zot.tags())
    emit({"mode": mode, "count": len(tags), "tags": tags})
    return 0


def cmd_fulltext(args: argparse.Namespace) -> int:
    """Retrieve the indexed full text of one attachment."""
    zot, mode = make_client(prefer=args.mode, library=args.library)
    try:
        result = zot.fulltext_item(args.attachment_key)
    except Exception as exc:  # noqa: BLE001
        return fail(f"could not retrieve full text for attachment: {exc}")
    emit({"mode": mode, "attachment_key": args.attachment_key, "fulltext": result})
    return 0


def cmd_doiindex(args: argparse.Namespace) -> int:
    """Build a DOI -> item-key index across the top-level library items."""
    zot, mode = make_client(prefer=args.mode, library=args.library)
    items = zot.everything(zot.top())
    index: dict[str, str] = {}
    for it in items:
        data = it.get("data", {})
        doi = data.get("DOI")
        if doi:
            index[doi] = data.get("key", it.get("key"))
    emit({"mode": mode, "count": len(index), "doi_index": index})
    return 0


def cmd_pdf(args: argparse.Namespace) -> int:
    """Resolve a PDF path: local Zotero storage first, then Web API download.

    Preserves the legacy local-storage-first behavior. Prints the resolved
    path on stdout (as JSON) and returns non-zero if no valid PDF is found.
    """
    key = args.attachment_key

    # 1. Local Zotero storage.
    storage = Path.home() / "Zotero" / "storage" / key
    if storage.is_dir():
        pdfs = sorted(storage.glob("*.pdf"))
        if pdfs:
            emit({"source": "local-storage", "path": str(pdfs[0])})
            return 0

    # 2. Web API download.
    try:
        zot, _ = make_client(prefer="web", library=args.library)
    except RuntimeError as exc:
        return fail(
            f"PDF not in local storage and Web API not configured for download — {exc}"
        )

    # Recover the original filename from item metadata; fall back to the key.
    try:
        meta = zot.item(key)
        filename = meta.get("data", {}).get("filename") or f"{key}.pdf"
    except Exception:  # noqa: BLE001
        filename = f"{key}.pdf"

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    try:
        content = zot.file(key)
    except Exception as exc:  # noqa: BLE001
        return fail(f"Web API download failed: {exc}")

    out_path.write_bytes(content)
    if not out_path.exists() or out_path.stat().st_size < PDF_MIN_BYTES:
        return fail(
            f"downloaded file is too small ({out_path.stat().st_size} bytes); "
            "the attachment may be a linked file or have no stored PDF"
        )
    emit({"source": "web-download", "path": str(out_path)})
    return 0


def select_item_keys(zot, args: argparse.Namespace) -> list[str]:
    """Resolve the ``bibtex`` selection flags to a list of Zotero item keys.

    Honors ``--item-key`` (repeatable), ``--query`` (metadata search, same path
    as the ``search`` command), and ``--doi`` (DOI -> item-key via the same
    index as ``doiindex``). Raises RuntimeError when nothing resolves.
    """
    keys: list[str] = list(args.item_key or [])
    if args.query:
        results = zot.items(q=args.query, qmode="titleCreatorYear", limit=args.limit)
        for it in results:
            data = it.get("data", {})
            if data.get("itemType") in (None, "attachment", "note"):
                continue
            k = data.get("key") or it.get("key")
            if k:
                keys.append(k)
    if args.doi:
        items = zot.everything(zot.top())
        index = {
            data.get("DOI"): (data.get("key") or it.get("key"))
            for it in items
            for data in [it.get("data", {})]
            if data.get("DOI")
        }
        for doi in args.doi:
            if doi in index:
                keys.append(index[doi])
            else:
                raise RuntimeError(f"no library item found for DOI {doi!r}")
    # De-duplicate, preserving order.
    seen: set[str] = set()
    ordered = [k for k in keys if not (k in seen or seen.add(k))]
    if not ordered:
        raise RuntimeError(
            "no items selected: pass --item-key, --query, and/or --doi"
        )
    return ordered


def cmd_bibtex(args: argparse.Namespace) -> int:
    """Emit BibTeX (BBT citekeys by default) and optionally sync a master .bib."""
    if not (args.item_key or args.query or args.doi):
        return fail("select items with --item-key, --query, and/or --doi")
    zot, mode = make_client(prefer=args.mode, library=args.library)
    item_keys = select_item_keys(zot, args)
    bbt_used, citekeys, text = resolve_keys(zot, item_keys, args.library)

    result: dict[str, object] = {
        "mode": mode,
        "library": args.library,
        "bbt_used": bbt_used,
        "bbt_fallback": not bbt_used,
        "keys": citekeys,
        "bib_path": None,
        "added": [],
        "skipped": [],
    }
    if not bbt_used:
        bbt_fallback_warning()
    if args.bib:
        added, skipped = sync_bib(Path(args.bib), text)
        result["bib_path"] = args.bib
        result["added"] = added
        result["skipped"] = skipped
        emit(result)
    else:
        result["bibtex"] = text
        emit(result)
    return 0


def bbt_fallback_warning() -> None:
    eprint(
        "warning: Better BibTeX unreachable — used Zotero's built-in "
        "translator. The emitted citekeys may NOT match your "
        "BBT-exported .bib (bbt_fallback=true)."
    )


def check_draft_target(draft: "Path", marker: str | None) -> None:
    """Validate the draft target (and marker, if given) without mutating it.

    Raises RuntimeError if the draft is absent or a given marker is not present.
    Lets ``cmd_cite`` reject a bad target *before* it syncs the master ``.bib``,
    so a typo'd ``--marker`` cannot pollute the user's `.bib`.
    """
    if not draft.exists():
        raise RuntimeError(f"draft file not found: {draft}")
    if marker is not None and marker not in draft.read_text(encoding="utf-8"):
        raise RuntimeError(
            f"marker {marker!r} not found in {draft} — nothing replaced"
        )


def insert_citation(draft: "Path", citation: str, marker: str | None) -> None:
    """Insert ``citation`` into ``draft``: replace the first ``marker`` or append.

    With ``marker`` given, the first occurrence is replaced in place; a missing
    marker raises RuntimeError rather than appending. Without ``marker``, the
    citation is appended on its own line. Raises RuntimeError if the draft is
    absent (the citation targets an existing draft, not a fresh file).
    """
    check_draft_target(draft, marker)
    text = draft.read_text(encoding="utf-8")
    if marker is not None:
        text = text.replace(marker, citation, 1)
    else:
        sep = "" if not text or text.endswith("\n") else "\n"
        text = text + sep + citation + "\n"
    draft.write_text(text, encoding="utf-8")


def cmd_cite(args: argparse.Namespace) -> int:
    """Insert a citation into a draft and sync its entry into the master .bib."""
    if not (args.item_key or args.query or args.doi):
        return fail("select an item with --item-key, --query, and/or --doi")
    if bool(args.tex) == bool(args.markdown):
        return fail("pass exactly one of --tex or --markdown")
    zot, mode = make_client(prefer=args.mode, library=args.library)
    item_keys = select_item_keys(zot, args)
    bbt_used, citekeys, text = resolve_keys(zot, item_keys, args.library)
    if not bbt_used:
        bbt_fallback_warning()

    # Cite the first resolved item; selection may match several, but a single
    # insertion is unambiguous and the .bib still syncs every resolved entry.
    key = citekeys[0]
    if args.tex:
        draft = Path(args.tex)
        citation = f"\\cite{{{key}}}"
    else:
        draft = Path(args.markdown)
        citation = f"[@{key}]"

    # Validate the draft target / marker BEFORE mutating the master .bib, so a
    # missing draft or typo'd --marker cannot leave a synced entry behind.
    check_draft_target(draft, args.marker)
    added, skipped = sync_bib(Path(args.bib), text)
    insert_citation(draft, citation, args.marker)

    emit(
        {
            "mode": mode,
            "library": args.library,
            "bbt_used": bbt_used,
            "bbt_fallback": not bbt_used,
            "edited_file": str(draft),
            "citation_key": key,
            "citation": citation,
            "bib_path": args.bib,
            "added": added,
            "skipped": skipped,
        }
    )
    return 0


def cmd_bibliography(args: argparse.Namespace) -> int:
    """Render formatted reference entries (default APA) for selected items."""
    if not (args.item_key or args.query or args.doi):
        return fail("select items with --item-key, --query, and/or --doi")
    zot, mode = make_client(prefer=args.mode, library=args.library)
    item_keys = select_item_keys(zot, args)
    bbt_used, entries = resolve_bibliography(zot, item_keys, args.library, args.style)
    if not bbt_used:
        bbt_fallback_warning()

    if args.text:
        for entry in entries:
            print(entry)
        return 0

    emit(
        {
            "mode": mode,
            "library": args.library,
            "style": args.style,
            "bbt_used": bbt_used,
            "bbt_fallback": not bbt_used,
            "count": len(entries),
            "entries": entries,
        }
    )
    return 0


# --------------------------------------------------------------------------- #
# Local connector transport and endpoints (write path)                        #
# --------------------------------------------------------------------------- #


class ConnectorError(RuntimeError):
    """The Zotero desktop connector is unreachable or returned an error.

    Callers on the ``auto`` path treat unreachability as the signal to fall back
    to the cloud Web API write path.
    """


class UrllibConnectorTransport:
    """Default stdlib transport for the connector; injectable for offline tests.

    ``request`` returns ``(status, body_bytes, headers)`` for any HTTP status so
    callers can branch on 201/409/etc., and raises ConnectorError only when the
    connector cannot be reached at all.
    """

    def request(self, url, data=None, headers=None, method="POST", timeout=30.0):
        import urllib.error
        import urllib.request

        req = urllib.request.Request(
            url, data=data, headers=headers or {}, method=method
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
                return resp.status, resp.read(), dict(resp.headers)
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), dict(exc.headers or {})
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ConnectorError(
                f"Zotero connector unreachable at {CONNECTOR_BASE}: {exc}"
            ) from exc


def _connector_post_json(path, body, transport, extra_headers=None):
    """POST a JSON body to a connector endpoint, returning ``(status, text)``."""
    headers = dict(CONNECTOR_HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    data = json.dumps(body).encode("utf-8")
    status, raw, _ = transport.request(
        f"{CONNECTOR_BASE}/{path}", data=data, headers=headers, method="POST"
    )
    text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
    return status, text


def connector_available(transport=None) -> bool:
    """Report whether the Zotero desktop connector answers its ping.

    The connector port responds even when the read-only local /api is disabled,
    so this is a distinct probe from ``local_api_available``.
    """
    transport = transport or UrllibConnectorTransport()
    try:
        status, _, _ = transport.request(
            f"{CONNECTOR_BASE}/ping",
            headers={"User-Agent": CONNECTOR_HEADERS["User-Agent"]},
            method="GET",
        )
    except ConnectorError:
        return False
    return 200 <= status < 300


def connector_selected_collection(transport=None) -> dict:
    """Read the library/collection currently selected in the Zotero desktop UI.

    ``saveItems`` takes no target parameter — items land wherever this points —
    so the workflow reports this before a local save and asks the user to switch
    the UI selection first if they want a different destination.
    """
    transport = transport or UrllibConnectorTransport()
    status, text = _connector_post_json("getSelectedCollection", {}, transport)
    if not (200 <= status < 300):
        raise ConnectorError(
            f"getSelectedCollection failed (HTTP {status}): {text[:200]}"
        )
    return json.loads(text) if text.strip() else {}


def summarize_selected(sel: dict | None) -> dict | None:
    """Reduce a getSelectedCollection payload to the fields the agent reports."""
    if not sel:
        return None
    return {
        "library_id": sel.get("libraryID"),
        "library_name": sel.get("libraryName"),
        "collection_id": sel.get("id"),
        "collection_name": sel.get("name"),
        "editable": sel.get("editable"),
        "targets": [
            {"id": t.get("id"), "name": t.get("name"), "level": t.get("level")}
            for t in (sel.get("targets") or [])
        ],
    }


def connector_save_items(item, transport=None, uri=None, max_retries=2):
    """Save one mapped item via the connector, returning ``(session_id, text)``.

    A fresh UUID sessionID is minted per attempt; a ``409 SESSION_EXISTS`` is
    retried with a new session. 200/201 are success. Raises ConnectorError on
    any other status or after exhausting retries.
    """
    transport = transport or UrllibConnectorTransport()
    last = ""
    for _ in range(max_retries + 1):
        session_id = str(uuid.uuid4())
        body = {
            "items": [item],
            "sessionID": session_id,
            "uri": uri or item.get("url") or "",
        }
        status, text = _connector_post_json("saveItems", body, transport)
        if status == 409:  # SESSION_EXISTS — mint a new session and retry.
            last = text
            continue
        if status in (200, 201):
            return session_id, text
        raise ConnectorError(f"saveItems failed (HTTP {status}): {text[:200]}")
    raise ConnectorError(
        f"saveItems failed after {max_retries} session-collision retries: {last[:200]}"
    )


def connector_update_session(session_id, target, transport=None, tags=""):
    """Steer a save session to a specific target id (a ``targets[].id`` value)."""
    transport = transport or UrllibConnectorTransport()
    body = {"sessionID": session_id, "target": target, "tags": tags}
    status, text = _connector_post_json("updateSession", body, transport)
    if not (200 <= status < 300):
        raise ConnectorError(f"updateSession failed (HTTP {status}): {text[:200]}")
    return text


# --------------------------------------------------------------------------- #
# Crossref/S2 record -> Zotero item mapper                                     #
# --------------------------------------------------------------------------- #

# Crossref work `type` -> Zotero itemType, for the econ/finance surface: journal
# articles, preprints (posted-content), and working-paper reports. Anything else
# falls through to the heuristic in ``choose_item_type``.
CROSSREF_TYPE_MAP = {
    "journal-article": "journalArticle",
    "posted-content": "preprint",
    "report": "report",
    "report-series": "report",
    "report-component": "report",
}
ITEM_TYPES = ("journalArticle", "preprint", "report")


def _raw(record: dict) -> dict:
    r = record.get("raw")
    return r if isinstance(r, dict) else {}


def _first(value):
    if isinstance(value, list):
        return value[0] if value else None
    return value


def choose_item_type(record: dict) -> str:
    """Pick the Zotero item type from the verbatim record, never inventing one.

    Crossref's `type` is authoritative when present. Otherwise: an arXiv record
    or any record with no published DOI is a preprint (unpublished working
    paper); a resolved DOI defaults to a journal article.
    """
    cr_type = record.get("type")
    if cr_type in CROSSREF_TYPE_MAP:
        return CROSSREF_TYPE_MAP[cr_type]
    ids = record.get("id") or {}
    if record.get("source") == "arxiv" or ids.get("arxiv"):
        return "preprint"
    if not ids.get("doi"):
        return "preprint"
    return "journalArticle"


def _creators(record: dict) -> list[dict]:
    """Map authors to Zotero creators, verbatim.

    Two-field (firstName/lastName) only when Crossref supplied the given/family
    split; otherwise a single-field ``name`` creator (S2/arXiv expose only a
    display name — never infer a split).
    """
    creators: list[dict] = []
    for a in record.get("authors") or []:
        given, family = a.get("given"), a.get("family")
        if given or family:
            creators.append(
                {
                    "creatorType": "author",
                    "firstName": given or "",
                    "lastName": family or "",
                }
            )
        elif a.get("name"):
            creators.append({"creatorType": "author", "name": a["name"]})
    return creators


def _record_date(record: dict) -> str | None:
    """Resolve a Zotero ``date`` string from the verbatim Crossref date-parts.

    Falls back to the record's year. Returns YYYY / YYYY-MM / YYYY-MM-DD.
    """
    raw = _raw(record)
    for key in ("published-print", "published-online", "published", "issued"):
        block = raw.get(key)
        if isinstance(block, dict):
            parts = block.get("date-parts") or []
            if parts and parts[0]:
                p = parts[0]
                if len(p) >= 3:
                    return f"{p[0]}-{p[1]:02d}-{p[2]:02d}"
                if len(p) == 2:
                    return f"{p[0]}-{p[1]:02d}"
                return str(p[0])
    year = record.get("year")
    return str(year) if year else None


def _clean_abstract(record: dict) -> str | None:
    """Return the abstract to store, ignoring the Crossref source.

    Crossref abstracts arrive JATS-tagged (``<jats:p>…``) and are spotty for
    econ; the client only falls back to them when S2/arXiv had none, so a
    ``crossref``-sourced abstract is dropped rather than stored tagged.
    """
    abstract = record.get("abstract")
    if not abstract or record.get("abstract_source") == "crossref":
        return None
    return abstract


def crossref_to_zotero(
    record: dict,
    item_type: str | None = None,
    pdf_url: str | None = None,
    pdf_divergence: str | None = None,
) -> dict:
    """Map a verbatim citation-client record to a Zotero item dict.

    Covers the econ/finance item types (journalArticle, preprint, report). Every
    bibliographic field is taken verbatim from the record / its ``raw`` Crossref
    payload — nothing is agent-composed. ``report`` has no Zotero DOI field, so a
    report's DOI is preserved in ``extra``. The PDF version-divergence flag is
    surfaced as a tag and an ``extra`` line.
    """
    itype = item_type or choose_item_type(record)
    if itype not in ITEM_TYPES:
        raise RuntimeError(
            f"unsupported item type {itype!r}; use one of {', '.join(ITEM_TYPES)}"
        )
    ids = record.get("id") or {}
    ext = record.get("external_ids") or {}
    doi = ids.get("doi") or ext.get("DOI")
    raw = _raw(record)

    item: dict[str, object] = {"itemType": itype, "creators": _creators(record)}
    if record.get("title"):
        item["title"] = record["title"]
    date = _record_date(record)
    if date:
        item["date"] = date
    abstract = _clean_abstract(record)
    if abstract:
        item["abstractNote"] = abstract
    if record.get("url"):
        item["url"] = record["url"]
    if raw.get("language"):
        item["language"] = raw["language"]

    tags: list[dict] = []
    extra_lines: list[str] = []

    if itype == "journalArticle":
        venue = record.get("venue") or _first(raw.get("container-title"))
        if venue:
            item["publicationTitle"] = venue
        volume = record.get("volume") or raw.get("volume")
        if volume:
            item["volume"] = str(volume)
        if raw.get("issue"):
            item["issue"] = str(raw["issue"])
        pages = record.get("pages") or raw.get("page")
        if pages:
            item["pages"] = str(pages)
        issn = _first(raw.get("ISSN"))
        if issn:
            item["ISSN"] = issn
        if doi:
            item["DOI"] = doi
    elif itype == "preprint":
        repository = record.get("venue") or _first(raw.get("container-title"))
        if not repository and (record.get("source") == "arxiv" or ids.get("arxiv")):
            repository = "arXiv"
        if repository:
            item["repository"] = repository
        arxiv_id = ids.get("arxiv") or ext.get("ArXiv")
        if arxiv_id:
            item["archiveID"] = f"arXiv:{arxiv_id}"
        if doi:
            item["DOI"] = doi
    elif itype == "report":
        institution = record.get("venue") or _first(raw.get("container-title"))
        raw_inst = _first(raw.get("institution"))
        if isinstance(raw_inst, dict) and raw_inst.get("name"):
            institution = raw_inst["name"]
        if institution:
            item["institution"] = institution
        pages = record.get("pages") or raw.get("page")
        if pages:
            item["pages"] = str(pages)
        # Zotero's report type has no DOI field — preserve it in extra.
        if doi:
            extra_lines.append(f"DOI: {doi}")

    if pdf_divergence:
        tags.append({"tag": f"pdf-divergence: {pdf_divergence}"})
        extra_lines.append(f"PDF version divergence: {pdf_divergence}")
    if pdf_url:
        item["attachments"] = [
            {
                "title": "Full Text PDF",
                "mimeType": "application/pdf",
                "url": pdf_url,
            }
        ]
    if extra_lines:
        item["extra"] = "\n".join(extra_lines)
    if tags:
        item["tags"] = tags
    return item


def to_web_item(item: dict, collection: str | None = None) -> dict:
    """Adapt a mapped item for the Web API (pyzotero ``create_items``).

    The connector consumes the ``attachments`` array directly; the Web API takes
    attachments through a separate call, so drop it here. A ``--collection`` key
    targets a specific collection on the Web path (the connector ignores it and
    uses the UI selection).
    """
    web = {k: v for k, v in item.items() if k != "attachments"}
    if collection:
        web["collections"] = [collection]
    return web


# --------------------------------------------------------------------------- #
# Write-path subcommand handlers                                              #
# --------------------------------------------------------------------------- #


def _load_record(args: argparse.Namespace) -> dict:
    """Load a citation-client record from ``--record`` or stdin.

    Unwraps the ``metadata`` command's ``{record: …}`` envelope and a
    ``{records: [...]}`` list (first element), so a screening-time payload can be
    piped straight in.
    """
    if args.record:
        text = Path(args.record).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()
    if not text.strip():
        raise RuntimeError(
            "no record provided: pass --record PATH or pipe record JSON on stdin"
        )
    obj = json.loads(text)
    if isinstance(obj, dict):
        if isinstance(obj.get("record"), dict):
            return obj["record"]
        if isinstance(obj.get("records"), list) and obj["records"]:
            return obj["records"][0]
    if not isinstance(obj, dict):
        raise RuntimeError("record JSON must be an object (or a wrapper of one)")
    return obj


def find_duplicate_doi(doi, prefer, library, client_factory) -> str | None:
    """Return the item key of an existing library item with the same DOI, if any.

    Best-effort: if a client for the dedup target cannot be built or queried
    (e.g. the read-only local /api is disabled), returns None so the save still
    proceeds — the caller reports that dedup could not run.
    """
    factory = client_factory or make_client
    norm = doi.lower()
    try:
        zot, _ = factory(prefer=prefer, library=library)
        items = zot.everything(zot.top())
    except Exception:  # noqa: BLE001
        return None
    for it in items:
        data = it.get("data", {})
        existing = data.get("DOI")
        if existing and existing.lower() == norm:
            return data.get("key") or it.get("key")
    return None


def cmd_add(args, transport=None, client_factory=None) -> int:
    """Map a discovered record to a Zotero item and save it (connector or Web API).

    Path selection: ``--mode local`` forces the connector, ``--mode web`` forces
    the Web API. On ``auto`` a group ``--library`` or a ``--collection`` (which
    the connector cannot target) routes to the Web API; otherwise the connector
    is used when reachable, else the Web API.
    """
    record = _load_record(args)
    item = crossref_to_zotero(
        record,
        item_type=args.item_type,
        pdf_url=args.pdf_url,
        pdf_divergence=args.pdf_divergence,
    )
    ids = record.get("id") or {}
    doi = item.get("DOI") or ids.get("doi") or (record.get("external_ids") or {}).get(
        "DOI"
    )

    if args.dry_run:
        emit(
            {
                "saved": False,
                "dry_run": True,
                "item_type": item["itemType"],
                "doi": doi,
                "item": item,
            }
        )
        return 0

    lib_type, _ = parse_library(args.library)
    wants_web = args.mode == "web" or (
        args.mode == "auto" and (lib_type == "group" or bool(args.collection))
    )
    use_connector = args.mode == "local" or (
        args.mode == "auto" and not wants_web and connector_available(transport)
    )

    # Dedup upstream — the connector never dedups and will create duplicates.
    dedup_ran = False
    if not args.allow_duplicate and doi:
        prefer = "local" if use_connector else "web"
        library = "user" if use_connector else args.library
        existing = find_duplicate_doi(doi, prefer, library, client_factory)
        dedup_ran = True
        if existing:
            emit(
                {
                    "saved": False,
                    "duplicate": True,
                    "doi": doi,
                    "existing_item_key": existing,
                    "item_type": item["itemType"],
                }
            )
            return 0

    if use_connector:
        selected = None
        try:
            selected = connector_selected_collection(transport)
        except ConnectorError:
            pass
        session_id, _ = connector_save_items(
            item, transport=transport, uri=record.get("url")
        )
        moved_to = None
        if args.target:
            connector_update_session(session_id, args.target, transport=transport)
            moved_to = args.target
        emit(
            {
                "saved": True,
                "path": "local-connector",
                "item_type": item["itemType"],
                "doi": doi,
                "dedup_checked": dedup_ran,
                "selected_target": summarize_selected(selected),
                "moved_to_target": moved_to,
                "attached_pdf_url": args.pdf_url,
            }
        )
        return 0

    # Web API path.
    factory = client_factory or make_client
    zot, _ = factory(prefer="web", library=args.library)
    resp = zot.create_items([to_web_item(item, collection=args.collection)])
    success = resp.get("success", {}) if isinstance(resp, dict) else {}
    failed = resp.get("failed", {}) if isinstance(resp, dict) else {}
    if failed:
        return fail(f"Web API create_items rejected the item: {failed}")
    item_key = next(iter(success.values()), None)
    emit(
        {
            "saved": bool(item_key),
            "path": "web-api",
            "item_type": item["itemType"],
            "doi": doi,
            "dedup_checked": dedup_ran,
            "item_key": item_key,
            "library": args.library,
            "collection": args.collection,
        }
    )
    return 0 if item_key else 1


def cmd_attach(args, client_factory=None) -> int:
    """Attach a local PDF to an existing item via the Web API (write-scoped key).

    The connector attaches at save time through ``add --pdf-url`` (Zotero fetches
    the URL, honoring the auto-attach-PDF preference); attaching a local file to
    an already-saved item is the Web API path.
    """
    path = Path(args.file)
    if not path.exists():
        return fail(f"file not found: {path}")
    factory = client_factory or make_client
    zot, _ = factory(prefer="web", library=args.library)
    try:
        result = zot.attachment_simple([str(path)], args.item_key)
    except Exception as exc:  # noqa: BLE001
        return fail(f"attachment upload failed: {exc}")
    emit(
        {
            "path": "web-api",
            "parent_item_key": args.item_key,
            "file": str(path),
            "library": args.library,
            "result": result,
        }
    )
    return 0


def cmd_selected(args, transport=None) -> int:
    """Report the library/collection currently selected in the Zotero desktop UI."""
    try:
        sel = connector_selected_collection(transport)
    except ConnectorError as exc:
        return fail(str(exc))
    emit({"path": "local-connector", "selected_target": summarize_selected(sel)})
    return 0


# --------------------------------------------------------------------------- #
# Argument parsing                                                            #
# --------------------------------------------------------------------------- #


def add_mode_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--mode",
        choices=["auto", "local", "web"],
        default="auto",
        help="access mode (default: auto — local if available, else web)",
    )


def add_library_arg(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--library",
        default="user",
        metavar="LIB",
        help="target library: 'user' (default), a numeric group id, or "
        "'group:<id>' (list ids with the 'libraries' command)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zotero_tool.py",
        description="Local-first pyzotero command surface (JSON output).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("health", help="report version and detected access mode")
    p.set_defaults(func=cmd_health)

    p = sub.add_parser(
        "libraries", help="list the user library and all group libraries"
    )
    add_mode_arg(p)
    p.set_defaults(func=cmd_libraries)

    p = sub.add_parser("search", help="metadata or full-text library search")
    p.add_argument("query", help="search terms")
    p.add_argument(
        "--fulltext",
        action="store_true",
        help="full-text search of indexed content (local or web)",
    )
    p.add_argument("--limit", type=int, default=25, help="max results (default 25)")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("item", help="get a single item by key")
    p.add_argument("item_key")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_item)

    p = sub.add_parser("children", help="list child items / attachments of an item")
    p.add_argument("item_key")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_children)

    p = sub.add_parser("collections", help="list all collections")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_collections)

    p = sub.add_parser("tags", help="list all tags")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_tags)

    p = sub.add_parser(
        "fulltext", help="retrieve indexed full text of one attachment"
    )
    p.add_argument("attachment_key")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_fulltext)

    p = sub.add_parser("doiindex", help="build a DOI -> item-key index")
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_doiindex)

    p = sub.add_parser(
        "pdf", help="resolve PDF path (local storage first, then web download)"
    )
    p.add_argument("attachment_key")
    p.add_argument(
        "--out-dir", default="/tmp", help="download directory (default /tmp)"
    )
    add_library_arg(p)
    p.set_defaults(func=cmd_pdf)

    p = sub.add_parser(
        "bibtex",
        help="emit BibTeX (Better BibTeX citekeys by default) and optionally "
        "sync a master .bib",
    )
    p.add_argument(
        "--item-key",
        action="append",
        metavar="KEY",
        help="Zotero item key to export (repeatable)",
    )
    p.add_argument(
        "--query", metavar="TEXT", help="select items by metadata search"
    )
    p.add_argument(
        "--doi",
        action="append",
        metavar="DOI",
        help="select an item by DOI (repeatable)",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=25,
        help="max --query matches to include (default 25)",
    )
    p.add_argument(
        "--bib",
        metavar="PATH",
        help="master .bib to dedup-append into (default: print to stdout)",
    )
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_bibtex)

    p = sub.add_parser(
        "cite",
        help="insert a citation into a draft and sync its entry into a .bib",
    )
    p.add_argument(
        "--item-key",
        action="append",
        metavar="KEY",
        help="Zotero item key to cite (repeatable; the first is inserted)",
    )
    p.add_argument("--query", metavar="TEXT", help="select item by metadata search")
    p.add_argument(
        "--doi", action="append", metavar="DOI", help="select item by DOI (repeatable)"
    )
    p.add_argument(
        "--limit", type=int, default=25, help="max --query matches (default 25)"
    )
    p.add_argument("--tex", metavar="FILE", help="draft .tex file (inserts \\cite{KEY})")
    p.add_argument(
        "--markdown", metavar="FILE", help="draft .md file (inserts [@KEY])"
    )
    p.add_argument(
        "--marker",
        metavar="STR",
        help="replace the first occurrence of STR (default: append)",
    )
    p.add_argument(
        "--bib",
        required=True,
        metavar="PATH",
        help="master .bib to dedup-append the cited entry into",
    )
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_cite)

    p = sub.add_parser(
        "bibliography",
        help="render formatted reference entries (default APA) for items",
    )
    p.add_argument(
        "--item-key",
        action="append",
        metavar="KEY",
        help="Zotero item key to render (repeatable)",
    )
    p.add_argument("--query", metavar="TEXT", help="select items by metadata search")
    p.add_argument(
        "--doi", action="append", metavar="DOI", help="select items by DOI (repeatable)"
    )
    p.add_argument(
        "--limit", type=int, default=25, help="max --query matches (default 25)"
    )
    p.add_argument(
        "--style",
        default="apa",
        metavar="ID",
        help="CSL style id (default apa)",
    )
    p.add_argument(
        "--text",
        action="store_true",
        help="print rendered entries as plain text (default: JSON)",
    )
    add_mode_arg(p)
    add_library_arg(p)
    p.set_defaults(func=cmd_bibliography)

    p = sub.add_parser(
        "add",
        help="save a discovered paper (record JSON) to Zotero: local connector "
        "by default, Web API fallback",
    )
    p.add_argument(
        "--record",
        metavar="PATH",
        help="citation-client record JSON file (default: read from stdin)",
    )
    p.add_argument(
        "--mode",
        choices=["auto", "local", "web"],
        default="auto",
        help="write path: auto (connector if reachable, else Web API), local "
        "(connector), or web (Web API)",
    )
    p.add_argument(
        "--item-type",
        choices=list(ITEM_TYPES),
        help="override the inferred Zotero item type",
    )
    p.add_argument(
        "--collection",
        metavar="KEY",
        help="Web API: target collection key (routes auto mode to the Web API)",
    )
    p.add_argument(
        "--pdf-url",
        metavar="URL",
        help="attach a PDF by URL (connector fetches it, honoring auto-attach)",
    )
    p.add_argument(
        "--pdf-divergence",
        metavar="TEXT",
        help="surface a metadata-vs-PDF version divergence as a tag + extra note",
    )
    p.add_argument(
        "--target",
        metavar="ID",
        help="connector: steer the save session to a targets[].id (see 'selected')",
    )
    p.add_argument(
        "--allow-duplicate",
        action="store_true",
        help="skip the DOI dedup check (the connector never dedups)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="map and print the Zotero item without saving",
    )
    add_library_arg(p)
    p.set_defaults(func=cmd_add)

    p = sub.add_parser(
        "attach",
        help="attach a local PDF to an existing item via the Web API",
    )
    p.add_argument("--item-key", required=True, metavar="KEY", help="parent item key")
    p.add_argument("--file", required=True, metavar="PATH", help="PDF file to attach")
    add_library_arg(p)
    p.set_defaults(func=cmd_attach)

    p = sub.add_parser(
        "selected",
        help="report the library/collection selected in the Zotero desktop UI "
        "(local connector save target)",
    )
    p.set_defaults(func=cmd_selected)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as exc:
        return fail(str(exc))
    except Exception as exc:  # noqa: BLE001
        # Defensive: pyzotero / network errors. Message is tool-constructed and
        # the exception text from pyzotero does not contain credential values.
        return fail(f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    sys.exit(main())
