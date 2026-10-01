#!/usr/bin/env python3
"""Grade converted markdown books so skills only trust clean text.

Grades (see library/README.md for how skills must use them):
  A  clean text, math (if any) is real LaTeX        -> may teach/quote from it
  B  prose fine, but math/figures/tables unreliable -> prose only; equations/figures: cite page, user checks original
  C  heavily garbled                                -> table of contents only (for locating chapters)
  F  empty / failed / scanned                       -> excluded

Usage:
  python3 scripts/grade_library.py --md-root ~/BooksMD [--src-root ~/Books] [--copy A,B] [--sample 0]

Writes library/MANIFEST.csv, library/toc/<id>.md for every non-F book, and (with --copy)
library/text/<id>.md for the grades you list. Nothing is ever modified in --md-root.
"""
import argparse, csv, hashlib, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "library"
SRC_EXT = [".epub", ".azw3", ".mobi", ".pdf", ".djvu", ".html", ".htm", ".docx", ".txt"]  # preference order

LATEX = re.compile(r"\$\$|\\\(|\\\[|\$[^$\n]{1,200}\$|\\(frac|sum|int|alpha|beta|theta|sigma|mathbf|mathrm|partial|sqrt|cdot|leq|geq)\b")
MATHSYM = re.compile(r"[∑∫∂√∞≤≥≠≈±×÷∈∀∃∇αβγδθλμσπΣΠΩ]")
CID = re.compile(r"\(cid:\d+\)")
IMG = re.compile(r"!\[[^\]]*\]\([^)]*\)|<!--\s*image\s*-->|<img\b", re.I)
HEADING = re.compile(r"^(#{1,3})\s+(.{2,120})$", re.M)

def stats(text):
    lines = [l for l in text.splitlines() if l.strip()]
    words = re.findall(r"\w+", text)
    n_lines = max(len(lines), 1)
    short = sum(1 for l in lines if len(l.strip()) <= 3)                    # "exploded" equations
    sym_lines = sum(1 for l in lines if MATHSYM.search(l) and not LATEX.search(l))
    alnum = sum(c.isalnum() or c.isspace() for c in text)
    return {
        "words": len(words),
        "latex": len(LATEX.findall(text)),
        "raw_math_line_pct": round(100 * sym_lines / n_lines, 2),
        "short_line_pct": round(100 * short / n_lines, 2),
        "garbage_pct": round(100 * (text.count("\ufffd") + len(CID.findall(text)) * 5) / max(len(text), 1), 3),
        "nonalnum_pct": round(100 * (1 - alnum / max(len(text), 1)), 2),
        "images_per_10k_words": round(1e4 * len(IMG.findall(text)) / max(len(words), 1), 1),
        "headings": len(HEADING.findall(text)),
    }

def grade(s):
    flags = []
    if s["words"] < 3000 or s["garbage_pct"] > 1.0:
        return "F", ["too short or unreadable (scan/encoding?)"]
    math_heavy = s["raw_math_line_pct"] > 5
    if s["garbage_pct"] > 0.2 or s["nonalnum_pct"] > 35 or (s["short_line_pct"] > 30 and not math_heavy):
        return "C", ["garbled text"]
    g = "A"
    if s["raw_math_line_pct"] > 2 or (s["short_line_pct"] > 12 and s["latex"] < 20):
        g = "B"; flags.append("math not LaTeX: equations unreliable")
    if s["images_per_10k_words"] > 15:
        g = "B"; flags.append("figure-heavy: figures missing/unreliable")
    if s["headings"] < 5:
        flags.append("few headings: weak navigation")
    return g, flags

def source_for(md, md_root, src_root):
    if not src_root:
        return "", ""
    rel = md.relative_to(md_root).with_suffix("")
    for ext in SRC_EXT:
        cand = src_root / (str(rel) + ext)
        if cand.exists():
            return ext.lstrip("."), str(cand.relative_to(src_root))
    return "", ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md-root", required=True, type=Path)
    ap.add_argument("--src-root", type=Path)
    ap.add_argument("--copy", default="", help="grades whose text to copy into library/text, e.g. A,B")
    ap.add_argument("--copy-categories", default="", help="only copy text for these top-level folders, comma-separated")
    ap.add_argument("--sample", type=int, default=0, help="only grade the first N files (dry run)")
    a = ap.parse_args()
    copy = {g.strip().upper() for g in a.copy.split(",") if g.strip()}
    cats = {c.strip() for c in a.copy_categories.split(",") if c.strip()}
    mds = sorted(p for p in a.md_root.rglob("*.md") if "/tmp/" not in p.as_posix())
    if a.sample:
        mds = mds[: a.sample]
    (ROOT / "toc").mkdir(parents=True, exist_ok=True)
    if copy:
        (ROOT / "text").mkdir(parents=True, exist_ok=True)
    rows, counts = [], {}
    for i, md in enumerate(mds, 1):
        text = md.read_text(encoding="utf-8", errors="replace")
        s = stats(text)
        g, flags = grade(s)
        rel = md.relative_to(a.md_root)
        bid = hashlib.sha1(str(rel).encode()).hexdigest()[:10]
        fmt, src = source_for(md, a.md_root, a.src_root)
        if fmt in ("pdf", "djvu") and g == "A" and s["latex"] == 0 and s["raw_math_line_pct"] > 0.5:
            g = "B"; flags.append("PDF source with stray math symbols")
        if g != "F":
            heads = [f"{'  ' * (len(h) - 1)}- {t.strip()}" for h, t in HEADING.findall(text)]
            (ROOT / "toc" / f"{bid}.md").write_text(f"# TOC: {rel.stem}\ngrade: {g}\n\n" + "\n".join(heads[:400]) + "\n", encoding="utf-8")
        if g in copy and (not cats or (len(rel.parts) > 1 and rel.parts[0] in cats)):
            shutil.copyfile(md, ROOT / "text" / f"{bid}.md")
        rows.append({"id": bid, "grade": g, "flags": "; ".join(flags), "category": rel.parts[0] if len(rel.parts) > 1 else "",
                     "title": rel.stem, "source_format": fmt, "source_path": src, "md_path": str(rel), **s})
        counts[g] = counts.get(g, 0) + 1
        if i % 200 == 0:
            print(f"  {i}/{len(mds)}", file=sys.stderr)
    with open(ROOT / "MANIFEST.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("grades:", dict(sorted(counts.items())), f"-> {ROOT/'MANIFEST.csv'}")

if __name__ == "__main__":
    main()
