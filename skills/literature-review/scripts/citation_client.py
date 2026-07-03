#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Citation-graph and metadata client for the literature-review skill.

Stdlib-only. Each subcommand queries public, keyless APIs and emits JSON on
stdout for agent consumption:

    uv run --script <skill-root>/scripts/citation_client.py search "query" --source both
    uv run --script <skill-root>/scripts/citation_client.py references 10.1111/jofi.12345
    uv run --script <skill-root>/scripts/citation_client.py citations DOI:10.1111/jofi.12345
    uv run --script <skill-root>/scripts/citation_client.py metadata 10.1111/jofi.12345
    uv run --script <skill-root>/scripts/citation_client.py dedup --file records.json

Backends (see references/citation-client.md for the full command surface):

- Semantic Scholar (S2) — relevance search, backward ``references``, forward
  ``citations``, abstracts. Keyless anonymous pool by default; an optional key is
  read from the environment when present. S2 is treated as *optional*: on an
  outage or sustained rate-limiting the affected command degrades and says so
  (``s2_available: false``) rather than crashing.
- Crossref — authoritative published-version-of-record metadata by DOI/title, and
  an uneven ``reference`` array as a backward-references fallback. Keyless; the
  polite pool is used when ``CROSSREF_MAILTO`` is configured.
- arXiv — q-fin/econ preprint abstracts and metadata (Atom XML).
- OpenCitations — keyless DOI->DOI forward/backward edges (I4OC open references),
  used as the forward-``citations`` fallback when S2 is rate-limited or down.

Concurrent fan-out safety: a shared on-disk response cache and a cross-process
rate gate (one next-allowed-time file per backend host, guarded by ``fcntl``)
sit in front of the live HTTP call, so many client processes on one machine/IP
stay inside the server's per-IP window without being serialized. The per-process
retry/backoff in :class:`UrllibTransport` stays as the second line of defense.

Bibliographic fields are mapped verbatim from the source payload; the client
never composes metadata. Credentials are read from the environment or a
project-local ``Notes/.env`` and are never printed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from contextlib import contextmanager, suppress
from difflib import SequenceMatcher
from pathlib import Path

try:
    import fcntl  # POSIX only (macOS/Linux); absent on Windows.

    _HAS_FCNTL = True
except ImportError:  # pragma: no cover - exercised only on non-POSIX platforms
    _HAS_FCNTL = False

TOOL_VERSION = "1.1.0"

S2_BASE = "https://api.semanticscholar.org/graph/v1"
CROSSREF_BASE = "https://api.crossref.org"
ARXIV_BASE = "http://export.arxiv.org/api/query"
OPENCITATIONS_BASE = "https://opencitations.net/index/api/v2"

# Cross-process rate gate: conservative per-backend spacing (seconds/request)
# bounded across all fan-out processes sharing one IP + filesystem. S2's
# anonymous pool is ~1 req/s; Crossref's polite pool tolerates more; OpenCitations
# a few req/s; arXiv asks for 3s between requests.
DEFAULT_INTERVALS = {"s2": 1.1, "crossref": 0.2, "opencitations": 0.5, "arxiv": 3.0}
_DEFAULT_INTERVAL = 1.0

# Response-cache TTLs by result mutability. References/metadata/published records
# are effectively immutable; forward citations grow, so they expire sooner.
CACHE_TTL_LONG = 30 * 24 * 3600
CACHE_TTL_SHORT = 7 * 24 * 3600
DEFAULT_CACHE_DIR = "Notes/.cache/citation-client"

# Fields requested from S2 for a paper record. authorId/name are the only author
# fields S2 exposes; given/family are unavailable, so downstream must not assume
# a parsed name from this source.
S2_PAPER_FIELDS = (
    "externalIds,title,abstract,year,venue,publicationVenue,"
    "authors.name,authors.authorId,openAccessPdf,fieldsOfStudy,"
    "citationCount,referenceCount,url"
)

# Fuzzy-title dedup: at or above AUTO_MERGE the pair is auto-merged; in
# [REVIEW_BAND, AUTO_MERGE) it is flagged for human review, never auto-merged.
FUZZY_AUTO_MERGE = 0.98
FUZZY_REVIEW_BAND = 0.90


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def emit(payload: object) -> None:
    json.dump(payload, sys.stdout, indent=2, default=str, ensure_ascii=False)
    sys.stdout.write("\n")


def fail(message: str, code: int = 1) -> int:
    """Emit a tool-constructed error to stderr; never echoes credential values."""
    eprint(f"error: {message}")
    return code


# --------------------------------------------------------------------------- #
# Configuration                                                               #
# --------------------------------------------------------------------------- #


