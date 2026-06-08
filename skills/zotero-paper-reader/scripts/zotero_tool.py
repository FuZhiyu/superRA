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
from pathlib import Path

LOCAL_API_BASE = "http://localhost:23119/api"
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
