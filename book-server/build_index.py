#!/usr/bin/env python3
"""Build a full-text index of A/B-grade books for the book server.

Reads library/MANIFEST.csv (from scripts/grade_library.py) and the markdown under --md-root.
Only grades A and B are indexed, so C/F text can never be served.

Usage: python3 build_index.py --manifest ../library/MANIFEST.csv --md-root ~/BooksMD --db books.db
"""
import argparse, csv, sqlite3
from pathlib import Path

CHUNK = 40  # lines per searchable chunk

def build(manifest, md_root, db_path):
    """Rebuild db_path from the manifest's A/B books. Returns the number indexed."""
    from tqdm import tqdm
    rows = [r for r in csv.DictReader(open(manifest, encoding="utf-8")) if r["grade"] in ("A", "B")]
    tmp = Path(str(db_path) + ".new")  # build beside, then swap, so a running server never sees a half-built db
    if tmp.exists():
        tmp.unlink()
    db = sqlite3.connect(tmp)
    db.executescript("""
        CREATE TABLE books(id TEXT PRIMARY KEY, title TEXT, grade TEXT, flags TEXT, category TEXT, md_path TEXT, n_lines INT);
        CREATE VIRTUAL TABLE chunks USING fts5(book_id UNINDEXED, start_line UNINDEXED, body, tokenize='porter unicode61');
    """)
    n = 0
    for r in tqdm(rows, desc="index", unit="book"):
        p = md_root / r["md_path"]
        if not p.exists():
            continue
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        db.execute("INSERT INTO books VALUES (?,?,?,?,?,?,?)",
                   (r["id"], r["title"], r["grade"], r["flags"], r["category"], r["md_path"], len(lines)))
        db.executemany("INSERT INTO chunks VALUES (?,?,?)",
                       [(r["id"], i + 1, "\n".join(lines[i:i + CHUNK])) for i in range(0, len(lines), CHUNK)])
        n += 1
    db.commit(); db.close()
    tmp.replace(db_path)
    print(f"indexed {n} A/B books -> {db_path}")
    return n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--md-root", required=True, type=Path)
    ap.add_argument("--db", default="books.db", type=Path)
    a = ap.parse_args()
    build(a.manifest, a.md_root, a.db)

if __name__ == "__main__":
    main()