def load_env_file() -> dict[str, str]:
    """Read ``Notes/.env`` from the current working directory if present.

    Environment variables already set take precedence. Values are never logged.
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


def get_config() -> dict:
    """Resolve config from the environment, then ``Notes/.env``. No value logged.

    - S2 key: institutional-only now, so optional. Accepts either the S2 or the
      long ``SEMANTIC_SCHOLAR`` env name.
    - Crossref mailto: opts into Crossref's faster, more reliable polite pool.
    - OpenCitations token: optional; sent in the ``authorization`` header only when
      set (the API is keyless without it). Value is never printed.
    - Cache dir: coordination + response-cache root (``CITATION_CLIENT_CACHE_DIR``).
    - Intervals: per-backend rate-gate spacing, overridable via
      ``CITATION_CLIENT_INTERVAL_<BACKEND>`` (e.g. ``..._S2``).
    """
    file_values = load_env_file()

    def resolve(*names: str) -> str | None:
        for name in names:
            val = os.environ.get(name) or file_values.get(name)
            if val:
                return val
        return None

    intervals = dict(DEFAULT_INTERVALS)
    for backend in intervals:
        override = resolve(f"CITATION_CLIENT_INTERVAL_{backend.upper()}")
        if override:
            try:
                intervals[backend] = float(override)
            except ValueError:
                pass

    return {
        "s2_api_key": resolve("S2_API_KEY", "SEMANTIC_SCHOLAR_API_KEY"),
        "crossref_mailto": resolve("CROSSREF_MAILTO"),
        "opencitations_token": resolve("OPENCITATIONS_ACCESS_TOKEN"),
        "cache_dir": resolve("CITATION_CLIENT_CACHE_DIR"),
        "intervals": intervals,
    }


# --------------------------------------------------------------------------- #
# HTTP transport (injectable for offline testing)                             #
# --------------------------------------------------------------------------- #


class TransportError(RuntimeError):
    """A request could not be completed (network error or exhausted retries)."""


class UrllibTransport:
    """Default stdlib transport with retry/backoff and rate-limit courtesy.

    Retries 429/503 responses honoring a ``Retry-After`` header (or exponential
    backoff), and — for Crossref — sleeps between successful requests per the
    advertised ``X-Rate-Limit-Limit`` / ``X-Rate-Limit-Interval`` headers so a
    burst of paginated calls stays inside the server's window. ``sleep`` is
    injectable so this stays deterministic under test.
    """

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, timeout: float = 30.0, sleep=time.sleep):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.timeout = timeout
        self.sleep = sleep

    def _open(self, url: str, headers: dict[str, str] | None):
        import urllib.error
        import urllib.request

        req = urllib.request.Request(url, headers=headers or {})
        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = urllib.request.urlopen(req, timeout=self.timeout)  # noqa: S310
                return resp.status, resp.read(), dict(resp.headers)
            except urllib.error.HTTPError as exc:
                if exc.code in (429, 503) and attempt < self.max_retries:
                    self.sleep(self._retry_delay(exc.headers, attempt))
                    continue
                # Non-retryable HTTP status: surface it to the caller.
                return exc.code, exc.read(), dict(exc.headers or {})
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    self.sleep(self.base_delay * (2 ** attempt))
                    continue
        raise TransportError(f"request failed after retries: {last_exc}")

    def _retry_delay(self, headers, attempt: int) -> float:
        retry_after = headers.get("Retry-After") if headers else None
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
        return self.base_delay * (2 ** attempt)

    def _respect_crossref_window(self, url: str, resp_headers: dict[str, str]) -> None:
        if "crossref.org" not in url:
            return
        limit = resp_headers.get("X-Rate-Limit-Limit")
        interval = resp_headers.get("X-Rate-Limit-Interval")
        if not (limit and interval):
            return
        try:
            n = int(limit)
            secs = float(str(interval).rstrip("s") or 0)
        except ValueError:
            return
        if n > 0 and secs > 0:
            self.sleep(secs / n)

    def get_json(self, url: str, headers: dict[str, str] | None = None):
        status, body, resp_headers = self._open(url, headers)
        self._respect_crossref_window(url, resp_headers)
        text = body.decode("utf-8") if isinstance(body, (bytes, bytearray)) else str(body)
        try:
            data = json.loads(text) if text else None
        except json.JSONDecodeError:
            data = None
        return status, data, resp_headers

    def get_text(self, url: str, headers: dict[str, str] | None = None):
        status, body, resp_headers = self._open(url, headers)
        text = body.decode("utf-8") if isinstance(body, (bytes, bytearray)) else str(body)
        return status, text, resp_headers


def _encode(params: dict[str, object]) -> str:
    from urllib.parse import urlencode

    clean = {k: v for k, v in params.items() if v is not None and v != ""}
    return urlencode(clean)


# --------------------------------------------------------------------------- #
# Cross-process coordination (shared cache + rate gate + adaptive backoff)     #
# --------------------------------------------------------------------------- #
#
# The fan-out is unbounded: every screening agent shells out its own client
# process, and they share one IP and one filesystem. Coordination is via shared
# on-disk state so the collective request rate is bounded to what the server
# measures (per IP), without funnelling agents through a single serialized caller.


def backend_for_url(url: str) -> str:
    """Map a request URL to its backend name (for interval + gate-file selection)."""
    if "semanticscholar.org" in url:
        return "s2"
    if "crossref.org" in url:
        return "crossref"
    if "opencitations.net" in url:
        return "opencitations"
    if "arxiv.org" in url:
        return "arxiv"
    return "other"


def resolve_cache_dir(cfg: dict) -> Path:
    """Coordination + cache root: ``CITATION_CLIENT_CACHE_DIR`` or the project default."""
    return Path(cfg.get("cache_dir") or DEFAULT_CACHE_DIR)


def _cache_key(url: str) -> str:
    """Stable hash of a canonicalized URL: drop courtesy params (mailto/keys),
    sort the rest, so the same logical request keys the same cache entry across
    polite-pool vs anonymous configs."""
    from urllib.parse import parse_qsl, urlencode, urlsplit

    parts = urlsplit(url)
    volatile = {"mailto", "api_key", "apikey", "email", "access_token"}
    query = sorted(
        (k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k.lower() not in volatile
    )
    canon = f"{parts.scheme}://{parts.netloc}{parts.path}?{urlencode(query)}"
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


class ResponseCache:
    """Shared on-disk response cache. Reads are lock-free; writes are atomic
    (temp file + ``os.replace``). TTL varies by result mutability: forward
    ``citations`` grow, so they expire sooner than immutable references/metadata."""

    def __init__(self, cache_dir: Path, ttl_long: float = CACHE_TTL_LONG,
                 ttl_short: float = CACHE_TTL_SHORT, ttl_override: float | None = None,
                 now=time.time):
        self.cache_dir = Path(cache_dir)
        self.ttl_long = ttl_long
        self.ttl_short = ttl_short
        self.ttl_override = ttl_override
        self.now = now

    def _ttl_for(self, url: str) -> float:
        if self.ttl_override is not None:
            return self.ttl_override
        return self.ttl_short if "/citations" in url else self.ttl_long

    def _path(self, url: str) -> Path:
        return self.cache_dir / f"{_cache_key(url)}.json"

    def read(self, url: str, kind: str):
        """Return the cached payload if present, matching ``kind``, and unexpired; else None."""
        path = self._path(url)
        try:
            raw = path.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            return None
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            return None
        if entry.get("kind") != kind:
            return None
        age = self.now() - float(entry.get("fetched_at", 0))
        if age > self._ttl_for(url):
            return None
        return entry.get("payload")

    def write(self, url: str, kind: str, payload) -> None:
        """Atomically store a response payload keyed by canonicalized URL."""
        self._ensure_dir()
        entry = {"url": url, "kind": kind, "fetched_at": self.now(), "payload": payload}
        path = self._path(url)
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        try:
            tmp.write_text(json.dumps(entry, default=str), encoding="utf-8")
            os.replace(tmp, path)
        except OSError:
            with suppress(OSError):
                tmp.unlink()

    def _ensure_dir(self) -> None:
        _ensure_cache_gitignored(self.cache_dir)


class NoOpGate:
    """Fallback when ``fcntl`` is unavailable: per-process only, no coordination."""

    def wait(self, backend: str) -> None:  # noqa: D401
        return None

    def penalize(self, backend: str) -> None:
        return None

    def on_success(self, backend: str) -> None:
        return None


class RateGate:
    """Cross-process next-allowed-time gate. One state file per backend host,
    guarded by ``fcntl.flock``. The lock is held only for the brief read-modify-write
    of ``next_ts``; the wait itself happens outside the lock, so concurrency is
    preserved while the global request rate is bounded to one per ``interval``.

    Adaptive backoff: :meth:`penalize` widens the backend's shared interval on a
    429/503, slowing the whole fan-out; :meth:`on_success` decays it back."""

    def __init__(self, coord_dir: Path, intervals: dict[str, float] | None = None,
                 *, now=time.time, sleep=time.sleep,
                 penalty_factor: float = 2.0, decay: float = 0.5, max_interval: float = 60.0):
        self.coord_dir = Path(coord_dir)
        self.intervals = dict(intervals or DEFAULT_INTERVALS)
        self.now = now
        self.sleep = sleep
        self.penalty_factor = penalty_factor
        self.decay = decay
        self.max_interval = max_interval

    def _interval(self, backend: str) -> float:
        return self.intervals.get(backend, _DEFAULT_INTERVAL)

    def _file(self, backend: str) -> Path:
        return self.coord_dir / f"gate-{backend}.json"

    @contextmanager
    def _locked_state(self, backend: str):
        self.coord_dir.mkdir(parents=True, exist_ok=True)
        f = open(self._file(backend), "a+", encoding="utf-8")
        try:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.seek(0)
            raw = f.read()
            try:
                state = json.loads(raw) if raw.strip() else {}
            except json.JSONDecodeError:
                state = {}
            yield state
            f.seek(0)
            f.truncate()
            json.dump(state, f)
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()

    def _reserve(self, backend: str) -> float:
        """Claim the next slot: returns the absolute time the caller may fire."""
        base = self._interval(backend)
        with self._locked_state(backend) as state:
            interval = max(state.get("interval", base), base)
            slot = max(self.now(), state.get("next_ts", 0.0))
            state["interval"] = interval
            state["next_ts"] = slot + interval
        return slot

    def wait(self, backend: str) -> None:
        slot = self._reserve(backend)
        delay = slot - self.now()
        if delay > 0:
            self.sleep(delay)

    def penalize(self, backend: str) -> None:
        base = self._interval(backend)
        with self._locked_state(backend) as state:
            interval = min(max(state.get("interval", base), base) * self.penalty_factor, self.max_interval)
            state["interval"] = interval
            state["next_ts"] = max(state.get("next_ts", 0.0), self.now() + interval)

    def on_success(self, backend: str) -> None:
        base = self._interval(backend)
        with self._locked_state(backend) as state:
            interval = max(state.get("interval", base), base)
            state["interval"] = max(base, interval * self.decay)


class CoordinatedTransport:
    """Wrap a transport with the shared cache, the cross-process rate gate, and
    adaptive backoff. Cache hits skip the gate and the live call entirely; live
    calls are spaced by the gate; a 429/503 widens the shared interval and a 200
    decays it back and populates the cache."""

    def __init__(self, inner, cache: ResponseCache | None = None, gate=None):
        self.inner = inner
        self.cache = cache
        self.gate = gate or NoOpGate()

    def _fetch(self, url, headers, method, kind):
        if self.cache is not None:
            hit = self.cache.read(url, kind)
            if hit is not None:
                return 200, hit, {}
        self.gate.wait(backend_for_url(url))
        status, payload, resp_headers = method(url, headers)
        if status in (429, 503):
            self.gate.penalize(backend_for_url(url))
        elif status == 200 and payload is not None:
            self.gate.on_success(backend_for_url(url))
            if self.cache is not None:
                self.cache.write(url, kind, payload)
        return status, payload, resp_headers

    def get_json(self, url, headers=None):
        return self._fetch(url, headers, self.inner.get_json, "json")

    def get_text(self, url, headers=None):
        return self._fetch(url, headers, self.inner.get_text, "text")


def _ensure_cache_gitignored(cache_dir: Path) -> None:
    """Create the cache dir and drop a self-ignoring ``.gitignore`` (``*``) inside it,
    so cached responses never enter version control in any host project."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    marker = cache_dir / ".gitignore"
    if not marker.exists():
        with suppress(OSError):
            marker.write_text("# Auto-generated by citation_client.py — do not commit cached responses.\n*\n",
                              encoding="utf-8")


