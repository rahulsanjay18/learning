#!/usr/bin/env python3
"""Convert books to Markdown with a converter suited to each format (also step 2 of scripts/add_books.py).

Default is a DRY RUN that only prints commands. Add --run to execute.
Never modifies your originals. Skips any book whose .md already exists.

  pdf        -> marker_single (does its own OCR on scanned pages; LaTeX for equations)
  djvu       -> ddjvu -> pdf -> marker_single
  azw3/mobi  -> calibre ebook-convert -> epub -> pandoc
  epub       -> pandoc (retry); falls back to calibre repair -> pandoc
  html/docx  -> pandoc
  txt        -> copied as .md

Usage (paths default to scripts/library_paths.py):
  python3 scripts/reconvert.py              # dry run: books with no Markdown yet, and which PDFs need OCR
  python3 scripts/reconvert.py --run        # convert them (clean PDFs from their text layer; add --pdf for scans/math)
  python3 scripts/reconvert.py --csv --run  # the old retry list, library/RECONVERT.csv
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

def run_cmds(cmds):
    for c in cmds:
        try:
            r = subprocess.run(c, capture_output=True, text=True)
        except FileNotFoundError:
            return False, [f"missing tool {c[0]}"]
        if r.returncode != 0:
            return False, (r.stderr or r.stdout).strip().splitlines()[-1:] or ["failed"]
    return True, []

def pdf_text(src):
    """The PDF's own text layer (no OCR): PyMuPDF if installed, else poppler's pdftotext. "" if neither works."""
    try:
        import pymupdf
        with pymupdf.open(src) as doc:
            return "\n".join(page.get_text() for page in doc)
    except ImportError:
        pass
    except Exception:
        return ""
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-layout", str(src), "-"], capture_output=True, text=True, errors="replace")
        return r.stdout if r.returncode == 0 else ""
    return ""

def pdf_check(src):
    """Is this PDF easy (clean text layer, no broken math)? Grades its text layer with grade_library's rules:
    A = easy; B (math/figures), C (garbled), F (scan or empty) need marker. Returns (easy, grade, reason)."""
    import grade_library
    g, flags = grade_library.grade(grade_library.stats(pdf_text(src)))
    return g == "A", g, "; ".join(flags)

def convert_pdf_light(src, dest):
    """Text-layer PDF -> Markdown without OCR: pymupdf4llm (keeps headings) if installed, else the plain text layer."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        import pymupdf4llm
        try:
            md = pymupdf4llm.to_markdown(str(src), use_ocr=False, show_progress=False)
        except TypeError:
            md = pymupdf4llm.to_markdown(str(src))
    except ImportError:
        md = pdf_text(src)
    if not md.strip():
        return False, ["no text layer"]
    dest.write_text(md, encoding="utf-8")
    return True, []

def convert_one(rel, books_root, md_root, mode=None, light=False):
    """Convert one book (path relative to books_root). Returns (status, message): ok / FAILED / skipped / missing source."""
    src, dest = books_root / rel, (md_root / rel).with_suffix(".md")
    if not src.exists():
        return "missing source", ""
    if light and src.suffix.lower() == ".pdf":
        ok, err = convert_pdf_light(src, dest)
        return ("ok" if ok else "FAILED"), " ".join(err)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        cmds, kind = plan(src, dest, tmp, mode)
        if not cmds:
            return "skipped", f"unsupported format {src.suffix}"
        tool = missing_tool(cmds)
        if tool:
            return "skipped", tool
        dest.parent.mkdir(parents=True, exist_ok=True)
        ok, err = run_cmds(cmds)
        if ok and kind == "marker":
            ok = collect_marker(tmp, Path(cmds[-1][1]).stem, dest)
            err = [] if ok else ["marker produced no markdown"]
        if not ok and src.suffix.lower() == ".epub":  # retry broken epub through calibre
            fixed = tmp / "fixed.epub"
            ok, err = run_cmds([["ebook-convert", str(src), str(fixed)], pandoc(fixed, dest)])
        return ("ok" if ok else "FAILED"), " ".join(err)

