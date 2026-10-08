#!/usr/bin/env python3
"""Rebuild library/RECONVERT.csv: every book under --books-root that has no
matching .md under --md-root (same relative path, .md extension).

Same columns and rules as the original one-off list, so safe_convert.py reads it unchanged:
  category,ext,suggested_fix,path   (path like ./Category/Sub/Book.azw3)
A book counts as converted if ANY file with the same stem has an .md, so a new
book.epub made from an already-converted book.azw3 is not queued again.

Usage (from the learning repo):
  python3 scripts/make_reconvert.py --books-root "/media/rahul/Drive 2/Library/Library" \
      --md-root "/media/rahul/Drive 2/Library/Markdown_Library"
The old file is kept as library/RECONVERT.csv.bak.
"""
import argparse, collections, csv, os, shutil
from pathlib import Path

EXT = {".pdf", ".epub", ".djvu", ".mobi", ".azw3", ".htm", ".html", ".txt", ".docx"}
FIX = {".pdf": "marker (text PDFs) / ocrmypdf then marker (scans)",
       ".djvu": "ddjvu -format=pdf, then ocrmypdf + marker",
       ".azw3": "calibre ebook-convert -> .epub, then reconvert",
       ".mobi": "calibre ebook-convert -> .epub, then reconvert",
       ".epub": "retry (likely DRM or malformed); calibre ebook-convert repair",
       ".html": "pandoc -f html -t gfm", ".htm": "pandoc -f html -t gfm",
       ".txt": "copy as-is (already text)", ".docx": "pandoc -f docx -t gfm"}
LIB = Path(__file__).resolve().parent.parent / "library"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books-root", required=True, type=Path)
    ap.add_argument("--md-root", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=LIB / "RECONVERT.csv")
    a = ap.parse_args()
    for d in (a.books_root, a.md_root):
        if not d.is_dir():
            raise SystemExit(f"not a directory: {d}")

    have = set()
    for dp, _, fs in os.walk(a.md_root):
        rel = Path(dp).relative_to(a.md_root)
        if "tmp" in rel.parts:
            continue
        have.update(str(rel / Path(f).stem) for f in fs if f.lower().endswith(".md"))

    rows = []
    for dp, _, fs in os.walk(a.books_root):
        rel = Path(dp).relative_to(a.books_root)
        if not rel.parts or rel.parts[0] == "book lists":
            continue
        for f in fs:
            ext = Path(f).suffix.lower()
            if ext in EXT and str(rel / Path(f).stem) not in have:
                rows.append({"category": rel.parts[0], "ext": ext, "suggested_fix": FIX[ext],
                             "path": "./" + str(rel / f)})
    # one row per book: if book.azw3 and book.epub both exist, queue only the epub (cleaner conversion)
    PREF = [".epub", ".azw3", ".mobi", ".docx", ".html", ".htm", ".txt", ".pdf", ".djvu"]
    best = {}
    for r in rows:
        k = os.path.splitext(r["path"])[0]
        if k not in best or PREF.index(r["ext"]) < PREF.index(best[k]["ext"]):
            best[k] = r
    rows = sorted(best.values(), key=lambda r: (r["ext"], r["category"], r["path"]))

    a.out.parent.mkdir(parents=True, exist_ok=True)
    if a.out.exists():
        shutil.copy2(a.out, a.out.with_suffix(".csv.bak"))
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["category", "ext", "suggested_fix", "path"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} book(s) without markdown -> {a.out}")
    print("  " + ", ".join(f"{e} {n}" for e, n in collections.Counter(r['ext'] for r in rows).most_common()))


if __name__ == "__main__":
    main()
