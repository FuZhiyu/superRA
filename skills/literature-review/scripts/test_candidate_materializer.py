from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("candidate_materializer.py")


def run_cmd(*args: str, input_obj: object | None = None) -> dict:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=json.dumps(input_obj) if input_obj is not None else None,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(proc.stdout)


def sample_record() -> dict:
    return {
        "id": {"doi": "10.1111/JOFI.12345", "s2": "abc"},
        "title": "Market Liquidity and Heterogeneous Investors",
        "authors": [{"name": "Ada Smith", "family": "Smith"}],
        "year": 2024,
        "venue": "Journal of Finance",
        "abstract": "We study heterogeneous investors.",
        "url": "https://doi.org/10.1111/jofi.12345",
        "zotero": {
            "item_uri": "zotero://select/library/items/ABCD1234",
            "attachment_uri": "zotero://select/library/items/WXYZ9876",
        },
    }


def test_key_uses_author_venue_year_title() -> None:
    out = run_cmd("key", input_obj=sample_record())
    assert out[0]["key"].startswith("smith-journal-of-finance-2024-market-liquidity")
    assert out[0]["identity"]["doi"] == "10.1111/jofi.12345"


def test_materialize_creates_task_shaped_record(tmp_path: Path) -> None:
    out = run_cmd("materialize", "--store", str(tmp_path), "--provenance", "web:ssrn", input_obj=sample_record())
    task_path = Path(out["results"][0]["path"])
    text = task_path.read_text(encoding="utf-8")
    assert out["results"][0]["action"] == "created"
    assert "status: not-started" in text
    assert "## Discovery Provenance" in text
    assert "- Discovered via: web:ssrn" in text
    assert "- DOI: 10.1111/jofi.12345" in text
    assert "- Zotero item: zotero://select/library/items/ABCD1234" in text
    assert "- Zotero attachment: zotero://select/library/items/WXYZ9876" in text
    assert "## Quality" in text
    assert "- Outlet tier: " in text
    assert "- Identification strategy: " in text
    assert "- Decision: pending" in text
    assert "- Promotion recommendation: " in text
    assert "- Access: " in text


def test_materialize_reuses_existing_by_doi(tmp_path: Path) -> None:
    first = run_cmd("materialize", "--store", str(tmp_path), input_obj=sample_record())
    second_record = sample_record()
    second_record["title"] = "A Slightly Different Title"
    second = run_cmd("materialize", "--store", str(tmp_path), input_obj=second_record)
    assert first["results"][0]["key"] == second["results"][0]["key"]
    assert second["results"][0]["action"] == "matched-existing"