def build_default_transport(args, cfg: dict):
    """Construct the default coordinated transport honoring ``--no-cache`` /
    ``--cache-ttl`` and the resolved per-backend intervals. Degrades to a
    per-process-only gate when ``fcntl`` is unavailable."""
    coord_dir = resolve_cache_dir(cfg)
    # Self-ignore the coordination dir unconditionally: even under --no-cache the
    # RateGate writes gate-<backend>.json files here, so the .gitignore must exist
    # regardless of whether the response cache is enabled.
    _ensure_cache_gitignored(coord_dir)
    cache = None
    if not getattr(args, "no_cache", False):
        cache = ResponseCache(coord_dir, ttl_override=getattr(args, "cache_ttl", None))
    gate: object
    if _HAS_FCNTL:
        gate = RateGate(coord_dir, cfg.get("intervals"))
    else:
        gate = NoOpGate()
    return CoordinatedTransport(UrllibTransport(), cache=cache, gate=gate)


# --------------------------------------------------------------------------- #
# Identifier normalization                                                     #
# --------------------------------------------------------------------------- #

_DOI_RE = re.compile(r"10\.\d{4,9}/\S+", re.IGNORECASE)
_ARXIV_RE = re.compile(r"^(?:arxiv:)?(\d{4}\.\d{4,5}(?:v\d+)?|[a-z-]+(?:\.[A-Z]{2})?/\d{7})$", re.IGNORECASE)


def normalize_doi(doi: str | None) -> str | None:
    """Lowercase, strip URL/``doi:`` prefixes and surrounding whitespace.

    Returns None for a value that does not contain a DOI. Normalized DOIs are
    the primary dedup key, so this must be stable across the URL and bare forms.
    """
    if not doi:
        return None
    s = str(doi).strip()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^doi:", "", s, flags=re.IGNORECASE)
    m = _DOI_RE.search(s)
    if not m:
        return None
    return m.group(0).rstrip(".").lower()


def detect_id_type(identifier: str) -> str:
    """Classify a raw identifier as ``doi``, ``arxiv``, ``s2``, or ``corpusid``."""
    s = identifier.strip()
    low = s.lower()
    if low.startswith("corpusid:"):
        return "corpusid"
    if low.startswith("doi:") or normalize_doi(s):
        return "doi"
    if _ARXIV_RE.match(s):
        return "arxiv"
    if re.fullmatch(r"[0-9a-f]{40}", low):
        return "s2"
    if low.startswith(("s2:", "s2paperid:")):
        return "s2"
    return "s2"  # default: let S2 attempt to resolve it


def s2_paper_id(identifier: str) -> str:
    """Map a raw identifier to the S2 paper-id form (``DOI:...``/``arXiv:...``)."""
    kind = detect_id_type(identifier)
    if kind == "doi":
        return f"DOI:{normalize_doi(identifier)}"
    if kind == "arxiv":
        arxiv = re.sub(r"^arxiv:", "", identifier, flags=re.IGNORECASE)
        return f"arXiv:{arxiv}"
    if kind == "corpusid":
        return identifier if ":" in identifier else f"CorpusId:{identifier}"
    return re.sub(r"^s2(paperid)?:", "", identifier, flags=re.IGNORECASE)


def normalize_title(title: str | None) -> str:
    """Lowercase, strip punctuation, collapse whitespace — the fuzzy-match key."""
    if not title:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


# --------------------------------------------------------------------------- #
# Record mappers (verbatim field extraction; never agent-composed)            #
# --------------------------------------------------------------------------- #


