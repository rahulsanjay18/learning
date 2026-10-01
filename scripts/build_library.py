#!/usr/bin/env python3
"""Turn a book-list CSV (Goodreads export, Calibre CSV catalog, or any CSV with
title/author columns) into library/LIBRARY.md for the /teach skill.

Usage: python3 scripts/build_library.py my_books.csv [more.csv ...]
"""
import csv, re, sys
from pathlib import Path

ALIASES = {
    "title":  ["title"],
    "author": ["author", "authors", "author l-f"],
    "extra":  ["additional authors"],
    "isbn":   ["isbn13", "isbn", "isbn10"],
    "tags":   ["bookshelves", "tags", "shelves", "subjects", "genre"],
    "status": ["exclusive shelf", "status"],
    "format": ["formats", "format", "binding"],
}

def pick(row, key):
    lower = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
    for name in ALIASES[key]:
        if lower.get(name):
            return lower[name]
    return ""

def clean_isbn(s):  # Goodreads wraps ISBNs as ="9780..."
    return re.sub(r"[^0-9Xx]", "", s)

def main(paths):
    books = {}
    for p in paths:
        with open(p, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                title = pick(row, "title")
                if not title:
                    continue
                author = ", ".join(a for a in [pick(row, "author"), pick(row, "extra")] if a)
                new = {"title": title, "author": author, "isbn": clean_isbn(pick(row, "isbn")),
                       "tags": pick(row, "tags"), "status": pick(row, "status"), "format": pick(row, "format")}
                key = re.sub(r"\W+", " ", title.lower()).strip()
                old = books.get(key)
                if old:  # same book from two exports: keep the richer value per field
                    for k, v in new.items():
                        if k == "format" and v and old[k] and v not in old[k]:
                            old[k] = f"{old[k]}, {v}"
                        elif len(v) > len(old[k]):
                            old[k] = v
                else:
                    books[key] = new
    out = ["# My Library", "",
           "Books I own or have access to. When building RESOURCES.md for any topic, check here FIRST",
           "and prefer these over new sources when they are high-trust and on-mission.", ""]
    for b in sorted(books.values(), key=lambda b: (b["author"].lower(), b["title"].lower())):
        meta = [f"ISBN {b['isbn']}" if b["isbn"] else "", b["format"],
                f"tags: {b['tags']}" if b["tags"] else "", b["status"]]
        meta = " · ".join(m for m in meta if m)
        out.append(f"- _{b['title']}_ — {b['author'] or 'unknown author'}" + (f"  \n  {meta}" if meta else ""))
    dest = Path(__file__).resolve().parent.parent / "library" / "LIBRARY.md"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {len(books)} books to {dest}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
