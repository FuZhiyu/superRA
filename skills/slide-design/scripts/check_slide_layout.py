#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Cheap Beamer/PDF layout triage for slide-design work."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Finding:
    severity: str
    kind: str
    message: str
    page: int | None = None
    detail: str | None = None


@dataclass
class Word:
    text: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float


@dataclass
class Line:
    page: int
    text: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def compile_tex(tex_path: Path, workdir: Path) -> tuple[Path | None, Path | None, list[Finding]]:
    latexmk = shutil.which("latexmk")
    findings: list[Finding] = []
    if not latexmk:
        return None, None, [Finding("error", "missing-tool", "latexmk not found on PATH")]

    outdir = workdir / "build"
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = [
        latexmk,
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-outdir={outdir}",
        str(tex_path),
    ]
    proc = run(cmd, cwd=tex_path.parent)
    log_path = outdir / f"{tex_path.stem}.log"
    pdf_path = outdir / f"{tex_path.stem}.pdf"
    if proc.returncode != 0:
        findings.append(
            Finding(
                "error",
                "compile",
                f"latexmk exited with status {proc.returncode}",
                detail=(proc.stdout + "\n" + proc.stderr)[-2000:].strip(),
            )
        )
    return (pdf_path if pdf_path.exists() else None), (log_path if log_path.exists() else None), findings


def parse_log(log_path: Path | None) -> list[Finding]:
    if not log_path or not log_path.exists():
        return []

    findings: list[Finding] = []
    text = log_path.read_text(errors="replace")
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        if "Overfull \\hbox" in line or "Overfull \\vbox" in line:
            findings.append(Finding("warning", "overfull-box", line.strip(), detail=f"log line {idx}"))
        if "LaTeX Warning: File" in line and "not found" in line:
            findings.append(Finding("error", "missing-asset", line.strip(), detail=f"log line {idx}"))
        if line.startswith("! LaTeX Error:"):
            findings.append(Finding("error", "latex-error", line.strip(), detail=f"log line {idx}"))
    return findings


def extract_bbox_xml(pdf_path: Path, workdir: Path) -> tuple[Path | None, list[Finding]]:
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        return None, [Finding("error", "missing-tool", "pdftotext not found on PATH")]

    out_path = workdir / "bbox.html"
    proc = run([pdftotext, "-bbox", str(pdf_path), str(out_path)])
    if proc.returncode != 0:
        return None, [
            Finding(
                "error",
                "bbox-extract",
                f"pdftotext -bbox exited with status {proc.returncode}",
                detail=(proc.stdout + "\n" + proc.stderr)[-2000:].strip(),
            )
        ]
    return out_path, []


def parse_pages(bbox_path: Path) -> list[tuple[int, float, float, list[Word]]]:
    root = ET.parse(bbox_path).getroot()
    pages: list[tuple[int, float, float, list[Word]]] = []
    page_no = 0
    for page in root.iter():
        if strip_ns(page.tag) != "page":
            continue
        page_no += 1
        width = float(page.attrib.get("width", "0") or 0)
        height = float(page.attrib.get("height", "0") or 0)
        words: list[Word] = []
        for word in page.iter():
            if strip_ns(word.tag) != "word":
                continue
            text = "".join(word.itertext()).strip()
            if not text:
                continue
            words.append(
                Word(
                    text=html.unescape(text),
                    x_min=float(word.attrib["xMin"]),
                    y_min=float(word.attrib["yMin"]),
                    x_max=float(word.attrib["xMax"]),
                    y_max=float(word.attrib["yMax"]),
                )
            )
        pages.append((page_no, width, height, words))
    return pages


def strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def group_lines(page_no: int, words: Iterable[Word], y_tolerance: float = 3.0) -> list[Line]:
    sorted_words = sorted(words, key=lambda w: (w.y_min, w.x_min))
    buckets: list[list[Word]] = []
    for word in sorted_words:
        for bucket in buckets:
            bucket_y = sum(w.y_min for w in bucket) / len(bucket)
            if abs(word.y_min - bucket_y) <= y_tolerance:
                bucket.append(word)
                break
        else:
            buckets.append([word])

    lines: list[Line] = []
    for bucket in buckets:
        bucket.sort(key=lambda w: w.x_min)
        text = " ".join(w.text for w in bucket)
        lines.append(
            Line(
                page=page_no,
                text=text,
                x_min=min(w.x_min for w in bucket),
                y_min=min(w.y_min for w in bucket),
                x_max=max(w.x_max for w in bucket),
                y_max=max(w.y_max for w in bucket),
            )
        )
    return sorted(lines, key=lambda line: (line.page, line.y_min, line.x_min))


def detect_placeholder_pages(bbox_path: Path) -> list[Finding]:
    r"""Flag pages whose text contains the \includeifexists placeholder marker."""
    findings: list[Finding] = []
    # The house template's \includeifexists renders this string when a figure file is missing.
    # parse_log cannot catch these because \includeifexists swallows the missing-file warning.
    placeholder_marker = "Figure not available:"
    for page_no, _width, _height, words in parse_pages(bbox_path):
        # Reconstruct page text from all words to handle cases where pdftotext
        # splits the phrase across multiple word boxes.
        page_text = " ".join(w.text for w in words)
        if placeholder_marker in page_text:
            findings.append(
                Finding(
                    "warning",
                    "missing-asset",
                    f"Placeholder box detected (figure not available) on page {page_no}",
                    page=page_no,
                    detail=page_text[:300],
                )
            )
    return findings