def _empty_record(source: str) -> dict:
    return {
        "id": {"doi": None, "arxiv": None, "s2": None, "corpus_id": None},
        "title": None,
        "authors": [],
        "year": None,
        "venue": None,
        "abstract": None,
        "abstract_source": None,
        "url": None,
        "is_open_access": None,
        "external_ids": {},
        "source": source,
    }


def s2_paper_to_record(p: dict, include_raw: bool = False) -> dict:
    """Map an S2 paper object to the normalized record, verbatim."""
    rec = _empty_record("s2")
    ext = p.get("externalIds") or {}
    rec["id"]["doi"] = normalize_doi(ext.get("DOI"))
    rec["id"]["arxiv"] = ext.get("ArXiv")
    rec["id"]["s2"] = p.get("paperId")
    rec["id"]["corpus_id"] = ext.get("CorpusId") or p.get("corpusId")
    rec["external_ids"] = ext
    rec["title"] = p.get("title")
    rec["year"] = p.get("year")
    venue = p.get("venue")
    pub_venue = p.get("publicationVenue") or {}
    rec["venue"] = venue or (pub_venue.get("name") if isinstance(pub_venue, dict) else None)
    # S2 exposes only a display name per author (no given/family split).
    rec["authors"] = [
        {"name": a.get("name"), "given": None, "family": None, "s2_author_id": a.get("authorId")}
        for a in (p.get("authors") or [])
    ]
    if p.get("abstract"):
        rec["abstract"] = p["abstract"]
        rec["abstract_source"] = "s2"
    oa = p.get("openAccessPdf") or {}
    rec["is_open_access"] = bool(oa.get("url")) if oa else None
    rec["url"] = p.get("url") or (oa.get("url") if oa else None)
    rec["fields_of_study"] = p.get("fieldsOfStudy")
    rec["citation_count"] = p.get("citationCount")
    rec["reference_count"] = p.get("referenceCount")
    if include_raw:
        rec["raw"] = p
    return rec


def crossref_work_to_record(w: dict, include_raw: bool = False) -> dict:
    """Map a Crossref work to the normalized record, verbatim.

    Crossref is the published-version-of-record source: given/family author
    names are available, so both the structured split and a joined display name
    are populated.
    """
    rec = _empty_record("crossref")
    rec["id"]["doi"] = normalize_doi(w.get("DOI"))
    rec["external_ids"] = {"DOI": w.get("DOI")}
    titles = w.get("title") or []
    rec["title"] = titles[0] if titles else None
    rec["year"] = _crossref_year(w)
    containers = w.get("container-title") or []
    rec["venue"] = containers[0] if containers else None
    authors = []
    for a in w.get("author") or []:
        given = a.get("given")
        family = a.get("family")
        name = " ".join(x for x in [given, family] if x) or a.get("name")
        authors.append({"name": name, "given": given, "family": family})
    rec["authors"] = authors
    if w.get("abstract"):
        # Crossref abstracts are JATS-tagged and spotty for econ; kept verbatim.
        rec["abstract"] = w["abstract"]
        rec["abstract_source"] = "crossref"
    rec["url"] = w.get("URL")
    rec["is_open_access"] = None
    rec["type"] = w.get("type")
    rec["volume"] = w.get("volume")
    rec["pages"] = w.get("page")
    if include_raw:
        rec["raw"] = w
    return rec


def _crossref_year(w: dict) -> int | None:
    for key in ("published-print", "published-online", "published", "issued", "created"):
        block = w.get(key) or {}
        parts = block.get("date-parts") or []
        if parts and parts[0]:
            return parts[0][0]
    return None


def arxiv_entry_to_record(entry: dict, include_raw: bool = False) -> dict:
    """Map a parsed arXiv Atom entry (dict from ``parse_arxiv_atom``) verbatim."""
    rec = _empty_record("arxiv")
    rec["id"]["arxiv"] = entry.get("arxiv_id")
    rec["id"]["doi"] = normalize_doi(entry.get("doi"))
    rec["external_ids"] = {"ArXiv": entry.get("arxiv_id"), "DOI": entry.get("doi")}
    rec["title"] = entry.get("title")
    rec["year"] = entry.get("year")
    rec["venue"] = entry.get("primary_category")
    rec["authors"] = [{"name": n, "given": None, "family": None} for n in entry.get("authors", [])]
    if entry.get("summary"):
        rec["abstract"] = entry["summary"]
        rec["abstract_source"] = "arxiv"
    rec["url"] = entry.get("url")
    rec["is_open_access"] = True
    if include_raw:
        rec["raw"] = entry
    return rec


def merge_records(primary: dict, secondary: dict) -> dict:
    """Fill empty fields of ``primary`` from ``secondary`` (primary wins).

    Used to layer an abstract (S2/arXiv) onto an authoritative Crossref record
    without overwriting any verbatim published field.
    """
    out = json.loads(json.dumps(primary))
    for key in ("title", "year", "venue", "url"):
        if not out.get(key) and secondary.get(key):
            out[key] = secondary[key]
    if not out.get("abstract") and secondary.get("abstract"):
        out["abstract"] = secondary["abstract"]
        out["abstract_source"] = secondary.get("abstract_source")
    for idk in ("doi", "arxiv", "s2", "corpus_id"):
        if not out["id"].get(idk) and secondary["id"].get(idk):
            out["id"][idk] = secondary["id"][idk]
    if not out.get("authors") and secondary.get("authors"):
        out["authors"] = secondary["authors"]
    merged_ext = dict(secondary.get("external_ids") or {})
    merged_ext.update({k: v for k, v in (primary.get("external_ids") or {}).items() if v})
    out["external_ids"] = merged_ext
    return out


# --------------------------------------------------------------------------- #
# arXiv Atom parsing                                                           #
# --------------------------------------------------------------------------- #


def parse_arxiv_atom(xml_text: str) -> list[dict]:
    """Parse an arXiv Atom feed into a list of entry dicts (verbatim fields)."""
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(xml_text)
    entries: list[dict] = []
    for e in root.findall("a:entry", ns):
        raw_id = _text(e.find("a:id", ns))
        arxiv_id = None
        if raw_id:
            arxiv_id = re.sub(r"^https?://arxiv\.org/abs/", "", raw_id)
        published = _text(e.find("a:published", ns))
        year = int(published[:4]) if published and published[:4].isdigit() else None
        primary = e.find("arxiv:primary_category", ns)
        entries.append(
            {
                "arxiv_id": arxiv_id,
                "title": _clean(_text(e.find("a:title", ns))),
                "summary": _clean(_text(e.find("a:summary", ns))),
                "authors": [_text(n.find("a:name", ns)) for n in e.findall("a:author", ns)],
                "year": year,
                "doi": _text(e.find("arxiv:doi", ns)),
                "primary_category": primary.get("term") if primary is not None else None,
                "url": raw_id,
            }
        )
    return entries


def _text(node) -> str | None:
    return node.text if node is not None and node.text else None


