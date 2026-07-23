#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest"]
# ///
"""Offline tests for the zotero_tool write path (add / attach / connector).

Runs with no network, no Zotero desktop, and no credentials: the connector is
served by ``FakeConnectorTransport`` and the Web API by ``FakeZotero``. Fixtures
are hypothetical — no real library data. Run:

    uv run --with pytest python -m pytest skills/zotero-paper-reader/scripts/test_zotero_tool.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import zotero_tool as zt


# --------------------------------------------------------------------------- #
# Fakes                                                                       #
# --------------------------------------------------------------------------- #


class FakeConnectorTransport:
    """Serve scripted connector responses keyed by URL substring.

    ``routes`` maps a path fragment to a list of ``(status, payload)`` responses
    consumed in order (so a 409-then-201 retry can be scripted), or a single
    tuple reused for every call. ``payload`` is a dict/str (JSON-encoded) or
    bytes. ``calls`` records ``(method, url, headers, body)`` for assertions.
    """

    def __init__(self, routes):
        self.routes = {k: (v if isinstance(v, list) else [v]) for k, v in routes.items()}
        self.calls = []

    def request(self, url, data=None, headers=None, method="POST", timeout=30.0):
        body = None
        if data is not None:
            body = json.loads(data.decode("utf-8"))
        self.calls.append((method, url, dict(headers or {}), body))
        for frag, responses in self.routes.items():
            if frag in url:
                status, payload = responses.pop(0) if len(responses) > 1 else responses[0]
                if isinstance(payload, (dict, list)):
                    raw = json.dumps(payload).encode("utf-8")
                elif isinstance(payload, bytes):
                    raw = payload
                else:
                    raw = str(payload).encode("utf-8")
                return status, raw, {}
        return 404, b"", {}


class FakeZotero:
    """Minimal pyzotero stand-in for the Web API write/dedup paths."""

    def __init__(self, top_items=None, create_result=None, attach_result=None):
        self._top = top_items or []
        self._create_result = create_result or {"success": {"0": "NEWKEY01"}, "failed": {}}
        self._attach_result = attach_result or {"success": {}, "failure": {}}
        self.created = []
        self.attached = []

    def everything(self, x):
        return x

    def top(self):
        return self._top

    def create_items(self, items):
        self.created.append(items)
        return self._create_result

    def attachment_simple(self, files, parent):
        self.attached.append((files, parent))
        return self._attach_result


def factory_for(zot):
    def _factory(prefer="auto", library="user"):
        return zot, "web"
    return _factory


# --------------------------------------------------------------------------- #
# Fixtures                                                                    #
# --------------------------------------------------------------------------- #

JOURNAL_RECORD = {
    "id": {"doi": "10.1111/jofi.10001", "arxiv": None, "s2": "aaaa1111"},
    "external_ids": {"DOI": "10.1111/jofi.10001"},
    "title": "Heterogeneous Investors and Asset Prices",
    "authors": [
        {"name": "Ada Lovelace", "given": "Ada", "family": "Lovelace"},
        {"name": "Grace Hopper", "given": "Grace", "family": "Hopper"},
    ],
    "year": 2023,
    "venue": "The Journal of Finance",
    "abstract": "We study how investor heterogeneity shapes prices.",
    "abstract_source": "s2",
    "url": "https://doi.org/10.1111/jofi.10001",
    "type": "journal-article",
    "volume": "78",
    "pages": "1-40",
    "source": "crossref",
    "raw": {
        "type": "journal-article",
        "container-title": ["The Journal of Finance"],
        "volume": "78",
        "issue": "1",
        "page": "1-40",
        "ISSN": ["0022-1082"],
        "language": "en",
        "issued": {"date-parts": [[2023, 2, 15]]},
    },
}

ARXIV_RECORD = {
    "id": {"doi": None, "arxiv": "2101.00001", "s2": "bbbb2222"},
    "external_ids": {"ArXiv": "2101.00001"},
    "title": "A Preprint on Investor Beliefs",
    "authors": [{"name": "Alan Turing", "given": None, "family": None}],
    "year": 2021,
    "venue": None,
    "abstract": "A preprint abstract from arXiv.",
    "abstract_source": "arxiv",
    "url": "https://arxiv.org/abs/2101.00001",
    "type": None,
    "source": "arxiv",
    "raw": {},
}

REPORT_RECORD = {
    "id": {"doi": "10.3386/w30000", "arxiv": None, "s2": "cccc3333"},
    "external_ids": {"DOI": "10.3386/w30000"},
    "title": "A Working Paper on Beliefs",
    "authors": [{"name": "Katherine Johnson", "given": "Katherine", "family": "Johnson"}],
    "year": 2022,
    "venue": "National Bureau of Economic Research",
    "abstract": "<jats:p>JATS abstract.</jats:p>",
    "abstract_source": "crossref",
    "url": "https://doi.org/10.3386/w30000",
    "type": "report",
    "source": "crossref",
    "raw": {
        "type": "report",
        "institution": [{"name": "National Bureau of Economic Research"}],
        "issued": {"date-parts": [[2022]]},
    },
}


def run(argv, **kwargs):
    """Parse argv and dispatch, returning ``(exit_code, stdout_json)``."""
    import io
    from contextlib import redirect_stdout

    args = zt.build_parser().parse_args(argv)
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = args.func(args, **kwargs)
    out = buf.getvalue().strip()
    return code, (json.loads(out) if out else None)


# --------------------------------------------------------------------------- #
# Mapper                                                                      #
# --------------------------------------------------------------------------- #


def test_journal_article_mapping():
    item = zt.crossref_to_zotero(JOURNAL_RECORD)
    assert item["itemType"] == "journalArticle"
    assert item["title"] == "Heterogeneous Investors and Asset Prices"
    assert item["publicationTitle"] == "The Journal of Finance"
    assert item["volume"] == "78"
    assert item["issue"] == "1"
    assert item["pages"] == "1-40"
    assert item["ISSN"] == "0022-1082"
    assert item["DOI"] == "10.1111/jofi.10001"
    assert item["date"] == "2023-02-15"
    assert item["language"] == "en"
    assert item["creators"] == [
        {"creatorType": "author", "firstName": "Ada", "lastName": "Lovelace"},
        {"creatorType": "author", "firstName": "Grace", "lastName": "Hopper"},
    ]
    assert item["abstractNote"].startswith("We study")


def test_preprint_mapping_single_field_creator():
    item = zt.crossref_to_zotero(ARXIV_RECORD)
    assert item["itemType"] == "preprint"
    assert item["repository"] == "arXiv"
    assert item["archiveID"] == "arXiv:2101.00001"
    # No given/family -> single-field creator, never an inferred split.
    assert item["creators"] == [{"creatorType": "author", "name": "Alan Turing"}]
    assert "DOI" not in item


def test_report_mapping_doi_in_extra_and_crossref_abstract_ignored():
    item = zt.crossref_to_zotero(REPORT_RECORD)
    assert item["itemType"] == "report"
    assert item["institution"] == "National Bureau of Economic Research"
    # report has no DOI field -> preserved in extra.
    assert "DOI" not in item
    assert "DOI: 10.3386/w30000" in item["extra"]
    # Crossref-sourced (JATS) abstract is dropped, not stored tagged.
    assert "abstractNote" not in item
    assert item["date"] == "2022"


def test_pdf_divergence_flag():
    item = zt.crossref_to_zotero(
        JOURNAL_RECORD, pdf_divergence="metadata=JF 2023; pdf=SSRN WP 2021"
    )
    assert {"tag": "pdf-divergence: metadata=JF 2023; pdf=SSRN WP 2021"} in item["tags"]
    assert "PDF version divergence" in item["extra"]


def test_pdf_url_attachment_and_web_item_strips_it():
    item = zt.crossref_to_zotero(JOURNAL_RECORD, pdf_url="https://example.org/wp.pdf")
    assert item["attachments"][0]["url"] == "https://example.org/wp.pdf"
    assert item["attachments"][0]["mimeType"] == "application/pdf"
    web = zt.to_web_item(item, collection="COLL01")
    assert "attachments" not in web
    assert web["collections"] == ["COLL01"]


def test_item_type_override_and_validation():
    item = zt.crossref_to_zotero(JOURNAL_RECORD, item_type="report")
    assert item["itemType"] == "report"
    with pytest.raises(RuntimeError):
        zt.crossref_to_zotero(JOURNAL_RECORD, item_type="book")


def test_choose_item_type_heuristics():
    assert zt.choose_item_type(JOURNAL_RECORD) == "journalArticle"
    assert zt.choose_item_type(ARXIV_RECORD) == "preprint"
    assert zt.choose_item_type(REPORT_RECORD) == "report"
    # No DOI, no arxiv -> unpublished working paper -> preprint.
    assert zt.choose_item_type({"id": {}, "source": "web"}) == "preprint"


# --------------------------------------------------------------------------- #
# Connector endpoints                                                         #
# --------------------------------------------------------------------------- #


def test_connector_save_items_headers_and_fresh_session():
    tr = FakeConnectorTransport({"saveItems": (201, {"items": []})})
    session_id, _ = zt.connector_save_items({"itemType": "journalArticle"}, transport=tr)
    method, url, headers, body = tr.calls[0]
    assert headers["X-Zotero-Connector-API-Version"] == "3"
    assert not headers["User-Agent"].startswith("Mozilla")
    assert headers["zotero-allowed-request"] == "1"
    assert body["sessionID"] == session_id
    # A fresh UUID per save.
    import uuid

    uuid.UUID(session_id)


def test_connector_save_items_retries_on_session_exists():
    tr = FakeConnectorTransport(
        {"saveItems": [(409, "SESSION_EXISTS"), (201, {"items": []})]}
    )
    s1, _ = zt.connector_save_items({"itemType": "report"}, transport=tr)
    assert len(tr.calls) == 2
    # The retry mints a distinct session id.
    assert tr.calls[0][3]["sessionID"] != tr.calls[1][3]["sessionID"]


def test_connector_save_items_raises_on_error_status():
    tr = FakeConnectorTransport({"saveItems": (500, "boom")})
    with pytest.raises(zt.ConnectorError):
        zt.connector_save_items({"itemType": "report"}, transport=tr)


def test_selected_collection_summary():
    payload = {
        "libraryID": 1,
        "libraryName": "My Library",
        "id": None,
        "name": "My Library",
        "editable": True,
        "targets": [
            {"id": "L1", "name": "My Library", "level": 0},
            {"id": "C1", "name": "Asset Pricing", "level": 1},
        ],
    }
    tr = FakeConnectorTransport({"getSelectedCollection": (200, payload)})
    code, out = run(["selected"], transport=tr)
    assert code == 0
    sel = out["selected_target"]
    assert sel["library_name"] == "My Library"
    assert [t["id"] for t in sel["targets"]] == ["L1", "C1"]


def test_connector_available_probes_ping():
    up = FakeConnectorTransport({"ping": (200, "Zotero is running")})
    assert zt.connector_available(up) is True
    down = FakeConnectorTransport({"nomatch": (200, "x")})
    assert zt.connector_available(down) is False


# --------------------------------------------------------------------------- #
# add command — connector, web, dedup, dry-run                                #
# --------------------------------------------------------------------------- #


def _record_stdin(record, monkeypatch):
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(record)))


def test_add_dry_run_maps_without_saving(monkeypatch):
    _record_stdin(JOURNAL_RECORD, monkeypatch)
    code, out = run(["add", "--dry-run"])
    assert code == 0
    assert out["saved"] is False
    assert out["item"]["itemType"] == "journalArticle"


def test_add_local_connector_reports_target(monkeypatch):
    _record_stdin(JOURNAL_RECORD, monkeypatch)
    tr = FakeConnectorTransport(
        {
            "getSelectedCollection": (200, {"libraryID": 1, "libraryName": "My Library", "name": "My Library", "targets": []}),
            "saveItems": (201, {"items": []}),
        }
    )
    # No duplicate in the (empty) library.
    code, out = run(
        ["add", "--mode", "local"],
        transport=tr,
        client_factory=factory_for(FakeZotero(top_items=[])),
    )
    assert code == 0
    assert out["saved"] is True
    assert out["path"] == "local-connector"
    assert out["selected_target"]["library_name"] == "My Library"


def test_add_dedup_blocks_duplicate(monkeypatch):
    _record_stdin(JOURNAL_RECORD, monkeypatch)
    existing = [{"data": {"DOI": "10.1111/JOFI.10001", "key": "DUPKEY01"}}]
    tr = FakeConnectorTransport({"saveItems": (201, {"items": []})})
    code, out = run(
        ["add", "--mode", "local"],
        transport=tr,
        client_factory=factory_for(FakeZotero(top_items=existing)),
    )
    assert out["saved"] is False
    assert out["duplicate"] is True
    assert out["existing_item_key"] == "DUPKEY01"
    # Dedup short-circuits before any saveItems call.
    assert not any("saveItems" in c[1] for c in tr.calls)


def test_add_web_fallback_creates_item(monkeypatch):
    _record_stdin(JOURNAL_RECORD, monkeypatch)
    zot = FakeZotero(top_items=[], create_result={"success": {"0": "WEBKEY01"}, "failed": {}})
    code, out = run(["add", "--mode", "web"], client_factory=factory_for(zot))
    assert code == 0
    assert out["path"] == "web-api"
    assert out["item_key"] == "WEBKEY01"
    # The mapped item was passed through, attachments stripped.
    assert zot.created[0][0]["itemType"] == "journalArticle"


def test_add_web_reports_create_failure(monkeypatch):
    _record_stdin(JOURNAL_RECORD, monkeypatch)
    zot = FakeZotero(create_result={"success": {}, "failed": {"0": {"code": 400, "message": "bad"}}})
    code, _ = run(["add", "--mode", "web"], client_factory=factory_for(zot))
    assert code == 1


def test_add_group_library_routes_to_web(monkeypatch):
    _record_stdin(JOURNAL_RECORD, monkeypatch)
    zot = FakeZotero(top_items=[])
    # auto mode + a group library must not touch the connector.
    tr = FakeConnectorTransport({"nomatch": (200, "x")})
    code, out = run(
        ["add", "--library", "group:12345"],
        transport=tr,
        client_factory=factory_for(zot),
    )
    assert out["path"] == "web-api"
    assert tr.calls == []


# --------------------------------------------------------------------------- #
# attach                                                                      #
# --------------------------------------------------------------------------- #


def test_attach_web_uploads_file(tmp_path):
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-1.7 fake")
    zot = FakeZotero()
    code, out = run(
        ["attach", "--item-key", "PARENT01", "--file", str(pdf)],
        client_factory=factory_for(zot),
    )
    assert code == 0
    assert zot.attached == [([str(pdf)], "PARENT01")]


def test_attach_missing_file_fails(tmp_path):
    code, _ = run(
        ["attach", "--item-key", "P", "--file", str(tmp_path / "nope.pdf")],
        client_factory=factory_for(FakeZotero()),
    )
    assert code == 1


# --------------------------------------------------------------------------- #
# record loading                                                              #
# --------------------------------------------------------------------------- #


def test_load_record_unwraps_metadata_envelope(monkeypatch):
    _record_stdin({"identifier": "x", "record": JOURNAL_RECORD}, monkeypatch)
    args = zt.build_parser().parse_args(["add", "--dry-run"])
    rec = zt._load_record(args)
    assert rec["title"] == JOURNAL_RECORD["title"]
