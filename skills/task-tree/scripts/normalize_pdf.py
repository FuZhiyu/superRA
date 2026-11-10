#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pikepdf==10.13.0.post1",
#     "lxml==6.0.2",
# ]
# ///
"""Strip volatile metadata from PDFs in place, so a regenerated figure keeps its bytes.

    uv run --script normalize_pdf.py Figures/plot.pdf output/*.pdf
    uv run --script normalize_pdf.py --verify-render --json Figures/plot.pdf

Removes Info and XMP dates, Creator/Producer, TeX build paths (/PTEX.*), and
document IDs; keeps descriptive metadata, content, fonts, links, forms, and
attachments. QPDF rewrites objects deterministically with a content-derived
trailer ID, so a drawing saved twice yields identical bytes. Different drawing
commands that render alike still differ.

Each file is handled on its own: an encrypted, signed, or unreadable PDF, or one
whose second pass would differ, is skipped and left as written. --verify-render
also skips a file whose pages render differently at 96 dpi (needs Poppler's
pdftoppm). Replacements are atomic per file; a file symlink's target is rewritten.
Exit 0 unless the arguments are invalid; --json prints one record per file.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pikepdf
from lxml import etree

INFO_VOLATILE = {"/CreationDate", "/ModDate", "/Creator", "/Producer"}
XMP_VOLATILE = {
    "http://ns.adobe.com/xap/1.0/": {"CreateDate", "ModifyDate", "MetadataDate", "CreatorTool"},
    "http://ns.adobe.com/pdf/1.3/": {"Producer"},
    "http://ns.adobe.com/xap/1.0/mm/": {"DocumentID", "InstanceID", "OriginalDocumentID", "History"},
}


class Skip(Exception):
    """A PDF this tool leaves as written; the message is the reason."""


def _volatile_xmp(name) -> bool:
    qname = etree.QName(name)
    return qname.localname in XMP_VOLATILE.get(qname.namespace, set())


def normalize(data: bytes) -> bytes:
    try:
        pdf = pikepdf.Pdf.open(io.BytesIO(data), attempt_recovery=False)
    except pikepdf.PasswordError:
        raise Skip("encrypted") from None
    except pikepdf.PdfError:
        raise Skip("unreadable PDF") from None
    with pdf:
        if pdf.is_encrypted:
            raise Skip("encrypted")
        for obj in pdf.objects:
            if isinstance(obj, pikepdf.Dictionary) and (
                obj.get("/Type") == pikepdf.Name.Sig or "/ByteRange" in obj
            ):
                raise Skip("signed")
        if "/Info" in pdf.trailer:
            for key in list(pdf.docinfo.keys()):
                if key in INFO_VOLATILE or key.startswith("/PTEX."):
                    del pdf.docinfo[key]
            if not len(pdf.docinfo):
                del pdf.trailer["/Info"]
        if "/Metadata" in pdf.Root:
            try:
                xml = etree.fromstring(pdf.Root.Metadata.read_bytes(),
                                       etree.XMLParser(resolve_entities=False, no_network=True))
            except etree.XMLSyntaxError:
                raise Skip("malformed XMP metadata") from None
            for element in list(xml.iter()):
                if not isinstance(element.tag, str):
                    continue
                if _volatile_xmp(element.tag):
                    element.getparent().remove(element)
                    continue
                for key in list(element.attrib):
                    if _volatile_xmp(key):
                        del element.attrib[key]
            # Reserializing the root also drops variable xpacket padding and IDs.
            pdf.Root.Metadata.write(etree.tostring(xml))
        if "/ID" in pdf.trailer:
            del pdf.trailer["/ID"]
        output = io.BytesIO()
        pdf.save(output, min_version="1.4", deterministic_id=True, fix_metadata_version=False,
                 object_stream_mode=pikepdf.ObjectStreamMode.disable,
                 compress_streams=True, recompress_flate=True)
        return output.getvalue()


def _raster_digest(path: Path) -> bytes:
    digest = hashlib.sha256()
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(["pdftoppm", "-r", "96", str(path)],
                                   stdout=subprocess.PIPE, stderr=errors)
        for block in iter(lambda: process.stdout.read(1 << 20), b""):
            digest.update(block)
        if process.wait():
            errors.seek(0)
            raise Skip(f"pdftoppm failed: {errors.read().decode(errors='replace').strip()}")
    return digest.digest()


def clean(path: Path, verify_render: bool) -> str:
    """Rewrite *path* in place; 'normalized' or 'unchanged', else raise Skip."""
    target = path.resolve()
    original = target.read_bytes()
    cleaned = normalize(original)
    if cleaned == original:
        return "unchanged"
    if normalize(cleaned) != cleaned:
        raise Skip("a second pass would differ")
    fd, staging = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".pdf", dir=target.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(cleaned)
        if verify_render and _raster_digest(target) != _raster_digest(Path(staging)):
            raise Skip("rendered pages would change")
        if target.read_bytes() != original:
            raise Skip("file changed while it was being cleaned")
        shutil.copymode(target, staging)
        os.replace(staging, target)
    finally:
        Path(staging).unlink(missing_ok=True)
    return "normalized"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--verify-render", action="store_true", help="skip a file whose pages would render differently")
    parser.add_argument("--json", action="store_true", help="print one JSON record per file")
    args = parser.parse_args(argv)
    if args.verify_render and not shutil.which("pdftoppm"):
        parser.error("--verify-render needs pdftoppm (brew install poppler)")
    records = []
    for path in args.paths:
        try:
            records.append({"path": str(path), "result": clean(path, args.verify_render)})
        except Skip as exc:
            records.append({"path": str(path), "result": "skipped", "reason": str(exc)})
        except OSError as exc:
            records.append({"path": str(path), "result": "skipped", "reason": f"unreadable ({exc.strerror})"})
        except Exception as exc:  # one bad file never aborts the batch
            records.append({"path": str(path), "result": "skipped", "reason": f"cleaner error ({type(exc).__name__})"})
    if args.json:
        print(json.dumps(records))
    else:
        for record in records:
            print(f"{record['result']}: {record['path']}"
                  + (f" ({record['reason']})" if "reason" in record else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