def detect_layout_issues(bbox_path: Path) -> list[Finding]:
    # Heuristic constants below are calibrated to the house template
    # (10pt metropolis, \onehalfspacing). They may produce false negatives
    # (missed wraps) or false positives (spurious near-boundary warnings)
    # on other themes or font sizes — inspect flagged pages before acting.
    findings: list[Finding] = []
    findings.extend(detect_placeholder_pages(bbox_path))
    for page_no, width, height, words in parse_pages(bbox_path):
        lines = group_lines(page_no, words)
        page_lefts = [line.x_min for line in lines if len(line.text) > 8]
        if not page_lefts:
            continue
        left_margin = min(page_lefts)
        right_limit = width * 0.97 if width else float("inf")   # 0.97: right-edge boundary fraction
        bottom_limit = height * 0.96 if height else float("inf")  # 0.96: bottom-edge boundary fraction

        for line in lines:
            if is_footer_counter(line.text):
                continue
            if line.x_max > right_limit or line.y_max > bottom_limit:
                findings.append(
                    Finding(
                        "warning",
                        "near-boundary",
                        "Text appears close to a slide boundary",
                        page=page_no,
                        detail=line.text[:180],
                    )
                )

        for prev, curr in zip(lines, lines[1:]):
            if starts_bullet(curr.text) or is_footer_counter(prev.text) or is_footer_counter(curr.text):
                continue
            vertical_gap = curr.y_min - prev.y_min
            same_block = 7.0 <= vertical_gap <= 22.0   # 7–22pt: line-gap window for metropolis 10pt + \onehalfspacing
            continuation_indent = curr.x_min >= prev.x_min + 8.0  # 8pt: continuation indent threshold
            not_new_heading = not curr.text[:1].isdigit() and not re.match(r"^[A-Z][A-Za-z ]{0,35}:?$", curr.text)
            prev_unfinished = not prev.text.rstrip().endswith((".", ":", ";", "?", "!"))
            if same_block and continuation_indent and not_new_heading and (prev_unfinished or curr.x_min > left_margin + 20):
                findings.append(
                    Finding(
                        "info",
                        "possible-wrap",
                        "Possible wrapped bullet or continuation line",
                        page=page_no,
                        detail=f"{prev.text[:90]} / {curr.text[:90]}",
                    )
                )
    return findings


def starts_bullet(text: str) -> bool:
    return bool(re.match(r"^\s*(?:[•▶▪■◆◦-]|\d+[.)])\s+", text))


def is_footer_counter(text: str) -> bool:
    return bool(re.match(r"^\s*\d+\s*/\s*\d+\s*$", text))


def render_findings(findings: list[Finding], as_json: bool) -> str:
    if as_json:
        return json.dumps([asdict(f) for f in findings], indent=2)
    if not findings:
        return "No layout findings."
    lines: list[str] = []
    for finding in findings:
        page = f" page {finding.page}" if finding.page is not None else ""
        lines.append(f"[{finding.severity}] {finding.kind}{page}: {finding.message}")
        if finding.detail:
            lines.append(f"  {finding.detail}")
    return "\n".join(lines)


def render_flagged_pages(pdf_path: Path, findings: list[Finding], outdir: Path) -> list[Finding]:
    pages = sorted({f.page for f in findings if f.page is not None})
    if not pages:
        return []
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        return [Finding("error", "missing-tool", "pdftoppm not found on PATH; cannot render flagged pages")]
    outdir.mkdir(parents=True, exist_ok=True)
    rendered: list[Finding] = []
    for page in pages:
        prefix = outdir / f"{pdf_path.stem}-flagged"
        proc = run([pdftoppm, "-png", "-r", "100", "-f", str(page), "-l", str(page), str(pdf_path), str(prefix)])
        if proc.returncode == 0:
            rendered.append(Finding("info", "rendered-page", f"Flagged page {page} rendered under {outdir}", page=page))
        else:
            rendered.append(Finding("error", "render-failed", f"pdftoppm failed for page {page}", page=page))
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Beamer .tex file or rendered .pdf")
    parser.add_argument("--log", type=Path, help="Optional LaTeX log to parse when input is a PDF")
    parser.add_argument("--json", action="store_true", help="Emit JSON findings")
    parser.add_argument("--no-fail", action="store_true", help="Always exit 0 after reporting findings")
    parser.add_argument(
        "--render-flagged",
        type=Path,
        metavar="DIR",
        help="Render each flagged page to a PNG in DIR for visual inspection",
    )
    args = parser.parse_args()

    source = args.input.resolve()
    if not source.exists():
        print(f"Input not found: {source}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    with tempfile.TemporaryDirectory(prefix="slide-layout-") as tmp:
        workdir = Path(tmp)
        if source.suffix.lower() == ".tex":
            pdf_path, log_path, compile_findings = compile_tex(source, workdir)
            findings.extend(compile_findings)
        elif source.suffix.lower() == ".pdf":
            pdf_path = source
            log_path = args.log.resolve() if args.log else None
        else:
            print("Input must be a .tex or .pdf file", file=sys.stderr)
            return 2

        findings.extend(parse_log(log_path))
        if pdf_path and pdf_path.exists():
            bbox_path, bbox_findings = extract_bbox_xml(pdf_path, workdir)
            findings.extend(bbox_findings)
            if bbox_path:
                findings.extend(detect_layout_issues(bbox_path))
            if args.render_flagged:
                findings.extend(render_flagged_pages(pdf_path, findings, args.render_flagged.resolve()))

    print(render_findings(findings, args.json))
    has_problem = any(f.severity in {"error", "warning"} for f in findings)
    return 0 if args.no_fail or not has_problem else 1


if __name__ == "__main__":
    raise SystemExit(main())
