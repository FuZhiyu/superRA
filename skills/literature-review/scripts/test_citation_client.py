#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest"]
# ///
"""Offline tests for citation_client.

Runs with no network and no API keys: every API call is served by ``FakeTransport``
from inline synthetic fixtures, and the pure functions (normalization, dedup,
mappers) are exercised directly. Fixtures are hypothetical — no real library
data. Run:

    uv run --with pytest python -m pytest skills/literature-review/scripts/test_citation_client.py
"""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

import citation_client as cc


# --------------------------------------------------------------------------- #
# Fake transport                                                              #
# --------------------------------------------------------------------------- #


class FakeTransport:
    """Serve fixture responses keyed by URL substring — never touches the network.

    ``routes`` maps a substring to ``(status, payload)``. ``payload`` is a dict/list
    for JSON routes and a str for text (arXiv) routes. An unmatched URL returns 404.
    ``calls`` records every requested URL for assertion.
    """

    def __init__(self, routes: dict[str, tuple[int, object]]):
        self.routes = routes
        self.calls: list[str] = []

    def _match(self, url: str):
        self.calls.append(url)
        for frag, resp in self.routes.items():
            if frag in url:
                return resp
        return (404, None)

    def get_json(self, url, headers=None):
        status, payload = self._match(url)
        return status, payload, {}

    def get_text(self, url, headers=None):
        status, payload = self._match(url)
        return status, payload if isinstance(payload, str) else "", {}


# --------------------------------------------------------------------------- #
# Synthetic fixtures                                                          #
# --------------------------------------------------------------------------- #

S2_SEARCH = {
    "data": [
        {
            "paperId": "aaaa1111",
            "externalIds": {"DOI": "10.1111/jofi.10001", "ArXiv": "2101.00001", "CorpusId": 900001},
            "title": "Heterogeneous Investors and Asset Prices",
            "year": 2023,
            "venue": "Journal of Finance",
            "authors": [{"name": "Ada Lovelace", "authorId": "1"}, {"name": "Grace Hopper", "authorId": "2"}],
            "abstract": "We study how investor heterogeneity shapes equilibrium prices.",
            "openAccessPdf": {"url": "https://example.org/wp.pdf"},
            "fieldsOfStudy": ["Economics"],
            "citationCount": 12,
            "referenceCount": 40,
            "url": "https://www.semanticscholar.org/paper/aaaa1111",
        }
    ]
}

S2_REFERENCES = {
    "data": [
        {"citedPaper": {"paperId": "bbbb2222", "externalIds": {"DOI": "10.1111/jofi.10002"},
                        "title": "Belief Dispersion in Markets", "year": 2015, "authors": []}},
        {"citedPaper": {"paperId": "cccc3333", "externalIds": {}, "title": "A Note With No DOI", "year": 2010,
                        "authors": []}},
    ]
}

S2_CITATIONS = {
    "data": [
        {"citingPaper": {"paperId": "dddd4444", "externalIds": {"DOI": "10.1257/aer.20220001"},
                         "title": "Extensions of Heterogeneous Beliefs", "year": 2024, "authors": []}},
    ]
}

CROSSREF_WORK = {
    "message": {
        "DOI": "10.1111/jofi.10001",
        "title": ["Heterogeneous Investors and Asset Prices"],
        "container-title": ["The Journal of Finance"],
        "author": [{"given": "Ada", "family": "Lovelace"}, {"given": "Grace", "family": "Hopper"}],
        "published-print": {"date-parts": [[2023, 6, 1]]},
        "volume": "78",
        "page": "1-40",
        "type": "journal-article",
        "URL": "https://doi.org/10.1111/jofi.10001",
        "reference": [
            {"DOI": "10.1111/jofi.10002", "article-title": "Belief Dispersion in Markets", "year": "2015"},
            {"unstructured": "Some Author, A working paper with no DOI, 2010", "year": "2010"},
        ],
    }
}

CROSSREF_SEARCH = {"message": {"items": [CROSSREF_WORK["message"]]}}

ARXIV_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2101.00001v2</id>
    <title>Heterogeneous Investors and Asset Prices</title>
    <summary>  We study how investor heterogeneity
    shapes equilibrium prices.  </summary>
    <published>2021-01-04T00:00:00Z</published>
    <author><name>Ada Lovelace</name></author>
    <author><name>Grace Hopper</name></author>
    <arxiv:primary_category term="q-fin.PR"/>
    <arxiv:doi>10.1111/jofi.10001</arxiv:doi>
  </entry>
