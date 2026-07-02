#!/usr/bin/env python3
"""
Offline regression test for per-paper image namespacing.

Guards the collision fix: converting two papers into the SAME output directory
must produce disjoint image sets under separate images/<stem>/ subfolders with
zero overwrite, and each .md's image references must resolve to its own
subfolder.

Runs fully offline — the Mistral client, pypdf, and dotenv imports are stubbed
before importing the converter, and the network/key-dependent stages
(load_api_key, extract_pages, process_with_mistral) are monkeypatched to feed a
synthetic OCR response. No Mistral key, no network, no third-party deps.

Run standalone:  python3 test_image_namespacing.py
Or under pytest: pytest test_image_namespacing.py
"""

import base64
import importlib
import sys
import types
from pathlib import Path


def _install_import_stubs():
    """Stub the converter's third-party imports so it loads with no deps."""
    if "mistralai" not in sys.modules:
        mistralai = types.ModuleType("mistralai")
        client_mod = types.ModuleType("mistralai.client")
        client_mod.Mistral = object
        mistralai.client = client_mod
        sys.modules["mistralai"] = mistralai
        sys.modules["mistralai.client"] = client_mod
    if "pypdf" not in sys.modules:
        pypdf = types.ModuleType("pypdf")
        pypdf.PdfReader = object
        pypdf.PdfWriter = object
        sys.modules["pypdf"] = pypdf
    if "dotenv" not in sys.modules:
        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = lambda *a, **k: None
        sys.modules["dotenv"] = dotenv


def _load_converter():
    _install_import_stubs()
    sys.path.insert(0, str(Path(__file__).parent))
    return importlib.import_module("convert_pdf_to_markdown")


# --- synthetic OCR response ------------------------------------------------

# 1x1 JPEG bytes, base64-encoded, used as every synthetic figure.
_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRof"
    "Hh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA/8QAFAAB"
    "AAAAAAAAAAAAAAAAAAAACP/EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAT8AfwD/2Q=="
)


class _Img:
    def __init__(self, ident):
        self.id = ident
        # Distinct payload per image so an overwrite would be detectable.
        self.image_base64 = "data:image/jpeg;base64," + _JPEG_B64


class _Page:
    def __init__(self, markdown, images):
        self.markdown = markdown
        self.images = images


class _OcrResponse:
    def __init__(self, pages):
        self.pages = pages


def _make_response(n_images):
    """One page whose markdown references img-0..img-(n-1) in order."""
    refs = "\n\n".join(
        f"![img-{i}.jpeg](img-{i}.jpeg)" for i in range(n_images)
    )
    markdown = f"# Paper\n\n{refs}\n"
    images = [_Img(f"img-{i}.jpeg") for i in range(n_images)]
    return _OcrResponse([_Page(markdown, images)])


# --- test ------------------------------------------------------------------

def run(tmp_root):
    conv = _load_converter()

    out_dir = Path(tmp_root)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Two papers, both converted into the SAME output directory. Each returns a
    # different number of figures so we can prove neither clobbers the other.
    responses = {
        "paper_alpha": _make_response(2),
        "paper_beta": _make_response(3),
    }

    def fake_load_api_key():
        return "test-key-not-used"

    def fake_extract_pages(pdf_path, page_selection=None):
        return "unused-base64"

    conv.load_api_key = fake_load_api_key
    conv.extract_pages = fake_extract_pages
    # Dispatch on the stem the driver loop sets on the module before each call.
    conv.process_with_mistral = lambda api_key, base64_pdf: responses[conv._TEST_STEM]

    for stem in ("paper_alpha", "paper_beta"):
        conv._TEST_STEM = stem
        md_path = out_dir / f"{stem}.md"
        # Create a dummy input PDF so the path exists; contents are unused.
        pdf_path = out_dir / f"{stem}.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 dummy")
        conv.convert_pdf_to_markdown(pdf_path, md_path)

    # 1. Each paper's images live in its own subfolder.
    alpha_imgs = sorted((out_dir / "images" / "paper_alpha").glob("*.jpeg"))
    beta_imgs = sorted((out_dir / "images" / "paper_beta").glob("*.jpeg"))
    assert len(alpha_imgs) == 2, f"expected 2 alpha images, got {len(alpha_imgs)}"
    assert len(beta_imgs) == 3, f"expected 3 beta images, got {len(beta_imgs)}"

    # 2. No flat images/ files — nothing landed in the shared (collision) dir.
    flat = list((out_dir / "images").glob("*.jpeg"))
    assert not flat, f"unexpected flat images (collision layout): {flat}"

    # 3. Disjoint image paths → zero overwrite possible across papers.
    alpha_names = {p.name for p in alpha_imgs}
    beta_names = {p.name for p in beta_imgs}
    # Filenames overlap (img-0.jpeg etc.), but full paths are namespaced apart.
    alpha_paths = {p.resolve() for p in alpha_imgs}
    beta_paths = {p.resolve() for p in beta_imgs}
    assert alpha_paths.isdisjoint(beta_paths), "image paths collide across papers"
    assert "img-0.jpeg" in alpha_names and "img-0.jpeg" in beta_names, (
        "expected same filenames under different subfolders"
    )

    # 4. Each .md references only its own images/<stem>/ subfolder.
    alpha_md = (out_dir / "paper_alpha.md").read_text()
    beta_md = (out_dir / "paper_beta.md").read_text()
    assert "](images/paper_alpha/img-" in alpha_md
    assert "](images/paper_beta/" not in alpha_md
    assert "](images/paper_beta/img-" in beta_md
    assert "](images/paper_alpha/" not in beta_md
    # No dangling flat reference survives the rewrite.
    assert "](img-" not in alpha_md and "](img-" not in beta_md

    # 5. Every referenced image path resolves to a file on disk.
    for md_text, stem in ((alpha_md, "paper_alpha"), (beta_md, "paper_beta")):
        n = 2 if stem == "paper_alpha" else 3
        for i in range(n):
            ref = out_dir / "images" / stem / f"img-{i}.jpeg"
            assert ref.exists(), f"dangling reference: {ref}"

    print("OK: per-paper image namespacing holds; no overwrite, no dangling refs")


def test_image_namespacing(tmp_path):
    run(tmp_path)


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        run(td)
