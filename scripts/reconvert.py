#!/usr/bin/env python3
"""Retry the books in library/RECONVERT.csv with a converter suited to each format.

Default is a DRY RUN that only prints commands. Add --run to execute.
Never modifies your originals. Skips any book whose .md already exists.

  pdf        -> marker_single (does its own OCR on scanned pages; LaTeX for equations)
  djvu       -> ddjvu -> pdf -> marker_single
  azw3/mobi  -> calibre ebook-convert -> epub -> pandoc
  epub       -> pandoc (retry); falls back to calibre repair -> pandoc
  html/docx  -> pandoc
  txt        -> copied as .md

Usage:
  python3 scripts/reconvert.py --books-root ~/Books --md-root ~/BooksMD --new --run     # convert books added since last time
  python3 scripts/reconvert.py --books-root ~/Books --md-root ~/BooksMD                 # dry run, everything in RECONVERT.csv
  python3 scripts/reconvert.py --books-root ~/Books --md-root ~/BooksMD --only pdf --limit 3 --run
Then re-run scripts/grade_library.py.
"""
import argparse, csv, shutil, subprocess, sys, tempfile
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "library"

def pandoc(src, dest, fmt=None):
    cmd = ["pandoc", str(src), "-t", "gfm", "--wrap=none", "-o", str(dest),
           f"--extract-media={dest.parent / (dest.stem + '_assets')}"]
    return cmd[:2] + (["-f", fmt] if fmt else []) + cmd[2:]

def plan(src, dest, tmp, mode):
    ext = src.suffix.lower()
    marker = lambda pdf: ["marker_single", str(pdf), "--output_dir", str(tmp), "--output_format", "markdown"] + (["--mode", mode] if mode else [])
    if ext == ".pdf":
        return [marker(src)], "marker"
    if ext == ".djvu":
        pdf = tmp / (src.stem + ".pdf")
        return [["ddjvu", "-format=pdf", str(src), str(pdf)], marker(pdf)], "marker"
    if ext in (".azw3", ".mobi"):
        ep = tmp / (src.stem + ".epub")
        return [["ebook-convert", str(src), str(ep)], pandoc(ep, dest)], "pandoc"
    if ext == ".epub":
        return [pandoc(src, dest)], "pandoc"
    if ext in (".html", ".htm"):
        return [pandoc(src, dest, "html")], "pandoc"
    if ext == ".docx":
        return [pandoc(src, dest, "docx")], "pandoc"
    if ext == ".txt":
        return [["cp", str(src), str(dest)]], "copy"
    return [], "unsupported"

def collect_marker(tmp, stem, dest):
    out = tmp / stem
    mds = list(out.glob("*.md")) if out.exists() else []
    if not mds:
        return False
    shutil.move(str(mds[0]), dest)
    assets = dest.parent / (dest.stem + "_assets")
    rest = [p for p in out.iterdir()]
    if rest:
        assets.mkdir(exist_ok=True)
        for p in rest:
            shutil.move(str(p), assets / p.name)
    return True

TOOLS = {"ddjvu": "djvulibre-bin", "ebook-convert": "calibre", "pandoc": "pandoc", "marker_single": "pip install marker-pdf"}
EXTS = (".pdf", ".djvu", ".azw3", ".mobi", ".epub", ".html", ".htm", ".docx", ".txt")

def missing_tool(cmds):
    for c in cmds:
        if c[0] in TOOLS and not shutil.which(c[0]):
            return f"missing tool {c[0]} (install: {TOOLS[c[0]]})"
    return None

def new_books(books_root, md_root):
    """Books with no Markdown yet (same relative path, .md), as RECONVERT.csv-style rows."""
    rows = []
    for src in sorted(books_root.rglob("*")):
        rel = src.relative_to(books_root)
        if src.is_file() and src.suffix.lower() in EXTS and not (md_root / rel).with_suffix(".md").exists():
            rows.append({"path": str(rel), "ext": src.suffix.lower()})
    return rows

def run(cmds):
    for c in cmds:
        try:
            r = subprocess.run(c, capture_output=True, text=True)
        except FileNotFoundError:
            return False, [f"missing tool {c[0]}"]
        if r.returncode != 0:
            return False, (r.stderr or r.stdout).strip().splitlines()[-1:] or ["failed"]
    return True, []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--books-root", required=True, type=Path)
    ap.add_argument("--md-root", required=True, type=Path)
    ap.add_argument("--only", default="", help="comma list of extensions, e.g. pdf,djvu")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--mode", choices=["fast", "balanced"], help="marker mode (default: balanced on GPU, fast on CPU)")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--new", action="store_true", help="convert every book with no .md yet, instead of RECONVERT.csv")
    a = ap.parse_args()
    only = {"." + e.strip(". ").lower() for e in a.only.split(",") if e.strip()}
    rows = new_books(a.books_root, a.md_root) if a.new else list(csv.DictReader(open(LIB / "RECONVERT.csv", encoding="utf-8")))
    if only:
        rows = [r for r in rows if r["ext"] in only]
    if a.limit:
        rows = rows[: a.limit]
    log = []
    for i, r in enumerate(rows, 1):
        rel = Path(r["path"].lstrip("./"))
        src, dest = a.books_root / rel, (a.md_root / rel).with_suffix(".md")
        if dest.exists():
            continue
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            cmds, kind = plan(src, dest, tmp, a.mode)
            print(f"[{i}/{len(rows)}] {rel}")
            for c in cmds:
                print("   $", " ".join(f'"{x}"' if " " in x else x for x in c))
            if not a.run or not cmds:
                continue
            if not src.exists():
                log.append([str(rel), "missing source", ""]); continue
            tool = missing_tool(cmds)
            if tool:
                log.append([str(rel), "skipped", tool]); print("   -> skipped:", tool); continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            ok, err = run(cmds)
            if ok and kind == "marker":
                ok = collect_marker(tmp, Path(cmds[-1][1]).stem, dest)
                err = [] if ok else ["marker produced no markdown"]
            if not ok and r["ext"] == ".epub":  # retry broken epub through calibre
                fixed = tmp / "fixed.epub"
                ok, err = run([["ebook-convert", str(src), str(fixed)], pandoc(fixed, dest)])
            log.append([str(rel), "ok" if ok else "FAILED", " ".join(err)])
            print("   ->", "ok" if ok else f"FAILED: {' '.join(err)}")
    if a.run and log:
        with open(LIB / "RECONVERT-LOG.csv", "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(log)
        print(f"logged {len(log)} results to library/RECONVERT-LOG.csv")
        skipped = sorted({x[2] for x in log if x[1] == "skipped"})
        if skipped:
            print("skipped for missing tools:", "; ".join(skipped))
    if not a.run:
        print("\nDry run only. Add --run to execute.", file=sys.stderr)

if __name__ == "__main__":
    main()