</feed>"""


def _routes(**overrides):
    routes = {
        "/paper/search": (200, S2_SEARCH),
        "/references": (200, S2_REFERENCES),
        "/citations": (200, S2_CITATIONS),
        "/paper/DOI:": (200, S2_SEARCH["data"][0]),
        "/works/": (200, CROSSREF_WORK),
        "/works?": (200, CROSSREF_SEARCH),
        "export.arxiv.org": (200, ARXIV_ATOM),
    }
    routes.update(overrides)
    return routes


# --------------------------------------------------------------------------- #
# Normalization                                                               #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("10.1111/JOFI.10001", "10.1111/jofi.10001"),
        ("https://doi.org/10.1111/jofi.10001", "10.1111/jofi.10001"),
        ("doi:10.1111/jofi.10001", "10.1111/jofi.10001"),
        ("  10.1111/jofi.10001  ", "10.1111/jofi.10001"),
        ("not a doi", None),
        (None, None),
    ],
)
def test_normalize_doi(raw, expected):
    assert cc.normalize_doi(raw) == expected


@pytest.mark.parametrize(
    "ident,kind",
    [
        ("10.1111/jofi.10001", "doi"),
        ("https://doi.org/10.1111/jofi.10001", "doi"),
        ("2101.00001", "arxiv"),
        ("arXiv:2101.00001v2", "arxiv"),
        ("CorpusId:900001", "corpusid"),
        ("a" * 40, "s2"),
    ],
)
def test_detect_id_type(ident, kind):
    assert cc.detect_id_type(ident) == kind


def test_s2_paper_id_forms():
    assert cc.s2_paper_id("10.1111/JOFI.1") == "DOI:10.1111/jofi.1"
    assert cc.s2_paper_id("arXiv:2101.00001") == "arXiv:2101.00001"
    assert cc.s2_paper_id("CorpusId:5") == "CorpusId:5"


def test_normalize_title_strips_punctuation():
    assert cc.normalize_title("Belief Dispersion, in Markets!") == "belief dispersion in markets"


# --------------------------------------------------------------------------- #
# Mappers                                                                     #
# --------------------------------------------------------------------------- #


def test_s2_paper_to_record_verbatim():
    rec = cc.s2_paper_to_record(S2_SEARCH["data"][0])
    assert rec["id"]["doi"] == "10.1111/jofi.10001"
    assert rec["id"]["arxiv"] == "2101.00001"
    assert rec["title"] == "Heterogeneous Investors and Asset Prices"
    assert rec["abstract_source"] == "s2"
    assert [a["name"] for a in rec["authors"]] == ["Ada Lovelace", "Grace Hopper"]
    # S2 has no given/family split.
    assert rec["authors"][0]["family"] is None
    assert rec["is_open_access"] is True


def test_crossref_work_to_record_has_structured_authors():
    rec = cc.crossref_work_to_record(CROSSREF_WORK["message"])
    assert rec["source"] == "crossref"
    assert rec["year"] == 2023
    assert rec["venue"] == "The Journal of Finance"
    assert rec["authors"][0] == {"name": "Ada Lovelace", "given": "Ada", "family": "Lovelace"}
    assert rec["volume"] == "78"


def test_arxiv_parse_and_map():
    entries = cc.parse_arxiv_atom(ARXIV_ATOM)
    assert len(entries) == 1
    rec = cc.arxiv_entry_to_record(entries[0])
    assert rec["id"]["arxiv"] == "2101.00001v2"
    assert rec["year"] == 2021
    assert rec["venue"] == "q-fin.PR"
    # Whitespace collapsed but text verbatim.
    assert rec["abstract"] == "We study how investor heterogeneity shapes equilibrium prices."
    assert rec["abstract_source"] == "arxiv"


def test_merge_records_layers_abstract_without_overwriting():
    crossref = cc.crossref_work_to_record(CROSSREF_WORK["message"])
    assert crossref["abstract"] is None
    s2 = cc.s2_paper_to_record(S2_SEARCH["data"][0])
    merged = cc.merge_records(crossref, s2)
    # Authoritative Crossref venue is preserved; abstract layered from S2.
    assert merged["venue"] == "The Journal of Finance"
    assert merged["abstract_source"] == "s2"
    assert merged["id"]["arxiv"] == "2101.00001"


# --------------------------------------------------------------------------- #
# Dedup cascade                                                               #
# --------------------------------------------------------------------------- #


def test_dedup_exact_doi_merges():
    recs = [
        {"id": {"doi": "10.1111/jofi.1"}, "title": "A", "year": 2020},
        {"id": {"doi": "https://doi.org/10.1111/JOFI.1"}, "title": "A (preprint)", "year": 2019},
    ]
    out = cc.dedup_records(recs)
    assert out["n_clusters"] == 1
    assert out["clusters"][0]["match_basis"] == "doi"


def test_dedup_title_year_merges_with_reordered_authors():
    recs = [
        {"doi": None, "title": "Belief Dispersion in Markets", "year": 2015,
         "authors": [{"name": "Alice"}, {"name": "Bob"}]},
        {"doi": None, "title": "Belief Dispersion in Markets", "year": 2015,
         "authors": [{"name": "Bob"}, {"name": "Alice"}]},
    ]
    out = cc.dedup_records(recs)
    assert out["n_clusters"] == 1
    assert out["clusters"][0]["match_basis"] == "title-year"


def test_dedup_doiless_preprints_fuzzy_year_guard():
    # Same normalized title but different years must NOT merge.
    recs = [
        {"title": "A Model of Trade", "year": 2018},
        {"title": "A Model of Trade", "year": 2021},
    ]
    out = cc.dedup_records(recs)
    assert out["n_clusters"] == 2


def test_dedup_fuzzy_auto_merge_above_threshold():
    recs = [
        {"title": "Heterogeneous Investors and Asset Prices", "year": 2023},
        {"title": "Heterogeneous Investors and Asset Price", "year": 2023},  # ~0.99
    ]
    out = cc.dedup_records(recs)
    assert out["n_clusters"] == 1
    assert out["clusters"][0]["match_basis"] == "fuzzy-title"


def test_dedup_borderline_flagged_not_merged():
    # Close but below the auto-merge threshold (~0.94): stays separate, flagged.
    a = "Investor Sentiment and the Cross-Section of Stock Returns"
    b = "Investor Sentiment and the Cross-Section of Returns"
    recs = [{"title": a, "year": 2022}, {"title": b, "year": 2022}]
    out = cc.dedup_records(recs)
    assert out["n_clusters"] == 2
    assert len(out["review_pairs"]) == 1
    rp = out["review_pairs"][0]
    assert cc.FUZZY_REVIEW_BAND <= rp["ratio"] < cc.FUZZY_AUTO_MERGE
    assert rp["basis"] == "fuzzy-title"


def test_dedup_volpages_conflict_blocks_merge():
    recs = [
        {"title": "Same Title", "year": 2020, "volume": "10", "pages": "1-5"},
        {"title": "Same Title", "year": 2020, "volume": "11", "pages": "1-5"},
    ]
    out = cc.dedup_records(recs)
    assert out["n_clusters"] == 2
    assert out["review_pairs"][0]["basis"] == "title-year-volpages-conflict"


def test_dedup_canonical_is_richest_member():
    recs = [
        {"id": {"doi": "10.1/x"}, "title": "T", "year": 2020},
        {"id": {"doi": "10.1/x"}, "title": "T", "year": 2020, "abstract": "full", "venue": "JF",
         "authors": [{"name": "A"}]},
    ]
    out = cc.dedup_records(recs)
    assert out["clusters"][0]["canonical"]["abstract"] == "full"


# --------------------------------------------------------------------------- #
# API calls (offline via FakeTransport)                                       #
# --------------------------------------------------------------------------- #


def test_s2_search_maps_records():
    t = FakeTransport(_routes())
    recs = cc.s2_search(t, {}, "asset pricing", limit=5)
    assert len(recs) == 1
    assert recs[0]["source"] == "s2"


def test_s2_references_unwraps_cited_paper():
    t = FakeTransport(_routes())
    recs = cc.s2_references(t, {}, "10.1111/jofi.10001")
    assert [r["title"] for r in recs] == ["Belief Dispersion in Markets", "A Note With No DOI"]


def test_s2_citations_unwraps_citing_paper():
    t = FakeTransport(_routes())
    recs = cc.s2_citations(t, {}, "10.1111/jofi.10001")
    assert recs[0]["id"]["doi"] == "10.1257/aer.20220001"


def test_s2_unavailable_raises():
    t = FakeTransport(_routes(**{"/paper/search": (429, None)}))
    with pytest.raises(cc.S2Unavailable):
        cc.s2_search(t, {}, "x")


def test_crossref_work_and_references():
    t = FakeTransport(_routes())
    rec = cc.crossref_work(t, {}, "10.1111/jofi.10001")
    assert rec["venue"] == "The Journal of Finance"
    refs = cc.crossref_references(t, {}, "10.1111/jofi.10001")
    # Two references, one DOI-less unstructured.
    assert len(refs) == 2
    assert refs[1]["id"]["doi"] is None
    assert refs[1]["source"] == "crossref-reference"


def test_crossref_work_404_returns_none():
    t = FakeTransport(_routes(**{"/works/": (404, None)}))
    assert cc.crossref_work(t, {}, "10.9/missing") is None


def test_arxiv_get():
    t = FakeTransport(_routes())
    rec = cc.arxiv_get(t, "2101.00001")
    assert rec["source"] == "arxiv"
    assert rec["id"]["doi"] == "10.1111/jofi.10001"


# --------------------------------------------------------------------------- #
# Command handlers                                                            #
# --------------------------------------------------------------------------- #


def run_cmd(argv, transport):
    """Parse argv, invoke the handler with the fake transport, capture stdout JSON."""
    args = cc.build_parser().parse_args(argv)
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = args.func(args, transport=transport)
    out = buf.getvalue()
    return code, (json.loads(out) if out.strip() else None)


def test_cmd_search_both_sources(monkeypatch):
    monkeypatch.setattr(cc, "get_config", lambda: {"s2_api_key": None, "crossref_mailto": None})
    code, out = run_cmd(["search", "asset pricing", "--source", "both"], FakeTransport(_routes()))
    assert code == 0
    assert out["s2_available"] is True
    # One S2 + one Crossref record.
    assert out["count"] == 2


def test_cmd_search_degrades_when_s2_down(monkeypatch):
    monkeypatch.setattr(cc, "get_config", lambda: {"s2_api_key": None, "crossref_mailto": None})
    routes = _routes(**{"/paper/search": (503, None)})
    code, out = run_cmd(["search", "asset pricing", "--source", "both"], FakeTransport(routes))
    assert code == 0
    assert out["s2_available"] is False
    assert any("S2 unavailable" in n for n in out["notes"])
    # Crossref still returns its record.
    assert out["count"] == 1


def test_cmd_citations_s2_only_degrades(monkeypatch):
    monkeypatch.setattr(cc, "get_config", lambda: {"s2_api_key": None, "crossref_mailto": None})
    routes = _routes(**{"/citations": (429, None)})
    code, out = run_cmd(["citations", "10.1111/jofi.10001"], FakeTransport(routes))
    assert code == 0
    assert out["s2_available"] is False
    assert out["records"] == []
    assert any("web sweep" in n for n in out["notes"])


def test_cmd_metadata_prefers_crossref_version_of_record(monkeypatch):
    monkeypatch.setattr(cc, "get_config", lambda: {"s2_api_key": None, "crossref_mailto": None})
    code, out = run_cmd(["metadata", "10.1111/jofi.10001"], FakeTransport(_routes()))
    assert code == 0
    assert out["version_of_record"] is True
    assert "crossref" in out["sources_used"]
    rec = out["record"]
    # Authoritative published venue from Crossref, abstract layered from S2.
    assert rec["venue"] == "The Journal of Finance"
    assert rec["abstract"]
    assert rec["abstract_source"] == "s2"


def test_cmd_metadata_arxiv_only_no_published_version(monkeypatch):
    monkeypatch.setattr(cc, "get_config", lambda: {"s2_api_key": None, "crossref_mailto": None})
    # arXiv id whose S2 record carries no DOI and no Crossref hit.
    s2_no_doi = {"paperId": "z", "externalIds": {"ArXiv": "2109.09999"}, "title": "Fresh WP",
                 "year": 2021, "authors": []}
    routes = _routes(**{"/paper/DOI:": (404, None), "/paper/": (200, s2_no_doi), "/works/": (404, None)})
    code, out = run_cmd(["metadata", "2109.09999"], FakeTransport(routes))
    assert code == 0
    assert out["version_of_record"] is False
    assert "arxiv" in out["sources_used"]


def test_cmd_dedup_from_file(tmp_path, monkeypatch):
    records = [
        {"id": {"doi": "10.1/x"}, "title": "A", "year": 2020},
        {"id": {"doi": "10.1/X"}, "title": "A", "year": 2020},
        {"title": "Something Else Entirely", "year": 2019},
    ]
    f = tmp_path / "recs.json"
    f.write_text(json.dumps(records), encoding="utf-8")
    code, out = run_cmd(["dedup", "--file", str(f)], FakeTransport({}))
    assert code == 0
    assert out["n_clusters"] == 2


def test_cmd_dedup_bad_json_errors():
    args = cc.build_parser().parse_args(["dedup", "--file", "/nonexistent-xyz.json"])
    with pytest.raises(FileNotFoundError):
        args.func(args, transport=FakeTransport({}))


# --------------------------------------------------------------------------- #
# No-key path and secret hygiene                                              #
# --------------------------------------------------------------------------- #


def test_health_no_key_anonymous_pool(monkeypatch):
    monkeypatch.setattr(cc, "get_config", lambda: {"s2_api_key": None, "crossref_mailto": None})
    code, out = run_cmd(["health"], FakeTransport(_routes()))
    assert code == 0
    assert out["s2_key_mode"] == "anonymous-pool"
    assert out["config_present"]["S2_API_KEY"] is False
    assert out["dependencies"] == "stdlib-only"


def test_health_never_leaks_key_value(monkeypatch):
    secret = "sk-super-secret-value-do-not-print"
    monkeypatch.setattr(cc, "get_config", lambda: {"s2_api_key": secret, "crossref_mailto": None})
    args = cc.build_parser().parse_args(["health"])
    out_buf, err_buf = io.StringIO(), io.StringIO()
    with redirect_stdout(out_buf), redirect_stderr(err_buf):
        args.func(args, transport=FakeTransport(_routes()))
    assert secret not in out_buf.getvalue()
    assert secret not in err_buf.getvalue()
    payload = json.loads(out_buf.getvalue())
    assert payload["config_present"]["S2_API_KEY"] is True
    assert payload["s2_key_mode"] == "keyed"


def test_get_config_returns_none_without_env(monkeypatch, tmp_path):
    monkeypatch.delenv("S2_API_KEY", raising=False)
    monkeypatch.delenv("SEMANTIC_SCHOLAR_API_KEY", raising=False)
    monkeypatch.delenv("CROSSREF_MAILTO", raising=False)
    monkeypatch.chdir(tmp_path)  # no Notes/.env here
    cfg = cc.get_config()
    assert cfg["s2_api_key"] is None
    assert cfg["crossref_mailto"] is None
    assert cfg["opencitations_token"] is None
    assert cfg["cache_dir"] is None
    assert cfg["intervals"]["s2"] == cc.DEFAULT_INTERVALS["s2"]


def test_get_config_resolves_opencitations_cache_and_intervals(monkeypatch, tmp_path):
    for name in ("S2_API_KEY", "SEMANTIC_SCHOLAR_API_KEY", "CROSSREF_MAILTO"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("OPENCITATIONS_ACCESS_TOKEN", "oc-token")
    monkeypatch.setenv("CITATION_CLIENT_CACHE_DIR", "/tmp/some-cache")
    monkeypatch.setenv("CITATION_CLIENT_INTERVAL_S2", "2.5")
    monkeypatch.chdir(tmp_path)
    cfg = cc.get_config()
    assert cfg["opencitations_token"] == "oc-token"
    assert cfg["cache_dir"] == "/tmp/some-cache"
    assert cfg["intervals"]["s2"] == 2.5
    # An unset backend keeps its default.
    assert cfg["intervals"]["crossref"] == cc.DEFAULT_INTERVALS["crossref"]


# --------------------------------------------------------------------------- #
# Cross-process coordination — shared cache, rate gate, adaptive backoff       #
# --------------------------------------------------------------------------- #
#
# Deterministic and offline: a fake clock drives all timing (sleeps advance the
# clock, never wall-clock waits), the rate gate coordinates through real files in
# a tmp dir, and the transport is faked.


class FakeClock:
    """Injectable clock/sleep. ``sleep`` advances the clock instead of waiting."""

    def __init__(self, t: float = 1000.0):
        self.t = t
        self.sleeps: list[float] = []

    def now(self) -> float:
        return self.t

    def sleep(self, dur: float) -> None:
        self.sleeps.append(dur)
        if dur > 0:
            self.t += dur


class RecordingTransport:
    """Records the clock time of each live call; always returns a 200 JSON body."""

    def __init__(self, clock: FakeClock, status: int = 200, payload=None):
        self.clock = clock
        self.status = status
        self.payload = payload if payload is not None else {"ok": True}
        self.call_times: list[float] = []

    def get_json(self, url, headers=None):
        self.call_times.append(self.clock.now())
        return self.status, self.payload, {}

    def get_text(self, url, headers=None):
        self.call_times.append(self.clock.now())
        return self.status, "text-body", {}


def _gate_state(coord_dir: Path, backend: str) -> dict:
    return json.loads((coord_dir / f"gate-{backend}.json").read_text(encoding="utf-8"))


# --- response cache -------------------------------------------------------- #


def test_cache_hit_miss_kind_and_ttl(tmp_path):
    clock = FakeClock()
    cache = cc.ResponseCache(tmp_path, ttl_long=100, ttl_short=10, now=clock.now)
    url = "https://api.crossref.org/works/10.1111/jofi.10001"
    assert cache.read(url, "json") is None  # miss on an empty cache
    cache.write(url, "json", {"a": 1})
    assert cache.read(url, "json") == {"a": 1}  # hit
    assert cache.read(url, "text") is None  # kind mismatch is a miss
    clock.t += 200  # past the long TTL
    assert cache.read(url, "json") is None  # expired


def test_cache_shorter_ttl_for_forward_citations(tmp_path):
    clock = FakeClock()
    cache = cc.ResponseCache(tmp_path, ttl_long=100, ttl_short=10, now=clock.now)
    url = "https://api.semanticscholar.org/graph/v1/paper/DOI:10.1/x/citations?limit=5"
    cache.write(url, "json", {"data": []})
    clock.t += 20  # past the short (citations) TTL but within the long TTL
    assert cache.read(url, "json") is None


def test_cache_key_ignores_courtesy_params(tmp_path):
    cache = cc.ResponseCache(tmp_path)
    base = "https://api.crossref.org/works/10.1/x?rows=5"
    cache.write(base + "&mailto=a@b.org", "json", {"v": 1})
    # A different mailto (or none) resolves to the same cache entry.
    assert cache.read(base + "&mailto=c@d.org", "json") == {"v": 1}
    assert cache.read(base, "json") == {"v": 1}


def test_cache_atomic_write_leaves_no_tmp(tmp_path):
    cache = cc.ResponseCache(tmp_path)
    cache.write("https://api.crossref.org/works/10.1/y", "json", {"a": 1})
    assert list(tmp_path.glob("*.tmp")) == []
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_cache_dir_is_self_gitignored(tmp_path):
    cache_dir = tmp_path / "cache"
    cc._ensure_cache_gitignored(cache_dir)
    body = (cache_dir / ".gitignore").read_text(encoding="utf-8")
    assert "*" in body.splitlines()


# --- rate gate ------------------------------------------------------------- #


def test_rate_gate_spaces_concurrent_callers(tmp_path):
    # Several "processes" (separate gate instances) sharing one coord dir all
    # arrive at the same instant; each claims the next slot, spaced by interval.
    clock = FakeClock()
    interval = 1.1
    gates = [
        cc.RateGate(tmp_path, {"s2": interval}, now=clock.now, sleep=clock.sleep)
        for _ in range(4)
    ]
    slots = [g._reserve("s2") for g in gates]  # no clock advance between arrivals
    for earlier, later in zip(slots, slots[1:]):
        assert later - earlier >= interval - 1e-9


def test_coordinated_transport_spaces_live_calls(tmp_path):
    clock = FakeClock()
    interval = 1.1
    gate = cc.RateGate(tmp_path, {"s2": interval}, now=clock.now, sleep=clock.sleep)
    inner = RecordingTransport(clock)
    ct = cc.CoordinatedTransport(inner, cache=None, gate=gate)
    url = "https://api.semanticscholar.org/graph/v1/paper/search?query=x"
    for _ in range(3):
        ct.get_json(url)
    assert len(inner.call_times) == 3
    for earlier, later in zip(inner.call_times, inner.call_times[1:]):
        assert later - earlier >= interval - 1e-9


def test_rate_gate_never_holds_lock_during_wait(tmp_path):
    # The wait happens outside the lock: _reserve returns immediately (records no
    # sleep); wait() is the only method that sleeps.
    clock = FakeClock()
    gate = cc.RateGate(tmp_path, {"s2": 5.0}, now=clock.now, sleep=clock.sleep)
    gate._reserve("s2")
    assert clock.sleeps == []  # reserving a slot never sleeps under the lock
    gate.wait("s2")  # second call must wait a full interval
    assert clock.sleeps and clock.sleeps[-1] >= 5.0 - 1e-9


def test_rate_gate_penalize_widens_and_success_decays(tmp_path):
    clock = FakeClock()
    gate = cc.RateGate(tmp_path, {"s2": 1.0}, now=clock.now, sleep=clock.sleep,
                       penalty_factor=2.0, decay=0.5)
    gate.penalize("s2")
    assert _gate_state(tmp_path, "s2")["interval"] == 2.0
    gate.penalize("s2")
    assert _gate_state(tmp_path, "s2")["interval"] == 4.0
    gate.on_success("s2")
    assert _gate_state(tmp_path, "s2")["interval"] == 2.0
    for _ in range(5):
        gate.on_success("s2")  # decays back toward, never below, the base
    assert _gate_state(tmp_path, "s2")["interval"] == 1.0


def test_coordinated_transport_backs_off_on_429(tmp_path):
    clock = FakeClock()
    gate = cc.RateGate(tmp_path, {"s2": 1.0}, now=clock.now, sleep=clock.sleep)
    inner = FakeTransport(_routes(**{"/paper/search": (429, None)}))
    ct = cc.CoordinatedTransport(inner, cache=None, gate=gate)
    ct.get_json("https://api.semanticscholar.org/graph/v1/paper/search?query=x")
    # A 429 pushed the shared interval outward for all concurrent callers.
    assert _gate_state(tmp_path, "s2")["interval"] > 1.0


def test_coordinated_transport_serves_from_cache(tmp_path):
    cache = cc.ResponseCache(tmp_path)
    inner = FakeTransport(_routes())
    ct = cc.CoordinatedTransport(inner, cache=cache, gate=cc.NoOpGate())
    url = cc.S2_BASE + "/paper/search?query=x"
    _, first, _ = ct.get_json(url)
    n_calls = len(inner.calls)
    _, second, _ = ct.get_json(url)  # served from cache, no new live call
    assert len(inner.calls) == n_calls
    assert second == first


def test_build_default_transport_honors_cfg_and_flags(tmp_path):
    cfg = {
        "s2_api_key": None, "crossref_mailto": None, "opencitations_token": None,
        "cache_dir": str(tmp_path / "c"), "intervals": dict(cc.DEFAULT_INTERVALS),
    }
    args = cc.build_parser().parse_args(["search", "x"])
    ct = cc.build_default_transport(args, cfg)
    assert isinstance(ct, cc.CoordinatedTransport)
    assert ct.cache is not None
    assert (tmp_path / "c" / ".gitignore").exists()  # cache dir self-ignored

    args_no_cache = cc.build_parser().parse_args(["search", "x", "--no-cache"])
    cfg_nc = dict(cfg, cache_dir=str(tmp_path / "d"))
    assert cc.build_default_transport(args_no_cache, cfg_nc).cache is None


# --- OpenCitations backend + fallback chain -------------------------------- #

OC_CITATIONS = [
    {"oci": "06101-06201", "citing": "omid:br/061 doi:10.1257/aer.20220001",
     "cited": "omid:br/060 doi:10.1111/jofi.10001", "creation": "2024-03"},
    {"oci": "06102-06202", "citing": "doi:10.1016/j.jfineco.2023.01",
     "cited": "doi:10.1111/jofi.10001", "creation": "2023"},
]

OC_REFERENCES = [
    {"oci": "06001-06101", "citing": "doi:10.1111/jofi.10001",
     "cited": "doi:10.1111/jofi.10002", "creation": "2023"},
]


def test_oc_headers_send_token_only_when_set():
    assert "authorization" not in cc._oc_headers({})
    assert cc._oc_headers({"opencitations_token": "oc-token"})["authorization"] == "oc-token"


def test_opencitations_citations_parse_to_records():
    t = FakeTransport({"/index/api/v2/citations/": (200, OC_CITATIONS)})
    recs = cc.opencitations_citations(t, {}, "10.1111/jofi.10001")
    assert [r["source"] for r in recs] == ["opencitations", "opencitations"]
    # DOI extracted from the citing endpoint; creation year carried through.
    assert recs[0]["id"]["doi"] == "10.1257/aer.20220001"
    assert recs[0]["year"] == 2024
    assert recs[1]["id"]["doi"] == "10.1016/j.jfineco.2023.01"


def test_opencitations_references_use_cited_endpoint_no_year():
    t = FakeTransport({"/index/api/v2/references/": (200, OC_REFERENCES)})
    recs = cc.opencitations_references(t, {}, "10.1111/jofi.10001")
    assert recs[0]["id"]["doi"] == "10.1111/jofi.10002"
    # Backward edges carry the citing entity's creation date, not the cited
    # paper's — so no year is inferred for a reference.
    assert recs[0]["year"] is None


def test_opencitations_requires_doi():
    with pytest.raises(cc.OpenCitationsUnavailable):
        cc.opencitations_citations(FakeTransport({}), {}, "not-a-doi")


def _cfg_no_keys():
    return {
        "s2_api_key": None, "crossref_mailto": None, "opencitations_token": None,
        "cache_dir": None, "intervals": dict(cc.DEFAULT_INTERVALS),
    }


def test_cmd_citations_falls_back_to_opencitations(monkeypatch):
    monkeypatch.setattr(cc, "get_config", _cfg_no_keys)
    # OC route listed first so its more specific path wins the substring match.
    routes = {
        "/index/api/v2/citations/": (200, OC_CITATIONS),
        "/citations": (429, None),
    }
    code, out = run_cmd(["citations", "10.1111/jofi.10001"], FakeTransport(routes))
    assert code == 0
    assert out["s2_available"] is False
    assert out["source"] == "opencitations"
    assert out["count"] == 2
    assert any("version DOIs" in n for n in out["notes"])


def test_cmd_citations_union_dedups_version_dois(monkeypatch):
    monkeypatch.setattr(cc, "get_config", _cfg_no_keys)
    routes = {
        "/index/api/v2/citations/10.3386/w12345": (
            200,
            [
                {"citing": "doi:10.1257/aer.20220001", "cited": "doi:10.3386/w12345", "creation": "2024"},
                {"citing": "doi:10.1111/jofi.77777", "cited": "doi:10.3386/w12345", "creation": "2023"},
            ],
        ),
        "/index/api/v2/citations/10.2139/ssrn.12345": (
            200,
            [
                {"citing": "doi:10.1257/aer.20220001", "cited": "doi:10.2139/ssrn.12345", "creation": "2024"},
                {"citing": "doi:10.1093/rfs/hhaa001", "cited": "doi:10.2139/ssrn.12345", "creation": "2022"},
            ],
        ),
    }
    code, out = run_cmd(
        [
            "citations-union",
            "10.3386/w12345",
            "10.2139/ssrn.12345",
            "--source",
            "opencitations",
        ],
        FakeTransport(routes),
    )
    assert code == 0
    assert out["count"] == 3
    duplicated = [r for r in out["records"] if r["id"]["doi"] == "10.1257/aer.20220001"][0]
    assert len(duplicated["source_versions"]) == 2


def test_cmd_citations_chain_exhausts_to_web_sweep(monkeypatch):
    monkeypatch.setattr(cc, "get_config", _cfg_no_keys)
    routes = {
        "/index/api/v2/citations/": (500, None),  # OC also down
        "/citations": (429, None),  # S2 down
    }
    code, out = run_cmd(["citations", "10.1111/jofi.10001"], FakeTransport(routes))
    assert code == 0
    assert out["s2_available"] is False
    assert out["records"] == []
    assert any("web sweep" in n for n in out["notes"])


def test_cmd_citations_source_s2_pins_s2_only(monkeypatch):
    monkeypatch.setattr(cc, "get_config", _cfg_no_keys)
    routes = {
        "/index/api/v2/citations/": (200, OC_CITATIONS),  # available but must be skipped
        "/citations": (429, None),
    }
    code, out = run_cmd(["citations", "10.1111/jofi.10001", "--source", "s2"], FakeTransport(routes))
    assert code == 0
    assert out["s2_available"] is False
    assert out["records"] == []  # --source s2 does not try OpenCitations
    assert out["source"] != "opencitations"


def test_cmd_references_opencitations_source(monkeypatch):
    monkeypatch.setattr(cc, "get_config", _cfg_no_keys)
    routes = {"/index/api/v2/references/": (200, OC_REFERENCES)}
    code, out = run_cmd(
        ["references", "10.1111/jofi.10001", "--source", "opencitations"],
        FakeTransport(routes),
    )
    assert code == 0
    assert out["count"] == 1
    assert out["records"][0]["id"]["doi"] == "10.1111/jofi.10002"


def test_health_reports_new_config_and_never_leaks_oc_token(monkeypatch):
    secret = "oc-secret-token-do-not-print"
    monkeypatch.setattr(cc, "get_config", lambda: dict(_cfg_no_keys(), opencitations_token=secret))
    args = cc.build_parser().parse_args(["health"])
    out_buf, err_buf = io.StringIO(), io.StringIO()
    with redirect_stdout(out_buf), redirect_stderr(err_buf):
        args.func(args, transport=FakeTransport(_routes()))
    assert secret not in out_buf.getvalue()
    assert secret not in err_buf.getvalue()
    payload = json.loads(out_buf.getvalue())
    assert payload["config_present"]["OPENCITATIONS_ACCESS_TOKEN"] is True
    assert "opencitations" in payload["endpoints"]
    assert payload["rate_intervals"]["s2"] == cc.DEFAULT_INTERVALS["s2"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
