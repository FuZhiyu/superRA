from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
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


def test_materialize_merges_new_handles_into_existing_card(tmp_path: Path) -> None:
    first_record = sample_record()
    first_record["id"] = {"doi": "10.1111/JOFI.12345"}
    first_record.pop("pdf_url", None)
    first_record.pop("pdf_path", None)
    first = run_cmd("materialize", "--store", str(tmp_path), input_obj=first_record)

    second_record = sample_record()
    second_record["id"] = {
        "doi": "10.1111/JOFI.12345",
        "arxiv": "2401.00001",
        "s2": "S2-NEW",
        "corpus_id": "123456",
    }
    second_record["pdf_url"] = "https://example.test/paper.pdf"
    second_record["pdf_path"] = "attachments/paper.pdf"
    second_record["md_path"] = "attachments/paper.md"
    second = run_cmd("materialize", "--store", str(tmp_path), input_obj=second_record)

    task_path = Path(first["results"][0]["path"])
    text = task_path.read_text(encoding="utf-8")
    assert second["results"][0]["action"] == "matched-existing"
    assert set(second["results"][0]["merged_fields"]) >= {"arXiv", "S2", "Corpus ID", "PDF URL", "PDF path", "Markdown path"}
    assert "- arXiv: 2401.00001" in text
    assert "- S2: S2-NEW" in text
    assert "- Corpus ID: 123456" in text
    assert "- PDF URL: https://example.test/paper.pdf" in text
    assert "- PDF path: attachments/paper.pdf" in text
    assert "- Markdown path: attachments/paper.md" in text


def test_concurrent_materialize_merges_one_not_started_card(tmp_path: Path) -> None:
    records = []
    for i in range(6):
        rec = sample_record()
        rec["abstract"] = f"Abstract version {i}"
        records.append(rec)

    def call(i: int) -> dict:
        return run_cmd("materialize", "--store", str(tmp_path), "--provenance", f"web:lens-{i}", input_obj=records[i])

    with ThreadPoolExecutor(max_workers=6) as pool:
        outs = list(pool.map(call, range(6)))

    task_paths = {Path(out["results"][0]["path"]) for out in outs}
    assert len(task_paths) == 1
    assert len(list(tmp_path.glob("*/task.md"))) == 1
    text = next(iter(task_paths)).read_text(encoding="utf-8")
    assert "status: not-started" in text
    assert "## Metadata" in text
    assert "## Extraction" in text


def test_claim_transitions_exactly_one_concurrent_reader(tmp_path: Path) -> None:
    created = run_cmd("materialize", "--store", str(tmp_path), input_obj=sample_record())
    key = created["results"][0]["key"]

    def call(i: int) -> dict:
        return run_cmd("claim", key, "--store", str(tmp_path), "--by", f"dispatch-{i}")

    with ThreadPoolExecutor(max_workers=5) as pool:
        outs = list(pool.map(call, range(5)))

    winners = [out for out in outs if out["won"]]
    assert len(winners) == 1
    assert all(out["status"] == "in-progress" for out in outs)
    task_text = (tmp_path / key / "task.md").read_text(encoding="utf-8")
    assert "status: in-progress" in task_text
    assert "## Claim" in task_text
    assert "- Claimed by: dispatch-" in task_text


def test_promote_moves_and_rewrites_candidate_link(tmp_path: Path) -> None:
    source = run_cmd("materialize", "--store", str(tmp_path), input_obj=sample_record())
    key = source["results"][0]["key"]
    citing_record = sample_record()
    citing_record["id"] = {"doi": "10.1111/jofi.99999", "s2": "different"}
    citing_record["title"] = "A Citing Paper"
    citing = run_cmd("materialize", "--store", str(tmp_path), input_obj=citing_record)
    citing_path = Path(citing["results"][0]["path"])
    text = citing_path.read_text(encoding="utf-8")
    text = text.replace("- Source paper: ", f"- Source paper: {key}/task.md")
    text = text.replace(
        "- Local reason: Not recorded.",
        f"- Local reason: Plain mention {key} is not a path reference.",
    )
    citing_path.write_text(text, encoding="utf-8")

    dest = tmp_path / "permanent" / key
    out = run_cmd("promote", key, "--store", str(tmp_path), "--destination", str(dest))

    assert out["action"] == "promoted"
    assert dest.exists()
    assert not (tmp_path / key).exists()
    assert (dest / "task.md").exists()
    updated = citing_path.read_text(encoding="utf-8")
    assert "permanent" in updated
    assert f"Plain mention {key} is not a path reference." in updated
    assert out["updated_links"]
    assert str(citing_path) in out["unresolved_links"]