def _clean(s: str | None) -> str | None:
    return re.sub(r"\s+", " ", s).strip() if s else s


# --------------------------------------------------------------------------- #
# API calls                                                                    #
# --------------------------------------------------------------------------- #


def _s2_headers(cfg: dict) -> dict[str, str]:
    headers = {"User-Agent": f"literature-review-client/{TOOL_VERSION}"}
    if cfg.get("s2_api_key"):
        headers["x-api-key"] = str(cfg["s2_api_key"])
    return headers


def _crossref_url(path: str, params: dict, cfg: dict) -> str:
    params = dict(params)
    if cfg.get("crossref_mailto"):
        params["mailto"] = cfg["crossref_mailto"]
    return f"{CROSSREF_BASE}{path}?{_encode(params)}"


class S2Unavailable(RuntimeError):
    """S2 could not serve a request (outage, non-200, or exhausted retries).

    Callers catch this to degrade gracefully rather than fail the command.
    """


def _s2_get(transport, url: str, cfg: dict):
    try:
        status, data, _ = transport.get_json(url, headers=_s2_headers(cfg))
    except TransportError as exc:
        raise S2Unavailable(str(exc)) from exc
    if status != 200 or data is None:
        raise S2Unavailable(f"S2 returned HTTP {status}")
    return data


def s2_search(transport, cfg, query, limit=25, year=None, venue=None, fields_of_study=None, include_raw=False):
    params = {
        "query": query,
        "limit": min(limit, 100),
        "fields": S2_PAPER_FIELDS,
        "year": year,
        "venue": venue,
        "fieldsOfStudy": fields_of_study,
    }
    url = f"{S2_BASE}/paper/search?{_encode(params)}"
    data = _s2_get(transport, url, cfg)
    return [s2_paper_to_record(p, include_raw) for p in (data.get("data") or [])]


def s2_references(transport, cfg, paper_id, limit=100, include_raw=False):
    params = {"limit": min(limit, 1000), "fields": S2_PAPER_FIELDS}
    url = f"{S2_BASE}/paper/{s2_paper_id(paper_id)}/references?{_encode(params)}"
    data = _s2_get(transport, url, cfg)
    return [s2_paper_to_record(item.get("citedPaper") or {}, include_raw) for item in (data.get("data") or [])]


def s2_citations(transport, cfg, paper_id, limit=100, include_raw=False):
    params = {"limit": min(limit, 1000), "fields": S2_PAPER_FIELDS}
    url = f"{S2_BASE}/paper/{s2_paper_id(paper_id)}/citations?{_encode(params)}"
    data = _s2_get(transport, url, cfg)
    return [s2_paper_to_record(item.get("citingPaper") or {}, include_raw) for item in (data.get("data") or [])]


def s2_paper(transport, cfg, paper_id, include_raw=False):
    url = f"{S2_BASE}/paper/{s2_paper_id(paper_id)}?{_encode({'fields': S2_PAPER_FIELDS})}"
    data = _s2_get(transport, url, cfg)
    return s2_paper_to_record(data, include_raw)


def crossref_search(transport, cfg, query, limit=25, year_min=None, year_max=None, venue=None, include_raw=False):
    filters = ["type:journal-article"]
    if year_min:
        filters.append(f"from-pub-date:{year_min}-01-01")
    if year_max:
        filters.append(f"until-pub-date:{year_max}-12-31")
    params = {
        "query.bibliographic": query,
        "rows": min(limit, 100),
        "filter": ",".join(filters),
        "query.container-title": venue,
    }
    url = _crossref_url("/works", params, cfg)
    try:
        status, data, _ = transport.get_json(url, headers={"User-Agent": f"literature-review-client/{TOOL_VERSION}"})
    except TransportError as exc:
        raise RuntimeError(f"Crossref search failed: {exc}") from exc
    if status != 200 or data is None:
        raise RuntimeError(f"Crossref returned HTTP {status}")
    items = ((data.get("message") or {}).get("items")) or []
    return [crossref_work_to_record(w, include_raw) for w in items]


def crossref_work(transport, cfg, doi, include_raw=False):
    url = _crossref_url(f"/works/{normalize_doi(doi)}", {}, cfg)
    try:
        status, data, _ = transport.get_json(url, headers={"User-Agent": f"literature-review-client/{TOOL_VERSION}"})
    except TransportError as exc:
        raise RuntimeError(f"Crossref lookup failed: {exc}") from exc
    if status == 404:
        return None
    if status != 200 or data is None:
        raise RuntimeError(f"Crossref returned HTTP {status}")
    return crossref_work_to_record(data.get("message") or {}, include_raw)


def crossref_references(transport, cfg, doi, include_raw=False):
    """Backward references from Crossref's ``reference`` array (uneven fallback).

    Crossref reference entries are frequently DOI-less and carry only unstructured
    strings, so callers must treat this as a lossy backstop to the S2 graph.
    """
    work = crossref_work(transport, cfg, doi, include_raw=True)
    if work is None:
        return []
    refs = (work.get("raw") or {}).get("reference") or []
    out = []
    for r in refs:
        out.append(
            {
                "id": {"doi": normalize_doi(r.get("DOI")), "arxiv": None, "s2": None, "corpus_id": None},
                "title": r.get("article-title") or r.get("unstructured"),
                "authors": [{"name": r.get("author"), "given": None, "family": None}] if r.get("author") else [],
                "year": int(r["year"]) if str(r.get("year", "")).isdigit() else None,
                "venue": r.get("journal-title"),
                "abstract": None,
                "abstract_source": None,
                "url": None,
                "is_open_access": None,
                "external_ids": {"DOI": r.get("DOI")},
                "source": "crossref-reference",
                "unstructured": r.get("unstructured"),
                **({"raw": r} if include_raw else {}),
            }
        )
    return out


def arxiv_get(transport, arxiv_id, include_raw=False):
    url = f"{ARXIV_BASE}?{_encode({'id_list': re.sub(r'^arxiv:', '', arxiv_id, flags=re.IGNORECASE)})}"
    try:
        status, text, _ = transport.get_text(url, headers={"User-Agent": f"literature-review-client/{TOOL_VERSION}"})
    except TransportError as exc:
        raise RuntimeError(f"arXiv lookup failed: {exc}") from exc
    if status != 200 or not text:
        raise RuntimeError(f"arXiv returned HTTP {status}")
    entries = parse_arxiv_atom(text)
    return arxiv_entry_to_record(entries[0], include_raw) if entries else None


# --------------------------------------------------------------------------- #
# OpenCitations backend (keyless DOI->DOI edges; S2 forward-citation fallback) #
# --------------------------------------------------------------------------- #


class OpenCitationsUnavailable(RuntimeError):
    """OpenCitations could not serve a request (outage, non-200, or no DOI)."""


def _oc_headers(cfg: dict) -> dict[str, str]:
    headers = {"User-Agent": f"literature-review-client/{TOOL_VERSION}"}
    token = cfg.get("opencitations_token")
    if token:
        # Keyless by default; a token only raises rate limits. Never logged.
        headers["authorization"] = str(token)
    return headers