def convert_all(rows, books_root, md_root, mode=None, dry=False):
    """Convert rows ({"path", "ext"[, "light"]}) with a progress bar; returns [[path, status, message], ...] (also logged).
    Rows with "light" are PDFs that pdf_check() found easy: converted from their text layer, no marker."""
    from tqdm import tqdm
    light = {str(Path(r["path"].lstrip("./"))) for r in rows if r.get("light")}
    todo = [Path(r["path"]) for r in rows]
    if dry:
        for rel in todo:
            print("  would convert:", rel, "(text layer)" if str(rel) in light else "")
        return []
    log = []
    with tqdm(todo, desc="convert", unit="book") as bar:
        for rel in bar:
            bar.set_postfix_str(rel.name[:40])
            status, msg = convert_one(rel, books_root, md_root, mode, light=str(rel) in light)
            log.append([str(rel), status, msg])
            if status != "ok":
                bar.write(f"  {status}: {rel}" + (f" ({msg})" if msg else ""))
    if log:
        with open(LIB / "RECONVERT-LOG.csv", "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(log)
        skipped = sorted({x[2] for x in log if x[1] == "skipped" and x[2].startswith("missing tool")})
        if skipped:
            print("skipped for missing tools:", "; ".join(skipped))
    return log

EASY = {".epub", ".azw3", ".mobi", ".html", ".htm", ".docx", ".txt"}  # convert cleanly, no OCR

def failed_before():
    """Books whose latest attempt in RECONVERT-LOG.csv FAILED (paths relative to the books root)."""
    log = LIB / "RECONVERT-LOG.csv"
    if not log.exists():
        return set()
    last = {}
    for row in csv.reader(open(log, encoding="utf-8")):
        if len(row) >= 2:
            last[row[0]] = row[1]
    return {p for p, s in last.items() if s == "FAILED"}

def select(books_root, md_root, from_csv=False, pdf=False, retry_failed=False, only="", limit=0):
    """Which books to convert. Default: every book with no .md yet (or RECONVERT.csv with from_csv), minus earlier failures.
    PDFs are checked with pdf_check(): clean ones convert from their text layer; scans/math/DjVu only with pdf=True.
    Returns (rows, hard, n_failed_skipped)."""
    from tqdm import tqdm
    rows = list(csv.DictReader(open(LIB / "RECONVERT.csv", encoding="utf-8"))) if from_csv else new_books(books_root, md_root)
    for r in rows:
        r["path"] = str(Path(r["path"].lstrip("./")))
    skip = set() if retry_failed else failed_before()
    n_skipped = sum(r["path"] in skip for r in rows)
    rows = [r for r in rows if r["path"] not in skip and not (md_root / r["path"]).with_suffix(".md").exists()]
    exts = {"." + e.strip(". ").lower() for e in only.split(",") if e.strip()}
    if exts:
        rows = [r for r in rows if r["ext"] in exts]
    for r in tqdm([r for r in rows if r["ext"] == ".pdf"], desc="check pdfs", unit="pdf"):
        r["light"], g, why = pdf_check(books_root / r["path"])
        r["why"] = f"grade {g}" + (f": {why}" if why else "")
    hard = [r for r in rows if r["ext"] not in EASY and not r.get("light")]
    if not pdf:
        rows = [r for r in rows if r["ext"] in EASY or r.get("light")]
    return (rows[:limit] if limit else rows), hard, n_skipped

def add_args(ap):
    """The conversion flags, shared by this script and scripts/add_books.py."""
    from library_paths import BOOKS_ROOT, MD_ROOT
    ap.add_argument("--books-root", type=Path, default=BOOKS_ROOT)
    ap.add_argument("--md-root", type=Path, default=MD_ROOT)
    ap.add_argument("--only", default="", help="only these extensions, e.g. epub,pdf")
    ap.add_argument("--limit", type=int, default=0, help="convert at most N books")
    ap.add_argument("--pdf", action="store_true", help="also scanned/math PDFs and DjVu (marker: OCR + LaTeX, slow)")
    ap.add_argument("--mode", choices=["fast", "balanced"], help="marker mode for --pdf (default: balanced on GPU, fast on CPU)")
    ap.add_argument("--retry-failed", action="store_true", help="also retry books that failed before")
    ap.add_argument("--csv", action="store_true", help="convert library/RECONVERT.csv instead of every book without Markdown")

def run(a, dry=False):
    """Select, report and convert (the whole conversion step). Returns the log rows."""
    for root, name in ((a.books_root, "books root"), (a.md_root, "markdown root")):
        if not root.is_dir():
            sys.exit(f"{name} not found: {root} (is the drive mounted?)")
    tools = [t for t in TOOLS if a.pdf or t not in ("marker_single", "ddjvu")]
    print("converters:", ", ".join(f"{t} {'ok' if shutil.which(t) else 'MISSING'}" for t in tools))
    rows, hard, n_skipped = select(a.books_root, a.md_root, a.csv, a.pdf, a.retry_failed, a.only, a.limit)
    if hard:
        print(f"{len(hard)} books need OCR/marker" + ("" if a.pdf else ": not converted (add --pdf to include them)"))
        for r in hard[:20]:
            print(f"  {r['path']}  ({r.get('why') or r['ext']})")
        if len(hard) > 20:
            print(f"  … and {len(hard) - 20} more")
    print(f"{len(rows)} books to convert" + (f" ({n_skipped} earlier failures skipped; --retry-failed to retry)" if n_skipped else ""))
    log = convert_all(rows, a.books_root, a.md_root, a.mode, dry=dry)
    if log:
        print(f"converted {sum(x[1] == 'ok' for x in log)}/{len(log)}; logged to library/RECONVERT-LOG.csv")
    return log

def main():
    ap = argparse.ArgumentParser(description="Convert books to Markdown (dry run unless --run).")
    add_args(ap)
    ap.add_argument("--run", action="store_true", help="actually convert (default: list only)")
    ap.add_argument("--new", action="store_true", help=argparse.SUPPRESS)  # old flag; new books are now the default
    a = ap.parse_args()
    run(a, dry=not a.run)
    if not a.run:
        print("\nDry run only. Add --run to execute.", file=sys.stderr)

if __name__ == "__main__":
    main()
