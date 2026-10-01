#!/usr/bin/env python3
"""Extract searchable text from your own PDFs/EPUBs into library/text/, one .txt per book,
with page markers so lessons can cite "p. 112". Run locally, then commit library/text/.
Only the text gets committed, not the book files.

Usage: pip install pypdf && python3 scripts/extract_text.py ~/Books/*.pdf ~/Books/*.epub
"""
import re, sys, zipfile
from html.parser import HTMLParser
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "library" / "text"

def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:80]

def pdf_text(path):
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    return "\n".join(f"\n=== p. {i} ===\n{page.extract_text() or ''}" for i, page in enumerate(reader.pages, 1))

class _Strip(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []
    def handle_data(self, d): self.parts.append(d)
    def handle_endtag(self, tag):
        if tag in ("p", "div", "br", "h1", "h2", "h3", "li"): self.parts.append("\n")

def epub_text(path):
    out = []
    with zipfile.ZipFile(path) as z:
        names = sorted(n for n in z.namelist() if n.lower().endswith((".xhtml", ".html", ".htm")))
        for i, n in enumerate(names, 1):
            s = _Strip(); s.feed(z.read(n).decode("utf-8", "ignore"))
            out.append(f"\n=== section {i}: {Path(n).stem} ===\n" + re.sub(r"\n{3,}", "\n\n", "".join(s.parts)))
    return "".join(out)

def main(paths):
    OUT.mkdir(parents=True, exist_ok=True)
    for p in map(Path, paths):
        ext = p.suffix.lower()
        if ext not in (".pdf", ".epub"):
            print(f"skip {p.name}"); continue
        try:
            text = pdf_text(p) if ext == ".pdf" else epub_text(p)
        except Exception as e:
            print(f"FAILED {p.name}: {e}"); continue
        if len(text.strip()) < 200:
            print(f"WARNING {p.name}: almost no text (scanned PDF? needs OCR)")
        dest = OUT / f"{slug(p.stem)}.txt"
        dest.write_text(f"SOURCE: {p.name}\n{text}", encoding="utf-8")
        print(f"{p.name} -> {dest.relative_to(OUT.parent.parent)} ({dest.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