def _oc_extract_doi(field) -> str | None:
    """Pull the DOI from an OpenCitations id field (space-separated ``omid:.. doi:..``)."""
    for token in str(field or "").split():
        if token.lower().startswith("doi:"):
            return normalize_doi(token)
    return None


def _oc_edge_to_record(id_field, creation=None, include_raw: bool = False, raw=None) -> dict:
    """Map one OpenCitations edge endpoint (the citing or cited id) to a record.

    OpenCitations supplies only the DOI edge (and, for the citing entity, a
    ``creation`` date), so title/authors/venue are null — hydrate later via
    ``metadata`` if needed."""
    rec = _empty_record("opencitations")
    doi = _oc_extract_doi(id_field)
    rec["id"]["doi"] = doi
    rec["external_ids"] = {"DOI": doi} if doi else {}
    if creation and str(creation)[:4].isdigit():
        rec["year"] = int(str(creation)[:4])
    if include_raw and raw is not None:
        rec["raw"] = raw
    return rec


def _oc_get(transport, url: str, cfg: dict) -> list:
    try:
        status, data, _ = transport.get_json(url, headers=_oc_headers(cfg))
    except TransportError as exc:
        raise OpenCitationsUnavailable(str(exc)) from exc
    if status != 200 or data is None:
        raise OpenCitationsUnavailable(f"OpenCitations returned HTTP {status}")
    return data if isinstance(data, list) else []


def opencitations_citations(transport, cfg, doi, limit=None, include_raw=False) -> list[dict]:
    """Forward citations (papers citing ``doi``) via OpenCitations Index v2."""
    ndoi = normalize_doi(doi)
    if not ndoi:
        raise OpenCitationsUnavailable("OpenCitations needs a DOI (DOI->DOI edges only)")
    data = _oc_get(transport, f"{OPENCITATIONS_BASE}/citations/{ndoi}", cfg)
    out = [
        _oc_edge_to_record(edge.get("citing"), edge.get("creation"), include_raw, edge)
        for edge in data
    ]
    return out[:limit] if limit else out


def opencitations_references(transport, cfg, doi, limit=None, include_raw=False) -> list[dict]:
    """Backward references (papers ``doi`` cites) via OpenCitations Index v2."""
    ndoi = normalize_doi(doi)
    if not ndoi:
        raise OpenCitationsUnavailable("OpenCitations needs a DOI (DOI->DOI edges only)")
    data = _oc_get(transport, f"{OPENCITATIONS_BASE}/references/{ndoi}", cfg)
    out = [_oc_edge_to_record(edge.get("cited"), None, include_raw, edge) for edge in data]
    return out[:limit] if limit else out


# --------------------------------------------------------------------------- #
# Dedup cascade                                                                #
# --------------------------------------------------------------------------- #


def _rec_doi(rec: dict) -> str | None:
    doi = (rec.get("id") or {}).get("doi") if isinstance(rec.get("id"), dict) else None
    return normalize_doi(doi or rec.get("doi"))


def _rec_title(rec: dict) -> str | None:
    return rec.get("title")


def _rec_year(rec: dict):
    return rec.get("year")


def _rec_volpages(rec: dict):
    return (rec.get("volume"), rec.get("pages"))


def _richness(rec: dict) -> int:
    """Prefer the fullest member as a cluster canonical."""
    score = 0
    for key in ("title", "abstract", "venue", "url"):
        if rec.get(key):
            score += 1
    score += len(rec.get("authors") or [])
    if _rec_doi(rec):
        score += 2
    return score


def dedup_records(records: list[dict]) -> dict:
    """Run the dedup cascade over normalized (or minimal) records.

    Cascade: normalized DOI → exact normalized title+year → fuzzy title+year.
    A fuzzy pair at/above ``FUZZY_AUTO_MERGE`` is merged; a pair in the review
    band ``[FUZZY_REVIEW_BAND, FUZZY_AUTO_MERGE)`` is flagged for review and left
    in separate clusters — borderline matches are never auto-merged or dropped.
    Conflicting volume/pages on an otherwise exact title+year match block the
    merge and raise a review flag instead.
    """
    n = len(records)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        parent[find(i)] = find(j)

    basis: dict[frozenset, str] = {}
    review_pairs: list[dict] = []

    # 1. Exact DOI.
    by_doi: dict[str, int] = {}
    for i, rec in enumerate(records):
        doi = _rec_doi(rec)
        if not doi:
            continue
        if doi in by_doi:
            union(i, by_doi[doi])
            basis[frozenset((find(i), find(by_doi[doi])))] = "doi"
        else:
            by_doi[doi] = i

    # 2 & 3. Title+year exact, then fuzzy, over the pairwise upper triangle.
    for i in range(n):
        ti, yi = normalize_title(_rec_title(records[i])), _rec_year(records[i])
        if not ti:
            continue
        for j in range(i + 1, n):
            if find(i) == find(j):
                continue
            tj, yj = normalize_title(_rec_title(records[j])), _rec_year(records[j])
            if not tj:
                continue
            if yi is not None and yj is not None and yi != yj:
                continue
            if ti == tj:
                vi, vj = _rec_volpages(records[i]), _rec_volpages(records[j])
                if _volpages_conflict(vi, vj):
                    review_pairs.append(_pair(i, j, 1.0, "title-year-volpages-conflict"))
                    continue
                union(i, j)
                basis.setdefault(frozenset((find(i), find(j))), "title-year")
                continue
            ratio = SequenceMatcher(None, ti, tj).ratio()
            if ratio >= FUZZY_AUTO_MERGE:
                union(i, j)
                basis.setdefault(frozenset((find(i), find(j))), "fuzzy-title")
            elif ratio >= FUZZY_REVIEW_BAND:
                review_pairs.append(_pair(i, j, ratio, "fuzzy-title"))

    groups: dict[int, list[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)

    clusters = []
    for cid, (root, members) in enumerate(sorted(groups.items())):
        canonical = max((records[m] for m in members), key=_richness)
        mb = "doi" if any(_rec_doi(records[m]) for m in members) else basis.get(frozenset((root,)), None)
        if len(members) > 1 and mb is None:
            mb = "title-year"
        clusters.append(
            {
                "cluster_id": cid,
                "members": members,
                "size": len(members),
                "match_basis": mb if len(members) > 1 else "singleton",
                "canonical": canonical,
            }
        )
    return {
        "n_input": n,
        "n_clusters": len(clusters),
        "clusters": clusters,
        "review_pairs": review_pairs,
    }


def _pair(i: int, j: int, ratio: float, basis: str) -> dict:
    return {
        "a": i,
        "b": j,
        "ratio": round(ratio, 4),
        "basis": basis,
        "note": "borderline — flagged for review, not auto-merged",
    }


def _volpages_conflict(a, b) -> bool:
    va, pa = a
    vb, pb = b
    if va and vb and str(va) != str(vb):
        return True
    if pa and pb and str(pa) != str(pb):
        return True
    return False


# --------------------------------------------------------------------------- #
# Subcommand handlers                                                          #
# --------------------------------------------------------------------------- #


def cmd_search(args, transport=None) -> int:
    cfg = get_config()
    transport = transport or build_default_transport(args, cfg)
    result: dict = {"query": args.query, "source": args.source, "s2_available": True, "notes": []}
    records: list[dict] = []
    if args.source in ("s2", "both"):
        try:
            records += s2_search(
                transport, cfg, args.query, limit=args.limit,
                year=_year_range(args.year_min, args.year_max),
                venue=args.venue, fields_of_study=args.field, include_raw=args.raw,
            )
        except S2Unavailable as exc:
            result["s2_available"] = False
            result["notes"].append(f"S2 unavailable, degraded to remaining sources: {exc}")
    if args.source in ("crossref", "both"):
        records += crossref_search(
            transport, cfg, args.query, limit=args.limit,
            year_min=args.year_min, year_max=args.year_max, venue=args.venue, include_raw=args.raw,
        )
    result["count"] = len(records)
    result["records"] = records
    emit(result)
    return 0


def cmd_references(args, transport=None) -> int:
    cfg = get_config()
    transport = transport or build_default_transport(args, cfg)
    result: dict = {"paper": args.paper_id, "source": args.source, "s2_available": True, "notes": []}
    records: list[dict] = []
    if args.source == "s2":
        try:
            records = s2_references(transport, cfg, args.paper_id, limit=args.limit, include_raw=args.raw)
        except S2Unavailable as exc:
            result["s2_available"] = False
            result["notes"].append(
                f"S2 unavailable; retry with --source crossref or --source opencitations: {exc}"
            )
    elif args.source == "opencitations":
        if detect_id_type(args.paper_id) != "doi":
            return fail("opencitations references need a DOI (OpenCitations indexes DOI->DOI edges)")
        try:
            records = opencitations_references(transport, cfg, args.paper_id, limit=args.limit, include_raw=args.raw)
            result["notes"].append(
                "OpenCitations edges are DOI-only; union across a paper's version DOIs for complete coverage"
            )
        except OpenCitationsUnavailable as exc:
            result["notes"].append(f"OpenCitations unavailable: {exc}")
    else:
        if detect_id_type(args.paper_id) != "doi":
            return fail("crossref references need a DOI (Crossref indexes references by DOI)")
        records = crossref_references(transport, cfg, args.paper_id, include_raw=args.raw)
        result["notes"].append("Crossref reference array is uneven and often DOI-less; prefer S2 when available")
    result["count"] = len(records)
    result["records"] = records
    emit(result)
    return 0


def _oc_citations_fallback(args, transport, cfg, result: dict) -> bool:
    """Try OpenCitations for forward citations; populate ``result`` on success.

    Returns True if OpenCitations answered (even with zero records), False if it
    was unavailable so the caller can degrade to the web-sweep note."""
    if detect_id_type(args.paper_id) != "doi":
        result["notes"].append("OpenCitations fallback needs a DOI; falling back to the workflow-layer web sweep")
        return False
    try:
        records = opencitations_citations(transport, cfg, args.paper_id, limit=args.limit, include_raw=args.raw)
    except OpenCitationsUnavailable as exc:
        result["notes"].append(f"OpenCitations fallback unavailable: {exc}")
        return False
    result["source"] = "opencitations"
    result["count"] = len(records)
    result["records"] = records
    result["notes"].append(
        "forward citations from OpenCitations (DOI-only); union across a paper's version DOIs for complete coverage"
    )
    return True


def cmd_citations(args, transport=None) -> int:
    cfg = get_config()
    transport = transport or build_default_transport(args, cfg)
    result: dict = {"paper": args.paper_id, "source": args.source, "s2_available": True, "notes": []}

    # Direct OpenCitations selection: skip S2 entirely.
    if args.source == "opencitations":
        if not _oc_citations_fallback(args, transport, cfg, result):
            result.setdefault("count", 0)
            result.setdefault("records", [])
        emit(result)
        return 0

    # S2 first (source s2 or auto).
    try:
        records = s2_citations(transport, cfg, args.paper_id, limit=args.limit, include_raw=args.raw)
        result["source"] = "s2"
        result["count"] = len(records)
        result["records"] = records
        emit(result)
        return 0
    except S2Unavailable as exc:
        result["s2_available"] = False
        result["notes"].append(f"S2 forward citations unavailable: {exc}")

    # Fallback chain: S2 -> OpenCitations -> empty + web-sweep note. `--source s2`
    # pins S2 only (old behavior); the default `auto` tries OpenCitations next.
    if args.source == "auto" and _oc_citations_fallback(args, transport, cfg, result):
        emit(result)
        return 0

    result["count"] = 0
    result["records"] = []
    result["notes"].append("fall back to the workflow-layer forward web sweep")
    emit(result)
    return 0


def cmd_metadata(args, transport=None) -> int:
    cfg = get_config()
    transport = transport or build_default_transport(args, cfg)
    identifier = args.identifier
    kind = detect_id_type(identifier)
    sources_used: list[str] = []
    notes: list[str] = []
    s2_available = True

    crossref_rec = None
    s2_rec = None
    arxiv_rec = None

    # Resolve to a DOI when possible so Crossref can supply the version of record.
    doi = normalize_doi(identifier) if kind == "doi" else None

    if kind in ("s2", "arxiv", "corpusid"):
        try:
            s2_rec = s2_paper(transport, cfg, identifier, include_raw=args.raw)
            sources_used.append("s2")
            if not doi:
                doi = (s2_rec.get("id") or {}).get("doi")
        except S2Unavailable as exc:
            s2_available = False
            notes.append(f"S2 unavailable: {exc}")

    if doi:
        crossref_rec = crossref_work(transport, cfg, doi, include_raw=args.raw)
        if crossref_rec is not None:
            sources_used.append("crossref")
        else:
            notes.append(f"no Crossref record for DOI {doi} (working paper with no published version yet?)")

    # Abstract hydration: S2 first, else arXiv (q-fin/econ preprints).
    if s2_rec is None and doi:
        try:
            s2_rec = s2_paper(transport, cfg, f"DOI:{doi}", include_raw=args.raw)
            sources_used.append("s2")
        except S2Unavailable as exc:
            s2_available = False
            notes.append(f"S2 abstract unavailable: {exc}")

    arxiv_id = None
    if kind == "arxiv":
        arxiv_id = re.sub(r"^arxiv:", "", identifier, flags=re.IGNORECASE)
    elif s2_rec:
        arxiv_id = (s2_rec.get("id") or {}).get("arxiv")
    need_abstract = not (crossref_rec and crossref_rec.get("abstract")) and not (s2_rec and s2_rec.get("abstract"))
    if arxiv_id and (need_abstract or kind == "arxiv"):
        try:
            arxiv_rec = arxiv_get(transport, arxiv_id, include_raw=args.raw)
            if arxiv_rec:
                sources_used.append("arxiv")
        except RuntimeError as exc:
            notes.append(f"arXiv lookup failed: {exc}")

    # Assemble: Crossref is authoritative when present, else arXiv (preprint),
    # else S2. Layer an abstract from S2/arXiv without overwriting a published field.
    version_of_record = crossref_rec is not None
    if crossref_rec is not None:
        record = crossref_rec
        for other in (s2_rec, arxiv_rec):
            if other:
                record = merge_records(record, other)
    elif arxiv_rec is not None:
        record = arxiv_rec
        if s2_rec:
            record = merge_records(record, s2_rec)
    elif s2_rec is not None:
        record = s2_rec
    else:
        return fail(f"could not resolve metadata for {identifier!r} from any source")

    # Abstract preference: S2 plain text > arXiv (q-fin/econ) > Crossref (JATS,
    # spotty for econ). Override a Crossref abstract when a cleaner one exists;
    # retain the Crossref one only as a last resort rather than dropping data.
    for cand in (s2_rec, arxiv_rec):
        if cand and cand.get("abstract"):
            record["abstract"] = cand["abstract"]
            record["abstract_source"] = cand["abstract_source"]
            break

    emit(
        {
            "identifier": identifier,
            "id_type": kind,
            "version_of_record": version_of_record,
            "s2_available": s2_available,
            "sources_used": sources_used,
            "notes": notes,
            "record": record,
        }
    )
    return 0


def cmd_dedup(args, transport=None) -> int:
    if args.file:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    if not raw.strip():
        return fail("no input records: pass --file PATH or pipe a JSON array on stdin")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return fail(f"input is not valid JSON: {exc}")
    # Accept a bare array, or a {"records": [...]} / {"clusters":[{canonical}]} wrapper.
    if isinstance(payload, dict):
        records = payload.get("records") or [c.get("canonical") for c in payload.get("clusters", [])]
    else:
        records = payload
    if not isinstance(records, list) or not records:
        return fail("input must be a non-empty JSON array of records (or {'records': [...]})")
    emit(dedup_records(records))
    return 0


def cmd_health(args, transport=None) -> int:
    """Report tool/runtime versions, config presence (booleans only), and reachability."""
    cfg = get_config()
    transport = transport or build_default_transport(args, cfg)
    s2_reachable = None
    if args.probe:
        try:
            s2_search(transport, cfg, "asset pricing", limit=1)
            s2_reachable = True
        except S2Unavailable:
            s2_reachable = False
    emit(
        {
            "tool_version": TOOL_VERSION,
            "python_version": sys.version.split()[0],
            "dependencies": "stdlib-only",
            "endpoints": {
                "s2": S2_BASE,
                "crossref": CROSSREF_BASE,
                "arxiv": ARXIV_BASE,
                "opencitations": OPENCITATIONS_BASE,
            },
            "config_present": {
                "S2_API_KEY": bool(cfg["s2_api_key"]),
                "CROSSREF_MAILTO": bool(cfg["crossref_mailto"]),
                "OPENCITATIONS_ACCESS_TOKEN": bool(cfg.get("opencitations_token")),
                "CITATION_CLIENT_CACHE_DIR": bool(cfg.get("cache_dir")),
            },
            "s2_key_mode": "keyed" if cfg["s2_api_key"] else "anonymous-pool",
            "cache_dir": str(resolve_cache_dir(cfg)),
            "rate_intervals": cfg.get("intervals"),
            "coordination": "cross-process" if _HAS_FCNTL else "per-process (no fcntl)",
            "s2_reachable": s2_reachable,
        }
    )
    return 0


def _year_range(year_min, year_max) -> str | None:
    if year_min and year_max:
        return f"{year_min}-{year_max}"
    if year_min:
        return f"{year_min}-"
    if year_max:
        return f"-{year_max}"
    return None


# --------------------------------------------------------------------------- #
# Argument parsing                                                            #
# --------------------------------------------------------------------------- #


def _add_raw(p: argparse.ArgumentParser) -> None:
    p.add_argument("--raw", action="store_true", help="include the verbatim source payload under 'raw'")


def _add_cache_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--no-cache", action="store_true", help="bypass the shared on-disk response cache")
    p.add_argument(
        "--cache-ttl", type=float, metavar="SECONDS",
        help="override the cache TTL for this call (default ~30d, forward citations ~7d)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="citation_client.py",
        description="Citation-graph and metadata client (keyless, JSON output).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("search", help="relevance/bibliographic search (S2 and/or Crossref)")
    p.add_argument("query", help="search terms")
    p.add_argument("--source", choices=["s2", "crossref", "both"], default="both", help="backend(s) (default both)")
    p.add_argument("--limit", type=int, default=25, help="max results per source (default 25)")
    p.add_argument("--year-min", type=int, help="earliest publication year")
    p.add_argument("--year-max", type=int, help="latest publication year")
    p.add_argument("--venue", help="venue / container-title filter")
    p.add_argument("--field", help="S2 fieldsOfStudy filter (e.g. Economics)")
    _add_raw(p)
    _add_cache_flags(p)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("references", help="backward references of a paper (S2, Crossref/OpenCitations fallback)")
    p.add_argument("paper_id", help="DOI / arXiv id / S2 id")
    p.add_argument(
        "--source", choices=["s2", "crossref", "opencitations"], default="s2",
        help="backend (default s2); crossref/opencitations need a DOI",
    )
    p.add_argument("--limit", type=int, default=100, help="max references (default 100)")
    _add_raw(p)
    _add_cache_flags(p)
    p.set_defaults(func=cmd_references)

    p = sub.add_parser("citations", help="forward citations of a paper (S2 -> OpenCitations fallback)")
    p.add_argument("paper_id", help="DOI / arXiv id / S2 id")
    p.add_argument(
        "--source", choices=["auto", "s2", "opencitations"], default="auto",
        help="auto = S2 then OpenCitations fallback (default); s2 = S2 only; opencitations = OpenCitations only",
    )
    p.add_argument("--limit", type=int, default=100, help="max citations (default 100)")
    _add_raw(p)
    _add_cache_flags(p)
    p.set_defaults(func=cmd_citations)

    p = sub.add_parser("metadata", help="hydrate verbatim metadata by identifier")
    p.add_argument("identifier", help="DOI / arXiv id / S2 id")
    _add_raw(p)
    _add_cache_flags(p)
    p.set_defaults(func=cmd_metadata)

    p = sub.add_parser("dedup", help="run the dedup cascade over a JSON array of records")
    p.add_argument("--file", metavar="PATH", help="JSON array of records (default: read stdin)")
    p.set_defaults(func=cmd_dedup)

    p = sub.add_parser("health", help="report versions, config presence, and reachability")
    p.add_argument("--probe", action="store_true", help="probe S2 reachability (one network call)")
    p.set_defaults(func=cmd_health)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as exc:
        return fail(str(exc))
    except Exception as exc:  # noqa: BLE001
        return fail(f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    sys.exit(main())
